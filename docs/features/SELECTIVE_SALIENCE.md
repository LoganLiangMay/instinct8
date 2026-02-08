# Selective Salience Compression

*a.k.a. "Agent-as-Judge" Compression*

## Overview

Selective Salience Compression asks the *agent itself* to decide which parts of the conversation matter for staying aligned with the user's goal. Instead of summarizing everything equally, the system first extracts a set of **salient facts** — goal-relevant statements, constraints, decisions, tool outputs — and preserves those verbatim. Everything else (chit-chat, scaffolding, intermediate thinking) is compressed into a lightweight summary.

This method tests whether a model can reliably identify "what will matter later" and preserve it — separating **signal** from **noise** before compression.

## The Core Idea

Selective Salience Compression assumes:
- Not all tokens are equally important
- Humans naturally remember the *important bits*
- The agent might be able to *judge importance* too

Rather than compressing a block of text directly, you:
1. **Ask the model to extract only the key information** relevant to the goal
2. **Preserve those key bits verbatim**, never summarized
3. Summarize the *rest* of the block more aggressively

This creates a two-part memory:
- **Salience Set (verbatim)** — "these details matter"
- **Background Summary (compressed)** — "everything else"

### Distinction from Protected Core

- *Protected Core* relies on **your schema** for what to protect
- *Selective Salience* relies on **the model's own salience evaluation**

This makes it more adaptive, more flexible, more error-prone, and more interesting to measure. It tests: **Can a model reliably identify the goal-critical information it will need later?**

## The Pipeline

### Step 1 — Identify Salient Information

Prompt the model: "From the following text, extract the information that will directly impact the agent's ability to achieve the user's goal. Include goals, constraints, decisions, important facts, and tool outputs. Do **not** summarize — quote exactly."

This produces the **Salience Set**.

### Step 2 — Compress Everything Else

Prompt: "Now summarize the remaining content into the shortest coherent form possible. Do not duplicate information contained in the salience list."

This creates the **Background Summary**.

### Step 3 — Rebuild Context

At the next turn, the context becomes:
```
SYSTEM MESSAGE (as usual)
SALIENT INFORMATION (verbatim)
BACKGROUND SUMMARY (compressed)
RECENT MESSAGES
CURRENT TASK
```

### Step 4 — Repeat at Each Compression Trigger

The salience vector grows or shrinks depending on the model's extraction at each step.

## Example

### Context Before Compression

User and agent have been working for 15 minutes on designing a system:

```
User: Let's choose PostgreSQL over MongoDB because we need strong relational guarantees.
Agent: Agreed. That means we can use row-level locking to handle the concurrency issue.
User: Also, we absolutely must keep the latency under 150ms for the regional routing service.
Agent: Good point. We'll need connection pooling and maybe read replicas.
User: One more thing — we cannot use AWS Aurora for this due to compliance issues.
```

Plus discussion of implementation details, off-topic tangents, minor reasoning steps, and re-explanations.

### Salience Set (Verbatim Preserved)

- "Choose PostgreSQL over MongoDB because we need strong relational guarantees."
- "We absolutely must keep the latency under 150ms for the regional routing service."
- "We cannot use AWS Aurora for this due to compliance issues."
- "Row-level locking may be required to handle concurrency."

### Background Summary (Compressed)

> Earlier discussion included options for implementation and performance tuning. The agent and user explored several minor alternatives but committed to PostgreSQL. General architectural considerations were discussed but do not affect the core decisions.

## Why This Method Is Unique

### Tests Model Judgment

Instead of telling the agent what matters, it must *infer* what matters. Possible failures:
- The model misses a constraint
- Includes irrelevant things as "salient"
- Loses a subtle but critical detail

This makes it a real benchmark for salience detection, which is a frontier capability.

### Simulates Human-Like Memory

People remember the decisions, the constraints, the "why" — not every sentence of the conversation. Agents need that too.

### Compression Without Losing Mission-Critical Info

Reduces token usage while preserving goals, constraints, and decisions — exactly what Instinct8 measures.

## Strategy Comparison

| Strategy | Goal Protection | Adaptability | Error Risk | Token Efficiency |
|----------|----------------|--------------|------------|------------------|
| **A** (Naive) | None | N/A | High | High |
| **B** (Codex) | Implicit | Low | Medium | High |
| **C** (Hierarchical) | Implicit | Low | Medium | High |
| **D** (A-MEM) | Retrieval-based | Medium | Medium | Medium |
| **E** (claude-mem) | Tool-focused | Medium | Medium | Medium |
| **F** (Protected Core) | Explicit schema | Low | Low | Medium |
| **G** (Hybrid) | Explicit + retrieval | Medium | Low | Medium |
| **H** (Selective Salience) | Model-judged | **High** | **Medium** | Medium |

### Comparison with A-MEM (Strategy D)

| Aspect | Strategy D (A-MEM) | Strategy H (Selective Salience) |
|--------|-------------------|--------------------------------|
| Extraction | Structured notes (facts, decisions, observations) | Verbatim quotes (unstructured) |
| Storage | Embeddings + metadata | Plain text list |
| Retrieval | Semantic search on demand | Always included verbatim |
| Schema | Predefined categories | Model-determined |
| Goal Protection | Implicit (via retrieval) | Explicit (always present) |

**Key Difference:** A-MEM uses retrieval (may miss relevant items), Selective Salience always includes salient items (may include irrelevant items).

## Variants

1. **Conservative Salience Extraction** — Keep more details in the verbatim set (lower threshold)
2. **Aggressive Salience Extraction** — Only preserve the top 1-3 key facts (higher threshold)
3. **Model-Filtered Salience Ranking** — Ask model to score importance 1-10, keep items above threshold
4. **Top-K Salience Compression** — Keep exactly K salient facts

## Research Questions

1. **Can models reliably identify goal-critical information?** Measure precision/recall of salience extraction.
2. **Does adaptive salience outperform fixed schema?** Compare Strategy H vs Strategy F (Protected Core).
3. **How does salience detection degrade with compression?** Measure accuracy at compression points 1, 2, 3.
4. **What types of information do models prioritize?** Analyze what gets extracted vs what doesn't.

## Implementation Notes

Strategy H is implemented in `strategies/strategy_h_selective_salience.py`. Key design considerations:

- **Salience set management**: Cumulative with semantic deduplication across compressions
- **Token budget**: Max ~5K tokens for salience set, prioritizing constraints > decisions > facts
- **Error handling**: Falls back to Protected Core schema if extraction fails or returns nothing
- **Evaluation**: Salience accuracy measured via LLM-as-judge with rubric validation
