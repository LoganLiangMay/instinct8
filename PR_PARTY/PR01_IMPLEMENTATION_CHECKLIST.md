# PR#01: Implementation Checklist

**Use this as your daily todo list.** Check off items as you complete them.

---

## Pre-Implementation Setup (30 minutes)

- [ ] Read main planning document (`PR01_SELECTIVE_SALIENCE_COMPRESSION.md`) (~45 min)
- [ ] Read implementation recommendations (`docs/implementation_recommendations.md`) (~15 min)
- [ ] Prerequisites verified
  - [ ] OpenAI API key set in environment: `export OPENAI_API_KEY="sk-..."`
  - [ ] Python 3.10+ installed
  - [ ] Virtual environment activated
- [ ] Dependencies installed
  ```bash
  pip install openai sentence-transformers scikit-learn tiktoken
  ```
- [ ] Git branch created
  ```bash
  git checkout -b feature/pr01-selective-salience
  ```
- [ ] Test OpenAI API connection
  ```python
  from openai import OpenAI
  client = OpenAI()
  # Test with simple call
  ```

---

## Phase 1: Core Implementation (8-10 hours)

### 1.1: Set Up Dependencies and Base Structure (1 hour)

#### Create File
- [ ] Create `strategies/strategy_h_selective_salience.py`

#### Add Imports
- [ ] Add imports
  ```python
  from typing import Any, Dict, List, Optional
  from dataclasses import dataclass, field
  import json
  from openai import OpenAI
  from sentence_transformers import SentenceTransformer
  from sklearn.metrics.pairwise import cosine_similarity
  import numpy as np
  import tiktoken
  
  from .strategy_base import CompressionStrategy
  ```

#### Create Class Skeleton
- [ ] Create `SelectiveSalienceStrategy` class inheriting from `CompressionStrategy`
- [ ] Add `__init__` method with parameters:
  - `extraction_model: str = "gpt-4o"`
  - `compression_model: str = "gpt-4o-mini"`
  - `salience_token_budget: int = 5000`
  - `similarity_threshold: float = 0.85`
- [ ] Initialize OpenAI client
- [ ] Initialize sentence transformer model (`all-MiniLM-L6-v2`)
- [ ] Initialize tiktoken encoder

#### Test
- [ ] Test class instantiation
- [ ] Test OpenAI client connection
- [ ] Test sentence transformer loads correctly

**Checkpoint:** Base structure working ✓

**Commit:** `feat(strategy-h): add base class structure`

---

### 1.2: Implement `initialize()` Method (15 minutes)

#### Implement Method
- [ ] Store `original_goal` and `constraints`
- [ ] Initialize empty `salience_set` list
- [ ] Add logging

#### Test
- [ ] Test initialization stores goal and constraints
- [ ] Test salience_set starts empty

**Commit:** `feat(strategy-h): implement initialize method`

---

### 1.3: Implement `_extract_salient_information()` Method (2-3 hours)

#### Design Prompt
- [ ] Create salience extraction prompt template
- [ ] Include original goal and constraints in prompt
- [ ] Specify JSON output format
- [ ] Request verbatim quotes (not summaries)
- [ ] Include examples of what to include/exclude

#### Implement Method
- [ ] Format conversation context using `format_context()` helper
- [ ] Build prompt with goal, constraints, context
- [ ] Call OpenAI API with JSON mode
- [ ] Parse JSON response
- [ ] Extract `salient_items` list
- [ ] Handle empty extraction (return empty list)
- [ ] Add error handling with logging

#### Test
- [ ] Test with mock API response (valid JSON)
- [ ] Test with mock API response (empty items)
- [ ] Test with mock API response (malformed JSON)
- [ ] Test error handling (API failure)

**Checkpoint:** Salience extraction working ✓

**Commit:** `feat(strategy-h): implement salience extraction`

---

### 1.4: Implement `_compress_background()` Method (1-2 hours)

#### Design Prompt
- [ ] Create background compression prompt template
- [ ] Include salience set (to avoid duplication)
- [ ] Request 2-3 sentence summary
- [ ] Specify not to duplicate salience items

#### Implement Method
- [ ] Format conversation context
- [ ] Build prompt with salience set and context
- [ ] Call OpenAI API (use compression_model, not extraction_model)
- [ ] Extract summary text
- [ ] Handle errors (return fallback summary)

#### Test
- [ ] Test with mock API response
- [ ] Test that salience items are not duplicated in summary
- [ ] Test error handling

**Checkpoint:** Background compression working ✓

**Commit:** `feat(strategy-h): implement background compression`

---

### 1.5: Implement `_build_context()` Method (30 minutes)

#### Implement Method
- [ ] Build context string with sections:
  - System prompt (if available)
  - SALIENT INFORMATION section with items
  - BACKGROUND SUMMARY section
  - RECENT TURNS section (last 3 turns)
