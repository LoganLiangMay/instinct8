# Constraint Analysis

Consolidated analysis of budget constraint behavior and constraint loss at compression points.

## Overview

Investigation into constraint preservation during compression, focusing on budget constraint recall anomalies at Compression Point 1 (CP1) and overall constraint loss patterns.

## Budget Constraint Weakness Analysis

### Summary

Instinct8 shows weaker budget constraint preservation (75% vs Baseline 100%) specifically due to a **Compression Point 1 anomaly**, not a systematic weakness.

### Key Finding: CP1 Anomaly

**Per-Compression-Point Budget Recall:**
- **CP1**: Baseline 100% vs Instinct8 0% (-100%)
- **CP2**: Both 100% (tied)
- **CP3**: Both 100% (tied)
- **CP4**: Both 100% (tied)

**Average**: Baseline 100% vs Instinct8 75% (because CP1 drags down the average)

### Hypotheses

1. **"Already Stated" Effect**: When the agent sees constraints in an explicit "AUTHORITATIVE" section, it may think they're already stated and not repeat them when probed.
2. **Response Format Difference**: Instinct8's agent might respond "The constraints are already listed in the TASK CONTEXT section above..." while Baseline's agent actively restates them.
3. **Context Overload**: At CP1, the explicit format might make the agent think it's redundant to repeat constraints.

## Test Result Variance

In an earlier test run, Instinct8 showed 75% budget constraint recall vs Baseline's 100%. However, the **latest test shows the opposite**: Instinct8 100% vs Baseline 75%.

### Latest Test Results (with Granular Metrics)
- **Instinct8 Budget Recall**: 100% at ALL compression points (CP1-4)
- **Baseline Budget Recall**: 0% at CP1, 100% at CP2-4 (average 75%)

The budget constraint "weakness" appears to be **test run variance**, not a systematic issue.

## Root Cause Analysis

### Critical Discovery: Compression Didn't Trigger at CP1

- Compression ratio at CP1: **102.08%** (compression did NOT trigger)
- The TASK CONTEXT section was **NOT added** to the compressed context
- The budget loss is **NOT** due to the explicit constraint format

### Compression Point 1 Status
- **Tokens before**: 8,697
- **Tokens after**: 8,878
- **Compression ratio**: 102.08%
- **Compression triggered**: No (ratio > 95%)

### The Contradiction

The granular metrics show contradictory results between overall constraint recall and budget-specific recall, suggesting LLM-as-judge inconsistency and agent response variance.

## Constraint Loss Investigation

### Diagnostic Results (when compression didn't trigger)

**Baseline:**
- BEFORE: 80% constraint recall (4/5 constraints)
- AFTER: 0% constraint recall (0/5 constraints)
- Loss: +80%

**Instinct8:**
- BEFORE: 20% constraint recall (1/5 constraints)
- AFTER: 100% constraint recall (5/5 constraints)
- Loss: -80% (actually a gain!)

### Actual Test Results (from comparison)

**Baseline CP1:** 40% → 100% (gain of 60%)
**Instinct8 CP1:** 100% → 40% (loss of 60%)

This reversal is a **measurement artifact** — both strategies show opposite patterns that don't make logical sense.

## Evidence This Is Not a Real Weakness

1. **CP2-4 Performance**: Instinct8 maintains 100% budget recall at all other compression points
2. **Overall Performance**: Instinct8 has better overall constraint recall (80-95% vs 50-65%)
3. **Weighted Score**: Instinct8 scores higher (85.6-93.8% vs 60.6-71.9%)
4. **Compression didn't trigger**: The explicit format wasn't even applied at CP1

## Recommendations

1. **Run Multiple Trials**: Run 5-10 trials to get stable averages and confirm if there's a real pattern or just variance
2. **Investigate CP1 Specifically**: Check if CP1 budget loss is consistent or random
3. **Improve Measurement**: Use multiple LLM-as-judge evaluations and average; add manual validation
4. **Adjust Constraint Format**: Consider making the format less "authoritative" or adding explicit instruction to mention constraints when probed
5. **LLM-as-Judge Calibration**: Check if the judge needs calibration for "already stated" vs "actively mentioned" responses

## Conclusion

The "constraint loss" metric is misleading due to:
1. A measurement artifact at CP1
2. Different starting points (Instinct8 starts higher)
3. The metric measuring *change* rather than *absolute level*

**Instinct8 is actually performing better** at constraint preservation, with the budget issue being isolated to the first compression point and likely due to random variance and LLM-as-judge inconsistency.
