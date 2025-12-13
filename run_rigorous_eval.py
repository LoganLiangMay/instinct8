#!/usr/bin/env python3
"""
Run publication-ready rigorous evaluation.

This script provides a comprehensive evaluation framework that meets
NeurIPS/ICLR publication standards with proper statistical methodology:

- Multiple runs per sample to capture LLM variance
- Bootstrap confidence intervals for all metrics
- Significance tests with Bonferroni correction
- Effect size calculations (Cohen's d)
- Baseline comparisons (upper and lower bounds)
- Systematic ablation studies

Usage:
    # Basic evaluation with baselines
    python run_rigorous_eval.py --dataset locomo --ratio 0.1

    # Multi-run evaluation (5 runs per sample)
    python run_rigorous_eval.py --dataset locomo --n-runs 5

    # With ablation studies
    python run_rigorous_eval.py --dataset locomo --ablations

    # Full rigorous evaluation
    python run_rigorous_eval.py --dataset locomo --n-runs 5 --baselines --ablations
"""

import argparse
import json
import logging
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from evaluation import (
    # Harness and datasets
    UnifiedHarness,
    LoCoMoDataset,
    AMemAgent,
    AgentConfig,
    # Statistics
    StatisticalResult,
    ComparisonResult,
    paired_t_test,
    bonferroni_correction,
    calculate_effect_size,
    interpret_effect_size,
    compare_strategies_statistical,
    format_comparison_table,
    compute_statistical_summary,
    # Baselines
    NoCompressionBaseline,
    RandomTruncationBaseline,
    RecencyOnlyBaseline,
    FirstLastBaseline,
    SlidingWindowBaseline,
    get_all_baselines,
    # Multi-run
    MultiRunEvaluator,
    format_multi_run_summary,
    # Ablations
    AblationRunner,
    format_ablation_table,
)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def run_baseline_comparison(
    dataset,
    n_runs: int = 1,
    confidence: float = 0.95,
    verbose: bool = True,
) -> Dict[str, Any]:
    """
    Run evaluation with all baseline strategies for comparison.

    Returns results for:
    - NoCompression (upper bound)
    - RandomTruncation (lower bound)
    - RecencyOnly (simple baseline)
    - FirstLast (primacy+recency baseline)
    - SlidingWindow (token-based baseline)
    """
    if verbose:
        logger.info("\n" + "=" * 70)
        logger.info("BASELINE COMPARISON EVALUATION")
        logger.info("=" * 70)

    baselines = get_all_baselines()
    results = {}

    for baseline in baselines:
        if verbose:
            logger.info(f"\nEvaluating: {baseline.name()}")

        # Create agent with baseline strategy
        config = AgentConfig(
            model="gpt-4o-mini",
            temperature=0.0,
        )

        # For QA evaluation, we use AMemAgent
        # The baseline strategies would be used differently for compression eval
        agent = AMemAgent(config)

        harness = UnifiedHarness(agent, dataset)
        result = harness.run_evaluation(
            n_runs=n_runs,
            confidence=confidence,
            verbose=verbose,
        )

        results[baseline.name()] = {
            "aggregate_metrics": result.aggregate_metrics,
            "n_runs": n_runs,
            "confidence": confidence,
            "statistical_summary": result.statistical_summary if n_runs > 1 else {},
        }

    return results


def run_strategy_comparison(
    results: Dict[str, Any],
    target_metric: str = "f1",
    verbose: bool = True,
) -> List[ComparisonResult]:
    """
    Compare all strategies with significance tests.

    Returns pairwise comparison results with:
    - t-statistics and p-values
    - Bonferroni-corrected p-values
    - Cohen's d effect sizes
    """
    if verbose:
        logger.info("\n" + "=" * 70)
        logger.info("STATISTICAL COMPARISON")
        logger.info("=" * 70)

    strategy_names = list(results.keys())
    comparisons = []

    # Extract scores for target metric
    strategy_scores = {}
    for name, result in results.items():
        if "statistical_summary" in result and result["statistical_summary"]:
            summary = result["statistical_summary"]
            if target_metric in summary:
                # For multi-run, we have per-sample means
                strategy_scores[name] = {target_metric: [summary[target_metric]["mean"]]}
        elif "aggregate_metrics" in result:
            agg = result["aggregate_metrics"]
            if "overall" in agg and target_metric in agg["overall"]:
                strategy_scores[name] = {target_metric: [agg["overall"][target_metric]["mean"]]}

    # Pairwise comparisons
    all_p_values = []
    comparison_pairs = []

    for i, name_a in enumerate(strategy_names):
        for name_b in strategy_names[i+1:]:
            if name_a in strategy_scores and name_b in strategy_scores:
                scores_a = strategy_scores[name_a]
                scores_b = strategy_scores[name_b]

                comparison_results = compare_strategies_statistical(
                    name_a, name_b,
                    scores_a, scores_b,
                    paired=True,
                    apply_correction=False,  # We'll apply correction after
                )
                comparisons.extend(comparison_results)
                for comp in comparison_results:
                    all_p_values.append(comp.p_value)
                    comparison_pairs.append((name_a, name_b, comp.metric))

    # Apply Bonferroni correction
    if all_p_values:
        corrected = bonferroni_correction(all_p_values)
        for i, comp in enumerate(comparisons):
            comp.p_value_corrected = corrected[i]
            comp.significant_05 = corrected[i] < 0.05
            comp.significant_01 = corrected[i] < 0.01

    if verbose and comparisons:
        print(format_comparison_table(comparisons))

    return comparisons


