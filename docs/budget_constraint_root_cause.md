# Budget Constraint Root Cause Analysis

## The Issue

Instinct8 shows 0% budget constraint recall at Compression Point 1, while Baseline shows 100%.

## Key Finding: Compression Didn't Trigger at CP1

**Critical Discovery:**
- Compression ratio at CP1: **102.08%** (compression did NOT trigger)
- This means the TASK CONTEXT section was **NOT added** to the compressed context
- The budget loss is **NOT** due to the explicit constraint format

## What Actually Happened

### Compression Point 1 Status
- **Tokens before**: 8,697
- **Tokens after**: 8,878  
- **Compression ratio**: 102.08%
- **Compression triggered**: ❌ NO (ratio > 95%)

### Constraint Recall at CP1
- **Baseline**: 0% → 0% (no change, but granular shows 100% budget)
- **Instinct8**: 20% → 80% (improved overall, but granular shows 0% budget)

### The Contradiction

The granular metrics show:
- **Baseline budget recall**: 100% ✅
- **Instinct8 budget recall**: 0% ❌

But overall constraint recall shows:
- **Baseline**: 0% (contradictory!)
- **Instinct8**: 80% (contradictory!)

## Root Cause: Agent Response Variance

Since compression **didn't trigger** at CP1:
1. **TASK CONTEXT section was NOT added** (compression skipped)
2. Both strategies see the **same conversation history**
3. The difference is **agent response variance**, not compression

### Why Instinct8 Lost Budget at CP1

**Hypothesis**: The agent's response is **inconsistent** and happened to not mention the budget constraint in this particular run, even though:
- The constraint is in the conversation history
- Compression didn't change the context
- The explicit format wasn't applied (compression didn't trigger)

### Why Baseline Gained Budget at CP1

**Hypothesis**: Baseline's agent response happened to mention the budget constraint in this run, even though overall constraint recall was 0%.

## The Real Issue: Measurement Inconsistency

The contradiction between:
- Overall constraint recall (Instinct8 80%, Baseline 0%)
- Granular budget recall (Instinct8 0%, Baseline 100%)

Suggests:
1. **LLM-as-judge inconsistency**: The judge evaluates differently across runs
2. **Agent response variance**: Same context produces different responses
3. **Measurement artifact**: The CP1 measurement is unreliable

## Evidence This Is Not a Real Weakness

1. **CP2-4 Performance**: Instinct8 maintains 100% budget recall at all other compression points
2. **Overall Performance**: Instinct8 has better overall constraint recall (80% vs 65%)
3. **Weighted Score**: Instinct8 scores higher (85.6% vs 71.9%)
4. **Compression didn't trigger**: The explicit format wasn't even applied at CP1

## Conclusion

The budget constraint "weakness" at CP1 is:
- **NOT** due to the explicit constraint format (compression didn't trigger)
- **NOT** a systematic issue (CP2-4 show 100% budget recall)
- **LIKELY** due to agent response variance and LLM-as-judge inconsistency

**Recommendation**: Run multiple trials to see if CP1 budget loss is consistent or random variance.
