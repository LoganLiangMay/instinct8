#!/usr/bin/env python3
"""
Evaluate your Codex CLI's compaction performance.

This script benchmarks whatever Codex CLI is installed on your system,
measuring goal retention under context compression, task completion,
and other metrics.

Usage:
    # Evaluate installed Codex CLI
    python run_codex_cli_eval.py

    # Specify path to Codex binary
    python run_codex_cli_eval.py --codex-path /path/to/codex

    # Run specific number of tasks
    python run_codex_cli_eval.py --num-tasks 3

    # Verbose output
    python run_codex_cli_eval.py --verbose

Example Output:
    ============================================================
    CODEX CLI COMPACTION EVALUATION
    ============================================================
    Codex Binary:  /usr/local/bin/codex
    Version:       codex 1.2.3
    Tasks:         3 coding scenarios

    RESULTS:
    ┌──────────────────┬───────────────┐
    │ Metric           │ Score         │
    ├──────────────────┼───────────────┤
    │ Goal Retention   │ 0.92          │
    │ Task Completion  │ 0.85          │
    │ Has Code         │ 1.00          │
    │ No Errors        │ 0.90          │
    └──────────────────┴───────────────┘
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

from evaluation.codex_cli_wrapper import (
    CodexCLIWrapper,
    CodexResponse,
    find_codex,
    get_codex_version,
)
from evaluation.datasets import CodingDataset, CodingTask

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def calculate_goal_retention(
    original_goal: str,
    probed_goal: str,
) -> float:
    """
    Calculate how well the goal was retained after context operations.

    Uses simple keyword overlap as a proxy for semantic similarity.
    For production, consider using embeddings or LLM-based evaluation.

    Args:
        original_goal: The original task goal
        probed_goal: What Codex reported as the current goal

    Returns:
        Retention score between 0 and 1
    """
    if not probed_goal.strip():
        return 0.0

    # Normalize text
    original_words = set(original_goal.lower().split())
    probed_words = set(probed_goal.lower().split())

    # Remove common stop words
    stop_words = {'the', 'a', 'an', 'is', 'are', 'was', 'were', 'be', 'been',
                  'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will',
                  'would', 'could', 'should', 'may', 'might', 'must', 'shall',
                  'to', 'of', 'in', 'for', 'on', 'with', 'at', 'by', 'from',
                  'as', 'into', 'through', 'during', 'before', 'after', 'above',
                  'below', 'between', 'under', 'again', 'further', 'then',
                  'once', 'here', 'there', 'when', 'where', 'why', 'how', 'all',
                  'each', 'few', 'more', 'most', 'other', 'some', 'such', 'no',
                  'nor', 'not', 'only', 'own', 'same', 'so', 'than', 'too',
                  'very', 'just', 'and', 'but', 'if', 'or', 'because', 'until',
                  'while', 'this', 'that', 'these', 'those', 'what', 'which',
                  'who', 'whom', 'i', 'you', 'he', 'she', 'it', 'we', 'they'}

    original_keywords = original_words - stop_words
    probed_keywords = probed_words - stop_words

    if not original_keywords:
        return 1.0 if not probed_keywords else 0.5

    # Calculate Jaccard similarity
    intersection = original_keywords & probed_keywords
    union = original_keywords | probed_keywords

    if not union:
        return 1.0

    return len(intersection) / len(union)


def evaluate_task_completion(
    task: CodingTask,
    codex_output: str,
) -> Dict[str, float]:
    """
    Evaluate how well the task was completed.

    Args:
        task: The coding task specification
        codex_output: Output from Codex CLI

    Returns:
        Dictionary of completion metrics
    """
    metrics = {
        "has_output": 1.0 if codex_output.strip() else 0.0,
        "output_length": len(codex_output),
    }

    # Check for code blocks
    has_code = "```" in codex_output or "def " in codex_output or "class " in codex_output
    metrics["has_code"] = 1.0 if has_code else 0.0

    # Check for error indicators
    error_indicators = ["error", "exception", "failed", "traceback"]
    has_errors = any(ind in codex_output.lower() for ind in error_indicators)
    metrics["no_errors"] = 0.0 if has_errors else 1.0

    # Simple completion heuristic
    metrics["task_completion"] = (
        metrics["has_output"] * 0.3 +
        metrics["has_code"] * 0.4 +
        metrics["no_errors"] * 0.3
    )

    return metrics


def run_evaluation(
    codex: CodexCLIWrapper,
    tasks: List[CodingTask],
    verbose: bool = False,
) -> Dict[str, Any]:
    """
    Run full evaluation on all tasks.

    Args:
        codex: CodexCLIWrapper instance
        tasks: List of coding tasks to evaluate
        verbose: Print detailed progress

    Returns:
        Dictionary of aggregated results
    """
    results = []

    for i, task in enumerate(tasks):
        if verbose:
            logger.info(f"\nTask {i+1}/{len(tasks)}: {task.task_id}")
            logger.info(f"Goal: {task.specification.goal[:100]}...")

        # Build task prompt
        task_prompt = f"""# Coding Task

## Goal
{task.specification.goal}

## Constraints
{chr(10).join('- ' + c for c in task.specification.constraints)}

## Starting Code
```{task.specification.language}
{task.specification.starting_code}
```

