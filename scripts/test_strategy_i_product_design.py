#!/usr/bin/env python3
"""
Test Strategy I (A-MEM + Protected Core Hybrid) on Product Design Template

This script runs Strategy I on the product-design-009-healthcare template
to verify the hybrid strategy works correctly.
"""

import json
import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from evaluation.harness import load_template, run_single_trial, EvaluationResults, _calculate_aggregate_summary
from strategies.strategy_i_hybrid_amem_protected import StrategyI_AMemProtectedCore


def main():
    # Check for API key
    if not os.getenv("OPENAI_API_KEY") and not os.getenv("ANTHROPIC_API_KEY"):
        print("ERROR: OPENAI_API_KEY or ANTHROPIC_API_KEY environment variable not set!")
        print("Please set it with: export OPENAI_API_KEY='your-key-here'")
        sys.exit(1)
    
    # Load template
    template_path = project_root / "templates" / "product-design-009-healthcare-8k-4compactions.json"
    
    if not template_path.exists():
        print(f"ERROR: Template not found at {template_path}")
        sys.exit(1)
    
    print("=" * 70)
    print("TESTING STRATEGY I: A-MEM + Protected Core Hybrid")
    print("=" * 70)
    print(f"Template: {template_path.name}")
    print("=" * 70)
    
    template = load_template(str(template_path))
    
    # Extract template info
    initial_setup = template["initial_setup"]
    original_goal = initial_setup["original_goal"]
    constraints = initial_setup["hard_constraints"]
    system_prompt = initial_setup["system_prompt"]
    
    print(f"\nGoal: {original_goal}")
    print(f"Constraints: {len(constraints)} constraints")
    print(f"Turns: {len(template['turns'])} turns")
    print(f"Compression points: {sum(1 for t in template['turns'] if t.get('is_compression_point', False))}")
    
    # Create Strategy I
    print("\n" + "=" * 70)
    print("INITIALIZING STRATEGY I")
    print("=" * 70)
    
    strategy = StrategyI_AMemProtectedCore(
        system_prompt=system_prompt,
        backend="auto",  # Will use available API key
    )
    
    strategy.initialize(original_goal, constraints)
    
    print("✓ Strategy I initialized")
    print("  - Protected Core: Active")
    print("  - A-MEM Memory System: Active")
    
    # Run single trial
    print("\n" + "=" * 70)
    print("RUNNING TRIAL")
    print("=" * 70)
    
    result = run_single_trial(
        strategy=strategy,
        template=template,
        trial_id=1,
        use_granular_metrics=True,
    )
    
    # Print results
    print("\n" + "=" * 70)
    print("RESULTS")
    print("=" * 70)
    
    summary = result.summary
    print(f"\nGoal Coherence:")
    print(f"  Before: {summary.get('avg_goal_coherence_before', 0):.3f}")
    print(f"  After:  {summary.get('avg_goal_coherence_after', 0):.3f}")
    print(f"  Drift:  {summary.get('avg_goal_drift', 0):.3f}")
    
    print(f"\nConstraint Recall:")
    print(f"  Before: {summary.get('avg_constraint_recall_before', 0):.3f}")
    print(f"  After:  {summary.get('avg_constraint_recall_after', 0):.3f}")
    print(f"  Loss:   {summary.get('avg_constraint_loss', 0):.3f}")
    
    print(f"\nBehavioral Alignment: {summary.get('avg_behavioral_alignment_after', 0):.2f}/5.0")
    print(f"Compression Ratio: {summary.get('avg_compression_ratio', 0):.3f}")
    print(f"Drift Events: {summary.get('drift_events_detected', 0)}")
    
    # Show compression points
    print(f"\nCompression Points: {len(result.compression_points)}")
    for i, cp in enumerate(result.compression_points, 1):
        cp_id = cp.get("compression_point_id", i)
        turn_id = cp.get("turn_id", "?")
        metrics_before = cp.get("metrics_before", {})
        metrics_after = cp.get("metrics_after", {})
        drift = cp.get("drift", {})
        
        print(f"  CP {cp_id} (Turn {turn_id}):")
        print(f"    Goal coherence: {metrics_before.get('goal_coherence', 0):.3f} → {metrics_after.get('goal_coherence', 0):.3f}")
        print(f"    Constraint recall: {metrics_before.get('constraint_recall', 0):.3f} → {metrics_after.get('constraint_recall', 0):.3f}")
        if drift.get("drift_detected", False):
            print(f"    ⚠ Drift detected!")
    
    # Save results
    output_dir = project_root / "results"
    output_dir.mkdir(exist_ok=True)
    
    results = EvaluationResults(
        strategy_name="Strategy I - A-MEM + Protected Core Hybrid",
        template_id=template["template_id"],
        num_trials=1,
        trials=[result],
        aggregate_summary=summary,
    )
    
    output_path = output_dir / "strategy_i_product_design_test.json"
    with open(output_path, "w") as f:
        json.dump(results.to_dict(), f, indent=2)
    
    print(f"\n" + "=" * 70)
    print(f"Results saved to: {output_path}")
    print("=" * 70)
    
    return results


if __name__ == "__main__":
    main()

