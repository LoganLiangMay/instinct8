# Strategy H Evaluation Methods: Selective Salience Compression

**Strategy:** Strategy H - Selective Salience Compression (Agent-as-Judge)  
**Evaluation Focus:** Salience Detection Accuracy & Goal Coherence Preservation  
**Date:** 2025-01-XX

---

## Executive Summary

Evaluating **Selective Salience Compression** requires measuring two distinct capabilities:
1. **Salience Detection Accuracy**: Can the model correctly identify goal-critical information?
2. **Goal Coherence Preservation**: Does preserving model-judged salience maintain goal alignment?

This document presents **three comprehensive evaluation methodologies**, ranked by accuracy and practicality for this specific use case.

---

## Top 3 Evaluation Methodologies

### 🥇 **Method 1: Ground Truth Comparison with Precision/Recall/F1 (RECOMMENDED)**

**Why This Is Best:**
- Provides objective, quantitative metrics
- Standard in information extraction research
- Allows comparison across strategies
- Measures both what was extracted correctly and what was missed

**How It Works:**

#### Step 1: Create Ground Truth Salience Sets

For each conversation template, human annotators identify what information is truly goal-critical:

```python
@dataclass
class GroundTruthSalience:
    """Ground truth salience for a conversation template."""
    template_id: str
    compression_point: int
    
    # Categories of salient information
    goals: List[str]  # Explicit goals and goal changes
    constraints: List[str]  # Hard constraints (must/must not)
    decisions: List[str]  # Key decisions with rationales
    critical_facts: List[str]  # Facts that affect future actions
    important_tool_outputs: List[str]  # Tool results that matter
    
    # Non-salient examples (for false positive detection)
    non_salient_examples: List[str]  # Things that should NOT be extracted
    
    # Metadata
    annotator_id: str
    annotation_date: str
    inter_annotator_agreement: float  # If multiple annotators
```

**Annotation Process:**
1. **Multiple annotators** (3-5) independently annotate each template
2. **Inter-annotator agreement** measured (Fleiss' kappa or Krippendorff's alpha)
3. **Consensus building** for disagreements
4. **Final ground truth** = items agreed upon by ≥2/3 annotators

#### Step 2: Extract Model Salience

Run Strategy H on the same templates, extract salience at each compression point:

```python
def extract_model_salience(
    strategy: SelectiveSalienceStrategy,
    template: ConversationTemplate,
    compression_point: int
) -> List[str]:
    """Extract what the model thinks is salient."""
    context = template.turns[:compression_point]
    strategy.compress(context, compression_point)
    return strategy.salience_set
```

#### Step 3: Calculate Precision, Recall, F1

```python
def evaluate_salience_accuracy(
    model_salience: List[str],
    ground_truth: GroundTruthSalience
) -> Dict[str, float]:
    """
    Calculate precision, recall, F1 for salience detection.
    
    Uses semantic similarity (not exact string match) because:
    - Model may paraphrase slightly
    - Exact quotes may vary in wording
    - We care about semantic equivalence
    """
    # Flatten ground truth into single list
    gt_all = (
        ground_truth.goals +
        ground_truth.constraints +
        ground_truth.decisions +
        ground_truth.critical_facts +
        ground_truth.important_tool_outputs
    )
    
    # Calculate semantic similarity between model and ground truth
    # Using sentence embeddings (e.g., sentence-transformers)
    model_embeddings = get_embeddings(model_salience)
    gt_embeddings = get_embeddings(gt_all)
    
    # Match each model item to closest ground truth item
    # Threshold: similarity > 0.85 = match
    matches = find_semantic_matches(
        model_embeddings, 
        gt_embeddings, 
        threshold=0.85
    )
    
    # True Positives: model items that match ground truth
    tp = len(matches)
    
    # False Positives: model items that don't match ground truth
    fp = len(model_salience) - tp
    
    # False Negatives: ground truth items that model missed
    matched_gt_indices = [m[1] for m in matches]
    fn = len(gt_all) - len(set(matched_gt_indices))
    
    # Calculate metrics
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0
    
    return {
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "true_positives": tp,
        "false_positives": fp,
        "false_negatives": fn,
        "total_model_items": len(model_salience),
        "total_ground_truth_items": len(gt_all)
    }
```

