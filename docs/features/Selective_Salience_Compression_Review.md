# Selective Salience Compression - Review & Recommendations

**Date:** 2025-01-XX  
**Reviewer:** AI Assistant  
**Status:** ✅ Strong Concept, Needs Implementation Details

---

## Executive Summary

**Selective Salience Compression** is a promising approach that tests whether models can reliably identify goal-critical information. It's well-positioned as a distinct strategy from Protected Core, offering a more adaptive but potentially more error-prone alternative.

**Recommendation:** ✅ **Include as Strategy H** in the evaluation framework, but add implementation details and address the concerns below.

---

## Strengths

### 1. Clear Differentiation from Protected Core

The document correctly identifies the key distinction:
- **Protected Core**: Fixed schema (goals, constraints, decisions)
- **Selective Salience**: Model-determined salience (adaptive, flexible)

This makes it a valuable addition to the strategy matrix.

### 2. Tests Frontier Capability

The approach tests whether models can:
- Identify what will matter later
- Distinguish signal from noise
- Preserve critical information without explicit schema

This is a legitimate research question.

### 3. Human-Like Memory Pattern

The two-part structure (salient verbatim + compressed background) mirrors how humans remember:
- Important decisions and constraints (verbatim)
- General context (compressed)

### 4. Good Example

The PostgreSQL example effectively demonstrates:
- What gets preserved (constraints, decisions, rationales)
- What gets compressed (chit-chat, redundant statements)

---

## Areas for Improvement

### 1. Missing Implementation Details

**Current State:** High-level description with example prompts  
**Needed:** Concrete implementation matching the `CompressionStrategy` interface

**Recommendation:** Add a full implementation section:

```python
class StrategyH_SelectiveSalience(CompressionStrategy):
    """
    Selective Salience Compression: Model identifies and preserves 
    goal-critical information verbatim, compresses the rest.
    """
    
    def __init__(self, model: str = "claude-sonnet-4-20250514"):
        self.client = Anthropic()
        self.model = model
        self.salience_extraction_prompt = """..."""
        self.background_summary_prompt = """..."""
    
    def compress(
        self,
        context: List[Dict[str, Any]],
        trigger_point: int,
    ) -> str:
        """
        Steps:
        1. Extract salient information (verbatim)
        2. Compress remaining content
        3. Rebuild context: SYSTEM + SALIENT + BACKGROUND + RECENT
        """
        to_compress = context[:trigger_point]
        
        # Step 1: Extract salient information
        salience_set = self._extract_salient_information(to_compress)
        
        # Step 2: Compress background
        background_summary = self._compress_background(
            to_compress, salience_set
        )
        
        # Step 3: Rebuild context
        return self._build_context(
            salience_set, background_summary, context[-3:]
        )
    
    def _extract_salient_information(
        self, context: List[Dict[str, Any]]
    ) -> List[str]:
        """Extract goal-critical information verbatim."""
        # Implementation details...
    
    def _compress_background(
        self, context: List[Dict[str, Any]], salience_set: List[str]
    ) -> str:
        """Compress everything except salient information."""
        # Implementation details...
```

### 2. Unclear Prompt Engineering

**Issue:** The prompts are described but not fully specified.

**Recommendation:** Provide exact prompts with rationale:

```python
SALIENCE_EXTRACTION_PROMPT = """You are performing selective salience extraction for context compression.

From the following conversation, extract ONLY the information that will directly impact the agent's ability to achieve the user's goal. 

Include:
- Explicit goals and goal changes
- Hard constraints (must/must not)
- Key decisions with rationales
- Critical facts or requirements
- Important tool outputs that affect future actions

Do NOT include:
- Conversational scaffolding
- Redundant explanations
- Intermediate reasoning steps
- Off-topic tangents

CRITICAL: Quote exactly—do not summarize or paraphrase. Preserve the original wording.

Conversation to analyze:
{conversation}

Output format (one item per line, verbatim quotes):
- "Quote 1"
- "Quote 2"
- ...
"""

BACKGROUND_SUMMARY_PROMPT = """Summarize the following conversation, excluding any information that appears in the salience list.

Salience List (do not duplicate):
{salience_list}

Remaining conversation:
{remaining_conversation}

Create a concise summary (2-3 sentences) of the non-critical context."""
```

### 3. Salience Set Growth Management

