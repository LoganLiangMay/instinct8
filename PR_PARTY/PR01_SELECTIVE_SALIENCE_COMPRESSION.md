# PR#01: Selective Salience Compression (Strategy H)

**Estimated Time:** 20-30 hours  
**Complexity:** MEDIUM-HIGH  
**Dependencies:** None (new strategy implementation)  
**Status:** 📋 PLANNED

---

## Overview

### What We're Building

We're implementing **Strategy H: Selective Salience Compression** (also known as "Agent-as-Judge" compression). This strategy tests whether models can reliably identify goal-critical information without explicit schema protection.

Unlike Protected Core (Strategy F) which uses a fixed schema, Selective Salience relies on the model's own judgment to identify what matters for goal achievement. The model extracts salient information verbatim, then compresses everything else into a lightweight summary.

### Why It Matters

This strategy tests a **frontier capability**: Can models reliably predict what information they'll need later? This is valuable because:

1. **Adaptive**: No fixed schema means it can adapt to different task types
2. **Tests Model Judgment**: Measures whether models can identify salience accurately
3. **Human-Like**: Mimics how humans remember (important bits verbatim, rest compressed)
4. **Research Value**: Provides empirical data on model salience detection capabilities

### Success in One Sentence

"This PR is successful when Strategy H is fully implemented, tested, integrated with the evaluation harness, and demonstrates measurable salience detection accuracy (>0.75 precision/recall) while maintaining goal coherence (>0.90)."

---

## Technical Design

### Architecture Decisions

#### Decision 1: OpenAI API vs Anthropic API
**Options Considered:**
1. Anthropic Claude API - Used by other strategies
2. OpenAI API - Different model family, user preference

**Chosen:** OpenAI API

**Rationale:**
- User has OpenAI API key available
- GPT-4o provides excellent reasoning for salience extraction
- GPT-4o-mini provides cost-effective background compression
- Consistent API usage simplifies integration

**Trade-offs:**
- Gain: Cost optimization (can use cheaper models)
- Lose: Different API than other strategies (but isolated to Strategy H)

#### Decision 2: Semantic Deduplication Approach
**Options Considered:**
1. `all-MiniLM-L6-v2` (sentence-transformers) - Fast, good accuracy
2. `all-mpnet-base-v2` - Higher accuracy, slower
3. OpenAI embeddings API - No local dependencies, API costs

**Chosen:** `all-MiniLM-L6-v2`

**Rationale:**
- Fast enough for real-time deduplication (~5ms per embedding)
- Accurate enough for task (68.7% similarity accuracy)
- No API costs or rate limits
- Runs locally (no external dependencies during runtime)

**Trade-offs:**
- Gain: Fast, free, reliable
- Lose: Slightly less accurate than mpnet (but sufficient for deduplication)

#### Decision 3: Salience Set Management
**Options Considered:**
1. Cumulative with deduplication (grows across compressions)
2. Reset at each compression (fresh extraction each time)
3. Sliding window (keep last N items)

**Chosen:** Cumulative with deduplication

**Rationale:**
- Preserves important information across multiple compressions
- Deduplication prevents unbounded growth (semantic similarity filtering)
- Token usage tracked for monitoring/logging (no hard limit)
- Matches human memory (we remember important things, not just recent)
- If model correctly identifies salience, we should preserve it all

**Trade-offs:**
- Gain: Better information preservation
- Lose: More complex implementation (need deduplication logic)

#### Decision 4: Error Handling Strategy
**Options Considered:**
1. Fallback to Protected Core schema
2. Retry with different prompt
3. Return error and skip compression
4. Use previous salience set

**Chosen:** Fallback to Protected Core schema

**Rationale:**
- Ensures compression always succeeds
- Provides reasonable default behavior
- Can log fallback for analysis
- Better than failing silently

**Trade-offs:**
- Gain: Robust error handling
- Lose: May mask extraction failures (but logging addresses this)

### Data Model

**Strategy H State:**
```python
@dataclass
class SelectiveSalienceState:
    salience_set: List[str]  # Cumulative salient items (verbatim quotes)
    original_goal: str
    constraints: List[str]
    extraction_model: str  # e.g., "gpt-4o"
    compression_model: str  # e.g., "gpt-4o-mini"
    similarity_threshold: float  # e.g., 0.85
    # Note: No token budget - rely on deduplication to prevent unbounded growth
```

