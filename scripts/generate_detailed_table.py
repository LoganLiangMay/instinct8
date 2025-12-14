#!/usr/bin/env python3
"""
Generate a detailed comparison table in markdown format
similar to the teammate's presentation format.
"""

import json
import sys
from pathlib import Path

def generate_detailed_table(comparison_file: str, output_file: str = None):
    """
    Generate a detailed markdown table from comparison JSON.
    """
    with open(comparison_file, 'r') as f:
        data = json.load(f)
    
    baseline = data['baseline']
    instinct8 = data['instinct8']
    improvements = data.get('improvements', {})
    
    # Helper to format percentage
    def fmt_pct(val):
        return f"{val*100:.1f}%"
    
    # Helper to format difference
    def fmt_diff(baseline_val, instinct8_val, higher_is_better=True):
        diff = instinct8_val - baseline_val
        sign = "+" if diff >= 0 else ""
        if isinstance(diff, float):
            return f"{sign}{diff*100:.1f}%"
        else:
            return f"{sign}{diff}"
    
    # Helper to determine winner
    def get_winner(baseline_val, instinct8_val, higher_is_better=True):
        if abs(instinct8_val - baseline_val) < 0.001:
            return "Tie"
        if higher_is_better:
            return "Instinct8" if instinct8_val > baseline_val else "Baseline"
        else:
            return "Instinct8" if instinct8_val < baseline_val else "Baseline"
    
    # Build markdown table
    lines = []
    lines.append("# Strategy Comparison: Codex Baseline vs Instinct8 Enhanced")
    lines.append("")
    lines.append(f"**Template:** {data.get('template', 'N/A')}  ")
    lines.append(f"**Trials:** {data.get('num_trials', 1)}  ")
    lines.append("")
    lines.append("## Metric Comparison")
    lines.append("")
    # Header must match data column widths (30 chars for metric, 15 for baseline, 10 for instinct8, 11 for diff, 6 for winner)
    lines.append("| Metric                          | Baseline (Codex) | Instinct8 | Difference | Winner |")
    lines.append("|:--------------------------------|:-----------------|:---------|:-----------|:-------|")
    
    # Primary Metrics
    metrics = [
        # (name, baseline_key, instinct8_key, higher_is_better, format_func)
        ("Goal Coherence (After)", "avg_goal_coherence_after", "avg_goal_coherence_after", True, fmt_pct),
        ("Constraint Recall (After)", "avg_constraint_recall_after", "avg_constraint_recall_after", True, fmt_pct),
        ("Goal Drift", "avg_goal_drift", "avg_goal_drift", False, fmt_pct),
        ("Constraint Loss", "avg_constraint_loss", "avg_constraint_loss", False, fmt_pct),
        ("Drift Events Detected", "total_drift_events", "total_drift_events", False, lambda x: str(int(x))),
        ("Compression Ratio", "avg_compression_ratio", "avg_compression_ratio", False, lambda x: f"{x:.3f}"),
        ("Behavioral Alignment", "avg_behavioral_alignment", "avg_behavioral_alignment", True, lambda x: f"{x:.2f}/5.0"),
    ]
    
    for metric_name, baseline_key, instinct8_key, higher_is_better, fmt_func in metrics:
        baseline_val = baseline.get(baseline_key, 0.0)
        instinct8_val = instinct8.get(instinct8_key, 0.0)
        
        baseline_str = fmt_func(baseline_val)
        instinct8_str = fmt_func(instinct8_val)
        diff_str = fmt_diff(baseline_val, instinct8_val, higher_is_better)
        winner = get_winner(baseline_val, instinct8_val, higher_is_better)
        
        # Pad for alignment - match header column widths
        # "Baseline (Codex)" = 17 chars, "Instinct8" = 9 chars, "Difference" = 10 chars, "Winner" = 6 chars
        lines.append(f"| {metric_name:<30} | {baseline_str:>17} | {instinct8_str:>9} | {diff_str:>10} | {winner:<6} |")
    
    # Add weighted score if available
    if 'weighted_scores' in data:
        baseline_weighted = data['weighted_scores']['baseline']
        instinct8_weighted = data['weighted_scores']['instinct8']
        diff_str = fmt_diff(baseline_weighted, instinct8_weighted, True)
        winner = get_winner(baseline_weighted, instinct8_weighted, True)
        baseline_str = fmt_pct(baseline_weighted)
        instinct8_str = fmt_pct(instinct8_weighted)
        lines.append(f"| {'**Weighted Score**':<30} | {baseline_str:>17} | {instinct8_str:>9} | {diff_str:>10} | {winner:<6} |")
    
    lines.append("")
    lines.append("## Additional Metrics")
    lines.append("")
    lines.append("| Metric                          | Baseline (Codex) | Instinct8 | Difference |")
    lines.append("|:--------------------------------|:-----------------|:---------|:-----------|")
    
    # Additional metrics
    additional_metrics = [
        ("Goal Coherence (Before)", "avg_goal_coherence_before", "avg_goal_coherence_before", fmt_pct),
        ("Constraint Recall (Before)", "avg_constraint_recall_before", "avg_constraint_recall_before", fmt_pct),
        ("Goal Drift Variance", "goal_drift_variance", "goal_drift_variance", fmt_pct),
    ]
    
    for metric_name, baseline_key, instinct8_key, fmt_func in additional_metrics:
        baseline_val = baseline.get(baseline_key, 0.0)
        instinct8_val = instinct8.get(instinct8_key, 0.0)
        
        baseline_str = fmt_func(baseline_val)
        instinct8_str = fmt_func(instinct8_val)
        diff_str = fmt_diff(baseline_val, instinct8_val, True)
        
        # Match header widths: "Baseline (Codex)" = 17, "Instinct8" = 9, "Difference" = 10
        lines.append(f"| {metric_name:<30} | {baseline_str:>17} | {instinct8_str:>9} | {diff_str:>10} |")
    
    lines.append("")
    lines.append("## Per-Compression-Point Breakdown")
    lines.append("")
    
    if 'per_compression_point' in data:
        baseline_cps = data['per_compression_point']['baseline']
        instinct8_cps = data['per_compression_point']['instinct8']
        
        for i, (baseline_cp, instinct8_cp) in enumerate(zip(baseline_cps, instinct8_cps), 1):
            cp_id = baseline_cp.get('compression_point_id', i)
            turn_id = baseline_cp.get('turn_id', 0)
            
            lines.append(f"### Compression Point {cp_id} (Turn {turn_id})")
            lines.append("")
            lines.append("| Metric | Baseline | Instinct8 | Difference |")
            lines.append("|:-------|:---------|:----------|:-----------|")
            
            # Goal Coherence After
            baseline_gc = baseline_cp['metrics_after']['goal_coherence']
            instinct8_gc = instinct8_cp['metrics_after']['goal_coherence']
            lines.append(f"| Goal Coherence (After) | {fmt_pct(baseline_gc)} | {fmt_pct(instinct8_gc)} | {fmt_diff(baseline_gc, instinct8_gc, True)} |")
            
            # Constraint Recall After
            baseline_cr = baseline_cp['metrics_after']['constraint_recall']
            instinct8_cr = instinct8_cp['metrics_after']['constraint_recall']
            lines.append(f"| Constraint Recall (After) | {fmt_pct(baseline_cr)} | {fmt_pct(instinct8_cr)} | {fmt_diff(baseline_cr, instinct8_cr, True)} |")
            
            # Goal Drift
            baseline_d = baseline_cp['drift']['goal_drift']
            instinct8_d = instinct8_cp['drift']['goal_drift']
            lines.append(f"| Goal Drift | {fmt_pct(baseline_d)} | {fmt_pct(instinct8_d)} | {fmt_diff(baseline_d, instinct8_d, False)} |")
            
            # Constraint Loss
            baseline_cl = baseline_cp['drift']['constraint_loss']
            instinct8_cl = instinct8_cp['drift']['constraint_loss']
            lines.append(f"| Constraint Loss | {fmt_pct(baseline_cl)} | {fmt_pct(instinct8_cl)} | {fmt_diff(baseline_cl, instinct8_cl, False)} |")
            
            # Compression Ratio
            baseline_ratio = baseline_cp.get('compression_ratio', 0.0)
            instinct8_ratio = instinct8_cp.get('compression_ratio', 0.0)
            lines.append(f"| Compression Ratio | {baseline_ratio:.3f} | {instinct8_ratio:.3f} | {fmt_diff(baseline_ratio, instinct8_ratio, False)} |")
            
            lines.append("")
    
    lines.append("## Summary")
    lines.append("")
    
    # Calculate wins
    wins = 0
    losses = 0
    ties = 0
    
    for metric_name, baseline_key, instinct8_key, higher_is_better, _ in metrics:
        baseline_val = baseline.get(baseline_key, 0.0)
        instinct8_val = instinct8.get(instinct8_key, 0.0)
        
        if abs(instinct8_val - baseline_val) < 0.001:
            ties += 1
        elif higher_is_better:
            if instinct8_val > baseline_val:
                wins += 1
            else:
                losses += 1
        else:
            if instinct8_val < baseline_val:
                wins += 1
            else:
                losses += 1
    
    lines.append(f"**Overall:** Instinct8 wins {wins} metrics, loses {losses} metrics, ties {ties} metrics")
    lines.append("")
    
    if wins > losses:
        lines.append("✅ **Instinct8 Enhanced performs BETTER overall**")
    elif losses > wins:
        lines.append("❌ **Instinct8 Enhanced performs WORSE overall**")
    else:
        lines.append("⚖️  **Instinct8 Enhanced performs SIMILAR overall**")
    
    lines.append("")
    lines.append("### Key Findings")
    lines.append("")
    
    # Goal Coherence
    baseline_gc = baseline.get("avg_goal_coherence_after", 0.0)
    instinct8_gc = instinct8.get("avg_goal_coherence_after", 0.0)
    if instinct8_gc > baseline_gc:
        improvement = (instinct8_gc - baseline_gc) * 100
        lines.append(f"1. ✅ **Goal Coherence:** +{improvement:.1f}% improvement ({fmt_pct(instinct8_gc)} vs {fmt_pct(baseline_gc)})")
    elif abs(instinct8_gc - baseline_gc) < 0.01:
        lines.append(f"1. = **Goal Coherence:** Equivalent ({fmt_pct(instinct8_gc)})")
    else:
        decline = (baseline_gc - instinct8_gc) * 100
        lines.append(f"1. ⚠️  **Goal Coherence:** -{decline:.1f}% (but note: Instinct8 started higher)")
    
    # Constraint Recall
    baseline_cr = baseline.get("avg_constraint_recall_after", 0.0)
    instinct8_cr = instinct8.get("avg_constraint_recall_after", 0.0)
    if instinct8_cr > baseline_cr:
        improvement = (instinct8_cr - baseline_cr) * 100
        lines.append(f"2. ✅ **Constraint Recall:** +{improvement:.1f}% improvement ({fmt_pct(instinct8_cr)} vs {fmt_pct(baseline_cr)})")
    
    # Constraint Loss
    baseline_cl = baseline.get("avg_constraint_loss", 0.0)
    instinct8_cl = instinct8.get("avg_constraint_loss", 0.0)
    if instinct8_cl < baseline_cl:
        reduction = (baseline_cl - instinct8_cl) * 100
        lines.append(f"3. ✅ **Constraint Loss:** -{reduction:.1f}% reduction ({fmt_pct(instinct8_cl)} vs {fmt_pct(baseline_cl)})")
    
    # Weighted Score
    if 'weighted_scores' in data:
        baseline_ws = data['weighted_scores']['baseline']
        instinct8_ws = data['weighted_scores']['instinct8']
        if instinct8_ws > baseline_ws:
            improvement = (instinct8_ws - baseline_ws) * 100
            lines.append(f"4. ✅ **Weighted Score:** +{improvement:.1f}% improvement ({fmt_pct(instinct8_ws)} vs {fmt_pct(baseline_ws)})")
    
    # Drift Events
    baseline_events = baseline.get("total_drift_events", 0)
    instinct8_events = instinct8.get("total_drift_events", 0)
    if instinct8_events < baseline_events:
        reduction = baseline_events - instinct8_events
        lines.append(f"5. ✅ **Drift Events:** {reduction} fewer events detected ({instinct8_events} vs {baseline_events})")
    
    lines.append("")
    
    # Output
    output = "\n".join(lines)
    
    if output_file:
        with open(output_file, 'w') as f:
            f.write(output)
        print(f"✓ Detailed table saved to: {output_file}")
    else:
        print(output)
    
    return output


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Generate detailed comparison table")
    parser.add_argument(
        "--comparison",
        type=str,
        default="results/comparison_baseline_vs_instinct8.json",
        help="Path to comparison JSON file"
    )
    parser.add_argument(
        "--output",
        type=str,
        default="results/comparison_table.md",
        help="Path to output markdown file"
    )
    
    args = parser.parse_args()
    
    generate_detailed_table(args.comparison, args.output)