#### Step 4: Category-Specific Analysis

Break down performance by information type:

```python
def evaluate_by_category(
    model_salience: List[str],
    ground_truth: GroundTruthSalience
) -> Dict[str, Dict[str, float]]:
    """Evaluate precision/recall for each category."""
    categories = {
        "goals": ground_truth.goals,
        "constraints": ground_truth.constraints,
        "decisions": ground_truth.decisions,
        "critical_facts": ground_truth.critical_facts,
        "tool_outputs": ground_truth.important_tool_outputs
    }
    
    results = {}
    for category, gt_items in categories.items():
        # Find model items that match this category
        matches = find_semantic_matches(model_salience, gt_items, threshold=0.85)
        tp = len(matches)
        fp = len(model_salience) - tp
        fn = len(gt_items) - len(set([m[1] for m in matches]))
        
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        
        results[category] = {
            "precision": precision,
            "recall": recall,
            "f1": 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0
        }
    
    return results
```

**Advantages:**
- ✅ Objective and quantitative
- ✅ Standard metrics (precision/recall/F1)
- ✅ Allows category-specific analysis
- ✅ Comparable across strategies
- ✅ Identifies failure modes (what types of info are missed)

**Disadvantages:**
- ⚠️ Requires human annotation (time-consuming)
- ⚠️ Semantic similarity threshold is a hyperparameter
- ⚠️ May miss subtle salience (e.g., implicit constraints)

**Implementation Effort:** Medium (requires annotation pipeline)

**Recommended For:** Primary evaluation method

---

### 🥈 **Method 2: LLM-as-Judge with Structured Rubric**

**Why This Is Second Best:**
- Faster than human annotation
- Can evaluate at scale
- Provides detailed reasoning
- Can assess plausibility and faithfulness

**How It Works:**

#### Step 1: Design Evaluation Rubric

Create a structured rubric for LLM judges to evaluate salience:

```python
SALIENCE_EVALUATION_RUBRIC = """You are evaluating whether a model correctly identified goal-critical information during context compression.

EVALUATION CRITERIA:

1. **Goal Relevance** (Critical)
   - Does the extracted item directly relate to achieving the user's goal?
   - Score: 1-5 (5 = directly goal-critical, 1 = irrelevant)

2. **Constraint Preservation** (Critical)
   - Is this a hard constraint (must/must not) that affects future actions?
   - Score: 1-5 (5 = critical constraint, 1 = not a constraint)

3. **Decision Importance** (Important)
   - Is this a key decision that affects the path forward?
   - Score: 1-5 (5 = critical decision, 1 = minor choice)

4. **Fact Criticality** (Important)
   - Will this fact be needed for future actions?
   - Score: 1-5 (5 = essential fact, 1 = trivial detail)

5. **Completeness** (Overall)
   - Does the extraction include all critical information?
   - Score: 1-5 (5 = complete, 1 = missing critical items)

6. **Noise Level** (Overall)
   - Does the extraction include irrelevant information?
   - Score: 1-5 (5 = no noise, 1 = mostly noise)

ORIGINAL GOAL: {original_goal}
CONSTRAINTS: {constraints}

CONVERSATION CONTEXT:
{conversation_context}

MODEL'S EXTRACTED SALIENCE:
{model_salience}

EVALUATION TASK:
For each item in the model's extracted salience, rate it on criteria 1-4.
Then provide overall scores for criteria 5-6.

Output format (JSON):
{{
  "item_evaluations": [
    {{
      "item": "exact quote from model_salience",
      "goal_relevance": 1-5,
      "constraint_preservation": 1-5,
      "decision_importance": 1-5,
      "fact_criticality": 1-5,
      "overall_score": 1-5,
      "reasoning": "why this score"
    }}
  ],
  "completeness_score": 1-5,
  "noise_level_score": 1-5,
  "missing_critical_items": ["item 1", "item 2"],
  "irrelevant_items": ["item 1", "item 2"],
  "overall_assessment": "detailed reasoning"
}}
"""
```

#### Step 2: Run LLM Evaluation

