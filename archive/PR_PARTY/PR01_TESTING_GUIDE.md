# PR#01: Testing Guide

**Strategy:** Strategy H - Selective Salience Compression  
**Purpose:** Comprehensive testing strategy for salience extraction and compression

---

## Test Categories

### 1. Unit Tests (Mocked API)

**Purpose:** Test logic without API costs, fast execution

**Test Suite:** `tests/test_strategy_h.py`

#### 1.1: Core Methods

**Test: `initialize()` Method**
- [ ] Test stores original goal correctly
- [ ] Test stores constraints correctly
- [ ] Test salience_set initialized as empty list
- [ ] Test logging works

**Test: `update_goal()` Method**
- [ ] Test goal updated correctly
- [ ] Test logging includes rationale
- [ ] Test updated goal used in next extraction

**Test: `name()` Method**
- [ ] Test returns correct name: "Strategy H - Selective Salience Compression"

**Test: `compress()` Method (Basic Flow)**
- [ ] Test with empty context (returns empty/fallback)
- [ ] Test with single turn
- [ ] Test with multiple turns
- [ ] Test calls extraction, compression, rebuilding in order
- [ ] Test error handling (API failures)

#### 1.2: Salience Extraction

**Test: `_extract_salient_information()` Method**
- [ ] Test with mock valid JSON response
  - Valid items extracted
  - Items are strings (verbatim quotes)
- [ ] Test with mock empty items list
  - Returns empty list
  - No errors
- [ ] Test with mock malformed JSON
  - Error handling works
  - Fallback triggered
- [ ] Test with mock API error
  - Exception caught
  - Fallback to Protected Core schema
- [ ] Test prompt includes goal and constraints
- [ ] Test prompt requests verbatim quotes

**Mock Setup:**
```python
@patch('openai.OpenAI')
def test_extract_salience(mock_openai):
    mock_response = Mock()
    mock_response.choices = [Mock()]
    mock_response.choices[0].message.content = '{"salient_items": ["quote 1", "quote 2"]}'
    # ... setup ...
```

#### 1.3: Background Compression

**Test: `_compress_background()` Method**
- [ ] Test with mock valid response
  - Summary returned
  - Summary doesn't duplicate salience items
- [ ] Test with salience items in context
  - Salience items excluded from compression
- [ ] Test error handling
  - API failure handled gracefully
  - Fallback summary returned

#### 1.4: Context Rebuilding

**Test: `_build_context()` Method**
- [ ] Test all sections included:
  - System prompt (if available)
  - SALIENT INFORMATION section
  - BACKGROUND SUMMARY section
  - RECENT TURNS section
- [ ] Test format is correct
- [ ] Test with empty salience set
- [ ] Test with empty background summary
- [ ] Test with empty recent turns

---

### 2. Salience Management Tests

#### 2.1: Semantic Deduplication

**Test: `_deduplicate_semantically()` Method**
- [ ] Test with known similar items
  - Items: ["We must use PostgreSQL", "PostgreSQL is required"]
  - Expected: One item removed (similarity > 0.85)
- [ ] Test with different items
  - Items: ["Use PostgreSQL", "Budget is $10K"]
  - Expected: Both kept (similarity < 0.85)
- [ ] Test with empty list
  - Returns empty list
- [ ] Test with single item
  - Returns single item
- [ ] Test threshold parameter
  - Lower threshold (0.80) removes more items
  - Higher threshold (0.90) removes fewer items
- [ ] Test keeps shorter item when duplicates found
- [ ] Test performance (<1 second for 100 items)

**Test Data:**
```python
similar_items = [
    "We must use PostgreSQL",
    "PostgreSQL is required",  # Similar to first
    "Budget is $10K",  # Different
]
```

#### 2.2: Token Budget Management

**Test: `_apply_token_budget()` Method**
- [ ] Test with items under budget
  - All items kept
- [ ] Test with items over budget
  - Items prioritized (constraints > decisions > facts)
  - Items selected up to budget
- [ ] Test with single large item
  - Item truncated to fit budget
- [ ] Test prioritization logic
  - Constraints kept first
  - Decisions kept second
  - Facts kept last
- [ ] Test token counting accuracy
  - Uses tiktoken correctly
  - Counts match expected values

**Test Data:**
```python
large_items = ["x" * 200] * 10  # Each ~50 tokens
budget = 100  # Can fit ~2 items
```

#### 2.3: Salience Set Merging

**Test: `_merge_salience()` Method**
- [ ] Test merging adds new items
  - Existing: ["item 1"]
  - New: ["item 2"]
  - Result: ["item 1", "item 2"]