**No new database collections** - Strategy H is stateless between compressions (state stored in instance).

### API Design

**New Class:**
```python
class SelectiveSalienceStrategy(CompressionStrategy):
    """
    Selective Salience Compression: Model identifies and preserves 
    goal-critical information verbatim, compresses the rest.
    """
    
    def __init__(
        self,
        extraction_model: str = "gpt-4o",
        compression_model: str = "gpt-4o-mini",
        similarity_threshold: float = 0.85,
    ):
        """
        Initialize Strategy H with configuration.
        
        Note: No token budget parameter - we rely on semantic deduplication
        to prevent unbounded growth. Token usage is tracked for monitoring.
        """
        pass
    
    def initialize(self, original_goal: str, constraints: List[str]) -> None:
        """Store initial goal and constraints for salience extraction guidance."""
        pass
    
    def update_goal(self, new_goal: str, rationale: str = "") -> None:
        """Update goal if it evolves mid-task."""
        pass
    
    def compress(
        self,
        context: List[Dict[str, Any]],
        trigger_point: int,
    ) -> str:
        """
        Compress context using selective salience extraction.
        
        Steps:
        1. Extract salient information (verbatim quotes)
        2. Merge with existing salience set (deduplicate)
        3. Compress background (everything except salient items)
        4. Rebuild context: SYSTEM + SALIENT + BACKGROUND + RECENT
        """
        pass
    
    # Private methods
    def _extract_salient_information(
        self, context: List[Dict[str, Any]]
    ) -> List[str]:
        """Extract goal-critical information verbatim."""
        pass
    
    def _compress_background(
        self, context: List[Dict[str, Any]], salience_set: List[str]
    ) -> str:
        """Compress everything except salient items."""
        pass
    
    def _merge_salience(
        self, existing: List[str], new: List[str]
    ) -> List[str]:
        """Merge new salience with existing, deduplicate semantically."""
        pass
    
    def _deduplicate_semantically(
        self, items: List[str], threshold: float = 0.85
    ) -> List[str]:
        """Remove semantically similar items using embeddings."""
        pass
    
    def _token_count(self, text: str) -> int:
        """Count tokens for tracking/monitoring (no enforcement)."""
        pass
    
    def _build_context(
        self,
        salience_set: List[str],
        background_summary: str,
        recent_turns: List[Dict[str, Any]],
    ) -> str:
        """Rebuild context with salience first, then background, then recent."""
        pass
```

### Component Hierarchy
```
SelectiveSalienceStrategy/
├── OpenAI Client (for extraction & compression)
├── SentenceTransformer (for deduplication)
├── Salience Set Manager
│   └── Deduplication Engine (semantic similarity filtering)
├── Token Tracker (for monitoring/logging)
└── Context Rebuilder
```

---

## Implementation Details

### File Structure
**New Files:**
```
strategies/
├── strategy_h_selective_salience.py (~600 lines)
│   ├── SelectiveSalienceStrategy class
│   ├── Salience extraction logic
│   ├── Background compression logic
│   ├── Deduplication logic
│   └── Context rebuilding logic
└── __init__.py (updated to export Strategy H)

evaluation/
├── metrics.py (updated)
│   └── measure_salience_accuracy() function (NEW)

tests/
├── test_strategy_h.py (~400 lines)
│   ├── Unit tests (mocked API)
│   ├── Integration tests (real templates, mocked API)
│   └── Edge case tests

templates/
├── test-simple.json (NEW - minimal test template)
└── test-edge-cases.json (NEW - edge case template)
```

**Modified Files:**
- `strategies/__init__.py` (+5 lines) - Export Strategy H
- `strategies/strategy_base.py` (+1 line) - Update docstring (7 → 8 strategies)
- `evaluation/metrics.py` (+150 lines) - Add salience accuracy metrics
- `evaluation/harness.py` (+30 lines) - Collect salience metrics if available

### Key Implementation Steps

#### Phase 1: Core Implementation (8-10 hours)
1. Set up OpenAI client and dependencies
2. Implement `_extract_salient_information()` with prompt
3. Implement `_compress_background()` with prompt
4. Implement `_build_context()` to rebuild context
5. Basic error handling

#### Phase 2: Salience Management (4-6 hours)
1. Implement semantic deduplication using sentence-transformers
2. Implement token tracking (for monitoring/logging)
3. Implement salience set merging logic
4. Remove token budget enforcement (rely on deduplication)

