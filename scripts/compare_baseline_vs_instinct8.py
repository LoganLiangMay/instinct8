#!/usr/bin/env python3
"""
Compare Codex Baseline vs Instinct8 Enhanced Strategy

Runs both strategies on the same template and generates a comparison report.
"""

import json
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from evaluation.harness import run_baseline_evaluation, EvaluationResults
from strategies.strategy_b_codex import StrategyB_CodexCheckpoint


def run_comparison(
    template_path: str,
    num_trials: int = 1,
    output_dir: str = "results",
):
    """
    Run both baseline and instinct8 strategies and compare results.
    """
    print("=" * 70)
    print("COMPARISON: Codex Baseline vs Instinct8 Enhanced")
    print("=" * 70)
    
    # Run Baseline (no goal preservation)
    print("\n" + "=" * 70)
    print("RUNNING BASELINE (Codex Original - No Goal Preservation)")
    print("=" * 70)
    
    # Temporarily modify the strategy creation to use baseline mode
    from evaluation.harness import load_template, run_single_trial, MockAgent, MetricsCollector
    from dataclasses import dataclass, field
    from typing import List
    
    template = load_template(template_path)
    
    baseline_trials = []
    for trial_id in range(1, num_trials + 1):
        strategy = StrategyB_CodexCheckpoint(
            system_prompt=template["initial_setup"]["system_prompt"],
            use_goal_preservation=False  # Baseline mode
        )
        result = run_single_trial(strategy, template, trial_id)
        baseline_trials.append(result)
    
    baseline_results = EvaluationResults(
        strategy_name="Codex Baseline",
        template_id=template["template_id"],
        num_trials=num_trials,
        trials=baseline_trials,
        aggregate_summary=_calculate_aggregate_summary(baseline_trials),
    )
    
    baseline_output = Path(output_dir) / "baseline_codex_8k_results.json"
    with open(baseline_output, "w") as f:
        json.dump(baseline_results.to_dict(), f, indent=2)
    print(f"\n✓ Baseline results saved to: {baseline_output}")
    
    # Run Instinct8 (with goal preservation)
    print("\n" + "=" * 70)
    print("RUNNING INSTINCT8 (Enhanced - With Goal Preservation)")
    print("=" * 70)
    
    instinct8_trials = []
    for trial_id in range(1, num_trials + 1):
        strategy = StrategyB_CodexCheckpoint(
            system_prompt=template["initial_setup"]["system_prompt"],
            use_goal_preservation=True  # Instinct8 mode
        )
        result = run_single_trial(strategy, template, trial_id)
        instinct8_trials.append(result)
    
    instinct8_results = EvaluationResults(
        strategy_name="Instinct8 Enhanced",
        template_id=template["template_id"],
        num_trials=num_trials,
        trials=instinct8_trials,
        aggregate_summary=_calculate_aggregate_summary(instinct8_trials),
    )
    
    instinct8_output = Path(output_dir) / "instinct8_8k_results.json"
    with open(instinct8_output, "w") as f:
        json.dump(instinct8_results.to_dict(), f, indent=2)
    print(f"\n✓ Instinct8 results saved to: {instinct8_output}")
    
    # Generate detailed comparison table
    print("\n" + "=" * 90)
    print("COMPARISON: Codex Baseline vs Instinct8 Enhanced")
    print("=" * 90)
    
    baseline_summary = baseline_results.aggregate_summary
    instinct8_summary = instinct8_results.aggregate_summary
    
    # Get compression points for detailed analysis
    baseline_trial = baseline_results.trials[0]
    instinct8_trial = instinct8_results.trials[0]
    
    # Handle both dict and object access
    if isinstance(baseline_trial, dict):
        baseline_cps = baseline_trial.get('compression_points', [])
    else:
        baseline_cps = baseline_trial.compression_points
    
    if isinstance(instinct8_trial, dict):
        instinct8_cps = instinct8_trial.get('compression_points', [])
    else:
        instinct8_cps = instinct8_trial.compression_points
    
    # Extract key metrics for calculations
    baseline_coherence_after = baseline_summary.get("avg_goal_coherence_after", 0.0)
    instinct8_coherence_after = instinct8_summary.get("avg_goal_coherence_after", 0.0)
    baseline_constraint_after = baseline_summary.get("avg_constraint_recall_after", 0.0)
    instinct8_constraint_after = instinct8_summary.get("avg_constraint_recall_after", 0.0)
    baseline_behavioral = baseline_summary.get("avg_behavioral_alignment", 0.0)
    instinct8_behavioral = instinct8_summary.get("avg_behavioral_alignment", 0.0)
    baseline_ratio = baseline_summary.get("avg_compression_ratio", 0.0)
    instinct8_ratio = instinct8_summary.get("avg_compression_ratio", 0.0)
    baseline_drift = baseline_summary.get("avg_goal_drift", 0.0)
    instinct8_drift = instinct8_summary.get("avg_goal_drift", 0.0)
    baseline_constraint_loss = baseline_summary.get("avg_constraint_loss", 0.0)
    instinct8_constraint_loss = instinct8_summary.get("avg_constraint_loss", 0.0)
    baseline_events = baseline_summary.get("total_drift_events", 0)
    instinct8_events = instinct8_summary.get("total_drift_events", 0)
    baseline_coherence_before = baseline_summary.get("avg_goal_coherence_before", 0.0)
    instinct8_coherence_before = instinct8_summary.get("avg_goal_coherence_before", 0.0)
    baseline_constraint_before = baseline_summary.get("avg_constraint_recall_before", 0.0)
    instinct8_constraint_before = instinct8_summary.get("avg_constraint_recall_before", 0.0)
    
    # Helper function to format percentage
    def fmt_pct(val):
        return f"{val*100:.1f}%"
    
    # Helper function to format delta with sign
    def fmt_delta(baseline, instinct8, higher_is_better=True):
        delta = instinct8 - baseline
        sign = "+" if delta >= 0 else ""
        color_indicator = "✓" if (delta > 0 and higher_is_better) or (delta < 0 and not higher_is_better) else "✗"
        return f"{sign}{delta*100:.1f}% {color_indicator}"
    
    # Calculate weighted score (similar to teammate's table)
    # Weight: Goal Coherence 40%, Constraint Recall 30%, Behavioral Alignment 20%, Compression Efficiency 10%
    def calculate_weighted_score(coherence, constraint, behavioral, compression_ratio):
        # Normalize behavioral alignment (0-5 scale to 0-1)
        behavioral_norm = behavioral / 5.0
        # Compression efficiency (lower ratio = better, so invert)
        compression_score = 1.0 - compression_ratio if compression_ratio < 1.0 else 0.0
        
        weighted = (
            coherence * 0.40 +
            constraint * 0.30 +
            behavioral_norm * 0.20 +
            compression_score * 0.10
        )
        return weighted
    
    baseline_weighted = calculate_weighted_score(
        baseline_coherence_after,
        baseline_constraint_after,
        baseline_behavioral,
        baseline_ratio
    )
    instinct8_weighted = calculate_weighted_score(
        instinct8_coherence_after,
        instinct8_constraint_after,
        instinct8_behavioral,
        instinct8_ratio
    )
    
    print(f"\n{'Metric':<35} {'Baseline':<18} {'Instinct8':<18} {'Delta':<18}")
    print("-" * 90)
    
    # === FINAL STATE METRICS (Most Important) ===
    print("\n📊 FINAL STATE METRICS (After All Compressions):")
    print("-" * 90)
    
    # Goal Coherence After (higher is better) - FINAL STATE
    coherence_delta = fmt_delta(baseline_coherence_after, instinct8_coherence_after, higher_is_better=True)
    print(f"{'Goal Coherence (Final)':<35} {fmt_pct(baseline_coherence_after):<18} {fmt_pct(instinct8_coherence_after):<18} {coherence_delta:<18}")
    
    # Constraint Recall After (higher is better) - FINAL STATE
    constraint_delta = fmt_delta(baseline_constraint_after, instinct8_constraint_after, higher_is_better=True)
    print(f"{'Constraint Recall (Final)':<35} {fmt_pct(baseline_constraint_after):<18} {fmt_pct(instinct8_constraint_after):<18} {constraint_delta:<18}")
    
    # Behavioral Alignment (higher is better) - FINAL STATE
    behavioral_delta = fmt_delta(baseline_behavioral, instinct8_behavioral, higher_is_better=True)
    print(f"{'Behavioral Alignment (Final)':<35} {baseline_behavioral:.2f}/5.0{'':<12} {instinct8_behavioral:.2f}/5.0{'':<12} {fmt_delta(baseline_behavioral/5.0, instinct8_behavioral/5.0, higher_is_better=True):<18}")
    
    # === DRIFT METRICS ===
    print("\n📉 DRIFT METRICS:")
    print("-" * 90)
    
    # Goal Drift (lower is better)
    drift_delta = fmt_delta(baseline_drift, instinct8_drift, higher_is_better=False)
    print(f"{'Avg Goal Drift':<35} {fmt_pct(baseline_drift):<18} {fmt_pct(instinct8_drift):<18} {drift_delta:<18}")
    
    # Constraint Loss (lower is better)
    constraint_loss_delta = fmt_delta(baseline_constraint_loss, instinct8_constraint_loss, higher_is_better=False)
    print(f"{'Avg Constraint Loss':<35} {fmt_pct(baseline_constraint_loss):<18} {fmt_pct(instinct8_constraint_loss):<18} {constraint_loss_delta:<18}")
    
    # Drift Events (lower is better)
    events_delta = baseline_events - instinct8_events
    events_delta_str = f"{events_delta:+d} {'✓' if events_delta > 0 else '✗' if events_delta < 0 else '='}"
    print(f"{'Total Drift Events':<35} {baseline_events:<18} {instinct8_events:<18} {events_delta_str:<18}")
    
    # === BEFORE STATE (for context) ===
    print("\n📈 INITIAL STATE (Before Compressions):")
    print("-" * 90)
    
    print(f"{'Goal Coherence (Initial)':<35} {fmt_pct(baseline_coherence_before):<18} {fmt_pct(instinct8_coherence_before):<18} {'(context)':<18}")
    
    print(f"{'Constraint Recall (Initial)':<35} {fmt_pct(baseline_constraint_before):<18} {fmt_pct(instinct8_constraint_before):<18} {'(context)':<18}")
    
    # === COMPRESSION EFFICIENCY ===
    print("\n🗜️  COMPRESSION EFFICIENCY:")
    print("-" * 90)
    
    ratio_delta = fmt_delta(baseline_ratio, instinct8_ratio, higher_is_better=False)  # Lower ratio = better compression
    print(f"{'Avg Compression Ratio':<35} {baseline_ratio:.3f}{'':<14} {instinct8_ratio:.3f}{'':<14} {ratio_delta:<18}")
    
    # Calculate compression percentage
    baseline_comp_pct = (1 - baseline_ratio) * 100
    instinct8_comp_pct = (1 - instinct8_ratio) * 100
    print(f"{'Compression % (size reduction)':<35} {baseline_comp_pct:.1f}%{'':<14} {instinct8_comp_pct:.1f}%{'':<14} {fmt_delta(baseline_comp_pct/100, instinct8_comp_pct/100, higher_is_better=True):<18}")
    
    # === SUMMARY ===
    print("\n" + "=" * 90)
    print("SUMMARY:")
    print("=" * 90)
    
    # Count wins (weighted by importance)
    wins = 0
    losses = 0
    ties = 0
    
    # Primary metrics (weight 2x)
    if abs(instinct8_coherence_after - baseline_coherence_after) < 0.01:
        ties += 1
    elif instinct8_coherence_after > baseline_coherence_after:
        wins += 2
    else:
        losses += 2
    
    if instinct8_constraint_after > baseline_constraint_after:
        wins += 2
    elif instinct8_constraint_after < baseline_constraint_after:
        losses += 2
    else:
        ties += 1
    
    if instinct8_behavioral > baseline_behavioral:
        wins += 1
    elif instinct8_behavioral < baseline_behavioral:
        losses += 1
    else:
        ties += 1
    
    if instinct8_constraint_loss < baseline_constraint_loss:
        wins += 2  # Constraint preservation is critical
    elif instinct8_constraint_loss > baseline_constraint_loss:
        losses += 2
    else:
        ties += 1
    
    if instinct8_weighted > baseline_weighted:
        wins += 1
    elif instinct8_weighted < baseline_weighted:
        losses += 1
    else:
        ties += 1
    
    if instinct8_events < baseline_events:
        wins += 1
    elif instinct8_events > baseline_events:
        losses += 1
    else:
        ties += 1
    
    print(f"\nInstinct8 vs Baseline: {wins} wins, {losses} losses, {ties} ties (weighted)")
    
    if wins > losses:
        print("✅ Instinct8 Enhanced performs BETTER overall")
    elif losses > wins:
        print("❌ Instinct8 Enhanced performs WORSE overall")
    else:
        print("⚖️  Instinct8 Enhanced performs SIMILAR overall")
    
    print("\nKey Findings:")
    if instinct8_constraint_after > baseline_constraint_after:
        improvement = (instinct8_constraint_after - baseline_constraint_after) * 100
        print(f"  ✓ Constraint preservation: +{improvement:.1f}% improvement (Instinct8 maintains {fmt_pct(instinct8_constraint_after)} vs Baseline {fmt_pct(baseline_constraint_after)})")
    
    if abs(instinct8_coherence_after - baseline_coherence_after) < 0.01:
        print(f"  = Goal coherence: Equivalent final state ({fmt_pct(instinct8_coherence_after)})")
    elif instinct8_coherence_after > baseline_coherence_after:
        improvement = (instinct8_coherence_after - baseline_coherence_after) * 100
        print(f"  ✓ Goal coherence: +{improvement:.1f}% improvement")
    else:
        decline = (baseline_coherence_after - instinct8_coherence_after) * 100
        print(f"  ⚠ Goal coherence: -{decline:.1f}% (but note: Instinct8 started higher)")
    
    if instinct8_behavioral > baseline_behavioral:
        improvement = (instinct8_behavioral - baseline_behavioral) / 5.0 * 100
        print(f"  ✓ Behavioral alignment: +{improvement:.1f}% improvement")
    
    if instinct8_weighted > baseline_weighted:
        improvement = (instinct8_weighted - baseline_weighted) * 100
        print(f"  ✓ Weighted composite score: +{improvement:.1f}% improvement")
    elif instinct8_weighted < baseline_weighted:
        decline = (baseline_weighted - instinct8_weighted) * 100
        print(f"  ⚠ Weighted composite score: -{decline:.1f}%")
    
    if instinct8_constraint_loss == 0.0 and baseline_constraint_loss > 0:
        print(f"  ✓ Perfect constraint preservation: Instinct8 maintains 100% constraints vs Baseline {fmt_pct(baseline_constraint_loss)} loss")
    
    print()
    
    # Save comparison
    comparison = {
        "template": template_path,
        "num_trials": num_trials,
        "baseline": baseline_summary,
        "instinct8": instinct8_summary,
        "improvements": {
            "goal_drift_reduction": baseline_drift - instinct8_drift,
            "goal_coherence_increase": instinct8_coherence_after - baseline_coherence_after,
            "constraint_loss_reduction": baseline_constraint_loss - instinct8_constraint_loss,
            "drift_events_reduction": baseline_events - instinct8_events,
            "weighted_score_delta": instinct8_weighted - baseline_weighted,
        },
        "weighted_scores": {
            "baseline": baseline_weighted,
            "instinct8": instinct8_weighted,
        },
        "per_compression_point": {
            "baseline": baseline_cps,
            "instinct8": instinct8_cps,
        }
    }
    
    comparison_output = Path(output_dir) / "comparison_baseline_vs_instinct8.json"
    with open(comparison_output, "w") as f:
        json.dump(comparison, f, indent=2)
    
    print(f"\n✓ Comparison saved to: {comparison_output}")
    print("\n" + "=" * 70)


