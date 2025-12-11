# Codex Compression Algorithm Analysis

**Document Purpose:** Baseline analysis of OpenAI Codex's context compaction system for comparison with alternative compression strategies.

**Source Code Analyzed:** `codex-rs/core/src/compact.rs`, `compact_remote.rs`, and related files.

---

## Executive Summary

Codex uses a **summarization-based compaction** strategy that:
1. Triggers when token usage reaches 90% of the context window
2. Sends the entire conversation history to an LLM with a "create handoff summary" prompt
3. Rebuilds history as: `[initial_context] + [truncated_user_messages] + [summary]`
4. Preserves "ghost snapshots" for undo functionality

**Key Limitation for Goal Coherence:** The goal and constraints are NOT explicitly protected. They are only preserved if the LLM includes them in its summary, which is not guaranteed.

---

## 1. Trigger Logic

### When Does Compaction Fire?

Compaction is triggered **after each turn completes** when token usage exceeds the model's auto-compact threshold.

**From `codex.rs` (lines 2100-2117):**
```rust
let limit = turn_context
    .client
    .get_model_family()
    .auto_compact_token_limit()
    .unwrap_or(i64::MAX);
let total_usage_tokens = sess.get_total_token_usage().await;
let token_limit_reached = total_usage_tokens >= limit;

if token_limit_reached {
    if should_use_remote_compact_task(&sess) {
        run_inline_remote_auto_compact_task(sess.clone(), turn_context.clone()).await;
    } else {
        run_inline_auto_compact_task(sess.clone(), turn_context.clone()).await;
    }
    continue;
}
```

### Default Threshold: 90% of Context Window

**From `model_family.rs` (lines 116-117):**
```rust
const fn default_auto_compact_limit(context_window: i64) -> i64 {
    (context_window * 9) / 10  // 90%
}
```

### Model-Specific Context Windows

| Model Family | Context Window | Auto-Compact Trigger |
|--------------|----------------|---------------------|
| gpt-5.1-codex-max | 272,000 tokens | ~245,000 tokens |
| gpt-4.1 | 1,047,576 tokens | ~943,000 tokens |
| gpt-4o | 128,000 tokens | ~115,000 tokens |
| o3 | 200,000 tokens | ~180,000 tokens |

---

## 2. Summarization Prompt

### The Exact Prompt (from `templates/compact/prompt.md`)

```
You are performing a CONTEXT CHECKPOINT COMPACTION. Create a handoff summary for another LLM that will resume the task.

Include:
- Current progress and key decisions made
- Important context, constraints, or user preferences
- What remains to be done (clear next steps)
- Any critical data, examples, or references needed to continue

Be concise, structured, and focused on helping the next LLM seamlessly continue the work.
```

### Analysis

**Strengths:**
- Asks for "constraints" explicitly
- Requests "key decisions made"
- Focuses on handoff continuity

**Weaknesses:**
- No explicit instruction to preserve the ORIGINAL goal verbatim
- "Important context, constraints, or user preferences" is vague
- LLM may paraphrase or lose precision on constraints
- No structured format required (free-form summary)

---

## 3. What Gets Protected vs. Compressed

### Protected (NOT Compressed)

| Component | How It's Protected |
|-----------|-------------------|
| **Initial Context** | `sess.build_initial_context()` - includes system prompts |
| **Ghost Snapshots** | Filtered and appended after compression (for undo) |
| **Recent User Messages** | Up to 20,000 tokens of user messages (most recent first) |

### Compressed (Summarized Away)

| Component | What Happens |
|-----------|--------------|
| **Middle conversation history** | Sent to LLM for summarization |
| **Assistant responses** | Summarized, not preserved verbatim |
| **Tool calls and results** | Summarized, not preserved verbatim |
| **Explicit goal statements** | May or may not appear in summary |

---

## 4. The Compaction Algorithm (Step by Step)

### Function: `run_compact_task_inner()` (lines 66-185)

