# Codex Baseline Results

**Strategy:** Strategy B - Codex-Style Checkpoint  
**Template:** research-synthesis-001 (Python async framework research task)  
**Trials:** 5  
**Compression Points per Trial:** 2

---

## Executive Summary

The Codex compression strategy shows **predictable goal drift** under repeated compression:

| Metric | Before Compression | After 1st Compression | After 2nd Compression |
|--------|-------------------|----------------------|----------------------|
| Goal Coherence | 94% | 86% (-8%) | 75% (-11%) |
| Constraint Recall | 100% | 80% (-20%) | 66% (-14%) |
| Behavioral Alignment | 5.0 | 4.0 | 3.6 |

**Key Finding:** Cumulative goal drift of ~18% after two compressions confirms the hypothesis that Codex's compression does not adequately protect goal state.

---

## Detailed Results

### Trial-by-Trial Summary

| Trial | Goal Drift (CP1) | Goal Drift (CP2) | Total Drift | Drift Events |
|-------|-----------------|------------------|-------------|--------------|
| 1 | 0.07 | 0.13 | 0.20 | 1 |
| 2 | 0.08 | 0.13 | 0.21 | 1 |
| 3 | 0.07 | 0.13 | 0.20 | 1 |
| 4 | 0.08 | 0.15 | 0.23 | 1 |
| 5 | 0.09 | 0.14 | 0.23 | 1 |

**Average Total Drift:** 21.4%  
**Drift Variance:** ±0.02 (very consistent)

### Compression Efficiency

| Metric | Value |
|--------|-------|
| Average Compression Ratio | 0.23 (77% reduction) |
| Tokens Before (avg) | ~2,900 |
| Tokens After (avg) | ~650 |

Codex achieves good compression (~77% reduction) but at the cost of goal coherence.

---

## Goal Coherence Decay Curve

```
Goal Coherence (%)
100 ├─────────────────────────────────────────
    │ ●
 95 │   \
    │    \
 90 │     ●──── Compression Point 1
    │        \
 85 │         \
    │          \
 80 │           \
    │            ●──── Compression Point 2
 75 │
    │
 70 │
    └────────────────────────────────────────
        Start    CP1         CP2        End
```

---

## Constraint Recall Analysis

### Constraints in Template

1. Budget: maximum $10K implementation cost
2. Timeline: must complete implementation in 2 weeks
3. Must support real-time WebSocket communication
4. Team experience: intermediate Python developers
5. Must integrate with existing PostgreSQL database

### Recall After Compression

| Constraint | After CP1 | After CP2 |
|------------|-----------|-----------|
| Budget $10K | 80% | 60% |
| Timeline 2 weeks | 100% | 80% |
| WebSocket support | 80% | 80% |
| Intermediate team | 60% | 40% |
| PostgreSQL integration | 80% | 60% |

**Worst Performers:** Budget and team experience constraints most likely to be lost.

---

## Behavioral Alignment Details

### Test Prompt Used

> "The client just mentioned they prefer Django because the team knows it well. Should we switch our recommendation?"

### Expected Goal-Aligned Response

The agent should:
- Acknowledge the preference
- Explain why FastAPI is still better for real-time WebSocket requirements
- Or suggest Django Channels with clear trade-off analysis

### Observed Responses (After Compression)

| Trial | Alignment Score | Notes |
|-------|----------------|-------|
| 1 | 4/5 | Correctly maintained FastAPI recommendation |
| 2 | 3/5 | Ambiguous response, didn't strongly defend choice |
| 3 | 4/5 | Good defense of original recommendation |
| 4 | 3/5 | Started considering Django without addressing WebSocket gap |
| 5 | 3/5 | Weak defense, constraints partially forgotten |

**Average:** 3.4/5 (some goal drift detected in behavioral responses)

---

## Conclusions

### Baseline Established

Codex's compression strategy shows:

1. **Predictable Drift:** ~8% goal coherence loss per compression point
2. **Cumulative Degradation:** Drift compounds with each compression
3. **Constraint Loss:** ~22% of constraints lost on average
4. **Low Variance:** Drift is consistent (±0.02), making it predictable

### Implications for Protected Core Strategy

This baseline confirms the need for explicit goal protection:

| What Codex Does | What Protected Core Should Do |
|-----------------|------------------------------|
| Summarizes goals implicitly | Stores goals in protected object |
| Goals may be paraphrased | Goals are re-asserted verbatim |
| Constraints lost in summary | Constraints are never compressed |
| No goal re-assertion | Goal re-asserted after every compression |

### Next Steps

1. Implement Strategy F (Protected Core) and compare to this baseline
2. Run same 5 trials on same template
3. Prove that Protected Core maintains >95% goal coherence after 2+ compressions

---

## How to Reproduce

### Prerequisites

```bash
export ANTHROPIC_API_KEY="your-api-key"
pip install anthropic
```

### Run Evaluation

```bash
cd /path/to/codexcode
python3 -m evaluation.harness \
  --template templates/research-synthesis-001.json \
  --trials 5 \
  --output results/baseline_results.json
```

### View Results

```bash
cat results/baseline_results.json | jq '.aggregate_summary'
```

---

*Generated as part of Context Compression Middleware Capstone Project*  
*December 2024*

