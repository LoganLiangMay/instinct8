#!/usr/bin/env python3
"""
Run evaluation on baseline Codex strategy.

This script evaluates the Codex-style checkpoint strategy (Strategy B)
on all coding tasks in the templates/coding/ directory.
"""

import sys
from pathlib import Path

# Add project root to path (scripts/ is one level down)
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from evaluation import (
    UnifiedHarness,
    CodingDataset,
    CodexAgent,
    AgentConfig,
)
from strategies import StrategyB_CodexCheckpoint


def run_coding_evaluation():
    """Run evaluation on coding tasks with baseline Codex strategy."""
    print("=" * 70)
    print("CODEX BASELINE EVALUATION")
    print("=" * 70)

    # Load coding dataset
    dataset_path = project_root / "templates" / "coding"

    if not dataset_path.exists():
        print(f"Error: Dataset path does not exist: {dataset_path}")
        return None

    print(f"\nLoading dataset from: {dataset_path}")
    dataset = CodingDataset(dataset_path)

    print(f"Dataset: {dataset.name}")
    print(f"Evaluation type: {dataset.evaluation_type}")

    stats = dataset.get_statistics()
    print(f"\nDataset Statistics:")
    print(f"  Samples: {stats['num_samples']}")
    print(f"  Total turns: {stats['total_turns']}")
    print(f"  Compression points: {stats.get('total_compression_points', 'N/A')}")
    if 'task_type_distribution' in stats:
        print(f"  Task types: {stats['task_type_distribution']}")

    # Create baseline Codex strategy
    print("\n" + "-" * 70)
    print("Initializing Codex baseline strategy...")
    strategy = StrategyB_CodexCheckpoint(
        system_prompt="You are a coding assistant helping with software development tasks.",
        model="gpt-4o-mini",
        backend="openai",
    )

    # Create agent
    config = AgentConfig(
        model="gpt-4o-mini",
        backend="openai",
    )

    agent = CodexAgent(
        config=config,
        strategy=strategy,
        compaction_threshold=80000,  # 80k tokens before auto-compact
    )

    print(f"Agent: {agent.name}")
    print(f"Compaction threshold: 80,000 tokens")

    # Create harness and run evaluation
    print("\n" + "-" * 70)
    print("Running evaluation...")

    harness = UnifiedHarness(
        agent=agent,
        dataset=dataset,
        cache_dir=str(project_root / "cache" / "codex_eval"),
    )

    results = harness.run_evaluation(
        num_samples=None,  # All samples
        verbose=True,
    )

    # Print detailed results
    print("\n" + "=" * 70)
    print("DETAILED RESULTS")
    print("=" * 70)

    for sample_result in results.sample_results:
        print(f"\n--- Sample: {sample_result.sample_id} ---")
        print(f"  Evaluation type: {sample_result.evaluation_type}")
        print(f"  Context sizes: {sample_result.context_sizes[:5]}..." if len(sample_result.context_sizes) > 5 else f"  Context sizes: {sample_result.context_sizes}")

        if sample_result.coding_metrics:
            print("  Coding metrics:")
            for metric, value in sample_result.coding_metrics.items():
                if isinstance(value, float):
                    print(f"    {metric}: {value:.4f}")
                else:
                    print(f"    {metric}: {value}")

        if sample_result.compression_points:
            print(f"  Compression points: {len(sample_result.compression_points)}")
            for i, cp in enumerate(sample_result.compression_points):
                print(f"    Point {i+1}:")
                print(f"      Goal coherence: {cp.get('goal_coherence_before', 'N/A')} -> {cp.get('goal_coherence_after', 'N/A')}")
                print(f"      Compression ratio: {cp.get('compression_ratio', 'N/A')}")

    # Save results
    output_path = project_root / "results" / "codex_baseline_eval.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    results.save(str(output_path))
    print(f"\nResults saved to: {output_path}")

    return results


def run_compression_template_evaluation():
    """Run evaluation on compression templates if they exist."""
    print("\n" + "=" * 70)
    print("COMPRESSION TEMPLATE EVALUATION")
    print("=" * 70)

    from evaluation import TemplateDataset

    template_path = project_root / "templates"

    # Look for template JSON files (not in coding subdirectory)
    template_files = list(template_path.glob("*.json"))

    if not template_files:
        print("No compression template files found in templates/")
        return None

    print(f"Found {len(template_files)} template files")

    for template_file in template_files:
        print(f"\n--- Evaluating: {template_file.name} ---")

        try:
            dataset = TemplateDataset(str(template_file))

            strategy = StrategyB_CodexCheckpoint(
                system_prompt="You are a helpful assistant.",
                model="gpt-4o-mini",
                backend="openai",
            )

            config = AgentConfig(model="gpt-4o-mini", backend="openai")
            agent = CodexAgent(config=config, strategy=strategy)

            harness = UnifiedHarness(agent=agent, dataset=dataset)
            results = harness.run_evaluation(verbose=True)

            # Save results
            output_path = project_root / "results" / f"template_{template_file.stem}_eval.json"
            results.save(str(output_path))
            print(f"Results saved to: {output_path}")

        except Exception as e:
            print(f"Error evaluating {template_file.name}: {e}")


if __name__ == "__main__":
    print("\n" + "#" * 70)
    print("# CODEX BASELINE EVALUATION SUITE")
    print("#" * 70 + "\n")

    # Run coding evaluation
    coding_results = run_coding_evaluation()

    # Run compression template evaluation if available
    run_compression_template_evaluation()

    print("\n" + "#" * 70)
    print("# EVALUATION COMPLETE")
    print("#" * 70)