```python
def evaluate_with_llm_judge(
    model_salience: List[str],
    conversation_context: str,
    original_goal: str,
    constraints: List[str],
    judge_model: str = "claude-opus-4"
) -> Dict[str, Any]:
    """Use LLM-as-judge to evaluate salience extraction."""
    
    prompt = SALIENCE_EVALUATION_RUBRIC.format(
        original_goal=original_goal,
        constraints=", ".join(constraints),
        conversation_context=conversation_context,
        model_salience="\n".join(f"- {item}" for item in model_salience)
    )
    
    response = anthropic_client.messages.create(
        model=judge_model,
        max_tokens=4000,
        messages=[{"role": "user", "content": prompt}]
    )
    
    # Parse JSON response
    evaluation = json.loads(response.content[0].text)
    
    # Calculate aggregate metrics
    item_scores = [item["overall_score"] for item in evaluation["item_evaluations"]]
    avg_item_score = sum(item_scores) / len(item_scores) if item_scores else 0
    
    # Calculate precision (based on noise level)
    # Higher noise level score = lower false positives
    precision_estimate = evaluation["noise_level_score"] / 5.0
    
    # Calculate recall (based on completeness)
    # Higher completeness score = lower false negatives
    recall_estimate = evaluation["completeness_score"] / 5.0
    
    f1_estimate = 2 * precision_estimate * recall_estimate / (
        precision_estimate + recall_estimate
    ) if (precision_estimate + recall_estimate) > 0 else 0.0
    
    return {
        "avg_item_score": avg_item_score,
        "precision_estimate": precision_estimate,
        "recall_estimate": recall_estimate,
        "f1_estimate": f1_estimate,
        "completeness_score": evaluation["completeness_score"],
        "noise_level_score": evaluation["noise_level_score"],
        "missing_critical_items": evaluation["missing_critical_items"],
        "irrelevant_items": evaluation["irrelevant_items"],
        "item_evaluations": evaluation["item_evaluations"],
        "overall_assessment": evaluation["overall_assessment"]
    }
```

#### Step 3: Multi-Judge Consensus

Run evaluation with multiple judge models and aggregate:

```python
def evaluate_with_multi_judge(
    model_salience: List[str],
    conversation_context: str,
    original_goal: str,
    constraints: List[str],
    judge_models: List[str] = ["claude-opus-4", "gpt-4-turbo", "claude-sonnet-4"]
) -> Dict[str, Any]:
    """Run evaluation with multiple judges and aggregate results."""
    
    evaluations = []
    for judge_model in judge_models:
        eval_result = evaluate_with_llm_judge(
            model_salience, conversation_context, original_goal, constraints, judge_model
        )
        evaluations.append(eval_result)
    
    # Aggregate scores (average)
    aggregated = {
        "avg_item_score": np.mean([e["avg_item_score"] for e in evaluations]),
        "precision_estimate": np.mean([e["precision_estimate"] for e in evaluations]),
        "recall_estimate": np.mean([e["recall_estimate"] for e in evaluations]),
        "f1_estimate": np.mean([e["f1_estimate"] for e in evaluations]),
        "completeness_score": np.mean([e["completeness_score"] for e in evaluations]),
        "noise_level_score": np.mean([e["noise_level_score"] for e in evaluations]),
        "judge_agreement": calculate_agreement(evaluations),  # Inter-judge correlation
        "individual_evaluations": evaluations
    }
    
    return aggregated
```

**Advantages:**
- ✅ Faster than human annotation
- ✅ Scalable to many templates
- ✅ Provides detailed reasoning
- ✅ Can assess plausibility and faithfulness
- ✅ Multi-judge consensus improves reliability

**Disadvantages:**
- ⚠️ LLM judges may have biases
- ⚠️ Less objective than ground truth
- ⚠️ Requires careful rubric design
- ⚠️ Cost (API calls for each evaluation)

**Implementation Effort:** Low-Medium (requires rubric design and API integration)

**Recommended For:** Secondary evaluation method, rapid iteration

---

### 🥉 **Method 3: Downstream Task Performance (Goal Coherence Proxy)**

**Why This Is Third:**
- Measures ultimate goal: does salience preservation maintain goal coherence?
- Indirect but practical
- Aligns with overall evaluation framework

**How It Works:**