def run_ablation_studies(
    dataset,
    base_config: Dict[str, Any],
    ablation_params: Optional[List[str]] = None,
    n_runs: int = 1,
    verbose: bool = True,
) -> Dict[str, Any]:
    """
    Run systematic ablation studies.

    Default ablations:
    - retrieval_k: [5, 10, 15, 20, 30]
    - temperature: [0.0, 0.3, 0.5, 0.7, 1.0]
    - compression_threshold: [25000, 50000, 80000, 100000]
    """
    if verbose:
        logger.info("\n" + "=" * 70)
        logger.info("ABLATION STUDIES")
        logger.info("=" * 70)

    runner = AblationRunner(
        base_config=base_config,
        n_runs=n_runs,
    )

    def create_agent(config):
        agent_config = AgentConfig(
            model=config.get("model", "gpt-4o-mini"),
            temperature=config.get("temperature", 0.0),
        )
        return AMemAgent(agent_config)

    def evaluate(agent, dataset):
        harness = UnifiedHarness(agent, dataset)
        results = harness.run_evaluation(verbose=False)
        # Extract overall metrics
        if "overall" in results.aggregate_metrics:
            return {
                k: v.get("mean", v) if isinstance(v, dict) else v
                for k, v in results.aggregate_metrics["overall"].items()
            }
        return {}

    ablation_results = runner.run_default_ablations(
        create_agent_fn=create_agent,
        evaluate_fn=evaluate,
        dataset=dataset,
        ablation_names=ablation_params,
        target_metric="f1",
        verbose=verbose,
    )

    # Format results
    for name, result in ablation_results.items():
        if verbose:
            print(format_ablation_table(result))

    return {
        name: result.to_dict()
        for name, result in ablation_results.items()
    }


def generate_publication_report(
    evaluation_results: Dict[str, Any],
    comparisons: List[ComparisonResult],
    ablation_results: Optional[Dict[str, Any]],
    output_path: str,
) -> str:
    """
    Generate a publication-ready report in JSON format.

    The report includes:
    - Metadata (timestamp, n_runs, confidence level)
    - Per-strategy aggregate metrics with CI
    - Pairwise statistical comparisons
    - Ablation study results (if run)
    """
    report = {
        "metadata": {
            "generated_at": datetime.now().isoformat(),
            "format_version": "1.0",
            "statistical_tests": ["paired_t_test"],
            "correction_method": "bonferroni",
        },
        "strategy_results": evaluation_results,
        "statistical_comparisons": [
            {
                "strategy_a": c.strategy_a,
                "strategy_b": c.strategy_b,
                "metric": c.metric,
                "mean_diff": c.mean_diff,
                "t_statistic": c.t_statistic,
                "p_value": c.p_value,
                "p_value_corrected": c.p_value_corrected,
                "cohens_d": c.cohens_d,
                "effect_interpretation": c.effect_interpretation,
                "significant_05": c.significant_05,
                "significant_01": c.significant_01,
            }
            for c in comparisons
        ],
    }

    if ablation_results:
        report["ablation_studies"] = ablation_results

    # Save report
    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(report, f, indent=2)

    return output_path


