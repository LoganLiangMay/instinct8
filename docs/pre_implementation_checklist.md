# Pre-Implementation Checklist for Strategy H

**Purpose:** Identify all requirements, dependencies, and clarifications needed before implementing Selective Salience Compression (Strategy H)

**Date:** 2025-01-XX

---

## ✅ What We Have

### Documentation
- [x] Strategy H concept document (`Selective Salience Compression.md`)
- [x] Strategy H added to PRD with implementation structure
- [x] Evaluation methods documented (3 methods, detailed implementation)
- [x] LLM-as-Judge implementation guide (OpenAI-specific)
- [x] Base class interface understood (`CompressionStrategy`)

### Understanding
- [x] How Codex compacts (baseline for comparison)
- [x] How other strategies work (Strategy B as reference)
- [x] Evaluation framework structure
- [x] OpenAI API requirements

---

## ❓ What We Need to Clarify

### 1. Implementation Details

#### 1.1 OpenAI Client Setup
**Question:** How should we initialize the OpenAI client?
- [ ] Use `openai` Python library?
- [ ] API key from environment variable (`OPENAI_API_KEY`)?
- [ ] Any specific configuration needed (timeouts, retries)?

**Action:** Confirm OpenAI client setup approach

#### 1.2 Model Selection for Salience Extraction
**Question:** Which OpenAI model should Strategy H use for salience extraction?
- [ ] GPT-4o (best quality, more expensive)
- [ ] GPT-4 Turbo (balanced)
- [ ] GPT-4o-mini (cost-effective)
- [ ] Make it configurable?

**Current PRD says:** `model: str = "claude-sonnet-4-20250514"` ❌ (needs update)

**Action:** Update PRD to use OpenAI model, decide on default

#### 1.3 Model Selection for Background Compression
**Question:** Should background compression use the same model or a cheaper one?
- [ ] Same model (simpler, consistent)
- [ ] Cheaper model (GPT-4o-mini for compression, GPT-4o for extraction)
- [ ] Make it configurable?

**Action:** Decide on compression model strategy

#### 1.4 Salience Set Management
**Questions:**
- [ ] How to handle cumulative salience set growth?
- [ ] What's the token budget for salience set? (PRD mentions 5K tokens)
- [ ] How to deduplicate semantically? (need embedding model?)
- [ ] Should salience set persist across multiple compressions?

**Action:** Finalize salience set management strategy

#### 1.5 Error Handling
**Questions:**
- [ ] What happens if salience extraction fails?
- [ ] What happens if extraction returns nothing?
- [ ] What happens if extraction returns too much (>50 items)?
- [ ] Fallback strategy? (e.g., use Protected Core schema?)

**Action:** Define error handling and fallback strategies

### 2. Integration Points

#### 2.1 Context Format
**Question:** Confirm context format matches existing strategies?
- [ ] Context is `List[Dict[str, Any]]` with keys: `id`, `role`, `content`, `tool_call`, `is_compression_point`
- [ ] Use `format_context()` helper from base class?
- [ ] Any special handling needed?

**Action:** Verify context format compatibility

#### 2.2 Evaluation Harness Integration
**Questions:**
- [ ] How does Strategy H integrate with evaluation harness?
- [ ] Does it need special handling for salience accuracy metrics?
- [ ] How to collect salience extraction results for evaluation?

**Action:** Review evaluation harness integration requirements

#### 2.3 Logging and Debugging
**Questions:**
- [ ] Use `self.log()` from base class?
- [ ] What level of logging needed?
- [ ] Should we log extracted salience for debugging?

**Action:** Define logging requirements

### 3. Prompt Engineering

#### 3.1 Salience Extraction Prompt
**Questions:**
- [ ] Finalize exact prompt wording (PRD has draft)
- [ ] Should prompt include examples?
- [ ] How to ensure verbatim quotes (not paraphrases)?
- [ ] Use structured outputs (JSON mode) or parse free-form?

**Action:** Finalize salience extraction prompt

#### 3.2 Background Compression Prompt
**Questions:**
- [ ] Finalize exact prompt wording
- [ ] How to ensure no duplication with salience set?
- [ ] What level of compression? (2-3 sentences?)

**Action:** Finalize background compression prompt