def _calculate_aggregate_summary(trials):
    """Calculate aggregate summary from trial results."""
    if not trials:
        return {}
    
    all_summaries = [t.summary for t in trials]
    
    # Average each metric
    def avg(key: str) -> float:
        values = [s.get(key, 0) for s in all_summaries]
        return sum(values) / len(values) if values else 0.0
    
    def variance(key: str) -> float:
        values = [s.get(key, 0) for s in all_summaries]
        if len(values) < 2:
            return 0.0
        mean = sum(values) / len(values)
        return sum((v - mean) ** 2 for v in values) / len(values)
    
    return {
        "num_trials": len(trials),
        "avg_goal_coherence_before": avg("avg_goal_coherence_before"),
        "avg_goal_coherence_after": avg("avg_goal_coherence_after"),
        "avg_goal_drift": avg("avg_goal_drift"),
        "goal_drift_variance": variance("avg_goal_drift"),
        "avg_constraint_recall_before": avg("avg_constraint_recall_before"),
        "avg_constraint_recall_after": avg("avg_constraint_recall_after"),
        "avg_constraint_loss": avg("avg_constraint_loss"),
        "avg_behavioral_alignment": avg("avg_behavioral_alignment_after"),
        "total_drift_events": sum(
            s.get("drift_events_detected", 0) for s in all_summaries
        ),
        "avg_compression_ratio": avg("avg_compression_ratio"),
    }


if __name__ == "__main__":
    import argparse
    import os
    
    # Check for API key
    if not os.getenv("OPENAI_API_KEY"):
        print("ERROR: OPENAI_API_KEY environment variable not set!")
        print("Please set it with: export OPENAI_API_KEY='your-key-here'")
        sys.exit(1)
    
    parser = argparse.ArgumentParser(description="Compare Codex Baseline vs Instinct8")
    parser.add_argument(
        "--template",
        type=str,
        default="templates/research-synthesis-008-8k-4compactions-realistic.json",
        help="Path to conversation template"
    )
    parser.add_argument(
        "--trials",
        type=int,
        default=1,
        help="Number of trials to run"
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="results",
        help="Output directory for results"
    )
    
    args = parser.parse_args()
    
    run_comparison(
        template_path=args.template,
        num_trials=args.trials,
        output_dir=args.output_dir,
    )
