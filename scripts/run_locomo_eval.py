#!/usr/bin/env python3
"""
Run A-mem's LoCoMo Benchmark on Codex Agents

This script evaluates Codex compression strategies using A-mem's original
LoCoMo benchmark for direct comparison.

Usage:
    # Run with default settings (10% of dataset)
    python run_locomo_eval.py

    # Run full dataset
    python run_locomo_eval.py --ratio 1.0

    # Run specific categories only
    python run_locomo_eval.py --categories 1 2 4

    # Compare multiple strategies
    python run_locomo_eval.py --compare
"""

import os
import sys
import argparse
from pathlib import Path

# Add project root to path (scripts/ is one level down)
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from evaluation.locomo_eval import (
    evaluate_codex_on_locomo,
    compare_strategies_on_locomo,
)
from strategies import StrategyB_CodexCheckpoint


def main():
    parser = argparse.ArgumentParser(
        description="Run LoCoMo benchmark evaluation on Codex agents"
    )
    parser.add_argument(
        "--dataset",
        type=str,
        default=str(project_root / "data" / "A-mem" / "data" / "locomo10.json"),
        help="Path to LoCoMo dataset JSON"
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default=str(project_root / "results" / "locomo"),
        help="Directory to save results"
    )
    parser.add_argument(
        "--ratio",
        type=float,
        default=0.1,
        help="Fraction of dataset to evaluate (0.0-1.0)"
    )
    parser.add_argument(
        "--categories",
        type=int,
        nargs="+",
        default=None,
        help="Categories to evaluate (1-5), default all"
    )
    parser.add_argument(
        "--backend",
        type=str,
        default="openai",
        choices=["openai", "anthropic"],
        help="LLM backend to use"
    )
    parser.add_argument(
        "--model",
        type=str,
        default="gpt-4o-mini",
        help="LLM model name"
    )
    parser.add_argument(
        "--compression-threshold",
        type=int,
        default=50000,
        help="Token threshold for triggering compression"
    )
    parser.add_argument(
        "--compare",
        action="store_true",
        help="Compare multiple strategies"
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Reduce output verbosity"
    )

    args = parser.parse_args()

    # Create output directory
    os.makedirs(args.output_dir, exist_ok=True)

    print("#" * 70)
    print("# A-MEM LOCOMO BENCHMARK - CODEX AGENT EVALUATION")
    print("#" * 70)
    print(f"\nDataset: {args.dataset}")
    print(f"Output: {args.output_dir}")
    print(f"Ratio: {args.ratio * 100:.0f}%")
    print(f"Backend: {args.backend} / {args.model}")
    if args.categories:
        print(f"Categories: {args.categories}")
    print()

    if args.compare:
        # Compare multiple strategies
        print("Mode: Strategy Comparison")

        strategies = [
            StrategyB_CodexCheckpoint(
                system_prompt="You are a helpful assistant answering questions about conversations.",
                model=args.model if args.backend == "openai" else "claude-sonnet-4-20250514",
                backend=args.backend,
            ),
            # Add more strategies here as they're implemented:
            # StrategyD_AMemStyle(),
            # StrategyG_Hybrid(),
        ]

        results = compare_strategies_on_locomo(
            strategies=strategies,
            dataset_path=args.dataset,
            output_dir=args.output_dir,
            llm_backend=args.backend,
            llm_model=args.model,
            ratio=args.ratio,
        )

    else:
        # Single strategy evaluation
        print("Mode: Single Strategy Evaluation (Codex Baseline)")

        strategy = StrategyB_CodexCheckpoint(
            system_prompt="You are a helpful assistant answering questions about conversations.",
            model=args.model if args.backend == "openai" else "claude-sonnet-4-20250514",
            backend=args.backend,
        )

        output_path = os.path.join(
            args.output_dir,
            f"locomo_codex_baseline_{args.backend}.json"
        )

        results = evaluate_codex_on_locomo(
            strategy=strategy,
            dataset_path=args.dataset,
            output_path=output_path,
            llm_backend=args.backend,
            llm_model=args.model,
            compression_threshold=args.compression_threshold,
            ratio=args.ratio,
            categories=args.categories,
            verbose=not args.quiet,
        )

        # Print key metrics
        print("\n" + "=" * 70)
        print("KEY METRICS (for comparison with A-mem)")
        print("=" * 70)

        if "overall" in results.aggregate_metrics:
            metrics = results.aggregate_metrics["overall"]
            key_metrics = [
                ("Exact Match", "exact_match"),
                ("F1 Score", "f1"),
                ("ROUGE-1 F", "rouge1_f"),
                ("ROUGE-L F", "rougeL_f"),
                ("BLEU-1", "bleu1"),
                ("BLEU-4", "bleu4"),
                ("BERTScore F1", "bert_f1"),
                ("METEOR", "meteor"),
                ("SBERT Similarity", "sbert_similarity"),
            ]

            for name, key in key_metrics:
                if key in metrics:
                    m = metrics[key]
                    print(f"  {name:<20}: {m['mean']:.4f} (std: {m['std']:.4f})")

        # Print per-category breakdown
        print("\n" + "-" * 70)
        print("PER-CATEGORY BREAKDOWN")
        print("-" * 70)

        for cat in [1, 2, 3, 4, 5]:
            cat_key = f"category_{cat}"
            if cat_key in results.aggregate_metrics:
                cat_metrics = results.aggregate_metrics[cat_key]
                cat_name = {
                    1: "Single-hop",
                    2: "Temporal",
                    3: "Open-domain",
                    4: "Multi-hop",
                    5: "Adversarial",
                }.get(cat, f"Category {cat}")

                f1 = cat_metrics.get("f1", {}).get("mean", 0)
                em = cat_metrics.get("exact_match", {}).get("mean", 0)
                count = cat_metrics.get("f1", {}).get("count", 0)

                print(f"  {cat_name:<15}: F1={f1:.4f}, EM={em:.4f} (n={count})")

    print("\n" + "#" * 70)
    print("# EVALUATION COMPLETE")
    print("#" * 70)
    print(f"\nResults saved to: {args.output_dir}")


if __name__ == "__main__":
    main()