- [ ] Test deduplication removes similar items
  - Existing: ["Use PostgreSQL"]
  - New: ["PostgreSQL is required"]
  - Result: One item (deduplicated)
- [ ] Test token budget enforced
  - Combined items exceed budget
  - Result fits within budget
- [ ] Test cumulative growth
  - Multiple merges accumulate items
  - Deduplication prevents unbounded growth
- [ ] Test with empty existing set
- [ ] Test with empty new set

---

### 3. Integration Tests (Real Templates, Mocked API)

**Purpose:** Test full flow with realistic data

#### 3.1: Full Compression Flow

**Test: Complete Compression Cycle**
- [ ] Load `test-simple.json` template
- [ ] Initialize Strategy H with template goal/constraints
- [ ] Run compression at compression point
- [ ] Verify salience extracted
- [ ] Verify background compressed
- [ ] Verify context rebuilt correctly
- [ ] Verify salience set updated

**Test: Multiple Compressions**
- [ ] Load template with multiple compression points
- [ ] Run first compression
- [ ] Verify salience set populated
- [ ] Run second compression
- [ ] Verify salience set accumulates (with deduplication)
- [ ] Verify token budget enforced across compressions

#### 3.2: Integration with Evaluation Harness

**Test: Harness Integration**
- [ ] Create Strategy H instance
- [ ] Run `run_single_trial()` with Strategy H
- [ ] Verify salience metrics collected (if ground truth available)
- [ ] Verify results format matches expected structure
- [ ] Verify no errors in harness execution

**Test: Metrics Collection**
- [ ] Extract salience from Strategy H
- [ ] Get ground truth from template
- [ ] Calculate salience accuracy metrics
- [ ] Verify precision/recall/F1 calculated correctly
- [ ] Verify metrics included in results

---

### 4. Edge Cases

#### 4.1: Empty Context
- [ ] Test `compress()` with empty context
  - Returns appropriate fallback
  - No errors

#### 4.2: No Salience Extracted
- [ ] Test when extraction returns empty list
  - Fallback to Protected Core schema
  - Compression still succeeds
  - Logs fallback

#### 4.3: Too Much Salience Extracted
- [ ] Test when extraction returns >50 items
  - Token budget enforced
  - Prioritization applied
  - Compression succeeds

#### 4.4: Goal Evolution
- [ ] Test `update_goal()` mid-task
- [ ] Test new goal used in next extraction
- [ ] Test salience reflects current goal

#### 4.5: Implicit Constraints
- [ ] Test extraction with implicit constraints
- [ ] Verify model can identify implicit constraints
- [ ] Verify constraints preserved in salience set

#### 4.6: Very Long Salience Items
- [ ] Test with items exceeding token budget individually
- [ ] Verify truncation works
- [ ] Verify important parts preserved

---

### 5. Performance Tests

#### 5.1: Deduplication Performance
- [ ] Test with 10 items (<0.1 seconds)
- [ ] Test with 50 items (<0.5 seconds)
- [ ] Test with 100 items (<1 second)
- [ ] Test with 200 items (<2 seconds)

#### 5.2: Extraction Performance
- [ ] Test extraction API call (<10 seconds)
- [ ] Test with small context (<5 seconds)
- [ ] Test with large context (<15 seconds)

#### 5.3: Compression Performance
- [ ] Test compression API call (<5 seconds)
- [ ] Test with small context (<3 seconds)
- [ ] Test with large context (<8 seconds)

#### 5.4: Total Compression Time
- [ ] Test full compression cycle (<20 seconds)
- [ ] Test with multiple compressions (each <20 seconds)

---

### 6. Evaluation Tests (Real API, Real Templates)

**Purpose:** Validate end-to-end with real API

**Note:** These tests cost API credits. Run manually before releases.

#### 6.1: Salience Accuracy Evaluation

**Test: Ground Truth Comparison**
- [ ] Run Strategy H on `research-synthesis-001.json`
- [ ] Extract salience at compression points
- [ ] Compare with ground truth salience
- [ ] Calculate precision/recall/F1
- [ ] Verify precision >0.75
- [ ] Verify recall >0.75
- [ ] Verify F1 >0.77

**Test: Category-Specific Accuracy**
- [ ] Test constraint extraction accuracy
- [ ] Test decision extraction accuracy
- [ ] Test goal extraction accuracy
- [ ] Test fact extraction accuracy

#### 6.2: Goal Coherence Preservation

**Test: Goal Coherence Maintenance**
- [ ] Run Strategy H on template
- [ ] Measure goal coherence before compression
- [ ] Measure goal coherence after compression
- [ ] Verify coherence >0.90 maintained
- [ ] Compare with other strategies

