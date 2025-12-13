#!/usr/bin/env python3
"""
Compare Codex versions: baseline vs modified.

This script evaluates your modified Codex against the baseline and shows
a side-by-side comparison of performance metrics.

DIRECTORY STRUCTURE:
    instinct8/main/
    ├── codex/                        # BASELINE - do not modify
    │   └── codex-rs/
    ├── codex-experimental/           # PUT YOUR MODIFIED CODEX HERE
    │   └── codex-rs/
    ├── evaluation/
    └── run_comparison_eval.py

HOW TO ADD YOUR MODIFIED CODEX:
    1. Copy your modified Codex repo to: codex-experimental/
       $ cp -r /path/to/your/codex codex-experimental/

    2. Build it:
       $ cd codex-experimental/codex-rs && cargo build --release

    3. Run comparison:
       $ python run_comparison_eval.py

CUSTOM NAMING:
    You can use any name instead of "codex-experimental":
    $ python run_comparison_eval.py --name my-codex-v2

    This will look for: codex-my-codex-v2/ or my-codex-v2/

Usage:
    # Compare baseline vs codex-experimental/ (default)
    python run_comparison_eval.py

    # Compare baseline vs a custom-named version
    python run_comparison_eval.py --name graphrag

    # Build both and compare
    python run_comparison_eval.py --build-all

    # Explicit path to modified binary
    python run_comparison_eval.py --modified /path/to/codex

    # Save results
    python run_comparison_eval.py --output results/comparison.json
"""

import argparse
import json
import logging
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from evaluation.codex_cli_wrapper import (
    CodexCLIWrapper,
    find_codex,
)
from evaluation.datasets import CodingDataset, CodingTask

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Default paths relative to this script
SCRIPT_DIR = Path(__file__).parent
REPO_ROOT = SCRIPT_DIR.parent

# Baseline Codex is included in main/codex/
BASELINE_CODEX_PATH = SCRIPT_DIR / "codex" / "codex-rs" / "target" / "release" / "codex"
BASELINE_CODEX_SRC = SCRIPT_DIR / "codex" / "codex-rs"

# Default modified Codex location (codex-experimental/)
DEFAULT_MODIFIED_NAME = "experimental"


def find_modified_codex(name: str = None) -> tuple[Path, Path]:
    """
    Find the modified Codex binary and source directory.

    Searches for directories in this order:
    1. codex-{name}/ (if name provided)
    2. {name}/ (if name provided)
    3. codex-experimental/ (default)

    Args:
        name: Optional name to search for (e.g., "graphrag" finds codex-graphrag/)

    Returns:
        Tuple of (binary_path, source_path)
    """
    name = name or DEFAULT_MODIFIED_NAME

    # Directories to check (in order of preference)
    candidates = [
        SCRIPT_DIR / f"codex-{name}" / "codex-rs",
        SCRIPT_DIR / name / "codex-rs",
        SCRIPT_DIR / f"codex-{name}",
        SCRIPT_DIR / name,
    ]

    for src_dir in candidates:
        if src_dir.exists():
            # Check for Rust project structure
            binary = src_dir / "target" / "release" / "codex"
            if (src_dir / "Cargo.toml").exists():
                return binary, src_dir
            # Check if this IS the codex-rs directory
            parent_binary = src_dir.parent / "codex-rs" / "target" / "release" / "codex"
            if (src_dir.parent / "codex-rs" / "Cargo.toml").exists():
                return parent_binary, src_dir.parent / "codex-rs"

    # Fallback to default path
    default_src = SCRIPT_DIR / f"codex-{DEFAULT_MODIFIED_NAME}" / "codex-rs"
    default_binary = default_src / "target" / "release" / "codex"
    return default_binary, default_src