- [ ] Format each section clearly
- [ ] Return complete context string

#### Test
- [ ] Test context format is correct
- [ ] Test all sections included
- [ ] Test with empty salience set
- [ ] Test with empty background summary

**Checkpoint:** Context rebuilding working ✓

**Commit:** `feat(strategy-h): implement context rebuilding`

---

### 1.6: Implement Basic `compress()` Method (1 hour)

#### Implement Method
- [ ] Get context up to trigger_point
- [ ] Call `_extract_salient_information()`
- [ ] Call `_merge_salience()` (basic version - just append for now)
- [ ] Call `_compress_background()`
- [ ] Call `_build_context()`
- [ ] Return compressed context
- [ ] Add logging

#### Test
- [ ] Test full compression flow
- [ ] Test with empty context
- [ ] Test with single turn
- [ ] Test error handling

**Checkpoint:** Basic compression flow working ✓

**Commit:** `feat(strategy-h): implement basic compress method`

---

### 1.7: Implement `name()` Method (5 minutes)

#### Implement Method
- [ ] Return `"Strategy H - Selective Salience Compression"`

#### Test
- [ ] Test name returns correctly

**Commit:** `feat(strategy-h): implement name method`

---

### 1.8: Implement `update_goal()` Method (15 minutes)

#### Implement Method
- [ ] Store new goal
- [ ] Log goal update
- [ ] Note: Goal will be used in next extraction prompt

#### Test
- [ ] Test goal update stored correctly
- [ ] Test goal used in next extraction

**Commit:** `feat(strategy-h): implement update_goal method`

---

## Phase 2: Salience Management (6-8 hours)

### 2.1: Implement Semantic Deduplication (2-3 hours)

#### Install Dependencies
- [ ] Verify `sentence-transformers` installed
- [ ] Verify `scikit-learn` installed
- [ ] Test embedding generation

#### Implement `_deduplicate_semantically()` Method
- [ ] Load `all-MiniLM-L6-v2` model (in `__init__`)
- [ ] Generate embeddings for all items
- [ ] Calculate cosine similarity matrix
- [ ] Find pairs with similarity > threshold
- [ ] For duplicates, keep shorter item
- [ ] Return deduplicated list

#### Test
- [ ] Test with known similar items (should deduplicate)
- [ ] Test with different items (should keep all)
- [ ] Test with empty list
- [ ] Test with single item
- [ ] Test threshold parameter (0.85 default)
- [ ] Measure performance (<1 second for 100 items)

**Checkpoint:** Deduplication working ✓

**Commit:** `feat(strategy-h): implement semantic deduplication`

---

### 2.2: Implement Token Tracking (30 minutes)

#### Install Dependencies
- [ ] Verify `tiktoken` installed
- [ ] Test token counting

#### Implement Token Counting
- [ ] Create `_token_count()` helper method
- [ ] Use tiktoken to count tokens accurately
- [ ] Test with various text lengths

#### Add Token Tracking to `compress()` Method
- [ ] Track tokens for new salience items
- [ ] Track total salience set tokens
- [ ] Track background summary tokens
- [ ] Track recent turns tokens
- [ ] Log token breakdown for monitoring
- [ ] Calculate compression ratio

#### Test
- [ ] Test token counting accuracy
- [ ] Test token tracking logs correctly
- [ ] Test with various text lengths
- [ ] Verify compression ratio calculation

**Note:** No token budget enforcement - we rely on semantic deduplication to prevent unbounded growth. Token tracking is for monitoring/logging only.

**Checkpoint:** Token tracking working ✓

**Commit:** `feat(strategy-h): add token tracking for monitoring`

---

### 2.3: Implement Salience Set Merging (1-2 hours)

#### Implement `_merge_salience()` Method
- [ ] Combine existing and new salience items
- [ ] Call `_deduplicate_semantically()` on combined list
- [ ] Return merged and deduplicated salience set
- [ ] Update `self.salience_set`
- [ ] Log token count for monitoring

#### Test
- [ ] Test merging adds new items
- [ ] Test deduplication removes similar items
- [ ] Test cumulative growth across compressions (no hard limit)
- [ ] Test with empty existing set
- [ ] Test with empty new set
- [ ] Verify token tracking logs correctly

**Checkpoint:** Salience merging working ✓

**Commit:** `feat(strategy-h): implement salience set merging`

---

### 2.4: Update `compress()` to Use Merging (30 minutes)

#### Update Method
- [ ] Replace basic merge with `_merge_salience()` call
- [ ] Ensure salience set persists across compressions
- [ ] Add logging for salience set size

#### Test
- [ ] Test salience accumulates across compressions
- [ ] Test deduplication works across compressions
- [ ] Test token budget enforced across compressions