**Issue:** Document mentions "salience vector grows or shrinks" but doesn't specify:
- How to handle cumulative salience sets
- Whether to deduplicate across compressions
- Token budget for salience set

**Recommendation:** Add explicit management strategy:

```python
def _manage_salience_set(
    self, 
    new_salience: List[str], 
    existing_salience: List[str]
) -> List[str]:
    """
    Merge new salience with existing, handling:
    - Deduplication (semantic similarity)
    - Token budget (max 5K tokens)
    - Recency weighting (prefer newer items)
    """
    # Combine and deduplicate
    combined = existing_salience + new_salience
    deduplicated = self._deduplicate_semantically(combined)
    
    # Apply token budget
    if self._token_count(deduplicated) > 5000:
        # Prioritize: constraints > decisions > facts
        deduplicated = self._prioritize_and_truncate(deduplicated)
    
    return deduplicated
```

### 4. Error Handling & Edge Cases

**Missing:** What happens when:
- Model extracts nothing as salient?
- Model extracts everything as salient?
- Model misidentifies salience (includes noise, misses signal)?

**Recommendation:** Add fallback strategies:

```python
def _extract_salient_information(self, context):
    """Extract with fallbacks."""
    try:
        salience = self._call_model(SALIENCE_EXTRACTION_PROMPT)
        
        # Validation
        if not salience or len(salience) == 0:
            # Fallback: extract explicit constraints/goals only
            return self._fallback_extract_constraints(context)
        
        if len(salience) > 50:  # Too much extracted
            # Fallback: rank and take top 20
            return self._rank_and_filter(salience, top_k=20)
        
        return salience
    except Exception as e:
        # Fallback to Protected Core schema
        return self._schema_based_extraction(context)
```

### 5. Comparison with Strategy D (A-MEM)

**Issue:** Selective Salience seems similar to A-MEM but the distinction isn't clear.

**Recommendation:** Add explicit comparison:

| Aspect | Strategy D (A-MEM) | Strategy H (Selective Salience) |
|--------|-------------------|--------------------------------|
| Extraction | Structured notes (facts, decisions, observations) | Verbatim quotes (unstructured) |
| Storage | Embeddings + metadata | Plain text list |
| Retrieval | Semantic search on demand | Always included verbatim |
| Schema | Predefined categories | Model-determined |
| Goal Protection | Implicit (via retrieval) | Explicit (always present) |

**Key Difference:** A-MEM uses retrieval (may miss relevant items), Selective Salience always includes salient items (may include irrelevant items).

### 6. Evaluation Metrics

**Missing:** How to measure salience detection accuracy.

**Recommendation:** Add evaluation metrics:

```python
def evaluate_salience_accuracy(
    extracted_salience: List[str],
    ground_truth_salience: List[str],
    original_context: List[Dict]
) -> Dict[str, float]:
    """
    Measure:
    1. Precision: % of extracted items that are actually salient
    2. Recall: % of ground truth items that were extracted
    3. False positives: Noise included as salient
    4. False negatives: Critical info missed
    """
    # Implementation...
```

### 7. Integration with Evaluation Framework

**Issue:** Doesn't specify how this fits into the existing 7-strategy framework.

**Recommendation:** Position as **Strategy H**:

- **Strategy A**: Naive summarization (baseline)
- **Strategy B**: Codex-style checkpoint
- **Strategy C**: Hierarchical summarization
- **Strategy D**: A-MEM agentic memory
- **Strategy E**: claude-mem observational memory
- **Strategy F**: Protected Core (schema-based)
- **Strategy G**: Hybrid (A-MEM + Protected Core)
- **Strategy H**: Selective Salience (model-judged) ← **NEW**

### 8. Variants Section Needs Detail

**Current:** Lists variants but doesn't specify how to implement them.

**Recommendation:** Add implementation notes:

```python
# Variant 1: Conservative Salience
# Keep more details (lower threshold)
SALIENCE_THRESHOLD = 0.3  # Lower = more items

# Variant 2: Aggressive Salience  
# Only top 1-3 facts
SALIENCE_THRESHOLD = 0.9  # Higher = fewer items
MAX_SALIENCE_ITEMS = 3

# Variant 3: Model-Filtered Ranking
# Score importance 1-10, keep >7
def _rank_salience(self, items):
    scores = self._model_score_importance(items)
    return [item for item, score in zip(items, scores) if score >= 7]

# Variant 4: Top-K Salience
# Keep exactly K items
def _top_k_salience(self, items, k=10):
    ranked = self._rank_salience(items)
    return ranked[:k]
```