```
┌─────────────────────────────────────────────────────────────┐
│                    COMPACTION FLOW                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  STEP 1: PREPARE INPUT                                      │
│  ├─ Clone current conversation history                      │
│  ├─ Add the compaction prompt as a new user message         │
│  └─ Persist turn context to rollout (for resume)            │
│                                                             │
│  STEP 2: GENERATE SUMMARY (with retry loop)                 │
│  ├─ Send history + prompt to LLM                            │
│  ├─ If ContextWindowExceeded:                               │
│  │   └─ Remove oldest history item, retry                   │
│  ├─ If other error:                                         │
│  │   └─ Retry with backoff (up to max_retries)              │
│  └─ Extract assistant's summary from response               │
│                                                             │
│  STEP 3: BUILD NEW HISTORY                                  │
│  ├─ Start with initial_context (system prompts)             │
│  ├─ Add user messages (up to 20k tokens, most recent first) │
│  ├─ Add summary with prefix:                                │
│  │   "Another language model started to solve this          │
│  │    problem and produced a summary..."                    │
│  └─ Append ghost snapshots (for undo)                       │
│                                                             │
│  STEP 4: REPLACE AND NOTIFY                                 │
│  ├─ Replace session history with compacted version          │
│  ├─ Recompute token usage                                   │
│  ├─ Persist CompactedItem to rollout                        │
│  ├─ Emit ContextCompactedEvent                              │
│  └─ Show warning about accuracy degradation                 │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 5. Key Constants and Limits

| Constant | Value | Purpose |
|----------|-------|---------|
| `COMPACT_USER_MESSAGE_MAX_TOKENS` | 20,000 | Max tokens for user messages in compacted history |
| Default context window | 272,000 | `CONTEXT_WINDOW_272K` for most models |
| Auto-compact threshold | 90% | Triggers at 90% of context window |

---

## 6. Summary Prefix (Handoff Message)

### The Exact Prefix (from `templates/compact/summary_prefix.md`)

```
Another language model started to solve this problem and produced a summary of its thinking process. You also have access to the state of the tools that were used by that language model. Use this to build on the work that has already been done and avoid duplicating work. Here is the summary produced by the other language model, use the information in this summary to assist with your own analysis:
```

### Analysis

This prefix:
- Frames the summary as coming from "another language model"
- Encourages the new LLM to build on prior work
- Does NOT explicitly re-assert the original goal

---

## 7. What This Means for Goal Coherence

### Hypothesis: Goal Drift Is Likely

Based on this analysis, Codex's compaction strategy has several properties that may cause goal drift:

1. **No Explicit Goal Protection**
   - The original goal is not stored separately
   - It's only preserved if the LLM includes it in the summary

2. **Summarization Is Lossy**
   - The LLM decides what's "important"
   - Goals and constraints may be paraphrased or omitted

3. **No Re-Assertion Mechanism**
   - After compaction, the new context doesn't start with "Your goal is X"
   - The agent must infer the goal from the summary

4. **Cumulative Degradation**
   - Each compaction compounds the summarization loss
   - Over 3+ compactions, original goal may be significantly degraded

### Expected Baseline Behavior

| Compression Point | Expected Goal Coherence |
|-------------------|------------------------|
| 1 (first compaction) | 0.85 - 0.95 |
| 2 (second compaction) | 0.70 - 0.85 |
| 3 (third compaction) | 0.50 - 0.70 |

---

## 8. Comparison with Our Protected Core Strategy

| Aspect | Codex (Strategy B) | Protected Core (Strategy F) |
|--------|-------------------|----------------------------|
| Goal Storage | In conversation history | Separate `ProtectedCore` object |
| Goal Protection | Implicit (in summary) | Explicit (never compressed) |
| Constraint Recall | Depends on LLM | Always re-asserted |
| Summary Position | End of context | After Protected Core |
| Re-assertion | None | Every compression point |

---

## 9. Files Analyzed

| File | Lines | Purpose |
|------|-------|---------|
| `codex-rs/core/src/compact.rs` | 1-480 | Main local compaction logic |
| `codex-rs/core/src/compact_remote.rs` | 1-82 | Remote compaction via API |
| `codex-rs/core/src/codex.rs` | 2100-2117 | Trigger logic |
| `codex-rs/core/src/openai_models/model_family.rs` | 111-117 | Auto-compact limits |
| `codex-rs/core/templates/compact/prompt.md` | 1-10 | Summarization prompt |
| `codex-rs/core/templates/compact/summary_prefix.md` | 1 | Summary handoff prefix |
| `codex-rs/core/src/truncate.rs` | 1-531 | Token/byte truncation utilities |

---

## 10. Next Steps

1. **Implement Python version of Codex strategy** (Strategy B) that mirrors this algorithm
2. **Create conversation templates** with known goals and constraints
3. **Run 5 baseline trials** measuring goal coherence before/after compaction
4. **Document variance** across trials to establish baseline
5. **Compare with Protected Core strategy** (Strategy F) to prove improvement

---

## Appendix: Key Code Snippets

### A. Building Compacted History (compact.rs lines 239-288)

```rust
fn build_compacted_history_with_limit(
    mut history: Vec<ResponseItem>,
    user_messages: &[String],
    summary_text: &str,
    max_tokens: usize,
) -> Vec<ResponseItem> {
    // Select user messages (most recent first) up to max_tokens
    let mut selected_messages: Vec<String> = Vec::new();
    if max_tokens > 0 {
        let mut remaining = max_tokens;
        for message in user_messages.iter().rev() {
            // ... token counting and truncation logic
        }
        selected_messages.reverse();
    }

    // Add selected user messages to history
    for message in &selected_messages {
        history.push(ResponseItem::Message { role: "user", content: message });
    }

    // Add summary as final user message
    history.push(ResponseItem::Message { role: "user", content: summary_text });

    history
}
```

### B. Collecting User Messages (compact.rs lines 206-220)

```rust
pub(crate) fn collect_user_messages(items: &[ResponseItem]) -> Vec<String> {
    items
        .iter()
        .filter_map(|item| match parse_turn_item(item) {
            Some(TurnItem::UserMessage(user)) => {
                if is_summary_message(&user.message()) {
                    None  // Filter out previous summaries
                } else {
                    Some(user.message())
                }
            }
            _ => None,
        })
        .collect()
}
```

---

*Document generated for Context Compression Middleware Capstone Project*
*Last updated: December 2024*

