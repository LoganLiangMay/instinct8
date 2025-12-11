# Evaluation Framework
# This package contains metrics collection and probing functions
# for measuring goal coherence under compression.

from .metrics import (
    measure_goal_coherence,
    measure_constraint_recall,
    measure_behavioral_alignment,
    MetricsCollector,
)
from .harness import (
    run_baseline_evaluation,
    run_single_trial,
    MockAgent,
    TrialResult,
    EvaluationResults,
)

__all__ = [
    "measure_goal_coherence",
    "measure_constraint_recall",
    "measure_behavioral_alignment",
    "MetricsCollector",
    "run_baseline_evaluation",
    "run_single_trial",
    "MockAgent",
    "TrialResult",
    "EvaluationResults",
]