---

## Research Questions This Strategy Tests

1. **Can models reliably identify goal-critical information?**
   - Measure: Precision/recall of salience extraction
   - Hypothesis: Models will miss subtle constraints but catch explicit ones

2. **Does adaptive salience outperform fixed schema?**
   - Compare: Strategy H vs Strategy F (Protected Core)
   - Hypothesis: Adaptive better for evolving goals, fixed better for stable goals

3. **How does salience detection degrade with compression?**
   - Measure: Salience accuracy at compression points 1, 2, 3
   - Hypothesis: Cumulative errors compound

4. **What types of information do models prioritize?**
   - Analyze: What gets extracted vs what doesn't
   - Hypothesis: Models favor explicit statements over implicit context

---

## Recommended Next Steps

### 1. Implementation (Priority: HIGH)

- [ ] Create `strategies/strategy_h_selective_salience.py`
- [ ] Implement `_extract_salient_information()` with exact prompts
- [ ] Implement `_compress_background()` with deduplication
- [ ] Add salience set management (growth, deduplication, token budget)
- [ ] Add error handling and fallbacks

### 2. Evaluation Metrics (Priority: HIGH)

- [ ] Add `evaluate_salience_accuracy()` function
- [ ] Define ground truth salience for test templates
- [ ] Measure precision/recall at each compression point
- [ ] Track false positives/negatives

### 3. Documentation (Priority: MEDIUM)

- [ ] Add to PRD as Strategy H
- [ ] Update strategy comparison table
- [ ] Document variants and when to use each
- [ ] Add to implementation checklist

### 4. Testing (Priority: MEDIUM)

- [ ] Run on same templates as other strategies
- [ ] Compare goal coherence vs Protected Core
- [ ] Measure salience detection accuracy
- [ ] Analyze failure modes

---

## Comparison Matrix

| Strategy | Goal Protection | Adaptability | Error Risk | Token Efficiency |
|----------|----------------|--------------|------------|------------------|
| **A** (Naive) | ❌ None | N/A | High | High |
| **B** (Codex) | ⚠️ Implicit | Low | Medium | High |
| **C** (Hierarchical) | ⚠️ Implicit | Low | Medium | High |
| **D** (A-MEM) | ⚠️ Retrieval-based | Medium | Medium | Medium |
| **E** (claude-mem) | ⚠️ Tool-focused | Medium | Medium | Medium |
| **F** (Protected Core) | ✅ Explicit schema | Low | Low | Medium |
| **G** (Hybrid) | ✅ Explicit + retrieval | Medium | Low | Medium |
| **H** (Selective Salience) | ✅ Model-judged | **High** | **Medium** | Medium |

**Key Insight:** Strategy H offers the highest adaptability but introduces model judgment errors. This makes it valuable for testing whether models can reliably identify salience.

---

## Final Recommendation

✅ **APPROVE** Selective Salience Compression as **Strategy H**

**Rationale:**
1. Tests a distinct hypothesis (model salience detection)
2. Complements Protected Core (adaptive vs fixed)
3. Addresses goal coherence directly
4. Fits evaluation framework

**Conditions:**
1. Add full implementation details
2. Define evaluation metrics for salience accuracy
3. Add error handling and fallbacks
4. Integrate into PRD as Strategy H

**Expected Outcome:**
- Strategy H will likely show:
  - Higher adaptability than Protected Core
  - Lower goal coherence than Protected Core (due to errors)
  - Better than naive summarization
  - Interesting failure modes to analyze

This makes it a valuable addition to the comparative evaluation framework.

---

## Questions to Answer

1. **Should salience set be cumulative or reset at each compression?**
   - Recommendation: Cumulative with deduplication

2. **What's the token budget for salience set?**
   - Recommendation: 5K tokens max, prioritize constraints > decisions > facts

3. **How to handle salience extraction failures?**
   - Recommendation: Fallback to Protected Core schema

4. **Should we test variants or just one implementation?**
   - Recommendation: Start with conservative variant, add others if time permits

5. **How to measure salience accuracy without ground truth?**
   - Recommendation: Use LLM-as-judge with rubric, validate on known templates

---

*Review completed: 2025-01-XX*

