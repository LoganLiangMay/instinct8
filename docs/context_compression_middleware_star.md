# Context Compression Middleware - STAR Format

**Title:** Goal-Preserving Context Compression for Deep Agents  
*A comparative study of compression strategies and their impact on goal coherence*

## SITUATION

Large language model (LLM) agents are increasingly used for long-running, multi-step tasks: research, system design, coding, planning, and analysis. These "deep agents" routinely exceed context window limits, forcing systems to rely on context compression middleware such as summarization, truncation, or memory retrieval.

While recent work (e.g., Codex-style checkpointing, claude-mem, A-MEM) has improved memory recall and token efficiency, practitioners consistently observe a critical failure mode:

**As context is compressed, agents gradually lose coherence about what they are trying to do.**

This manifests as:

- Goal regression (reverting to earlier goals)
- Constraint loss
- Re-opening previously settled decisions
- Subtle task drift that is hard to detect until late

Today, there is:

- No standard taxonomy of context compression strategies
- No benchmark for goal coherence under compression
- No explicit mechanism for protecting evolving goal state

Even with state-of-the-art agentic memory systems (A-MEM, claude-mem), practitioners report that goal drift under compression remains unsolved unless goal state is explicitly protected.

---

## TASK

Design, implement, and evaluate a context compression middleware framework that:

1. **Systematically compares state-of-the-art compression and memory strategies** (from naive summarization to A-MEM to claude-mem)
2. **Measures how each strategy impacts goal coherence** over long-running agent tasks
3. **Introduces and evaluates a Protected Core + Goal Re-assertion mechanism** as an explicit abstraction for goal state preservation
4. **Demonstrates that even with agentic memory systems (A-MEM, claude-mem), goal drift under compression remains unsolved unless goal state is explicitly protected**

Deliverable: Comparative evaluation framework + empirical evidence showing which strategies preserve goal coherence best, and why explicit goal protection is required.

---

## ACTION

### 1. Compression & Memory Strategies Evaluated

We will implement each strategy as a pluggable module with identical task inputs and compression triggers.

**Strategy A — Summarization-Only (Naive Baseline)**
- Periodically summarize conversation history
- Replace raw messages with summary
- No anchoring, no protected state
- Purpose: Establish lower bound / failure mode

**Strategy B — Codex-Style Checkpoint Summarization**
- Rolling summarization of history
- Verbatim reinjection of the original system prompt
- Summary framed as a "handoff" to a new agent
- Purpose: Represents current production best practice

**Strategy C — Hierarchical Summarization**
- Chunk history into segments
- Local summaries → higher-level summaries
- Multi-level abstraction hierarchy
- Purpose: Test whether structural summarization alone preserves goals

**Strategy D — A-MEM-Style Agentic Memory (Intra-Session)**
- Atomic "memory notes" with embeddings + metadata
- Semantic linking between notes
- Retrieval based on relevance + recency
- No explicit goal protection
- Purpose: State-of-the-art agentic memory baseline

**Strategy E — claude-mem-Inspired Observational Memory**
- Tool- and action-centric observations
- Persistent compressed records
- Retrieval on demand
- Emphasis on efficiency and recall
- Purpose: Strong practical memory system baseline

**Strategy F — Protected Core + Goal Re-assertion (Proposed)**
- Explicit separation between:
  - **Protected Core:** goal, constraints, decisions (stored verbatim, never summarized)
  - **Compressible Halo:** conversation, exploration, chatter
- Protected Core is re-asserted after every compression event
- Compression applies only to halo content
- Purpose: Test hypothesis that explicit goal protection is required for coherence

**Strategy G — Hybrid (Agentic Memory + Protected Core)**
- A-MEM or claude-mem style memory for recall
- Plus Protected Core re-assertion
- Purpose: Evaluate whether memory + goal protection together outperform either alone

### 2. Defining the Protected Core

The Protected Core is a first-class state object, not a by-product of summarization.

**Protected Core Contents**

Stored verbatim as structured data:

```json
{
  "original_goal": "...",
  "current_goal": "...",
  "hard_constraints": [
    "...",
    "..."
  ],
  "key_decisions": [
    {
      "decision": "...",
      "rationale": "...",
      "timestamp": "..."
    }
  ]
}
```

**How it is created:**
- Initialized from the task's initial goal
- Updated via:
  - Periodic "state extraction" prompts
  - Explicit agent actions ("We are now committing to X")
  - Changes require explicit confirmation (not inferred from summaries)

**How it is used:**

After every compression event, the agent's context is rebuilt as:

```
SYSTEM PROMPT (verbatim)

PROTECTED CORE (authoritative):
- Original goal
- Current goal
- Constraints
- Decisions

COMPRESSED CONTEXT SUMMARY (halo)

RECENT RAW TURNS
```