Please implement this task following the constraints.
"""

        # Run the task through Codex
        response = codex.run_prompt(task_prompt, timeout=120)

        if verbose:
            logger.info(f"  Response length: {len(response.output)} chars")
            logger.info(f"  Duration: {response.duration_seconds:.2f}s")
            if response.error:
                logger.warning(f"  Error: {response.error}")

        # Probe goal retention
        goal_response = codex.probe_goal("What is the main objective of this task?")

        if verbose:
            logger.info(f"  Goal probe response: {goal_response[:100]}...")

        # Calculate metrics
        goal_retention = calculate_goal_retention(
            task.specification.goal,
            goal_response
        )
        completion_metrics = evaluate_task_completion(task, response.output)

        task_result = {
            "task_id": task.task_id,
            "goal_retention": goal_retention,
            "duration_seconds": response.duration_seconds,
            "exit_code": response.exit_code,
            "error": response.error,
            **completion_metrics,
        }
        results.append(task_result)

        if verbose:
            logger.info(f"  Goal retention: {goal_retention:.2f}")
            logger.info(f"  Task completion: {completion_metrics['task_completion']:.2f}")

    # Aggregate results
    aggregated = {
        "num_tasks": len(results),
        "metrics": {},
    }

    metric_names = ["goal_retention", "task_completion", "has_code", "no_errors"]
    for metric in metric_names:
        values = [r.get(metric, 0) for r in results]
        if values:
            aggregated["metrics"][metric] = {
                "mean": sum(values) / len(values),
                "min": min(values),
                "max": max(values),
            }

    aggregated["per_task_results"] = results
    aggregated["total_duration"] = sum(r["duration_seconds"] for r in results)

    return aggregated


def print_results(
    results: Dict[str, Any],
    codex: CodexCLIWrapper,
) -> None:
    """Print results in a clean tabular format."""
    print("\n" + "=" * 60)
    print("CODEX CLI COMPACTION EVALUATION")
    print("=" * 60)
    print(f"\nCodex Binary:  {codex.codex_path}")
    print(f"Version:       {codex.version}")
    print(f"Tasks:         {results['num_tasks']} coding scenarios")
    print(f"Total Time:    {results['total_duration']:.1f}s")

    print("\nRESULTS:")
    print("+" + "-" * 20 + "+" + "-" * 15 + "+")
    print("|" + " Metric".ljust(20) + "|" + " Score".ljust(15) + "|")
    print("+" + "-" * 20 + "+" + "-" * 15 + "+")

    metrics = results.get("metrics", {})
    metric_display = [
        ("Goal Retention", "goal_retention"),
        ("Task Completion", "task_completion"),
        ("Has Code", "has_code"),
        ("No Errors", "no_errors"),
    ]

    for display_name, metric_key in metric_display:
        if metric_key in metrics:
            value = metrics[metric_key]["mean"]
            print(f"| {display_name:<18} | {value:>13.2f} |")

    print("+" + "-" * 20 + "+" + "-" * 15 + "+")

    # Per-task breakdown if there are multiple tasks
    if results["num_tasks"] > 1:
        print("\nPer-Task Breakdown:")
        for task_result in results["per_task_results"]:
            status = "OK" if task_result.get("exit_code", 0) == 0 else "ERR"
            print(f"  [{status}] {task_result['task_id']}: "
                  f"goal={task_result['goal_retention']:.2f}, "
                  f"completion={task_result['task_completion']:.2f}")


def main():
    parser = argparse.ArgumentParser(
        description="Evaluate your Codex CLI's compaction performance",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )

    parser.add_argument(
        "--codex-path",
        type=str,
        default=None,
        help="Path to Codex binary (auto-detected if not specified)",
    )
    parser.add_argument(
        "--tasks-dir",
        type=str,
        default="templates/coding/",
        help="Directory containing coding task templates (default: templates/coding/)",
    )
    parser.add_argument(
        "--num-tasks",
        type=int,
        default=None,
        help="Limit number of tasks to evaluate",
    )
    parser.add_argument(
        "--output",
        type=str,
        default=None,
        help="Save results to JSON file",
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Print detailed progress information",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=300,
        help="Timeout per task in seconds (default: 300)",
    )

    args = parser.parse_args()

    # Check if Codex is available
    if args.codex_path:
        codex_path = args.codex_path
    else:
        codex_path = find_codex()
        if not codex_path:
            print("ERROR: Codex CLI not found.")
            print("\nPlease install Codex CLI from https://github.com/openai/codex")
            print("Or specify the path with --codex-path /path/to/codex")
            print("\nNote: This script evaluates the REAL Codex CLI binary.")
            print("For simulation mode, use run_codex_eval.py instead.")
            return 1

    # Initialize wrapper
    try:
        codex = CodexCLIWrapper(
            codex_path=codex_path,
            timeout=args.timeout,
        )
    except Exception as e:
        print(f"ERROR: Failed to initialize Codex wrapper: {e}")
        return 1

    print(f"Found Codex: {codex.codex_path}")
    print(f"Version: {codex.version}")

    # Load tasks
    tasks_path = Path(args.tasks_dir)
    if not tasks_path.exists():
        print(f"ERROR: Tasks directory not found: {tasks_path}")
        print("\nPlease ensure coding task templates exist in the specified directory.")
        return 1

    try:
        dataset = CodingDataset(str(tasks_path))
        tasks = list(dataset)
        if args.num_tasks:
            tasks = tasks[:args.num_tasks]
    except Exception as e:
        print(f"ERROR: Failed to load tasks: {e}")
        return 1

    if not tasks:
        print("ERROR: No coding tasks found")
        return 1

    print(f"Loaded {len(tasks)} coding task(s)")

    # Run evaluation
    print("\nRunning evaluation...")
    with codex:
        results = run_evaluation(codex, tasks, verbose=args.verbose)

    # Print results
    print_results(results, codex)

    # Save to file if requested
    if args.output:
        output_data = {
            "codex_version": codex.version,
            "codex_path": codex.codex_path,
            "timestamp": datetime.now().isoformat(),
            **results,
        }
        with open(args.output, "w") as f:
            json.dump(output_data, f, indent=2)
        print(f"\nResults saved to: {args.output}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
