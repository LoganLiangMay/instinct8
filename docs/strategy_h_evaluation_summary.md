# Strategy H Evaluation: Top 3 Methods Summary

**Quick Reference** for evaluating Selective Salience Compression (Strategy H)

---

## 🥇 Method 1: Ground Truth Comparison (RECOMMENDED)

**What:** Compare model-extracted salience against human-annotated ground truth

**Metrics:** Precision, Recall, F1 Score

**How:**
1. Human annotators identify goal-critical information in templates
2. Model extracts salience using Strategy H
3. Calculate semantic similarity matches (threshold: 0.85)
4. Compute precision/recall/F1

**Pros:**
- ✅ Objective and quantitative
- ✅ Standard metrics
- ✅ Category-specific analysis possible
- ✅ Identifies failure modes

**Cons:**
- ⚠️ Requires human annotation (time-consuming)
- ⚠️ Semantic similarity threshold is hyperparameter

**Best For:** Primary evaluation, establishing baseline accuracy

**Expected Results:**
- Precision: 0.65-0.85 (target: >0.75)
- Recall: 0.70-0.90 (target: >0.80)
- F1: 0.70-0.85 (target: >0.77)

---

## 🥈 Method 2: LLM-as-Judge with Structured Rubric

**What:** Use LLM judges to evaluate salience extraction quality

**Metrics:** Precision estimate, Recall estimate, Completeness score, Noise level score

**How:**
1. Design structured rubric (goal relevance, constraint preservation, etc.)
2. LLM judges evaluate each extracted item (1-5 scale)
3. Aggregate scores across multiple judges
4. Calculate precision/recall estimates

**Pros:**
- ✅ Faster than human annotation
- ✅ Scalable to many templates
- ✅ Provides detailed reasoning
- ✅ Multi-judge consensus improves reliability

**Cons:**
- ⚠️ LLM judges may have biases
- ⚠️ Less objective than ground truth
- ⚠️ Requires careful rubric design

**Best For:** Secondary evaluation, rapid iteration, scaling

**Expected Correlation with Ground Truth:** 0.75-0.90

---

## 🥉 Method 3: Downstream Task Performance

**What:** Measure goal coherence preservation (indirect salience quality)

**Metrics:** Goal coherence score, Constraint recall, Behavioral alignment

**How:**
1. Run Strategy H on templates
2. Measure goal coherence at compression points
3. Compare with other strategies (especially Protected Core)
4. Infer salience quality from coherence preservation

**Pros:**
- ✅ Measures ultimate goal (goal coherence)
- ✅ No additional annotation needed
- ✅ Uses existing evaluation infrastructure

**Cons:**
- ⚠️ Indirect measure (doesn't directly assess salience)
- ⚠️ Confounded by other factors
- ⚠️ Can't identify what types of info are missed

**Best For:** Validation, quick sanity checks

**Expected Results:**
- Goal coherence: 0.80-0.95 (target: >0.90)
- vs Protected Core: 0.85-1.0 (target: >0.90)

---

## Recommended Evaluation Plan

### Phase 1: Primary (Method 1)
- Annotate 5-10 templates with ground truth
- Calculate precision/recall/F1
- Establish baseline accuracy

### Phase 2: Validation (Method 2)
- Design LLM-as-judge rubric
- Validate against ground truth
- Scale to all templates

### Phase 3: Goal Coherence (Method 3)
- Run Strategy H on all templates
- Compare with other strategies
- Validate salience preservation works

---

## Quick Comparison

| Method | Accuracy | Speed | Cost | Best Use Case |
|--------|----------|-------|------|---------------|
| **1. Ground Truth** | ⭐⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐ | Primary evaluation |
| **2. LLM-as-Judge** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐ | Scaling, iteration |
| **3. Downstream** | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | Validation, checks |

---

*See `strategy_h_evaluation_methods.md` for detailed implementation*