Instead of directly measuring salience accuracy, measure whether preserving model-judged salience maintains goal coherence better than other strategies.

#### Step 1: Run Strategy H on Templates

```python
def run_strategy_h_evaluation(
    template: ConversationTemplate,
    strategy: SelectiveSalienceStrategy
) -> Dict[str, Any]:
    """Run Strategy H and measure goal coherence at compression points."""
    
    results = {
        "compression_points": [],
        "goal_coherence_scores": [],
        "constraint_recall_scores": [],
        "behavioral_alignment_scores": []
    }
    
    # Run conversation
    for turn in template.turns:
        if turn.is_compression_point:
            # Compress context
            compressed = strategy.compress(
                template.turns[:turn.turn_id],
                turn.turn_id
            )
            
            # Measure goal coherence (using existing probes)
            goal_coherence = probe_goal(compressed, template.original_goal)
            constraint_recall = probe_constraints(compressed, template.constraints)
            behavioral_alignment = probe_behavior(compressed, template.next_task)
            
            results["compression_points"].append(turn.turn_id)
            results["goal_coherence_scores"].append(goal_coherence)
            results["constraint_recall_scores"].append(constraint_recall)
            results["behavioral_alignment_scores"].append(behavioral_alignment)
    
    return results
```

#### Step 2: Compare with Other Strategies

```python
def compare_strategies_on_goal_coherence(
    template: ConversationTemplate,
    strategies: List[CompressionStrategy]
) -> pd.DataFrame:
    """Compare all strategies on goal coherence preservation."""
    
    comparison = []
    
    for strategy in strategies:
        results = run_strategy_evaluation(template, strategy)
        
        comparison.append({
            "strategy": strategy.name(),
            "avg_goal_coherence": np.mean(results["goal_coherence_scores"]),
            "avg_constraint_recall": np.mean(results["constraint_recall_scores"]),
            "avg_behavioral_alignment": np.mean(results["behavioral_alignment_scores"]),
            "goal_coherence_decay": (
                results["goal_coherence_scores"][0] - 
                results["goal_coherence_scores"][-1]
            )
        })
    
    return pd.DataFrame(comparison)
```

#### Step 3: Analyze Salience Quality via Goal Coherence

If Strategy H performs well on goal coherence, infer that salience detection is accurate:

```python
def infer_salience_quality_from_coherence(
    strategy_h_results: Dict[str, Any],
    protected_core_results: Dict[str, Any]  # Baseline (best case)
) -> Dict[str, Any]:
    """
    Infer salience detection quality from goal coherence preservation.
    
    Hypothesis: If Strategy H maintains goal coherence similar to Protected Core,
    then salience detection is likely accurate.
    """
    
    h_coherence = strategy_h_results["avg_goal_coherence"]
    pc_coherence = protected_core_results["avg_goal_coherence"]
    
    # Calculate relative performance
    relative_performance = h_coherence / pc_coherence
    
    # Infer salience quality
    if relative_performance > 0.95:
        inferred_quality = "excellent"
    elif relative_performance > 0.85:
        inferred_quality = "good"
    elif relative_performance > 0.75:
        inferred_quality = "moderate"
    else:
        inferred_quality = "poor"
    
    return {
        "relative_performance": relative_performance,
        "inferred_salience_quality": inferred_quality,
        "strategy_h_coherence": h_coherence,
        "protected_core_coherence": pc_coherence,
        "gap": pc_coherence - h_coherence
    }
```

**Advantages:**
- ✅ Measures ultimate goal (goal coherence)
- ✅ Aligns with overall evaluation framework
- ✅ No additional annotation needed
- ✅ Practical and actionable