#### Phase 3: Integration (4-6 hours)
1. Integrate with evaluation harness
2. Add salience accuracy metrics to `MetricsCollector`
3. Update results format to include salience metrics
4. Test with real templates

#### Phase 4: Testing & Refinement (4-6 hours)
1. Write unit tests (mocked API)
2. Write integration tests (real templates, mocked API)
3. Refine prompts based on testing
4. Add structured outputs (JSON mode)
5. Improve error handling

### Code Examples

**Example 1: Salience Extraction**
```python
def _extract_salient_information(
    self, context: List[Dict[str, Any]]
) -> List[str]:
    """
    Extract goal-critical information verbatim.
    
    Uses GPT-4o with structured JSON output to extract
    salient quotes from conversation context.
    """
    # Format context for prompt
    context_text = self.format_context(context)
    
    # Build extraction prompt
    prompt = f"""You are performing selective salience extraction for context compression.

From the following conversation, extract ONLY the information that will directly impact the agent's ability to achieve the user's goal.

Original Goal: {self.original_goal}
Constraints: {', '.join(self.constraints)}

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
{context_text}

Output format (JSON):
{{
  "salient_items": [
    "exact quote 1",
    "exact quote 2",
    ...
  ]
}}"""
    
    try:
        response = self.client.chat.completions.create(
            model=self.extraction_model,
            max_tokens=2000,
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
        )
        
        result = json.loads(response.choices[0].message.content)
        return result.get("salient_items", [])
    
    except Exception as e:
        self.log(f"Salience extraction failed: {e}")
        # Fallback to Protected Core schema
        return self._fallback_extract_constraints(context)
```

**Example 2: Semantic Deduplication**
```python
def _deduplicate_semantically(
    self, items: List[str], threshold: float = 0.85
) -> List[str]:
    """
    Remove semantically similar items using sentence embeddings.
    
    Uses all-MiniLM-L6-v2 for fast, accurate similarity detection.
    """
    if len(items) <= 1:
        return items
    
    # Generate embeddings
    embeddings = self.embedding_model.encode(items, show_progress_bar=False)
    
    # Calculate similarity matrix
    from sklearn.metrics.pairwise import cosine_similarity
    similarity_matrix = cosine_similarity(embeddings)
    
    # Find duplicates
    to_remove = set()
    for i in range(len(items)):
        if i in to_remove:
            continue
        for j in range(i + 1, len(items)):
            if similarity_matrix[i][j] > threshold:
                # Keep shorter item (more concise)
                if len(items[i]) > len(items[j]):
                    to_remove.add(i)
                else:
                    to_remove.add(j)
    
    return [item for idx, item in enumerate(items) if idx not in to_remove]
```

---

## Testing Strategy

### Test Categories

**Unit Tests:**
- Salience extraction parsing (mock JSON responses)
- Background compression logic
- Semantic deduplication (known similar items)
- Token budget enforcement
- Error handling (empty extraction, API failures)
- Context rebuilding format

**Integration Tests:**
- Full compression flow with real templates
- Salience set accumulation across compressions
- Integration with evaluation harness
- Error recovery (fallback to Protected Core)

**Edge Cases:**
- Empty context
- No salience extracted
- Too much salience extracted (>50 items)
- Goal evolution mid-task
- Implicit constraints
- Very long salience items

**Performance Tests:**
- Deduplication speed (<1 second for 100 items)
- Token counting accuracy
- API call efficiency

### Test Templates

**1. Simple Template (`test-simple.json`):**
- 3-5 turns
- 1 compression point
- Clear goal and constraints
- Known ground truth salience

**2. Edge Case Template (`test-edge-cases.json`):**
- Goal evolution mid-task
- Implicit constraints
- Many similar salience items (test deduplication)
- Empty extraction scenario

**3. Real Template (`research-synthesis-001.json`):**
- Already exists
- Use for integration tests
- Has ground truth salience

---

## Success Criteria

**Feature is complete when:**
- [ ] Strategy H class implemented with all methods
- [ ] Semantic deduplication working correctly
- [ ] Token tracking implemented (for monitoring/logging)
- [ ] Error handling with fallbacks implemented
- [ ] Integration with evaluation harness complete
- [ ] Salience accuracy metrics added to `MetricsCollector`
- [ ] Unit tests passing (>80% coverage)
- [ ] Integration tests passing
- [ ] Tested on 3+ templates
- [ ] Salience accuracy >0.75 precision/recall (if ground truth available)
- [ ] Goal coherence >0.90 maintained
- [ ] Documentation complete