**Checkpoint:** Full salience management working ✓

**Commit:** `feat(strategy-h): integrate salience management into compress`

---

### 2.5: Implement Prioritization Logic (1 hour)

#### Implement `_prioritize_items()` Method
- [ ] Categorize items: constraints, decisions, facts
- [ ] Use keyword matching or LLM classification
- [ ] Sort: constraints first, then decisions, then facts
- [ ] Return prioritized list

#### Alternative: Simple Keyword-Based
- [ ] Check for constraint keywords ("must", "cannot", "required")
- [ ] Check for decision keywords ("chose", "decided", "selected")
- [ ] Default to facts category
- [ ] Sort by category

#### Test
- [ ] Test constraint items prioritized
- [ ] Test decision items come second
- [ ] Test facts come last
- [ ] Test with mixed categories

**Checkpoint:** Prioritization working ✓

**Commit:** `feat(strategy-h): implement item prioritization`

---

## Phase 3: Integration (4-6 hours)

### 3.1: Update Package Exports (15 minutes)

#### Update `strategies/__init__.py`
- [ ] Import `SelectiveSalienceStrategy`
- [ ] Add to `__all__` list
- [ ] Test import works

#### Update `strategy_base.py`
- [ ] Update docstring: "All 8 strategies" (was 7)

#### Test
- [ ] Test `from strategies import SelectiveSalienceStrategy` works
- [ ] Test class can be instantiated

**Commit:** `feat(strategy-h): update package exports`

---

### 3.2: Add Salience Accuracy Metrics (2-3 hours)

#### Add to `evaluation/metrics.py`
- [ ] Implement `measure_salience_accuracy()` function
- [ ] Use sentence-transformers for semantic matching
- [ ] Calculate precision, recall, F1
- [ ] Return metrics dictionary

#### Update `CompressionPointMetrics` Dataclass
- [ ] Add optional fields:
  - `salience_precision: Optional[float] = None`
  - `salience_recall: Optional[float] = None`
  - `salience_f1: Optional[float] = None`
- [ ] Update `to_dict()` method

#### Update `MetricsCollector.collect_at_compression_point()`
- [ ] Add optional `extracted_salience` parameter
- [ ] Add optional `ground_truth_salience` parameter
- [ ] If both provided, calculate salience metrics
- [ ] Add to metrics object

#### Test
- [ ] Test `measure_salience_accuracy()` with known matches
- [ ] Test precision/recall calculation
- [ ] Test integration with `MetricsCollector`
- [ ] Test with missing ground truth (should skip)

**Checkpoint:** Salience metrics integrated ✓

**Commit:** `feat(evaluation): add salience accuracy metrics`

---

### 3.3: Update Evaluation Harness (1-2 hours)

#### Update `evaluation/harness.py`
- [ ] In `run_single_trial()`, collect extracted salience from strategy
- [ ] Get ground truth salience from template (if available)
- [ ] Pass to `collect_at_compression_point()`
- [ ] Ensure salience metrics included in results

#### Test
- [ ] Test harness collects salience from Strategy H
- [ ] Test salience metrics appear in results
- [ ] Test with template that has ground truth
- [ ] Test with template without ground truth (should work)

**Checkpoint:** Harness integration complete ✓

**Commit:** `feat(harness): collect salience metrics for Strategy H`

---

### 3.4: Create Test Templates (1 hour)

#### Create `templates/test-simple.json`
- [ ] 3-5 turns
- [ ] 1 compression point
- [ ] Clear goal and constraints
- [ ] Known ground truth salience
- [ ] Follow template format from PRD

#### Create `templates/test-edge-cases.json`
- [ ] Goal evolution mid-task
- [ ] Implicit constraints
- [ ] Many similar salience items
- [ ] Edge cases for testing

#### Test
- [ ] Test templates load correctly
- [ ] Test templates have required fields
- [ ] Test ground truth salience is valid

**Checkpoint:** Test templates ready ✓

**Commit:** `feat(templates): add test templates for Strategy H`

---

## Phase 4: Testing & Refinement (4-6 hours)

### 4.1: Unit Tests - Core Methods (2 hours)

#### Create `tests/test_strategy_h.py`
- [ ] Test `initialize()` method
- [ ] Test `update_goal()` method
- [ ] Test `name()` method
- [ ] Test `_extract_salient_information()` with mocked API
- [ ] Test `_compress_background()` with mocked API
- [ ] Test `_build_context()` with various inputs
- [ ] Test `compress()` with mocked API

#### Mock Setup
- [ ] Create pytest fixtures for mocked OpenAI client
- [ ] Create sample API responses
- [ ] Test error handling

#### Test Coverage
- [ ] Aim for >80% code coverage
- [ ] Test all error paths
- [ ] Test edge cases

**Checkpoint:** Unit tests passing ✓

