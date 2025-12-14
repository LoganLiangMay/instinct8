#!/usr/bin/env python3
"""Test if granular metrics are being collected."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from evaluation.metrics import MetricsCollector
from evaluation.harness import load_template

template = load_template('templates/research-synthesis-001.json')
constraints = template['initial_setup']['hard_constraints']

collector = MetricsCollector(
    original_goal=template['initial_setup']['original_goal'],
    constraints=constraints,
    use_granular_metrics=True
)

# Simulate a compression point
constraints_before = 'We have a budget of $10K and need to finish in 2 weeks'
constraints_after = 'Budget is $10K, timeline is 2 weeks, need WebSockets and PostgreSQL'

metrics = collector.collect_at_compression_point(
    compression_point_id=1,
    turn_id=5,
    tokens_before=1000,
    tokens_after=500,
    goal_stated_before='Research frameworks',
    goal_stated_after='Research frameworks',
    constraints_stated_before=constraints_before,
    constraints_stated_after=constraints_after,
)

results = collector.get_results()
print(f'Results has granular_constraint_metrics: {"granular_constraint_metrics" in results}')
if 'granular_constraint_metrics' in results:
    granular = results['granular_constraint_metrics']
    print(f'  Keys: {list(granular.keys())}')
    print(f'  After metrics count: {len(granular.get("after", []))}')
    if granular.get('after'):
        print(f'  First CP keys: {list(granular["after"][0].keys())[:5]}')
else:
    print('  Checking collector attributes...')
    print(f'  Has granular_metrics_before: {hasattr(collector, "granular_metrics_before")}')
    if hasattr(collector, 'granular_metrics_before'):
        print(f'    Length: {len(collector.granular_metrics_before)}')
        if collector.granular_metrics_before:
            print(f'    First item type: {type(collector.granular_metrics_before[0])}')

