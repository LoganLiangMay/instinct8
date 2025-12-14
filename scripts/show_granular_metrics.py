#!/usr/bin/env python3
"""Display granular constraint metrics from comparison results."""

import json
import sys
from pathlib import Path

def show_granular_metrics(results_file: str = "results/comparison_baseline_vs_instinct8.json"):
    """Display granular constraint metrics from results."""
    
    # Load individual trial results
    baseline_file = Path("results/baseline_codex_8k_results.json")
    instinct8_file = Path("results/instinct8_8k_results.json")
    
    if not baseline_file.exists() or not instinct8_file.exists():
        print(f"Error: Results files not found")
        print(f"  Baseline: {baseline_file} {'exists' if baseline_file.exists() else 'missing'}")
        print(f"  Instinct8: {instinct8_file} {'exists' if instinct8_file.exists() else 'missing'}")
        return
    
    with open(baseline_file) as f:
        baseline_data = json.load(f)
    with open(instinct8_file) as f:
        instinct8_data = json.load(f)
    
    baseline_trial = baseline_data['trials'][0]
    instinct8_trial = instinct8_data['trials'][0]
    
    print("=" * 80)
    print("GRANULAR CONSTRAINT METRICS - Category Breakdown")
    print("=" * 80)
    
    # Check if granular metrics exist
    baseline_granular = baseline_trial.get('granular_constraint_metrics')
    instinct8_granular = instinct8_trial.get('granular_constraint_metrics')
    
    if not baseline_granular or not instinct8_granular:
        print("\n⚠ Granular metrics not found in results")
        print("  Make sure to run with use_granular_metrics=True")
        return
    
    # Aggregate across all compression points
    def aggregate_granular(granular_data):
        """Aggregate granular metrics across compression points."""
        if not granular_data or 'after' not in granular_data:
            return None
        
        after_metrics = granular_data['after']
        if not after_metrics:
            return None
        
        # Average across compression points
        categories = ['budget', 'timeline', 'technical', 'team', 'compliance', 'performance', 'other']
        category_totals = {cat: [] for cat in categories}
        overall_totals = []
        weighted_totals = []
        
        for cp_metrics in after_metrics:
            if 'category_recall' in cp_metrics:
                for cat in categories:
                    if cat in cp_metrics['category_recall']:
                        category_totals[cat].append(cp_metrics['category_recall'][cat])
                if 'overall_recall' in cp_metrics:
                    overall_totals.append(cp_metrics['overall_recall'])
                if 'weighted_score' in cp_metrics:
                    weighted_totals.append(cp_metrics['weighted_score'])
        
        # Calculate averages
        result = {}
        for cat in categories:
            if category_totals[cat]:
                result[cat] = sum(category_totals[cat]) / len(category_totals[cat])
            else:
                result[cat] = 1.0  # No constraints in this category
        
        if overall_totals:
            result['overall'] = sum(overall_totals) / len(overall_totals)
        if weighted_totals:
            result['weighted'] = sum(weighted_totals) / len(weighted_totals)
        
        return result
    
    baseline_agg = aggregate_granular(baseline_granular)
    instinct8_agg = aggregate_granular(instinct8_granular)
    
    if not baseline_agg or not instinct8_agg:
        print("\n⚠ Could not aggregate granular metrics")
        return
    
    print("\nOVERALL CONSTRAINT RECALL:")
    print(f"  Baseline:  {baseline_agg.get('overall', 0):.1%}")
    print(f"  Instinct8: {instinct8_agg.get('overall', 0):.1%}")
    print(f"  Improvement: {(instinct8_agg.get('overall', 0) - baseline_agg.get('overall', 0))*100:+.1f}%")
    
    print("\n" + "=" * 80)
    print("RECALL BY CONSTRAINT CATEGORY (After Compression):")
    print("=" * 80)
    print(f"{'Category':<15} {'Baseline':<12} {'Instinct8':<12} {'Difference':<12} {'Winner':<10}")
    print("-" * 80)
    
    categories = ['budget', 'timeline', 'technical', 'team', 'compliance', 'performance', 'other']
    category_names = {
        'budget': 'Budget',
        'timeline': 'Timeline',
        'technical': 'Technical',
        'team': 'Team',
        'compliance': 'Compliance',
        'performance': 'Performance',
        'other': 'Other',
    }
    
    for cat in categories:
        baseline_score = baseline_agg.get(cat, 1.0)
        instinct8_score = instinct8_agg.get(cat, 1.0)
        diff = instinct8_score - baseline_score
        winner = "Instinct8" if diff > 0.01 else ("Baseline" if diff < -0.01 else "Tie")
        
        print(f"{category_names[cat]:<15} {baseline_score:>10.1%} {instinct8_score:>10.1%} {diff:>+10.1%} {winner:<10}")
    
    print("\n" + "=" * 80)
    print("WEIGHTED SCORES (Favoring Critical Categories):")
    print("=" * 80)
    baseline_weighted = baseline_agg.get('weighted', 0)
    instinct8_weighted = instinct8_agg.get('weighted', 0)
    print(f"  Baseline:  {baseline_weighted:.1%}")
    print(f"  Instinct8: {instinct8_weighted:.1%}")
    print(f"  Improvement: {(instinct8_weighted - baseline_weighted)*100:+.1f}%")
    
    print("\n" + "=" * 80)

if __name__ == "__main__":
    results_file = sys.argv[1] if len(sys.argv) > 1 else "results/comparison_baseline_vs_instinct8.json"
    show_granular_metrics(results_file)