def calculate_goal_retention(original_goal: str, probed_goal: str) -> float:
    """Calculate goal retention score using keyword overlap."""
    if not probed_goal.strip():
        return 0.0

    stop_words = {'the', 'a', 'an', 'is', 'are', 'was', 'were', 'be', 'been',
                  'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will',
                  'would', 'could', 'should', 'may', 'might', 'must', 'shall',
                  'to', 'of', 'in', 'for', 'on', 'with', 'at', 'by', 'from',
                  'as', 'and', 'but', 'if', 'or', 'because', 'this', 'that',
                  'what', 'which', 'who', 'i', 'you', 'it', 'we', 'they'}

    original_words = set(original_goal.lower().split()) - stop_words
    probed_words = set(probed_goal.lower().split()) - stop_words

    if not original_words:
        return 1.0

    intersection = original_words & probed_words
    union = original_words | probed_words
    return len(intersection) / len(union) if union else 1.0


def evaluate_task_completion(task: CodingTask, output: str) -> Dict[str, float]:
    """Evaluate task completion metrics."""
    has_output = 1.0 if output.strip() else 0.0
    has_code = 1.0 if ("```" in output or "def " in output or "class " in output) else 0.0
    error_indicators = ["error", "exception", "failed", "traceback"]
    no_errors = 0.0 if any(ind in output.lower() for ind in error_indicators) else 1.0

    return {
        "has_output": has_output,
        "has_code": has_code,
        "no_errors": no_errors,
        "task_completion": has_output * 0.3 + has_code * 0.4 + no_errors * 0.3,
    }


def run_single_evaluation(
    codex: CodexCLIWrapper,
    tasks: List[CodingTask],
    verbose: bool = False,
) -> Dict[str, Any]:
    """Run evaluation on a single Codex version."""
    results = []

    for i, task in enumerate(tasks):
        if verbose:
            logger.info(f"  Task {i+1}/{len(tasks)}: {task.task_id}")

        task_prompt = f"""# Coding Task

## Goal
{task.specification.goal}

## Constraints
{chr(10).join('- ' + c for c in task.specification.constraints)}

## Starting Code
```{task.specification.language}
{task.specification.starting_code}
```

Please implement this task.
"""

        response = codex.run_prompt(task_prompt, timeout=120)
        goal_response = codex.probe_goal("What is the main objective?")

        goal_retention = calculate_goal_retention(task.specification.goal, goal_response)
        completion_metrics = evaluate_task_completion(task, response.output)

        results.append({
            "task_id": task.task_id,
            "goal_retention": goal_retention,
            "duration_seconds": response.duration_seconds,
            **completion_metrics,
        })

    # Aggregate
    metrics = {}
    for metric in ["goal_retention", "task_completion", "has_code", "no_errors"]:
        values = [r.get(metric, 0) for r in results]
        if values:
            metrics[metric] = sum(values) / len(values)

    return {
        "num_tasks": len(results),
        "metrics": metrics,
        "per_task": results,
        "total_duration": sum(r["duration_seconds"] for r in results),
    }


def build_codex(source_dir: Path) -> bool:
    """Build Codex from source using cargo."""
    if not source_dir.exists():
        logger.error(f"Source directory not found: {source_dir}")
        return False

    logger.info(f"Building Codex from {source_dir}...")
    try:
        result = subprocess.run(
            ["cargo", "build", "--release"],
            cwd=source_dir,
            capture_output=True,
            text=True,
            timeout=600,  # 10 minutes
        )
        if result.returncode == 0:
            logger.info("Build successful!")
            return True
        else:
            logger.error(f"Build failed: {result.stderr}")
            return False
    except FileNotFoundError:
        logger.error("Rust/Cargo not found. Install from https://rustup.rs")
        return False
    except subprocess.TimeoutExpired:
        logger.error("Build timed out")
        return False


