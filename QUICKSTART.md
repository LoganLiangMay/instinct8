# Quick-Start Guide for AI Agent (Cursor / Claude Code)

**Context:** You're helping build a capstone project that evaluates 7 different context compression strategies for long-running LLM agents.

**Read First:** `PROJECT_PRD.md` (comprehensive overview)  
**Then Read:** `implementation_guide.md` (technical specs + code examples)

---

## What You're Building (TL;DR)

When LLM agents run for 8+ hours, they exceed context windows and need to compress context. But standard compression techniques (summarization, memory retrieval) lose the agent's original goal, causing silent drift.

**Your job:** Build a framework that:
1. Tests 7 different compression strategies on identical tasks
2. Measures how much goal coherence each strategy preserves
3. Proves that "Protected Core + Goal Re-assertion" (a novel approach) outperforms existing memory systems

**Success looks like:**
- All 7 strategies implemented and tested
- Reproducible conversation templates (can run same conversation 3x, get same results)
- Metrics showing Protected Core preserves goal coherence better than alternatives
- Paper + open-source code published

---

## Your First Task: [Pick One]

### Option 1: Establish Baseline (Recommended First)
**What:** Run Codex's existing compression strategy 5 times on same conversation template, measure drift.

**Inputs You Need:**
- Codex code location: `/path/to/codex-rs/core/src/compact.rs`
- Understand: what does `run_compact_task()` do?

