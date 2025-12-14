#!/usr/bin/env python3
"""
Test Strategy F (Protected Core) on Product Pivot Template

This script runs Strategy F on the product-pivot-015-multi-shift template
to verify how Protected Core handles multiple goal shifts.
"""

import json
import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from evaluation.harness import load_template, run_single_trial, EvaluationResults
from evaluation.goal_tracking import track_goal_evolution, get_current_goal_at_turn
from strategies.strategy_f_protected_core import StrategyF_ProtectedCore


def main():
    # Check for API key
    if not os.getenv("OPENAI_API_KEY") and not os.getenv("ANTHROPIC_API_KEY"):
        print("ERROR: OPENAI_API_KEY or ANTHROPIC_API_KEY environment variable not set!")
        print("Please set it with: export OPENAI_API_KEY='your-key-here'")
        sys.exit(1)
    
    # Load template
    template_path = project_root / "templates" / "product-pivot-015-multi-shift-8k-4compactions.json"
    
    if not template_path.exists():
        print(f"ERROR: Template not found at {template_path}")
        sys.exit(1)
    
    print("=" * 70)
    print("TESTING STRATEGY F: Protected Core + Goal Re-assertion")
    print("=" * 70)
    print(f"Template: {template_path.name}")
    print("=" * 70)
    
    template = load_template(str(template_path))
    
    # Extract template info
    initial_setup = template["initial_setup"]
    original_goal = initial_setup["original_goal"]
    constraints = initial_setup["hard_constraints"]
    system_prompt = initial_setup["system_prompt"]
    
    print(f"\nInitial Goal: {original_goal}")
    print(f"Constraints: {len(constraints)} constraints")
    print(f"Turns: {len(template['turns'])} turns")
    print(f"Compression points: {sum(1 for t in template['turns'] if t.get('is_compression_point', False))}")
    
    # Check for goal shifts in the template
    shift_turns = []
    for turn in template['turns']:
        content = turn.get('content', '').lower()
        if 'actually' in content or 'pivot' in content or 'change' in content:
            if turn.get('role') == 'user':
                shift_turns.append(turn['turn_id'])
    
    if shift_turns:
        print(f"\nGoal shifts detected at turns: {shift_turns}")
        for turn_id in shift_turns:
            turn = next(t for t in template['turns'] if t['turn_id'] == turn_id)
            print(f"  Turn {turn_id}: {turn['content'][:100]}...")
    
    # Create Strategy F
    print("\n" + "=" * 70)
    print("INITIALIZING STRATEGY F")
    print("=" * 70)
    
    strategy = StrategyF_ProtectedCore(
        system_prompt=system_prompt,
        backend="auto",  # Will use available API key
    )
    
    strategy.initialize(original_goal, constraints)
    
    print("✓ Strategy F initialized")
    print("  - Protected Core: Active")
    print(f"  - Original Goal: {strategy.protected_core.original_goal[:80]}...")
    print(f"  - Hard Constraints: {len(strategy.protected_core.hard_constraints)} constraints")
    
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
    print(f"\nNOTE: Goal coherence measures against ORIGINAL goal.")
    print(f"      After goal shifts, lower scores may indicate correct adaptation to new goals.\n")
    
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
        
        # Check if this compression point is after a goal shift
        if shift_turns:
            shifts_before_cp = [s for s in shift_turns if s < turn_id]
            if shifts_before_cp:
                current_goal_at_cp = get_current_goal_at_turn(turn_id, goal_timeline, original_goal)
                if current_goal_at_cp != original_goal:
                    print(f"    ✓ After {len(shifts_before_cp)} goal shift(s) - measuring vs CURRENT goal")
                    print(f"      Current goal: {current_goal_at_cp[:70]}...")
                else:
                    print(f"    ⚠ After {len(shifts_before_cp)} goal shift(s) - but goal timeline not updated")
    
    # Save results
    output_dir = project_root / "results"
    output_dir.mkdir(exist_ok=True)
    
    results = EvaluationResults(
        strategy_name="Strategy F - Protected Core + Goal Re-assertion",
        template_id=template["template_id"],
        num_trials=1,
        trials=[result],
        aggregate_summary=summary,
    )
    
    output_path = output_dir / "strategy_f_product_pivot_test.json"
    with open(output_path, "w") as f:
        json.dump(results.to_dict(), f, indent=2)
    
    print(f"\n" + "=" * 70)
    print(f"Results saved to: {output_path}")
    print("=" * 70)
    
    return results


if __name__ == "__main__":
    main()

