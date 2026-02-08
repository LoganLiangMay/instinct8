# PR#01: Selective Salience Compression - Quick Start

---

## TL;DR (30 seconds)

**What:** Implement Strategy H - Selective Salience Compression, where the model itself identifies goal-critical information and preserves it verbatim while compressing everything else.

**Why:** Tests whether models can reliably identify salience (frontier capability), provides adaptive compression without fixed schema, and complements Protected Core strategy.

**Time:** 20-30 hours estimated

**Complexity:** MEDIUM-HIGH

**Status:** 📋 PLANNED

---

## Decision Framework (2 minutes)

### Should You Build This?

**Green Lights (Build it!):**
- ✅ You have 20+ hours available
- ✅ OpenAI API key available
- ✅ Want to test model salience detection capabilities
- ✅ Need adaptive compression strategy (no fixed schema)
- ✅ Excited about research value

**Red Lights (Skip/defer it!):**
- ❌ Time-constrained (<15 hours)
- ❌ No OpenAI API access
- ❌ Prefer simpler strategies first
- ❌ Not interested in salience detection research

**Decision Aid:** If you're unsure, start with Strategy B (Codex) first to understand the framework, then implement Strategy H.

---

## Prerequisites (5 minutes)

### Required
- [ ] OpenAI API key set: `export OPENAI_API_KEY="sk-..."`
- [ ] Python 3.10+ installed
- [ ] Virtual environment activated
- [ ] Dependencies installed:
  ```bash
  pip install openai sentence-transformers scikit-learn tiktoken
  ```
- [ ] Git branch created:
  ```bash
  git checkout -b feature/pr01-selective-salience
  ```

### Knowledge Prerequisites
- [ ] Understand `CompressionStrategy` interface (read `strategies/strategy_base.py`)
- [ ] Understand evaluation harness (read `evaluation/harness.py`)
- [ ] Understand Strategy B as reference (read `strategies/strategy_b_codex.py`)

---

## Getting Started (First Hour)

### Step 1: Read Documentation (45 minutes)
- [ ] Read this quick start (10 min)
- [ ] Read main specification (`PR01_SELECTIVE_SALIENCE_COMPRESSION.md`) (30 min)
- [ ] Read implementation recommendations (`docs/implementation_recommendations.md`) (5 min)
- [ ] Note any questions

### Step 2: Set Up Environment (15 minutes)
- [ ] Install dependencies (see Prerequisites)
- [ ] Test OpenAI API connection
- [ ] Test sentence-transformers loads correctly
- [ ] Open relevant files in editor:
  - `strategies/strategy_base.py` (reference)
  - `strategies/strategy_b_codex.py` (example)
  - `evaluation/harness.py` (integration points)

### Step 3: Start Phase 1
- [ ] Open implementation checklist (`PR01_IMPLEMENTATION_CHECKLIST.md`)
- [ ] Begin Task 1.1: Set Up Dependencies and Base Structure
- [ ] Commit when task complete

---

## Daily Progress Template

### Day 1 Goals (4-6 hours)
- [ ] Task 1.1: Base structure (1 h)
- [ ] Task 1.2: Initialize method (15 min)
- [ ] Task 1.3: Salience extraction (2-3 h)
- [ ] Task 1.4: Background compression (1-2 h)

**Checkpoint:** Core extraction and compression working

### Day 2 Goals (4-6 hours)
- [ ] Task 1.5: Context rebuilding (30 min)
- [ ] Task 1.6: Basic compress method (1 h)
- [ ] Task 2.1: Semantic deduplication (2-3 h)
- [ ] Task 2.2: Token budget (2 h)

**Checkpoint:** Salience management working

### Day 3 Goals (4-6 hours)
- [ ] Task 2.3: Salience merging (1-2 h)
- [ ] Task 2.4: Update compress (30 min)
- [ ] Task 2.5: Prioritization (1 h)
- [ ] Task 3.1: Package exports (15 min)
- [ ] Task 3.2: Salience metrics (2-3 h)

**Checkpoint:** Integration with evaluation complete

### Day 4 Goals (4-6 hours)
- [ ] Task 3.3: Harness updates (1-2 h)
- [ ] Task 3.4: Test templates (1 h)
- [ ] Task 4.1: Unit tests (2 h)
- [ ] Task 4.2: More unit tests (1 h)

**Checkpoint:** Tests passing

### Day 5 Goals (2-4 hours)
- [ ] Task 4.3: Integration tests (1-2 h)
- [ ] Task 4.4: Prompt refinement (1 h)
- [ ] Task 4.5: Error handling (1 h)
- [ ] Final testing and documentation

**Checkpoint:** Complete and ready for evaluation

---

## Common Issues & Solutions