def print_comparison(
    baseline_results: Dict[str, Any],
    modified_results: Dict[str, Any],
    baseline_version: str,
    modified_version: str,
) -> None:
    """Print side-by-side comparison of results."""
    print("\n" + "=" * 70)
    print("CODEX COMPARISON EVALUATION")
    print("=" * 70)

    print(f"\nBaseline:  {baseline_version}")
    print(f"Modified:  {modified_version}")
    print(f"Tasks:     {baseline_results['num_tasks']}")

    print("\n" + "-" * 70)
    print("RESULTS COMPARISON")
    print("-" * 70)

    print(f"\n{'Metric':<20} {'Baseline':>12} {'Modified':>12} {'Diff':>12} {'Change':>10}")
    print("-" * 70)

    b_metrics = baseline_results.get("metrics", {})
    m_metrics = modified_results.get("metrics", {})

    metrics_display = [
        ("Goal Retention", "goal_retention"),
        ("Task Completion", "task_completion"),
        ("Has Code", "has_code"),
        ("No Errors", "no_errors"),
    ]

    for display_name, metric_key in metrics_display:
        b_val = b_metrics.get(metric_key, 0)
        m_val = m_metrics.get(metric_key, 0)
        diff = m_val - b_val
        pct = (diff / b_val * 100) if b_val > 0 else 0

        indicator = "+" if diff > 0 else ""
        status = "BETTER" if diff > 0.01 else ("WORSE" if diff < -0.01 else "SAME")

        print(f"{display_name:<20} {b_val:>12.3f} {m_val:>12.3f} {indicator}{diff:>11.3f} {status:>10}")

    print("-" * 70)

    # Time comparison
    b_time = baseline_results.get("total_duration", 0)
    m_time = modified_results.get("total_duration", 0)
    time_diff = m_time - b_time

    print(f"\n{'Total Time (s)':<20} {b_time:>12.1f} {m_time:>12.1f} {time_diff:>+12.1f}")

    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)

    improvements = []
    regressions = []

    for display_name, metric_key in metrics_display:
        b_val = b_metrics.get(metric_key, 0)
        m_val = m_metrics.get(metric_key, 0)
        diff = m_val - b_val
        pct = (diff / b_val * 100) if b_val > 0 else 0

        if diff > 0.01:
            improvements.append(f"{display_name}: +{pct:.1f}%")
        elif diff < -0.01:
            regressions.append(f"{display_name}: {pct:.1f}%")

    if improvements:
        print(f"\nImprovements: {', '.join(improvements)}")
    if regressions:
        print(f"Regressions:  {', '.join(regressions)}")
    if not improvements and not regressions:
        print("\nNo significant differences detected.")

    print()