**Test: Constraint Recall**
- [ ] Run Strategy H on template
- [ ] Measure constraint recall before compression
- [ ] Measure constraint recall after compression
- [ ] Verify recall maintained (>0.80)

#### 6.3: Comparison with Other Strategies

**Test: Strategy Comparison**
- [ ] Run Strategy H on same template as Strategy B
- [ ] Compare goal coherence scores
- [ ] Compare constraint recall scores
- [ ] Compare compression ratios
- [ ] Analyze differences

---

## Acceptance Criteria

**Feature is complete when:**

### Functional Requirements
- [ ] Strategy H can be imported and instantiated
- [ ] `compress()` method returns formatted context string
- [ ] Salience extraction produces verbatim quotes
- [ ] Background compression excludes salience items
- [ ] Deduplication removes similar items
- [ ] Token budget enforced correctly
- [ ] Error handling graceful (fallbacks work)
- [ ] Integration with harness collects metrics

### Quality Requirements
- [ ] Test coverage >80%
- [ ] All unit tests passing
- [ ] All integration tests passing
- [ ] No critical bugs
- [ ] Performance targets met:
  - Deduplication: <1 second for 100 items
  - Extraction: <10 seconds
  - Compression: <5 seconds
  - Total: <20 seconds per compression point

### Evaluation Requirements
- [ ] Salience accuracy: >0.75 precision/recall (if ground truth available)
- [ ] Goal coherence: >0.90 maintained
- [ ] Tested on 3+ templates
- [ ] Results format matches expected structure

---

## Test Execution Plan

### Phase 1: Unit Tests (During Development)
- Run after each method implementation
- Fast feedback (<1 minute)
- No API costs
- **Command:** `pytest tests/test_strategy_h.py::TestCoreMethods -v`

### Phase 2: Integration Tests (After Phase 3)
- Run after integration complete
- Uses real templates, mocked API
- **Command:** `pytest tests/test_strategy_h.py::TestIntegration -v`

### Phase 3: Evaluation Tests (Before Release)
- Run manually before releases
- Uses real API (costs credits)
- **Command:** `pytest tests/test_strategy_h.py::TestEvaluation -v --integration`

### Phase 4: Full Test Suite (CI/CD)
- Run all tests except evaluation tests
- **Command:** `pytest tests/test_strategy_h.py -v --ignore=tests/test_strategy_h.py::TestEvaluation`

---

## Test Data

### Simple Test Template (`test-simple.json`)
```json
{
  "template_id": "test-simple",
  "initial_setup": {
    "original_goal": "Choose database",
    "hard_constraints": ["Must be PostgreSQL"]
  },
  "turns": [
    {"turn_id": 1, "role": "user", "content": "We need PostgreSQL"},
    {"turn_id": 2, "role": "assistant", "content": "OK"},
    {"turn_id": 3, "is_compression_point": true}
  ],
  "ground_truth": {
    "salient_items": [
      "We need PostgreSQL",
      "Must be PostgreSQL"
    ]
  }
}
```

### Edge Case Template (`test-edge-cases.json`)
- Goal evolution mid-task
- Implicit constraints
- Many similar salience items
- Empty extraction scenario
- Very long items

---

## Debugging Tips

### Issue: Salience Extraction Returns Nothing
**Debug Steps:**
1. Check prompt includes goal and constraints
2. Verify API response format
3. Check JSON parsing
4. Review logs for errors
5. Test with simpler prompt

### Issue: Deduplication Too Aggressive
**Debug Steps:**
1. Check similarity scores (log them)
2. Verify threshold (try 0.80)
3. Review which items removed
4. Test with known similar items

### Issue: Token Budget Exceeded
**Debug Steps:**
1. Verify token counting (use tiktoken)
2. Check prioritization logic
3. Review item sizes
4. Test with smaller budget

### Issue: Integration Fails
**Debug Steps:**
1. Verify Strategy H exports correctly
2. Check harness imports Strategy H
3. Verify metrics collection code
4. Review error messages

---

## Test Coverage Goals

**Target Coverage:**
- Core methods: >90%
- Salience management: >85%
- Error handling: >80%
- Integration: >75%
- **Overall: >80%**

**Coverage Command:**
```bash
pytest tests/test_strategy_h.py --cov=strategies.strategy_h_selective_salience --cov-report=html
```

---

## Continuous Testing

### During Development
- Run unit tests after each method
- Fix issues immediately
- Don't accumulate technical debt

### Before Commits
- Run full test suite (except evaluation)
- Verify coverage >80%
- Fix any failures

### Before Releases
- Run evaluation tests
- Verify quality metrics met
- Document any issues

---

*Testing Guide created: 2025-01-XX*  
*Last updated: 2025-01-XX*

