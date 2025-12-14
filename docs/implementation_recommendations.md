# Top Implementation Recommendations for Strategy H

**Date:** 2025-01-XX  
**Purpose:** Top suggestions for remaining implementation decisions

---

## 1. Semantic Deduplication Implementation

### 🥇 **Recommendation 1: `all-MiniLM-L6-v2` (BEST)**

**Why:**
- **Fastest**: 22M parameters, ~5ms per embedding
- **Good quality**: 68.7% accuracy on semantic similarity tasks
- **Small size**: ~80MB download, runs on CPU efficiently
- **Proven**: Most popular sentence-transformers model (10M+ downloads)
- **Perfect for deduplication**: Designed for semantic similarity

**Implementation:**
```python
from sentence_transformers import SentenceTransformer
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

# Initialize once (reuse across calls)
model = SentenceTransformer('all-MiniLM-L6-v2')

def deduplicate_salience(salience_items: List[str], threshold: float = 0.85) -> List[str]:
    """
    Remove semantically similar items from salience set.
    
    Args:
        salience_items: List of salience quotes
        threshold: Cosine similarity threshold (0.85 = 85% similar)
    
    Returns:
        Deduplicated list
    """
    if len(salience_items) <= 1:
        return salience_items
    
    # Generate embeddings
    embeddings = model.encode(salience_items, show_progress_bar=False)
    
    # Calculate similarity matrix
    similarity_matrix = cosine_similarity(embeddings)
    
    # Find duplicates (similarity > threshold)
    to_remove = set()
    for i in range(len(salience_items)):
        if i in to_remove:
            continue
        for j in range(i + 1, len(salience_items)):
            if similarity_matrix[i][j] > threshold:
                # Keep the shorter one (more concise)
                if len(salience_items[i]) > len(salience_items[j]):
                    to_remove.add(i)
                else:
                    to_remove.add(j)
    
    return [item for idx, item in enumerate(salience_items) if idx not in to_remove]
```

**Pros:**
- ✅ Fast (can deduplicate 100 items in <1 second)
- ✅ Good accuracy for deduplication task
- ✅ No API calls (runs locally)
- ✅ Small memory footprint

**Cons:**
- ⚠️ Less accurate than larger models (but sufficient for deduplication)

**When to Use:** Default choice for all deduplication

---

### 🥈 **Recommendation 2: `all-mpnet-base-v2` (HIGHER QUALITY)**

**Why:**
- **Better quality**: 76.6% accuracy (vs 68.7% for MiniLM)
- **Still fast**: ~15ms per embedding
- **Good balance**: Quality vs speed

**When to Use:**
- If you need higher accuracy
- If deduplication quality is critical
- If you have CPU cycles to spare

**Trade-off:** 3x slower than MiniLM, but better accuracy

---

### 🥉 **Recommendation 3: OpenAI Embeddings API (SIMPLEST)**

**Why:**
- **No local model**: Use OpenAI's `text-embedding-3-small`
- **Consistent**: Same API as rest of system
- **Simple**: No dependencies beyond OpenAI library

**When to Use:**
- If you want to avoid local dependencies
- If you're already using OpenAI for everything
- If cost is acceptable (~$0.02 per 1M tokens)

**Trade-off:** API calls add latency and cost, but simpler setup

---

### **Final Recommendation: `all-MiniLM-L6-v2`**

**Rationale:**
- Fast enough for real-time deduplication
- Accurate enough for the task (85% threshold catches duplicates)
- No API costs or rate limits
- Easy to integrate

**Installation:**
```bash
pip install sentence-transformers scikit-learn
```

---

## 2. Integration with Evaluation Harness

### 🥇 **Recommendation 1: Extend `MetricsCollector` Class**

**Why:**
- Already exists and handles goal coherence, constraint recall, behavioral alignment
- Easy to add salience-specific metrics
- Consistent with existing evaluation framework

**Implementation Approach:**

Add to `evaluation/metrics.py`:

```python
def measure_salience_accuracy(
    extracted_salience: List[str],
    ground_truth_salience: List[str],
    model: str = "gpt-4o-mini",  # Use cheaper model for evaluation
) -> Dict[str, float]:
    """
    Measure precision, recall, F1 for salience extraction.
    
    Uses semantic similarity matching (like deduplication).
    
    Returns:
        {
            "precision": 0.0-1.0,
            "recall": 0.0-1.0,
            "f1": 0.0-1.0,
            "true_positives": int,
            "false_positives": int,
            "false_negatives": int
        }
    """
    # Use same embedding model as deduplication
    from sentence_transformers import SentenceTransformer
    model_emb = SentenceTransformer('all-MiniLM-L6-v2')
    
    # Generate embeddings
    extracted_emb = model_emb.encode(extracted_salience)
    gt_emb = model_emb.encode(ground_truth_salience)
    
    # Match extracted items to ground truth (similarity > 0.85)
    from sklearn.metrics.pairwise import cosine_similarity
    similarity_matrix = cosine_similarity(extracted_emb, gt_emb)
    
    matches = []
    for i, extracted_item in enumerate(extracted_salience):
        best_match_idx = np.argmax(similarity_matrix[i])
        best_similarity = similarity_matrix[i][best_match_idx]
        if best_similarity > 0.85:
            matches.append((i, best_match_idx))
    
    tp = len(matches)
    fp = len(extracted_salience) - tp
    matched_gt_indices = set(m[1] for m in matches)
    fn = len(ground_truth_salience) - len(matched_gt_indices)
    
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0
    
    return {
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "true_positives": tp,
        "false_positives": fp,
        "false_negatives": fn,
    }
```

**Add to `MetricsCollector.collect_at_compression_point()`:**

```python
def collect_at_compression_point(
    self,
    compression_point_id: int,
    turn_id: int,
    # ... existing params ...
    extracted_salience: Optional[List[str]] = None,  # NEW
    ground_truth_salience: Optional[List[str]] = None,  # NEW
) -> CompressionPointMetrics:
    # ... existing code ...
    
    # NEW: Measure salience accuracy if available
    salience_metrics = None
    if extracted_salience and ground_truth_salience:
        salience_metrics = measure_salience_accuracy(
            extracted_salience, ground_truth_salience
        )
    
    # Add to metrics object
    # ...
```

**Update `CompressionPointMetrics` dataclass:**

```python
@dataclass
class CompressionPointMetrics:
    # ... existing fields ...
    
    # NEW: Salience accuracy (optional)
    salience_precision: Optional[float] = None
    salience_recall: Optional[float] = None
    salience_f1: Optional[float] = None
```

**Pros:**
- ✅ Consistent with existing evaluation framework
- ✅ Reuses existing infrastructure
- ✅ Easy to add to existing results

**Cons:**
- ⚠️ Requires ground truth salience (for Method 1 evaluation)

---

### 🥈 **Recommendation 2: Separate `SalienceEvaluator` Class**

**Why:**
- Keeps salience evaluation separate from goal coherence metrics
- Can use LLM-as-Judge (Method 2) without ground truth
- More flexible for different evaluation methods

**Implementation Approach:**

Create `evaluation/salience_evaluator.py`:

```python
class SalienceEvaluator:
    """
    Evaluates salience extraction quality using multiple methods.
    """
    
    def __init__(self, method: str = "semantic_similarity"):
        """
        Args:
            method: "semantic_similarity" or "llm_as_judge"
        """
        self.method = method
        if method == "semantic_similarity":
            from sentence_transformers import SentenceTransformer
            self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
    
    def evaluate(
        self,
        extracted_salience: List[str],
        ground_truth: Optional[List[str]] = None,
        conversation_context: Optional[str] = None,
        original_goal: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Evaluate salience extraction.
        
        If ground_truth provided: Use semantic similarity (Method 1)
        If no ground_truth: Use LLM-as-Judge (Method 2)
        """
        if ground_truth:
            return self._evaluate_with_ground_truth(extracted_salience, ground_truth)
        elif self.method == "llm_as_judge":
            return self._evaluate_with_llm_judge(
                extracted_salience, conversation_context, original_goal
            )
        else:
            raise ValueError("Need ground truth or LLM-as-Judge method")
    
    # ... implementation methods ...
```

**Pros:**
- ✅ Flexible (supports multiple evaluation methods)
- ✅ Can work without ground truth
- ✅ Clean separation of concerns

**Cons:**
- ⚠️ More code to maintain
- ⚠️ Need to integrate with harness separately

---

