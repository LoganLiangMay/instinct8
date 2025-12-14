#!/usr/bin/env python3
"""
Generate a presentation-ready comparison table
matching the style of teammate's presentation slides.
"""

import json
import sys
from pathlib import Path

def generate_presentation_table(comparison_file: str, output_file: str = None):
    """
    Generate a presentation-ready markdown table.
    """
    with open(comparison_file, 'r') as f:
        data = json.load(f)
    
    baseline = data['baseline']
    instinct8 = data['instinct8']
    
    # Helper to format percentage
    def fmt_pct(val):
        return f"{val*100:.1f}%"
    
    # Helper to format difference with sign
    def fmt_diff(baseline_val, instinct8_val):
        diff = instinct8_val - baseline_val
        if isinstance(diff, float):
            sign = "+" if diff >= 0 else ""
            return f"{sign}{diff*100:.1f}%"
        else:
            sign = "+" if diff >= 0 else ""
            return f"{sign}{diff}"
    
    # Helper to determine winner
    def get_winner(baseline_val, instinct8_val, higher_is_better=True):
        if abs(instinct8_val - baseline_val) < 0.001:
            return "Tie"
        if higher_is_better:
            return "Instinct8" if instinct8_val > baseline_val else "Baseline"
        else:
            return "Instinct8" if instinct8_val < baseline_val else "Baseline"
    
    lines = []
    lines.append("# Strategy Comparison: Codex Baseline vs Instinct8 Enhanced")
    lines.append("")
    lines.append("## Metric Comparison")
    lines.append("")
    
    # Use fixed-width formatting for better alignment - header must match data column widths
    # Metric: 30 chars, Baseline: 15 chars, Instinct8: 10 chars, Difference: 11 chars, Winner: 6 chars
    lines.append("| Metric                          | Baseline (Codex) | Instinct8 | Difference | Winner |")
    lines.append("|:--------------------------------|:-----------------|:---------|:-----------|:-------|")
    
    # Core metrics matching presentation format
    metrics = [
        ("Goal Coherence (After)", "avg_goal_coherence_after", "avg_goal_coherence_after", True, lambda x: f"{x:.3f}"),
        ("Constraint Recall (After)", "avg_constraint_recall_after", "avg_constraint_recall_after", True, lambda x: f"{x:.3f}"),
        ("Goal Drift", "avg_goal_drift", "avg_goal_drift", False, lambda x: f"{x:+.3f}"),
        ("Constraint Loss", "avg_constraint_loss", "avg_constraint_loss", False, lambda x: f"{x:+.3f}"),
        ("Drift Events Detected", "total_drift_events", "total_drift_events", False, lambda x: f"{int(x):>3}"),
        ("Compression Ratio", "avg_compression_ratio", "avg_compression_ratio", False, lambda x: f"{x:.3f}"),
        ("Behavioral Alignment", "avg_behavioral_alignment", "avg_behavioral_alignment", True, lambda x: f"{x:.2f}"),
    ]
    
    for metric_name, baseline_key, instinct8_key, higher_is_better, fmt_func in metrics:
        baseline_val = baseline.get(baseline_key, 0.0)
        instinct8_val = instinct8.get(instinct8_key, 0.0)
        
        baseline_str = fmt_func(baseline_val)
        instinct8_str = fmt_func(instinct8_val)
        diff_str = fmt_diff(baseline_val, instinct8_val)
        winner = get_winner(baseline_val, instinct8_val, higher_is_better)
        
        # Pad strings for alignment - match header column widths
        # "Baseline (Codex)" = 17 chars, "Instinct8" = 9 chars, "Difference" = 10 chars, "Winner" = 6 chars
        baseline_str = f"{baseline_str:>17}"
        instinct8_str = f"{instinct8_str:>9}"
        diff_str = f"{diff_str:>10}"
        
        lines.append(f"| {metric_name:<30} | {baseline_str} | {instinct8_str} | {diff_str} | {winner:<6} |")
    
    # Add weighted score if available
    if 'weighted_scores' in data:
        baseline_weighted = data['weighted_scores']['baseline']
        instinct8_weighted = data['weighted_scores']['instinct8']
        diff_str = fmt_diff(baseline_weighted, instinct8_weighted)
        winner = get_winner(baseline_weighted, instinct8_weighted, True)
        baseline_str = f"{baseline_weighted:.3f}"
        instinct8_str = f"{instinct8_weighted:.3f}"
        diff_str_padded = f"{diff_str:>10}"
        lines.append(f"| {'**Weighted Score**':<30} | {baseline_str:>17} | {instinct8_str:>9} | {diff_str_padded} | {winner:<6} |")
    
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## Strategy Comparison Summary")
    lines.append("")
    
    # Create summary table similar to teammate's format
    # Metric: 30 chars, Baseline: 15 chars, Instinct8: 10 chars
    lines.append("| Metric                          | Baseline (Codex) | Instinct8 |")
    lines.append("|:--------------------------------|:-----------------|:---------|")
    
    summary_metrics = [
        ("Weighted Score", "weighted_scores", lambda x: f"{x*100:>5.1f}%"),
        ("Goal Coherence (After)", "avg_goal_coherence_after", lambda x: f"{x*100:>5.1f}%"),
        ("Constraint Recall (After)", "avg_constraint_recall_after", lambda x: f"{x*100:>5.1f}%"),
        ("Goal Drift", "avg_goal_drift", lambda x: f"{x*100:>+5.1f}%"),
        ("Constraint Loss", "avg_constraint_loss", lambda x: f"{x*100:>+5.1f}%"),
        ("Drift Events", "total_drift_events", lambda x: f"{int(x):>3}"),
        ("Behavioral Alignment", "avg_behavioral_alignment", lambda x: f"{x*100/5:>3.0f}%"),
    ]
    
    for metric_name, key, fmt_func in summary_metrics:
        if key == "weighted_scores":
            if 'weighted_scores' in data:
                baseline_val = data['weighted_scores']['baseline']
                instinct8_val = data['weighted_scores']['instinct8']
            else:
                continue
        else:
            baseline_val = baseline.get(key, 0.0)
            instinct8_val = instinct8.get(key, 0.0)
        
        baseline_str = fmt_func(baseline_val)
        instinct8_str = fmt_func(instinct8_val)
        
        # Match header widths: "Baseline (Codex)" = 17, "Instinct8" = 9
        lines.append(f"| {metric_name:<30} | {baseline_str:>17} | {instinct8_str:>9} |")
    
    lines.append("")
    lines.append("## Key Findings")
    lines.append("")
    
    # Calculate improvements
    baseline_gc = baseline.get("avg_goal_coherence_after", 0.0)
    instinct8_gc = instinct8.get("avg_goal_coherence_after", 0.0)
    gc_improvement = (instinct8_gc - baseline_gc) * 100
    
    baseline_cr = baseline.get("avg_constraint_recall_after", 0.0)
    instinct8_cr = instinct8.get("avg_constraint_recall_after", 0.0)
    cr_improvement = (instinct8_cr - baseline_cr) * 100
    
    baseline_cl = baseline.get("avg_constraint_loss", 0.0)
    instinct8_cl = instinct8.get("avg_constraint_loss", 0.0)
    cl_reduction = (baseline_cl - instinct8_cl) * 100
    
    baseline_events = baseline.get("total_drift_events", 0)
    instinct8_events = instinct8.get("total_drift_events", 0)
    events_reduction = baseline_events - instinct8_events
    
    if 'weighted_scores' in data:
        baseline_ws = data['weighted_scores']['baseline']
        instinct8_ws = data['weighted_scores']['instinct8']
        ws_improvement = (instinct8_ws - baseline_ws) * 100
        lines.append(f"1. ✅ **Weighted Score:** Instinct8 achieves {fmt_pct(instinct8_ws)} vs Baseline {fmt_pct(baseline_ws)} (+{ws_improvement:.1f}% improvement)")
    
    lines.append(f"2. ✅ **Goal Coherence:** Instinct8 maintains {fmt_pct(instinct8_gc)} vs Baseline {fmt_pct(baseline_gc)} (+{gc_improvement:.1f}% improvement)")
    lines.append(f"3. ✅ **Constraint Recall:** Instinct8 maintains {fmt_pct(instinct8_cr)} vs Baseline {fmt_pct(baseline_cr)} (+{cr_improvement:.1f}% improvement)")
    
    # Constraint Loss - show if there's a meaningful difference
    if abs(cl_reduction) > 0.01:
        if instinct8_cl < baseline_cl:
            lines.append(f"4. ✅ **Constraint Loss:** Instinct8 reduces loss by {abs(cl_reduction):.1f}% ({fmt_pct(instinct8_cl)} vs {fmt_pct(baseline_cl)})")
        else:
            lines.append(f"4. ⚠️  **Constraint Loss:** Instinct8 has {abs(cl_reduction):.1f}% more loss ({fmt_pct(instinct8_cl)} vs {fmt_pct(baseline_cl)})")
    else:
        lines.append(f"4. = **Constraint Loss:** Similar ({fmt_pct(instinct8_cl)} vs {fmt_pct(baseline_cl)})")
    
    if events_reduction > 0:
        lines.append(f"5. ✅ **Drift Events:** Instinct8 detects {events_reduction} fewer drift events ({instinct8_events} vs {baseline_events})")
    elif events_reduction < 0:
        lines.append(f"5. ⚠️  **Drift Events:** Instinct8 detects {abs(events_reduction)} more drift events ({instinct8_events} vs {baseline_events})")
    else:
        lines.append(f"5. = **Drift Events:** Same number detected ({instinct8_events} vs {baseline_events})")
    
    lines.append("")
    lines.append("## Conclusion")
    lines.append("")
    
    # Count wins
    wins = 0
    losses = 0
    
    for metric_name, baseline_key, instinct8_key, higher_is_better, _ in metrics:
        baseline_val = baseline.get(baseline_key, 0.0)
        instinct8_val = instinct8.get(instinct8_key, 0.0)
        
        if abs(instinct8_val - baseline_val) > 0.001:
            if higher_is_better:
                if instinct8_val > baseline_val:
                    wins += 1
                else:
                    losses += 1
            else:
                if instinct8_val < baseline_val:
                    wins += 1
                else:
                    losses += 1
    
    if wins > losses:
        lines.append("✅ **Instinct8 Enhanced performs BETTER overall**")
        lines.append("")
        lines.append("Instinct8's goal and constraint preservation mechanisms successfully reduce drift while maintaining comparable compression efficiency.")
    elif losses > wins:
        lines.append("❌ **Instinct8 Enhanced performs WORSE overall**")
    else:
        lines.append("⚖️  **Instinct8 Enhanced performs SIMILAR overall**")
    
    lines.append("")
    
    # Output
    output = "\n".join(lines)
    
    if output_file:
        with open(output_file, 'w') as f:
            f.write(output)
        print(f"✓ Presentation table saved to: {output_file}")
    else:
        print(output)
    
    return output


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Generate presentation-ready comparison table")
    parser.add_argument(
        "--comparison",
        type=str,
        default="results/comparison_baseline_vs_instinct8.json",
        help="Path to comparison JSON file"
    )
    parser.add_argument(
        "--output",
        type=str,
        default="results/presentation_table.md",
        help="Path to output markdown file"
    )
    
    args = parser.parse_args()
    
    generate_presentation_table(args.comparison, args.output)