### Issue 1: OpenAI API Rate Limits
**Symptoms:** `429 Rate limit exceeded` errors  
**Cause:** Too many requests too quickly  
**Solution:**
```python
# Implement exponential backoff
import time
from openai import RateLimitError

def call_with_retry(func, max_retries=3):
    for i in range(max_retries):
        try:
            return func()
        except RateLimitError:
            wait_time = 2 ** i
            time.sleep(wait_time)
    raise
```

### Issue 2: Sentence Transformer Model Download Fails
**Symptoms:** `OSError: Unable to download model`  
**Cause:** Network issues or disk space  
**Solution:**
```bash
# Pre-download model
python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"
```

### Issue 3: Token Counting Inaccurate
**Symptoms:** Token budget exceeded unexpectedly  
**Cause:** Using character count instead of token count  
**Solution:**
```python
# Use tiktoken for accurate counting
import tiktoken
encoder = tiktoken.encoding_for_model("gpt-4o")
tokens = encoder.encode(text)
token_count = len(tokens)
```

### Issue 4: Deduplication Too Aggressive
**Symptoms:** Important items removed as duplicates  
**Cause:** Similarity threshold too high  
**Solution:**
- Lower threshold (try 0.80 instead of 0.85)
- Check similarity scores in logs
- Adjust threshold based on results

### Issue 5: Salience Extraction Returns Nothing
**Symptoms:** Empty salience set  
**Cause:** Prompt too strict or API error  
**Solution:**
- Check prompt clarity
- Verify API response format
- Implement fallback to Protected Core schema
- Log extraction for debugging

---

## Quick Reference

### Key Files
- `strategies/strategy_h_selective_salience.py` - Main implementation
- `evaluation/metrics.py` - Salience accuracy metrics
- `evaluation/harness.py` - Integration with evaluation framework
- `tests/test_strategy_h.py` - Unit and integration tests

### Key Functions
- `_extract_salient_information()` - Extract goal-critical quotes
- `_compress_background()` - Compress non-salient content
- `_deduplicate_semantically()` - Remove similar items
- `_apply_token_budget()` - Enforce token limits
- `compress()` - Main compression method

### Key Concepts
- **Salience Set**: Cumulative list of goal-critical items (verbatim quotes)
- **Semantic Deduplication**: Using embeddings to find similar items
- **Token Budget**: Maximum tokens allowed for salience set (default: 5000)
- **Similarity Threshold**: Cosine similarity threshold for deduplication (default: 0.85)

### Useful Commands
```bash
# Run tests
pytest tests/test_strategy_h.py -v

# Run with coverage
pytest tests/test_strategy_h.py --cov=strategies.strategy_h_selective_salience

# Test OpenAI connection
python -c "from openai import OpenAI; OpenAI().models.list()"

# Test sentence transformers
python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"
```

---

## Success Metrics

**You'll know it's working when:**
- [ ] Strategy H can be imported and instantiated
- [ ] `compress()` method returns formatted context string
- [ ] Salience extraction produces verbatim quotes
- [ ] Deduplication removes similar items
- [ ] Token budget enforced correctly
- [ ] Integration with harness collects metrics
- [ ] Tests passing (>80% coverage)

**Performance Targets:**
- Deduplication: <1 second for 100 items
- Extraction: <10 seconds per compression
- Compression: <5 seconds per compression
- Total: <20 seconds per compression point

**Quality Targets:**
- Salience accuracy: >0.75 precision/recall (if ground truth available)
- Goal coherence: >0.90 maintained
- Test coverage: >80%

---

## Help & Support

### Stuck?
1. Check main specification (`PR01_SELECTIVE_SALIENCE_COMPRESSION.md`) for details
2. Review Strategy B implementation (`strategies/strategy_b_codex.py`) as reference
3. Check implementation recommendations (`docs/implementation_recommendations.md`)
4. Review LLM-as-Judge guide (`docs/llm_as_judge_implementation_guide.md`)

### Want to Skip a Feature?
- **Can Skip:** Advanced prioritization (use simple keyword-based)
- **Can Skip:** Complex error recovery (basic fallback is fine)
- **Cannot Skip:** Core extraction, compression, deduplication

### Running Out of Time?
**Priority Order:**
1. Core extraction and compression (Phase 1)
2. Basic deduplication (Phase 2.1)
3. Token budget (Phase 2.2)
4. Integration (Phase 3)
5. Testing (Phase 4)

**Minimum Viable:** Phases 1-3 (core functionality)

---

## Motivation

**You've got this!** 💪

This is an exciting strategy that tests frontier capabilities. You're building something that:
- Tests whether models can identify what matters
- Provides adaptive compression without fixed schema
- Complements existing strategies
- Has real research value

The implementation is well-scoped, the recommendations are clear, and you have good examples to follow (Strategy B).

---

## Next Steps

**When ready:**
1. Run prerequisites (5 min)
2. Read main spec (30 min)
3. Start Phase 1 from checklist
4. Commit early and often

**Status:** Ready to build! 🚀

---

*Quick Start Guide created: 2025-01-XX*