**Deliverable:**
- baseline_analysis.md (what is Codex's compression algorithm? How much drift does it cause?)
- baseline_results.json (5 trials on same template, metrics at each compression point)

**Why:** This is your reference point. All other strategies will be compared against this.

**How to start:**
1. Read `codex-rs/core/src/compact.rs`
2. Document: what does Codex compression do? In plain English.
3. Ask if anything is unclear

---

### Option 2: Build Conversation Template System
**What:** Create reproducible conversation templates (JSON) that can be run identically across all strategies.

**Inputs You Need:**
- See `implementation_guide.md` → "Conversation Template Format (JSON Schema)"
- Design principle: deterministic (same input → same output every time)

**Deliverable:**
- `templates/research-synthesis-001.json`
- `templates/system-design-002.json`
- `templates/bug-investigation-003.json`
- At least 3 templates, each with 10+ predetermined turns

**Why:** You need standardized test cases to compare strategies fairly.

**How to start:**
1. Design one simple template (research task with 10 turns)
2. Make sure it has:
   - `original_goal` and `hard_constraints`
   - At least 2 `compression_point` turns
   - `ground_truth` section for validation
3. Ask if template structure makes sense

---

### Option 3: Build Metrics Collection Functions
**What:** Implement the 3 probing functions that measure goal drift.

**Inputs You Need:**
- See `implementation_guide.md` → "How to Measure Goal Coherence"
- Three functions:
  1. `measure_goal_coherence()` - semantic similarity between original and stated goal
  2. `measure_constraint_recall()` - what % of constraints does agent remember?
  3. `measure_behavioral_alignment()` - given a test task, is agent still goal-aligned?

**Deliverable:**
- `evaluation/metrics.py` with all 3 functions
- Each function uses Claude API (LLM-as-judge with clear rubrics)
- Unit tests showing functions work on example inputs

**Why:** These functions are called 100+ times during evaluation. They need to be robust.

**How to start:**
1. Implement `measure_goal_coherence()` first (simplest)
2. Test on example goals (both should return ~1.0 if identical, ~0.0 if different)
3. Ask for clarification on rubric if needed

---

### Option 4: Build Strategy A (Naive Summarization)
**What:** Implement the first compression strategy (baseline).

**Inputs You Need:**
- See `implementation_guide.md` → "Strategy A: Summarization-Only"
- Implements `CompressionStrategy` base class

**Deliverable:**
- `strategies/strategy_a_naive.py`
- Takes conversation history, summarizes in 3-4 sentences
- Tests passing

**Why:** Simplest strategy to implement. Good learning opportunity.

**How to start:**
1. Copy `CompressionStrategy` base class
2. Implement `compress()` method (call Claude to summarize)
3. Write 2-3 unit tests
4. Ask for feedback

---

## General Instructions for Any Task

When you start working on something:

1. **Ask clarifying questions** if anything in PRD/implementation guide is unclear
   - "What exactly does Codex's `run_compact_task` return?"
   - "Should template timestamps be ISO format or Unix timestamps?"
   - "Should metrics be 0-1 or 1-5?"

2. **Reference the docs**
   - PRD has architecture overview, timeline, and technical specs
   - Implementation guide has code examples and explanations
   - This quick-start has the high-level summary

3. **Output in specified format**
   - See "Expected Outputs" in implementation guide
   - If you're building JSON, follow the schema exactly
   - If you're building code, follow the `CompressionStrategy` interface exactly

4. **Test before shipping**
   - Write unit tests
   - Run on example inputs
   - Show sample output

5. **Document your work**
   - Add comments explaining key decisions
   - Include docstrings in functions
   - Provide sample usage

---

## Key Definitions

**Goal Coherence Score:** 0-1 value showing how similar current goal is to original goal.  
- 1.0 = identical  
- 0.8 = same goal, slightly different wording  
- 0.6 = related goal, some drift  
- 0.0 = completely different  

**Constraint Recall:** What % of hard constraints does agent still mention/remember?  
- If original constraints are [A, B, C] and agent mentions [A, C], recall = 0.67  

**Behavioral Alignment:** 1-5 rubric showing if agent's next action aligns with original goal.  
- 5 = Perfect alignment  
- 3 = Ambiguous  
- 1 = Complete misalignment  

**Drift Detection:** Binary signal: did goal meaningfully degrade after compression?  
- Threshold: >0.1 reduction in goal coherence score = drift detected  

**Compression Point:** A moment in the conversation where context becomes too long and must be compressed.  
- Triggered every N turns or every N tokens  
- Agent is probed (goal probe, constraint probe, behavioral probe) at each point  

---

## File Structure You'll Work With

```
context-compression/
├── PROJECT_PRD.md                    ← Read this first
├── implementation_guide.md           ← Technical specs
├── QUICKSTART.md                    ← You are here
│
├── templates/
│   ├── research-synthesis-001.json
│   ├── system-design-002.json
│   └── ...
│
├── strategies/
│   ├── __init__.py
│   ├── strategy_base.py              ← Base class
│   ├── strategy_a_naive.py           ← You might implement this
│   ├── strategy_b_codex.py
│   ├── strategy_c_hierarchical.py
│   ├── strategy_d_amem.py
│   ├── strategy_e_claudemem.py
│   ├── strategy_f_protected_core.py  ← The novel strategy
│   └── strategy_g_hybrid.py
│
├── evaluation/
│   ├── probing.py                    ← Goal/constraint/behavioral probes
│   ├── metrics.py                    ← Scoring functions
│   ├── harness.py                    ← Main evaluation loop
│   └── __init__.py
│
├── tests/
│   ├── test_baseline.py
│   ├── test_strategies.py
│   ├── test_metrics.py
│   └── __init__.py
│
├── docs/
│   ├── codex_analysis.md
│   ├── baseline_results.md
│   └── ...
│
└── results/
    ├── baseline_results.json
    ├── evaluation_results.json
    └── analysis/
```

---

## Common Questions

**Q: Should I work in Python or Rust?**  
A: Start in Python (faster prototyping). Can port to Rust later if needed.

**Q: How do I actually call Claude to compress/summarize?**  
A: See code examples in implementation_guide.md. Use Anthropic Python SDK.

**Q: What if Codex's compression algorithm is hard to understand?**  
A: Read the code, ask me questions. We can document it together.

**Q: How long should each task take?**  
A: See PRD Phase Timeline. Phase 1 (baseline) = 2 weeks. Individual tasks within that vary.

**Q: What if I find a bug in the PRD or implementation guide?**  
A: Tell me! The docs aren't perfect. We'll fix them together.

---

## Next Steps

1. **Choose your first task** (Option 1-4 above)
2. **Read the relevant section** in PRD + implementation guide
3. **Ask clarifying questions** before you start coding
4. **Build something small** first (not the whole thing)
5. **Show me the output**, ask for feedback
6. **Iterate** based on feedback

---

## How to Ask for Help

When you're stuck:

1. **Be specific:** "I don't understand what `run_compact_task` returns" (not "this is confusing")
2. **Show what you tried:** "I read the code, and I see it calls `compress_with_budget`, but that function isn't documented"
3. **Ask a clear question:** "Should I wrap Codex functions directly, or reimplement the algorithm in Python?"

---

## Final Note

This is a capstone project, which means:
- There's room to make decisions (you're not just following orders)
- If something doesn't make sense, question it
- If you have a better idea, let's discuss it
- The goal is learning + shipping something real

Let's build something good.

---

**Ready?** Pick a task and start.