#### 3.3 Output Format
**Questions:**
- [ ] Use OpenAI's JSON mode for structured outputs?
- [ ] Or parse free-form text with quotes?
- [ ] How to handle malformed outputs?

**Action:** Decide on output format and parsing strategy

### 4. Dependencies

#### 4.1 Required Libraries
**Checklist:**
- [ ] `openai` Python library (for API calls)
- [ ] Any embedding library for semantic deduplication? (e.g., `sentence-transformers`?)
- [ ] Any other dependencies?

**Action:** List all required dependencies

#### 4.2 Token Counting
**Questions:**
- [ ] How to count tokens? (use `tiktoken`?)
- [ ] Need approximate or exact counts?
- [ ] For salience set budget management?

**Action:** Decide on token counting approach

### 5. Testing Strategy

#### 5.1 Unit Tests
**Questions:**
- [ ] What to test?
  - [ ] Salience extraction (mock API responses)
  - [ ] Background compression
  - [ ] Salience set merging/deduplication
  - [ ] Error handling
  - [ ] Context rebuilding

**Action:** Define unit test requirements

#### 5.2 Integration Tests
**Questions:**
- [ ] Test with real templates?
- [ ] Test with mock templates?
- [ ] How to test without spending API credits?

**Action:** Define integration test approach

#### 5.3 Evaluation Tests
**Questions:**
- [ ] How to test salience accuracy?
- [ ] Use ground truth templates?
- [ ] Compare with other strategies?

**Action:** Define evaluation test requirements

### 6. Configuration

#### 6.1 Configurable Parameters
**Questions:**
- [ ] Which parameters should be configurable?
  - [ ] Model for salience extraction
  - [ ] Model for background compression
  - [ ] Salience set token budget
  - [ ] Semantic similarity threshold for deduplication
  - [ ] Max salience items
  - [ ] Recent turns to keep raw

**Action:** Define configuration parameters

#### 6.2 Default Values
**Questions:**
- [ ] What are good defaults?
- [ ] Conservative vs aggressive settings?

**Action:** Define default configuration

### 7. Edge Cases

#### 7.1 Empty Context
**Question:** What if `context[:trigger_point]` is empty?
- [ ] Return empty string?
- [ ] Return system prompt only?

**Action:** Define behavior

#### 7.2 No Salience Extracted
**Question:** What if model extracts nothing?
- [ ] Fallback to Protected Core schema?
- [ ] Use all context as salience?
- [ ] Error?

**Action:** Define fallback strategy

#### 7.3 Too Much Salience
**Question:** What if model extracts >50 items?
- [ ] Rank and take top K?
- [ ] Truncate by token budget?
- [ ] Error?

**Action:** Define handling strategy

#### 7.4 Goal Evolution
**Question:** How to handle goal changes mid-task?
- [ ] Update salience extraction prompt with new goal?
- [ ] Keep original goal for context?
- [ ] Track goal evolution in salience set?

**Action:** Define goal evolution handling

### 8. Performance Considerations

#### 8.1 API Call Optimization
**Questions:**
- [ ] Can we batch API calls?
- [ ] Cache identical extractions?
- [ ] Parallel extraction and compression?

**Action:** Define optimization strategy

#### 8.2 Cost Management
**Questions:**
- [ ] Expected cost per compression?
- [ ] How to minimize costs?
- [ ] Use cheaper models where possible?

**Action:** Define cost optimization strategy

### 9. Documentation Updates

#### 9.1 Code Documentation
**Checklist:**
- [ ] Docstrings for all methods
- [ ] Type hints
- [ ] Inline comments for complex logic

**Action:** Define documentation standards

#### 9.2 README Updates
**Checklist:**
- [ ] Update `strategies/__init__.py` to include Strategy H
- [ ] Update base class docstring (7 → 8 strategies)
- [ ] Add Strategy H to exports

**Action:** Update package documentation

### 10. Comparison with Other Strategies

#### 10.1 Differences to Highlight
**Questions:**
- [ ] How is Strategy H different from Strategy F (Protected Core)?
- [ ] How is Strategy H different from Strategy D (A-MEM)?
- [ ] What unique capabilities does it test?

**Action:** Document key differences

---

## 🔧 Technical Decisions Needed