**Performance Targets:**
- Deduplication: <1 second for 100 items
- Extraction: <10 seconds per compression
- Compression: <5 seconds per compression
- Total: <20 seconds per compression point

**Quality Gates:**
- Zero critical bugs
- Test coverage >80%
- No console errors
- All tests passing

---

## Risk Assessment

### Risk 1: OpenAI API Rate Limits
**Likelihood:** MEDIUM  
**Impact:** HIGH  
**Mitigation:** 
- Implement exponential backoff
- Use async requests where possible
- Monitor rate limits
- Consider upgrading tier if needed
**Status:** 🟡

### Risk 2: Semantic Deduplication Accuracy
**Likelihood:** LOW  
**Impact:** MEDIUM  
**Mitigation:**
- Use proven model (all-MiniLM-L6-v2)
- Test threshold (0.85) on sample data
- Allow threshold configuration
- Log deduplication decisions for analysis
**Status:** 🟢

### Risk 3: Salience Extraction Quality
**Likelihood:** MEDIUM  
**Impact:** HIGH  
**Mitigation:**
- Use best model (GPT-4o) for extraction
- Refine prompts based on testing
- Use structured outputs (JSON mode)
- Implement fallback to Protected Core schema
- Evaluate with ground truth
**Status:** 🟡

### Risk 4: Unbounded Salience Set Growth
**Likelihood:** LOW  
**Impact:** MEDIUM  
**Mitigation:**
- Semantic deduplication prevents true redundancy
- Token tracking for monitoring/logging
- If growth becomes problematic, can add soft limits later
- Trust model's salience judgment (if wrong, that's a salience accuracy issue)
**Status:** 🟢

### Risk 5: Integration with Evaluation Harness
**Likelihood:** LOW  
**Impact:** MEDIUM  
**Mitigation:**
- Follow existing patterns (Strategy B as reference)
- Test integration early
- Make salience metrics optional
**Status:** 🟢

---

## Open Questions

1. **Question 1:** Should salience set persist across multiple conversation sessions?
   - Option A: Yes, persist to file/database
   - Option B: No, reset for each new conversation
   - Decision needed by: Phase 2
   - **Decision:** Option B (reset for each conversation) - simpler, matches other strategies

2. **Question 2:** How to handle goal evolution in salience extraction?
   - Option A: Update prompt with new goal
   - Option B: Keep original goal, track evolution separately
   - Decision needed by: Phase 1
   - **Decision:** Option A (update prompt) - ensures salience reflects current goal

3. **Question 3:** Should we log all salience extractions for analysis?
   - Option A: Yes, log to file
   - Option B: No, only log errors
   - Decision needed by: Phase 3
   - **Decision:** Option A (log all) - valuable for analysis and debugging

---

## Timeline

**Total Estimate:** 20-30 hours

| Phase | Task | Time | Status |
|-------|------|------|--------|
| 1 | Core Implementation | 8-10 h | ⏳ |
| 2 | Salience Management | 6-8 h | ⏳ |
| 3 | Integration | 4-6 h | ⏳ |
| 4 | Testing & Refinement | 4-6 h | ⏳ |

**Breakdown:**
- Week 1: Phases 1-2 (Core + Management)
- Week 2: Phases 3-4 (Integration + Testing)

---

## Dependencies

**Requires:**
- [x] OpenAI API key
- [x] Python 3.10+
- [ ] `openai` library (install: `pip install openai`)
- [ ] `sentence-transformers` library (install: `pip install sentence-transformers`)
- [ ] `scikit-learn` library (install: `pip install scikit-learn`)
- [ ] `tiktoken` library (install: `pip install tiktoken`)
- [x] Evaluation harness (exists)
- [x] Strategy base class (exists)
- [x] Test templates (1 exists, need 2 more)

**Blocks:**
- None (independent strategy implementation)

---

## References

- Related PR: None (first PR)
- Design doc: `Selective Salience Compression.md`
- Evaluation methods: `docs/strategy_h_evaluation_methods.md`
- Implementation guide: `docs/llm_as_judge_implementation_guide.md`
- Recommendations: `docs/implementation_recommendations.md`
- PRD: `context_compression_prd.md` (Strategy H section)

---

*Document created: 2025-01-XX*  
*Last updated: 2025-01-XX*