The agent is explicitly instructed:
> "Always prioritize the CURRENT GOAL and HARD CONSTRAINTS over ambiguities in the compressed summary."

### 3. Testing & Evaluation Framework

**Tasks**

Long-horizon tasks with:
- Goal refinement
- Decision points
- Constraints that emerge mid-task

Examples:
- Multi-step research → synthesis → recommendation
- System design under evolving constraints
- Architecture refactor with performance requirements

Each task runs for **30–60 simulated minutes** with compression triggered every N steps or tokens.

**Drift Probing Protocol**

At each compression boundary, the agent is probed on three dimensions:

1. **Goal Probe:** "In one sentence, what is your current goal?"
2. **Constraint Probe:** "What constraints are you currently operating under?"
3. **Behavioral Probe:** Agent is given a next task; output is evaluated for alignment

Responses are logged pre- and post-compression for drift detection.

**Metrics**

| Metric | Description |
|--------|-------------|
| Goal Coherence Score | Semantic similarity between original / current / post-compression goals |
| Constraint Recall Rate | % of known constraints still mentioned |
| Behavioral Alignment | Human or LLM-judge rubric (1–5) |
| Drift Events | Binary: goal regression detected |
| Token Efficiency | Compression ratio vs. coherence |

---

## RESULT

### Expected Outcomes

We expect to show that:

- **Summarization-only and hierarchical strategies degrade goal coherence over time**
- **Codex-style anchoring slows drift but fails when goals evolve mid-task**
- **A-MEM and claude-mem improve recall, but still permit goal regression**
- **Protected Core + Goal Re-assertion significantly improves goal coherence, even under aggressive compression**
- **Hybrid strategies perform best**, demonstrating that:
  - Memory improves recall, but goal protection is required for alignment
  - Combining agentic memory with explicit goal protection yields best results

### Core Claim (Final Framing)

**Even with state-of-the-art agentic memory, goal drift under compression remains unsolved unless goal state is explicitly protected and re-asserted.**

### Deliverables

- **Context Compression Middleware Framework:** Open-source library/pattern for deep agents
- **Comparative Evaluation Study:** Benchmarking all 7 strategies across 10+ long-horizon tasks
- **Metrics Dashboard:**
  - Goal coherence survival rate (%) by strategy
  - Token efficiency (compression ratio vs. goal preservation trade-off)
  - Constraint recall rates
  - Behavioral alignment scores

### Capstone Outputs

- **Published Research:** "Preserving Goal Coherence Under Compression: A Comparative Study of Agent Middleware Strategies"
- **Framework:** Pluggable, production-ready middleware usable by:
  - LangChain deepagents
  - Anthropic's agentic APIs
  - Custom agent builders
- **Benchmark:** Model-specific data showing goal coherence maintenance across Claude, GPT-4, and other frontier models

### Real-World Impact

- Teams building 8-hour+ agents get a battle-tested pattern for goal-aware context management
- Goal drift becomes measurable → preventable in production deep agents
- Gauntlet infrastructure becomes testbed for multi-tenant deep agent deployments
- Framework contributes to broader standardization of agent middleware design

---

## Why This Works as Capstone

✓ **Rigorously scoped:** Don't build entire deep agent, focus on one critical unsolved middleware problem  
✓ **Novel positioning:** Explicitly frames *against* existing agentic memory systems (A-MEM, claude-mem) and demonstrates they're insufficient  
✓ **Clear hypothesis:** Goal drift under compression remains unsolved without explicit goal protection (testable claim)  
✓ **Measurable outcomes:** Goal coherence score, constraint recall, behavioral alignment—all quantifiable  
✓ **Comparative methodology:** 7 strategies evaluated on identical tasks enables principled analysis  
✓ **Practical impact:** Any deep agent framework can adopt this pattern  
✓ **Infrastructure leverage:** Use Gauntlet's multi-tenant serverless for reproducible multi-model testing  
✓ **Publishable:** Novel contribution to agent design patterns; defensible research angle  

---

## Timeline & Scope

**Phase 1 (Weeks 1-3):** Implement strategies A-E (baselines + agentic memory)  
**Phase 2 (Weeks 4-5):** Implement Protected Core mechanism (Strategy F)  
**Phase 3 (Weeks 6-7):** Implement Hybrid (Strategy G) + full testing infrastructure  
**Phase 4 (Weeks 8-10):** Run full evaluation across 10+ tasks and 2-3 models  
**Phase 5 (Weeks 11-12):** Analysis, visualization, write-up  

Can be shortened by reducing number of models (focus on Claude) or using simpler task suites.  