### 🥉 **Recommendation 3: Strategy H Returns Salience Metadata**

**Why:**
- Simplest integration
- Strategy H already extracts salience
- Harness can collect it automatically

**Implementation Approach:**

Modify `CompressionStrategy.compress()` to return metadata:

```python
@dataclass
class CompressionResult:
    """Result from compression operation."""
    compressed_context: str
    metadata: Dict[str, Any]  # Strategy-specific metadata

class SelectiveSalienceStrategy(CompressionStrategy):
    def compress(self, context, trigger_point) -> CompressionResult:
        # ... extraction logic ...
        
        return CompressionResult(
            compressed_context=compressed,
            metadata={
                "extracted_salience": self.salience_set,
                "salience_count": len(self.salience_set),
                "background_summary": background_summary,
            }
        )
```

**Update harness to collect:**

```python
# In run_single_trial()
compression_result = agent.compress(turn_id)

# Collect salience if available
if hasattr(compression_result, 'metadata'):
    extracted_salience = compression_result.metadata.get('extracted_salience')
    # Evaluate salience accuracy
    if extracted_salience and template.get('ground_truth_salience'):
        salience_metrics = evaluate_salience(extracted_salience, ...)
```

**Pros:**
- ✅ Minimal changes to harness
- ✅ Strategy-specific metadata preserved
- ✅ Flexible for future strategies

**Cons:**
- ⚠️ Requires changing return type of `compress()` method
- ⚠️ Breaking change for existing strategies

---

### **Final Recommendation: Recommendation 1 (Extend MetricsCollector)**

**Rationale:**
- Minimal changes to existing code
- Consistent with current evaluation approach
- Easy to add to results
- Can be optional (only when ground truth available)

---

## 3. Testing Approach

### 🥇 **Recommendation 1: Three-Layer Testing Strategy**

**Layer 1: Unit Tests (Mocked API)**

**Why:**
- Fast (no API calls)
- Isolated (test logic, not API)
- Reliable (deterministic)

**What to Test:**
- Salience extraction parsing (with mock responses)
- Background compression logic
- Salience set merging/deduplication
- Token budget management
- Error handling

**Example Structure:**

```python
# tests/test_strategy_h.py

import pytest
from unittest.mock import Mock, patch
from strategies.strategy_h_selective_salience import SelectiveSalienceStrategy

class TestSalienceExtraction:
    @patch('openai.OpenAI')
    def test_extract_salience_parses_json(self, mock_openai):
        """Test that salience extraction correctly parses JSON response."""
        # Mock OpenAI response
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = '{"salient_items": ["quote 1", "quote 2"]}'
        
        mock_client = Mock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client
        
        strategy = SelectiveSalienceStrategy()
        strategy.initialize("test goal", ["constraint 1"])
        
        result = strategy._extract_salient_information([...])
        assert len(result) == 2
        assert "quote 1" in result
    
    def test_deduplicate_salience(self):
        """Test semantic deduplication removes similar items."""
        strategy = SelectiveSalienceStrategy()
        
        items = [
            "We must use PostgreSQL",
            "PostgreSQL is required",  # Similar to first
            "Budget is $10K",  # Different
        ]
        
        deduplicated = strategy._deduplicate_salience(items, threshold=0.85)
        assert len(deduplicated) == 2  # One duplicate removed
    
    def test_token_budget_enforcement(self):
        """Test that salience set respects token budget."""
        strategy = SelectiveSalienceStrategy(salience_token_budget=100)
        
        # Add items that exceed budget
        large_items = ["x" * 200] * 10  # Each ~50 tokens
        
        result = strategy._apply_token_budget(large_items)
        assert strategy._token_count(result) <= 100
```

**Layer 2: Integration Tests (Real Templates, Mocked API)**

**Why:**
- Tests full flow without API costs
- Uses real template structure
- Validates integration points

**What to Test:**
- Full compression flow with real templates
- Context rebuilding
- Integration with evaluation harness
- Error handling with real data

**Example:**

