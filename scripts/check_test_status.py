#!/usr/bin/env python3
"""Check status of running comparison test and show results when complete."""

import time
import json
import sys
from pathlib import Path

def check_test_status():
    """Monitor test and show results when complete."""
    results_file = Path("results/comparison_baseline_vs_instinct8.json")
    
    print("Monitoring test progress...")
    print("(Press Ctrl+C to stop monitoring)")
    
    last_size = 0
    check_count = 0
    
    while True:
        check_count += 1
        
        # Check if test process is still running
        import subprocess
        result = subprocess.run(
            ["pgrep", "-f", "compare_baseline_vs_instinct8"],
            capture_output=True,
            text=True
        )
        is_running = bool(result.stdout.strip())
        
        # Check if results file exists and has been updated
        if results_file.exists():
            current_size = results_file.stat().st_size
            if current_size != last_size:
                print(f"✓ Results file updated ({current_size} bytes)")
                last_size = current_size
                
                # Try to read and check if it's complete
                try:
                    with open(results_file) as f:
                        data = json.load(f)
                    
                    # Check if it has both baseline and instinct8 data
                    if "baseline" in data and "instinct8" in data:
                        print("\n" + "="*70)
                        print("TEST COMPLETE! Results:")
                        print("="*70)
                        
                        # Show granular metrics if available
                        if "granular_constraint_metrics" in data.get("baseline", {}):
                            print("\n✓ Granular constraint metrics included!")
                        
                        # Show summary
                        baseline = data.get("baseline", {})
                        instinct8 = data.get("instinct8", {})
                        
                        print(f"\nBaseline:")
                        print(f"  Constraint Recall: {baseline.get('avg_constraint_recall_after', 0):.1%}")
                        print(f"  Goal Coherence: {baseline.get('avg_goal_coherence_after', 0):.1%}")
                        
                        print(f"\nInstinct8:")
                        print(f"  Constraint Recall: {instinct8.get('avg_constraint_recall_after', 0):.1%}")
                        print(f"  Goal Coherence: {instinct8.get('avg_goal_coherence_after', 0):.1%}")
                        
                        print(f"\nResults saved to: {results_file}")
                        return
                except (json.JSONDecodeError, KeyError):
                    # File might be incomplete, keep waiting
                    pass
        
        if is_running:
            print(f"[{check_count}] Test still running...", end="\r")
        else:
            print(f"\n[{check_count}] Test process completed. Checking results...")
            if results_file.exists():
                try:
                    with open(results_file) as f:
                        data = json.load(f)
                    print("✓ Results file is valid JSON")
                    if "baseline" in data and "instinct8" in data:
                        print("✓ Results appear complete")
                        return
                except:
                    pass
        
        time.sleep(5)

if __name__ == "__main__":
    try:
        check_test_status()
    except KeyboardInterrupt:
        print("\n\nMonitoring stopped. Check results manually:")
        print("  cat results/comparison_baseline_vs_instinct8.json")

