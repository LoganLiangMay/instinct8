# Granular Constraint Metrics

## Overview

The granular constraint metrics module provides detailed breakdowns of constraint recall by category, similar to the hierarchical metrics' domain/category/episode approach. This helps identify which types of constraints are being lost during compression.

## Features

### 1. Constraint Categorization

Constraints are automatically categorized into:
- **Budget**: Cost, price, spending limits
- **Timeline**: Deadlines, schedules, time constraints
- **Technical**: Integration, compatibility, protocol requirements
- **Team**: Developer experience, skill levels
- **Compliance**: GDPR, HIPAA, regulatory requirements
- **Performance**: Latency, throughput, scalability
- **Other**: Catch-all for unclassified constraints

### 2. Per-Category Recall Scores

Instead of a single overall recall score, you get:
- `budget_recall`: How well budget constraints are preserved
- `timeline_recall`: How well timeline constraints are preserved
- `technical_recall`: How well technical constraints are preserved
- `team_recall`: How well team constraints are preserved
- `compliance_recall`: How well compliance constraints are preserved
- `performance_recall`: How well performance constraints are preserved
- `other_recall`: How well other constraints are preserved

### 3. Category Drift

Measures the difference between the best and worst performing categories:
```
category_drift = max(category_recalls) - min(category_recalls)
```

High drift indicates that some constraint types are being preserved better than others.

### 4. Weighted Score

A weighted average that favors critical constraint categories:
- Technical: 25% (most common, critical for implementation)
- Budget: 15%
- Timeline: 15%
- Compliance: 15%
- Performance: 15%
- Team: 10%
- Other: 5%

## Usage

### Basic Usage

```python
from evaluation.granular_constraint_metrics import (
    measure_granular_constraint_recall,
    format_granular_constraint_report,
)

constraints = [
    "Budget: maximum $10K implementation cost",
    "Timeline: must complete implementation in 2 weeks",
    "Must support real-time WebSocket communication",
    "Team experience: intermediate Python developers",
    "Must integrate with existing PostgreSQL database",
]

agent_response = "We have a $10K budget, 2-week deadline, need WebSockets, and PostgreSQL integration"

# Measure granular recall
metrics = measure_granular_constraint_recall(constraints, agent_response)

# Print report
print(format_granular_constraint_report(metrics))
```

### With MetricsCollector

Enable granular metrics in `MetricsCollector`:

```python
from evaluation.metrics import MetricsCollector

collector = MetricsCollector(
    original_goal="Research frameworks...",
    constraints=constraints,
    use_granular_metrics=True,  # Enable granular metrics
)

# ... collect metrics at compression points ...

# Get results with granular breakdowns
results = collector.get_results()
granular_data = results["granular_constraint_metrics"]

# Get formatted report
report = collector.get_granular_constraint_report()
print(report)
```

## Example Output

```
============================================================
GRANULAR CONSTRAINT RECALL REPORT
============================================================

OVERALL RECALL: 80.0%

RECALL BY CATEGORY:
  Budget:        100.0%
  Timeline:      100.0%
  Technical:     66.7%
  Team:          100.0%
  Compliance:    100.0%
  Performance:   100.0%
  Other:         100.0%

DERIVED METRICS:
  Category Drift: +33.3%
    (difference between best and worst category)

WEIGHTED SCORE:   88.3%

------------------------------------------------------------
PER-CONSTRAINT RESULTS:

  BUDGET CONSTRAINTS:
    ✓ Budget: maximum $10K implementation cost

  TIMELINE CONSTRAINTS:
    ✓ Timeline: must complete implementation in 2 weeks

  TECHNICAL CONSTRAINTS:
    ✓ Must support real-time WebSocket communication
    ✗ Must integrate with existing PostgreSQL database

  TEAM CONSTRAINTS:
    ✓ Team experience: intermediate Python developers
```

## Benefits Over Simple Recall

1. **Identifies Weak Points**: Shows which constraint categories are being lost
2. **Better Diagnostics**: Helps understand why certain constraints are forgotten
3. **Actionable Insights**: Can focus improvement efforts on specific categories
4. **Consistent with Hierarchical Metrics**: Uses the same pattern as domain/category/episode recall

## Integration with Existing Code

The granular metrics are **backward compatible**. Existing code using `measure_constraint_recall()` will continue to work. To enable granular metrics:

1. Set `use_granular_metrics=True` in `MetricsCollector`
2. Access granular data via `get_results()["granular_constraint_metrics"]`
3. Use `get_granular_constraint_report()` for formatted output

## Comparison with Hierarchical Metrics

| Feature | Hierarchical Metrics | Granular Constraint Metrics |
|---------|---------------------|----------------------------|
| **Focus** | Information depth (domain/category/episode) | Constraint type (budget/timeline/technical) |
| **Use Case** | Testing hierarchical compression strategies | Testing constraint preservation |
| **Structure** | Probe-based with expected elements | Constraint-based with categories |
| **Scoring** | Recall + Precision + Fidelity | Recall + Category Drift + Weighted Score |

Both use the same underlying LLM-as-judge approach for semantic matching.