```python
class TestStrategyHIntegration:
    @patch('openai.OpenAI')
    def test_full_compression_flow(self, mock_openai):
        """Test complete compression flow with real template."""
        # Load real template
        template = load_template("templates/research-synthesis-001.json")
        
        # Mock API responses
        # ... setup mocks ...
        
        strategy = SelectiveSalienceStrategy()
        strategy.initialize(
            template["initial_setup"]["original_goal"],
            template["initial_setup"]["hard_constraints"]
        )
        
        # Run compression
        compressed = strategy.compress(
            template["turns"][:5],  # First 5 turns
            trigger_point=5
        )
        
        # Assertions
        assert "SALIENT INFORMATION" in compressed
        assert "BACKGROUND SUMMARY" in compressed
        assert len(strategy.salience_set) > 0
```

**Layer 3: Evaluation Tests (Real API, Real Templates)**

**Why:**
- Validates end-to-end with real API
- Tests actual quality
- Catches API-specific issues

**What to Test:**
- Run on 1-2 templates with real API
- Compare with other strategies
- Measure actual salience accuracy
- Validate cost/performance

**Example:**

```python
@pytest.mark.integration  # Skip in CI, run manually
class TestStrategyHEvaluation:
    def test_salience_accuracy_vs_ground_truth(self):
        """Test salience extraction accuracy on real template."""
        template = load_template("templates/research-synthesis-001.json")
        ground_truth = template["ground_truth"]["salient_items"]
        
        strategy = SelectiveSalienceStrategy()
        # ... run strategy ...
        
        extracted = strategy.salience_set
        
        # Evaluate
        metrics = measure_salience_accuracy(extracted, ground_truth)
        
        assert metrics["precision"] > 0.7
        assert metrics["recall"] > 0.7
        assert metrics["f1"] > 0.7
```

**Pros:**
- ✅ Comprehensive coverage
- ✅ Fast unit tests (no API calls)
- ✅ Realistic integration tests
- ✅ End-to-end validation

---

### 🥈 **Recommendation 2: Use `pytest` with Fixtures**

**Why:**
- Standard Python testing framework
- Great mocking support
- Fixtures for reusable test data

**Key Fixtures:**

```python
# conftest.py

import pytest
from strategies.strategy_h_selective_salience import SelectiveSalienceStrategy

@pytest.fixture
def mock_openai_client():
    """Mock OpenAI client for unit tests."""
    with patch('openai.OpenAI') as mock:
        yield mock

@pytest.fixture
def sample_template():
    """Load sample template for testing."""
    return load_template("templates/research-synthesis-001.json")

@pytest.fixture
def strategy_h(mock_openai_client):
    """Create Strategy H instance with mocked API."""
    return SelectiveSalienceStrategy()
```

**Pros:**
- ✅ Standard tooling
- ✅ Good ecosystem support
- ✅ Easy to run specific tests

---

### 🥉 **Recommendation 3: Test Templates**

**Create Minimal Test Templates:**

**1. Simple Template (`templates/test-simple.json`):**
- 3-5 turns
- 1 compression point
- Clear goal and constraints
- Known ground truth salience

**2. Edge Case Template (`templates/test-edge-cases.json`):**
- Goal evolution mid-task
- Implicit constraints
- Many similar salience items (test deduplication)
- Empty extraction scenario

**3. Real Template (`templates/research-synthesis-001.json`):**
- Already exists
- Use for integration tests
- Has ground truth

**Template Structure:**

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

**Pros:**
- ✅ Fast to run
- ✅ Easy to debug
- ✅ Covers edge cases
- ✅ Reusable

---

### **Final Recommendation: Three-Layer Testing Strategy**

**Rationale:**
- Unit tests: Fast, isolated, comprehensive
- Integration tests: Realistic, validate flow
- Evaluation tests: End-to-end validation

**Test Coverage Target:**
- Unit tests: >80% code coverage
- Integration tests: All major flows
- Evaluation tests: 1-2 real templates

**Test Execution:**
- Unit tests: Run in CI on every commit
- Integration tests: Run in CI (with mocked API)
- Evaluation tests: Run manually before releases

---

## Summary of Top Recommendations

| Area | Top Recommendation | Why |
|------|-------------------|-----|
| **Semantic Deduplication** | `all-MiniLM-L6-v2` | Fast, accurate enough, no API costs |
| **Evaluation Integration** | Extend `MetricsCollector` | Minimal changes, consistent framework |
| **Testing** | Three-layer strategy | Comprehensive, fast unit tests, realistic integration |

---

*Document created: 2025-01-XX*  
*Ready for implementation*