**Commit:** `test(strategy-h): add unit tests`

---

### 4.2: Unit Tests - Salience Management (1 hour)

#### Add Tests
- [ ] Test `_deduplicate_semantically()` with known similar items
- [ ] Test `_apply_token_budget()` with various sizes
- [ ] Test `_merge_salience()` with different scenarios
- [ ] Test prioritization logic

#### Test Edge Cases
- [ ] Empty lists
- [ ] Single items
- [ ] Very large items
- [ ] All items identical

**Checkpoint:** Salience management tests passing ✓

**Commit:** `test(strategy-h): add salience management tests`

---

### 4.3: Integration Tests (1-2 hours)

#### Create Integration Tests
- [ ] Test full compression flow with `test-simple.json`
- [ ] Test salience accumulation across compressions
- [ ] Test integration with evaluation harness
- [ ] Test error recovery (fallback to Protected Core)

#### Use Real Templates
- [ ] Load `test-simple.json`
- [ ] Load `research-synthesis-001.json`
- [ ] Run Strategy H on templates
- [ ] Verify results format

**Checkpoint:** Integration tests passing ✓

**Commit:** `test(strategy-h): add integration tests`

---

### 4.4: Prompt Refinement (1 hour)

#### Test Prompts
- [ ] Run Strategy H on test templates
- [ ] Review extracted salience quality
- [ ] Identify prompt issues
- [ ] Refine prompts based on results

#### Iterate
- [ ] Update extraction prompt
- [ ] Update compression prompt
- [ ] Test again
- [ ] Repeat until quality acceptable

**Checkpoint:** Prompts refined ✓

**Commit:** `refactor(strategy-h): refine extraction and compression prompts`

---

### 4.5: Error Handling Improvements (1 hour)

#### Add Fallback Strategies
- [ ] Implement `_fallback_extract_constraints()` method
- [ ] Use Protected Core schema as fallback
- [ ] Log all fallbacks for analysis
- [ ] Test fallback scenarios

#### Improve Error Messages
- [ ] Add detailed error logging
- [ ] Add error context
- [ ] Make errors actionable

**Checkpoint:** Error handling robust ✓

**Commit:** `feat(strategy-h): improve error handling and fallbacks`

---

## Testing Phase (2-3 hours)

### Unit Tests
- [ ] All unit tests passing
- [ ] Test coverage >80%
- [ ] All error paths tested
- [ ] Edge cases covered

### Integration Tests
- [ ] Full flow tested with templates
- [ ] Harness integration working
- [ ] Metrics collection working
- [ ] Results format correct

### Manual Testing
- [ ] Run Strategy H on `test-simple.json`
- [ ] Run Strategy H on `research-synthesis-001.json`
- [ ] Verify salience extraction quality
- [ ] Verify goal coherence maintained
- [ ] Check logs for errors

### Performance Testing
- [ ] Deduplication: <1 second for 100 items ✓
- [ ] Extraction: <10 seconds per compression ✓
- [ ] Compression: <5 seconds per compression ✓
- [ ] Total: <20 seconds per compression point ✓

---

## Bug Fixing (If needed)

### Bug #1: [Title]
- [ ] Reproduced
- [ ] Root cause identified
- [ ] Fix implemented
- [ ] Tested
- [ ] Documented

---

## Documentation Phase (1-2 hours)

- [ ] Code docstrings added (all methods)
- [ ] Type hints added (all methods)
- [ ] Inline comments for complex logic
- [ ] README updated (if applicable)
- [ ] Usage examples added
- [ ] Update `strategies/__init__.py` docstring

---

## Completion Checklist

- [ ] All phases complete
- [ ] All tests passing
- [ ] Performance targets met
- [ ] No critical bugs
- [ ] Documentation complete
- [ ] Code reviewed (self-review)
- [ ] Ready for evaluation testing

---

## Deployment Phase (Evaluation Testing)

### Pre-Evaluation Checklist
- [ ] All tests passing locally
- [ ] No console errors
- [ ] Strategy H can be imported and used
- [ ] Evaluation harness recognizes Strategy H

### Run Evaluation Tests
- [ ] Run Strategy H on `research-synthesis-001.json`
- [ ] Collect salience accuracy metrics (if ground truth available)
- [ ] Compare goal coherence with other strategies
- [ ] Verify results format matches expected structure

### Post-Evaluation
- [ ] Review salience extraction quality
- [ ] Review goal coherence preservation
- [ ] Document findings
- [ ] Note any issues for future improvement

---

## Completion Checklist

- [ ] All phases complete
- [ ] All tests passing
- [ ] Performance targets met
- [ ] No critical bugs
- [ ] Documentation complete
- [ ] Evaluation tested
- [ ] Ready for merge

---

**Status:** Ready to start implementation! 🚀