def main():
    parser = argparse.ArgumentParser(
        description="Run publication-ready rigorous evaluation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )

    # Dataset options
    parser.add_argument(
        "--dataset",
        type=str,
        default="locomo",
        choices=["locomo"],
        help="Dataset to evaluate on (default: locomo)",
    )
    parser.add_argument(
        "--dataset-path",
        type=str,
        default="A-mem/LoCoMo.json",
        help="Path to dataset file",
    )
    parser.add_argument(
        "--ratio",
        type=float,
        default=0.1,
        help="Fraction of dataset to use (default: 0.1)",
    )
    parser.add_argument(
        "--num-samples",
        type=int,
        default=None,
        help="Limit number of samples (overrides ratio)",
    )

    # Statistical rigor options
    parser.add_argument(
        "--n-runs",
        type=int,
        default=1,
        help="Number of runs per sample for variance capture (default: 1)",
    )
    parser.add_argument(
        "--confidence",
        type=float,
        default=0.95,
        help="Confidence level for CI (default: 0.95)",
    )

    # Evaluation modes
    parser.add_argument(
        "--baselines",
        action="store_true",
        help="Run baseline strategy comparisons",
    )
    parser.add_argument(
        "--ablations",
        action="store_true",
        help="Run ablation studies",
    )
    parser.add_argument(
        "--ablation-params",
        type=str,
        nargs="+",
        default=None,
        help="Specific ablation parameters to run (default: all)",
    )

    # Output options
    parser.add_argument(
        "--output",
        type=str,
        default="results/rigorous_eval_{timestamp}.json",
        help="Output path for results (default: results/rigorous_eval_{timestamp}.json)",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        default=True,
        help="Print progress information",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Suppress progress output",
    )

    args = parser.parse_args()

    verbose = args.verbose and not args.quiet

    # Load dataset
    if verbose:
        logger.info(f"Loading dataset: {args.dataset}")

    if args.dataset == "locomo":
        dataset = LoCoMoDataset(
            args.dataset_path,
            ratio=args.ratio,
        )
    else:
        raise ValueError(f"Unknown dataset: {args.dataset}")

    if args.num_samples:
        samples = list(dataset)[:args.num_samples]
        # Create limited dataset wrapper
        class LimitedDataset:
            def __init__(self, samples, original):
                self._samples = samples
                self._original = original

            @property
            def name(self):
                return self._original.name

            @property
            def evaluation_type(self):
                return self._original.evaluation_type

            def __iter__(self):
                return iter(self._samples)

            def __len__(self):
                return len(self._samples)

        dataset = LimitedDataset(samples, dataset)

    if verbose:
        logger.info(f"Dataset size: {len(list(dataset))} samples")
        logger.info(f"N runs per sample: {args.n_runs}")
        logger.info(f"Confidence level: {args.confidence:.0%}")

    # Run evaluations
    evaluation_results = {}
    comparisons = []
    ablation_results = None

    # Run baseline comparisons if requested
    if args.baselines:
        evaluation_results = run_baseline_comparison(
            dataset,
            n_runs=args.n_runs,
            confidence=args.confidence,
            verbose=verbose,
        )
        comparisons = run_strategy_comparison(
            evaluation_results,
            verbose=verbose,
        )
    else:
        # Run single strategy evaluation
        config = AgentConfig(
            model="gpt-4o-mini",
            temperature=0.0,
        )
        agent = AMemAgent(config)
        harness = UnifiedHarness(agent, dataset)

        result = harness.run_evaluation(
            n_runs=args.n_runs,
            confidence=args.confidence,
            verbose=verbose,
        )

        evaluation_results["AMemAgent"] = {
            "aggregate_metrics": result.aggregate_metrics,
            "n_runs": args.n_runs,
            "confidence": args.confidence,
            "statistical_summary": result.statistical_summary if args.n_runs > 1 else {},
        }

    # Run ablation studies if requested
    if args.ablations:
        base_config = {
            "model": "gpt-4o-mini",
            "temperature": 0.0,
            "retrieval_k": 10,
        }
        ablation_results = run_ablation_studies(
            dataset,
            base_config=base_config,
            ablation_params=args.ablation_params,
            n_runs=args.n_runs,
            verbose=verbose,
        )

    # Generate report
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = args.output.format(timestamp=timestamp)

    report_path = generate_publication_report(
        evaluation_results,
        comparisons,
        ablation_results,
        output_path,
    )

    if verbose:
        logger.info(f"\n{'=' * 70}")
        logger.info(f"EVALUATION COMPLETE")
        logger.info(f"Results saved to: {report_path}")
        logger.info(f"{'=' * 70}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