def main():
    parser = argparse.ArgumentParser(
        description="Compare baseline vs modified Codex versions",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )

    parser.add_argument(
        "--name",
        type=str,
        default=None,
        help="Name of modified Codex version (e.g., 'graphrag' looks for codex-graphrag/)",
    )
    parser.add_argument(
        "--baseline",
        type=str,
        default=str(BASELINE_CODEX_PATH),
        help="Path to baseline Codex binary (default: codex/codex-rs/target/release/codex)",
    )
    parser.add_argument(
        "--modified",
        type=str,
        default=None,
        help="Path to modified Codex binary (auto-detected from --name if not specified)",
    )
    parser.add_argument(
        "--build-all",
        action="store_true",
        help="Build both baseline and modified Codex before comparison",
    )
    parser.add_argument(
        "--build-baseline",
        action="store_true",
        help="Build only baseline Codex before comparison",
    )
    parser.add_argument(
        "--build-modified",
        action="store_true",
        help="Build only modified Codex before comparison",
    )
    parser.add_argument(
        "--tasks-dir",
        type=str,
        default="templates/coding/",
        help="Directory containing coding task templates",
    )
    parser.add_argument(
        "--num-tasks",
        type=int,
        default=None,
        help="Limit number of tasks",
    )
    parser.add_argument(
        "--output",
        type=str,
        default=None,
        help="Save comparison results to JSON file",
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Print detailed progress",
    )

    args = parser.parse_args()

    # Determine modified Codex paths
    if args.modified:
        modified_path = Path(args.modified)
        # Try to find source directory based on binary path
        modified_src = modified_path.parent.parent.parent  # target/release/codex -> codex-rs
        if not (modified_src / "Cargo.toml").exists():
            modified_src = None
    else:
        modified_path, modified_src = find_modified_codex(args.name)

    version_name = args.name or DEFAULT_MODIFIED_NAME

    # Build if requested
    if args.build_all or args.build_baseline:
        print("\n" + "-" * 70)
        print("Building BASELINE Codex...")
        print("-" * 70)
        if not build_codex(BASELINE_CODEX_SRC):
            print("ERROR: Failed to build baseline Codex")
            return 1

    if args.build_all or args.build_modified:
        print("\n" + "-" * 70)
        print(f"Building MODIFIED Codex ({version_name})...")
        print("-" * 70)
        if modified_src is None:
            print(f"ERROR: Cannot find source directory for modified Codex")
            print(f"\nPlease create: codex-{version_name}/codex-rs/")
            return 1
        if not build_codex(modified_src):
            print("ERROR: Failed to build modified Codex")
            return 1

    # Check baseline Codex
    baseline_path = Path(args.baseline)
    if not baseline_path.exists():
        print(f"ERROR: Baseline Codex not found at {baseline_path}")
        print("\nBuild it with: python run_comparison_eval.py --build-baseline")
        print("Or: cd codex/codex-rs && cargo build --release")
        return 1

    # Check modified Codex
    if not modified_path.exists():
        print(f"ERROR: Modified Codex not found at {modified_path}")
        print(f"\nTo set up your modified Codex:")
        print(f"  1. Copy your Codex to: codex-{version_name}/")
        print(f"  2. Build: cd codex-{version_name}/codex-rs && cargo build --release")
        print(f"  3. Run: python run_comparison_eval.py --name {version_name}")
        print(f"\nOr specify path directly: --modified /path/to/codex")
        return 1

    # Initialize wrappers
    try:
        baseline_codex = CodexCLIWrapper(codex_path=str(baseline_path))
        modified_codex = CodexCLIWrapper(codex_path=str(modified_path))
    except Exception as e:
        print(f"ERROR: Failed to initialize Codex wrapper: {e}")
        return 1

    print(f"Baseline Codex: {baseline_codex.codex_path}")
    print(f"  Version: {baseline_codex.version}")
    print(f"Modified Codex: {modified_codex.codex_path}")
    print(f"  Version: {modified_codex.version}")

    # Load tasks
    tasks_path = Path(args.tasks_dir)
    if not tasks_path.exists():
        print(f"ERROR: Tasks directory not found: {tasks_path}")
        return 1

    try:
        dataset = CodingDataset(str(tasks_path))
        tasks = list(dataset)
        if args.num_tasks:
            tasks = tasks[:args.num_tasks]
    except Exception as e:
        print(f"ERROR: Failed to load tasks: {e}")
        return 1

    print(f"\nLoaded {len(tasks)} task(s)")

    # Run evaluations
    print("\n" + "-" * 70)
    print("Evaluating BASELINE Codex...")
    print("-" * 70)
    with baseline_codex:
        baseline_results = run_single_evaluation(baseline_codex, tasks, args.verbose)

    print("\n" + "-" * 70)
    print("Evaluating MODIFIED Codex...")
    print("-" * 70)
    with modified_codex:
        modified_results = run_single_evaluation(modified_codex, tasks, args.verbose)

    # Print comparison
    print_comparison(
        baseline_results,
        modified_results,
        baseline_codex.version,
        modified_codex.version,
    )

    # Save results if requested
    if args.output:
        output_data = {
            "timestamp": datetime.now().isoformat(),
            "baseline": {
                "version": baseline_codex.version,
                "path": baseline_codex.codex_path,
                "results": baseline_results,
            },
            "modified": {
                "version": modified_codex.version,
                "path": str(modified_path),
                "results": modified_results,
            },
        }
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w") as f:
            json.dump(output_data, f, indent=2)
        print(f"Results saved to: {output_path}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
