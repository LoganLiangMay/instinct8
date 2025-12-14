# Metrics Accuracy Verification

## User Concern

The results show Instinct8 performing **suspiciously well**:
- Instinct8: 95% constraint recall vs Baseline 50%
- Instinct8: 100% budget recall vs Baseline 75%
- Instinct8: 93.8% weighted score vs Baseline 60.6%

**Question**: Is this accurate or is there a measurement issue?

## Verification Results

### 1. Numbers Are Internally Consistent ✅

**Instinct8 Constraint Recall by CP:**
- CP1: 80% (4/5 constraints)
- CP2: 100% (5/5 constraints)
- CP3: 100% (5/5 constraints)
- CP4: 100% (5/5 constraints)
- **Average: 95%** ✓

**Baseline Constraint Recall by CP:**
- CP1: 0% (0/5 constraints)
- CP2: 60% (3/5 constraints)
- CP3: 80% (4/5 constraints)
- CP4: 60% (3/5 constraints)
- **Average: 50%** ✓

The averages match the comparison file exactly.

### 2. Granular Metrics Match Overall Metrics ✅

For Instinct8 CP1:
- Overall recall: 80% (4/5 constraints)
- Granular breakdown shows exactly 4 constraints mentioned
- Budget recall: 100% (1/1 budget constraint mentioned)
- **Numbers are consistent**

### 3. Categorization Bug Found ⚠️

**Issue**: "Must support real-time WebSocket communication" was incorrectly categorized as "timeline" (because it contains "time") instead of "technical".

**Fix Applied**: Reordered categorization to check technical keywords before timeline keywords.

### 4. Potential Issues to Investigate

#### A. LLM-as-Judge Consistency
- The judge uses `_constraint_mentioned()` which calls an LLM
- LLM responses are non-deterministic
- Same agent response might be scored differently across runs
- **Need**: Multiple trials to verify consistency

#### B. Agent Response Variance
- LLM agent responses are non-deterministic
- Same context can produce different responses
- The 95% vs 50% gap might be partially due to variance
- **Need**: 5-10 trials to get stable averages

#### C. Test Run Differences
- Latest test shows Instinct8 100% budget recall
- Earlier test showed Instinct8 75% budget recall
- This suggests **high variance** between runs
- **Need**: Multiple trials to confirm if improvement is real

## Recommendations

1. **Run Multiple Trials**: Execute 5-10 trials to get stable averages
2. **Verify LLM-as-Judge**: Check if the judge is being consistent
3. **Check Agent Responses**: Store actual agent responses to verify they match metrics
4. **Compare with Earlier Test**: Understand why earlier test showed different results

## Conclusion

The numbers are **mathematically correct** and internally consistent, but:
- **High variance** between test runs suggests we need more trials
- The **95% vs 50% gap** is large and could be real improvement OR variance
- **Categorization bug** was fixed but doesn't affect overall recall

**Next Step**: Run 5-10 trials to confirm if the improvement is consistent or just variance.