**Disadvantages:**
- ⚠️ Indirect measure (doesn't directly assess salience)
- ⚠️ Confounded by other factors (compression quality, etc.)
- ⚠️ Can't identify what types of info are missed
- ⚠️ Less precise than direct evaluation

**Implementation Effort:** Low (uses existing evaluation infrastructure)

**Recommended For:** Validation method, quick sanity checks

---

## Recommended Evaluation Plan

### Phase 1: Primary Evaluation (Method 1)

**Goal:** Establish baseline salience detection accuracy

**Steps:**
1. **Annotate 5-10 templates** with ground truth salience
   - 3-5 annotators per template
   - Measure inter-annotator agreement
   - Build consensus ground truth
   
2. **Run Strategy H** on annotated templates
   - Extract salience at each compression point
   - Store model salience sets
   
3. **Calculate precision/recall/F1**
   - Use semantic similarity (threshold: 0.85)
   - Category-specific analysis
   - Identify failure modes

**Expected Output:**
- Baseline salience detection accuracy (precision, recall, F1)
- Category-specific performance breakdown
- Failure mode analysis (what gets missed, what gets included incorrectly)

### Phase 2: Validation (Method 2)

**Goal:** Validate findings and scale evaluation

**Steps:**
1. **Design LLM-as-judge rubric**
   - Based on findings from Phase 1
   - Refine criteria based on failure modes
   
2. **Run LLM evaluation** on same templates
   - Compare with ground truth results
   - Measure correlation
   
3. **Scale to all templates**
   - Use LLM-as-judge for remaining templates
   - Validate periodically with ground truth

**Expected Output:**
- LLM-as-judge evaluation for all templates
- Correlation with ground truth
- Scalable evaluation pipeline

### Phase 3: Goal Coherence Validation (Method 3)

**Goal:** Confirm salience preservation maintains goal coherence

**Steps:**
1. **Run Strategy H** on all templates
   - Measure goal coherence at compression points
   - Compare with other strategies
   
2. **Analyze correlation**
   - Does high salience accuracy → high goal coherence?
   - What's the gap vs Protected Core?

**Expected Output:**
- Goal coherence scores for Strategy H
- Comparison with other strategies
- Validation that salience preservation works

---

## Implementation Checklist

### Method 1: Ground Truth Comparison

- [ ] Design annotation interface/tool
- [ ] Recruit 3-5 annotators
- [ ] Annotate 5-10 templates (2-3 compression points each)
- [ ] Calculate inter-annotator agreement
- [ ] Build consensus ground truth
- [ ] Implement semantic similarity matching
- [ ] Calculate precision/recall/F1
- [ ] Category-specific analysis
- [ ] Failure mode documentation

### Method 2: LLM-as-Judge

- [ ] Design evaluation rubric
- [ ] Test rubric on sample templates
- [ ] Implement LLM evaluation function
- [ ] Add multi-judge consensus
- [ ] Validate against ground truth (correlation)
- [ ] Scale to all templates
- [ ] Document judge biases/limitations

### Method 3: Downstream Performance

- [ ] Integrate with existing evaluation harness
- [ ] Run Strategy H on all templates
- [ ] Compare with other strategies
- [ ] Analyze goal coherence preservation
- [ ] Document correlation with salience accuracy

---

## Expected Results

Based on research and similar evaluations:

| Metric | Expected Range | Target |
|--------|---------------|--------|
| **Precision** | 0.65 - 0.85 | >0.75 |
| **Recall** | 0.70 - 0.90 | >0.80 |
| **F1** | 0.70 - 0.85 | >0.77 |
| **Goal Coherence** | 0.80 - 0.95 | >0.90 |
| **vs Protected Core** | 0.85 - 1.0 | >0.90 |

**Category-Specific Expectations:**
- **Constraints**: High recall (>0.90), moderate precision (0.70-0.85)
- **Decisions**: Moderate recall (0.75-0.85), high precision (0.80-0.90)
- **Goals**: High recall (>0.90), high precision (>0.85)
- **Critical Facts**: Lower recall (0.65-0.75), variable precision

**Failure Modes Expected:**
- Missing implicit constraints
- Including conversational scaffolding
- Over-extracting minor decisions
- Missing subtle goal changes

---

## References

1. **Precision/Recall Evaluation**: Standard in information extraction (NLP research)
2. **LLM-as-Judge**: Used in evaluation frameworks (e.g., HELM, AlpacaEval)
3. **Semantic Similarity**: Sentence transformers for matching (sentence-transformers library)
4. **Inter-Annotator Agreement**: Fleiss' kappa, Krippendorff's alpha
5. **Goal Coherence Evaluation**: Based on Apollo Research (Arike et al., 2025)

---

*Document created: 2025-01-XX*  
*Last updated: 2025-01-XX*