### Decision 1: OpenAI Model Selection
**Options:**
- A) GPT-4o for everything (best quality, expensive)
- B) GPT-4 Turbo for everything (balanced)
- C) GPT-4o-mini for everything (cost-effective)
- D) GPT-4o for extraction, GPT-4o-mini for compression (hybrid)

**Recommendation:** Option D (hybrid approach)
- Use GPT-4o for salience extraction (critical, needs best quality)
- Use GPT-4o-mini for background compression (less critical, can be cheaper)

### Decision 2: Salience Set Token Budget
**Options:**
- A) 5K tokens (as mentioned in PRD)
- B) 10K tokens (more generous)
- C) Configurable (flexible)

**Recommendation:** Option C (configurable, default 5K)
- Allows experimentation
- Can adjust based on results

### Decision 3: Semantic Deduplication
**Options:**
- A) Use sentence-transformers for embeddings
- B) Use OpenAI embeddings API
- C) Simple string similarity (faster, less accurate)
- D) No deduplication (simpler)

**Recommendation:** Option A (sentence-transformers)
- Good balance of accuracy and cost
- Can run locally (no API calls)
- Fast enough for deduplication

### Decision 4: Output Format
**Options:**
- A) OpenAI JSON mode (structured, reliable)
- B) Free-form text with quotes (flexible, needs parsing)
- C) Function calling (most structured)

**Recommendation:** Option A (JSON mode)
- Reliable parsing
- Ensures consistent format
- Reduces errors

### Decision 5: Error Handling
**Options:**
- A) Fallback to Protected Core schema
- B) Retry with different prompt
- C) Return error and skip compression
- D) Use previous salience set

**Recommendation:** Option A (fallback to Protected Core)
- Ensures compression always succeeds
- Provides reasonable default
- Can log fallback for analysis

---

## 📋 Implementation Order

### Phase 1: Core Implementation (Week 1)
1. Set up OpenAI client
2. Implement `_extract_salient_information()` with basic prompt
3. Implement `_compress_background()` with basic prompt
4. Implement `_build_context()` to rebuild context
5. Basic error handling

### Phase 2: Salience Management (Week 1-2)
1. Implement salience set storage
2. Implement semantic deduplication
3. Implement token budget management
4. Implement prioritization (constraints > decisions > facts)

### Phase 3: Refinement (Week 2)
1. Refine prompts based on initial testing
2. Add structured outputs (JSON mode)
3. Improve error handling
4. Add logging

### Phase 4: Testing (Week 2-3)
1. Unit tests
2. Integration tests with templates
3. Evaluation tests
4. Compare with other strategies

### Phase 5: Documentation (Week 3)
1. Code documentation
2. Update package exports
3. Usage examples
4. Evaluation guide

---

## ✅ Pre-Implementation Actions

### Immediate Actions (Before Coding)
1. [ ] **Update PRD** - Change Anthropic references to OpenAI
2. [ ] **Decide on model selection** - Confirm default models
3. [ ] **Finalize prompts** - Get exact prompt wording
4. [ ] **Set up dependencies** - Install required libraries
5. [ ] **Create test templates** - Prepare test data

### Questions to Answer
1. [ ] What's the exact OpenAI API setup?
2. [ ] Which models for extraction vs compression?
3. [ ] How to handle semantic deduplication?
4. [ ] What are the error handling fallbacks?
5. [ ] How to integrate with evaluation harness?

---

## 🎯 Success Criteria

**Implementation is ready when:**
- [ ] All questions above are answered
- [ ] Dependencies are installed
- [ ] Test templates are prepared
- [ ] Prompts are finalized
- [ ] Error handling is defined
- [ ] Integration points are clear

---

## 📝 Notes

### Key Insights from Review
1. **PRD needs update** - Still references Anthropic/Claude models
2. **Base class needs update** - Says "7 strategies" but should be "8"
3. **Evaluation integration** - Need to understand how salience accuracy metrics are collected
4. **Cost optimization** - Important to use cheaper models where possible
5. **Error handling** - Critical for production use

### Risks to Mitigate
1. **API costs** - Can be expensive at scale, need optimization
2. **Prompt quality** - Initial prompts may need iteration
3. **Semantic deduplication** - May need tuning
4. **Error cases** - Need robust fallbacks

---

*Checklist created: 2025-01-XX*  
*Review before starting implementation*

