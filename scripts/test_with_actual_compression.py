#!/usr/bin/env python3
"""Test with actual compression triggered to see what agent says."""

import sys
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from strategies.strategy_b_codex import StrategyB_CodexCheckpoint
from evaluation.harness import MockAgent, load_template
from evaluation.metrics import _constraint_mentioned, _get_client
from evaluation.token_budget import BUDGET_8K, estimate_tokens

def test_with_compression():
    """Force compression to trigger and see agent response."""
    
    template_path = "templates/research-synthesis-008-8k-4compactions-realistic.json"
    template = load_template(template_path)
    
    original_goal = template["initial_setup"]["original_goal"]
    constraints = template["initial_setup"]["hard_constraints"]
    system_prompt = template["initial_setup"]["system_prompt"]
    budget_constraint = "Budget: maximum $10K implementation cost"
    
    print("=" * 80)
    print("TESTING WITH ACTUAL COMPRESSION TRIGGERED")
    print("=" * 80)
    
    # Find CP1
    turns = template["turns"]
    cp1_turn = None
    turns_before_cp1 = []
    
    for turn in turns:
        if turn.get("is_compression_point", False) and cp1_turn is None:
            cp1_turn = turn
            break
        turns_before_cp1.append(turn)
    
    # Build enough context to trigger compression
    strategy = StrategyB_CodexCheckpoint(
        system_prompt=system_prompt,
        backend="openai",
        token_budget=BUDGET_8K,
        use_goal_preservation=True
    )
    strategy.initialize(original_goal, constraints)
    
    agent = MockAgent(
        strategy=strategy,
        system_prompt=system_prompt,
        original_goal=original_goal,
        constraints=constraints,
        model="gpt-4o"
    )
    
    # Build context
    print("Building context...")
    for turn in turns_before_cp1:
        agent.add_turn({
            "id": turn["turn_id"],
            "role": turn["role"],
            "content": turn["content"],
        })
    
    # Check if compression will trigger
    context_before = agent.context
    reconstructed = strategy.render_reconstructed_prompt(context_before)
    estimated_tokens = estimate_tokens(reconstructed)
    trigger_threshold = BUDGET_8K.trigger_tokens
    
    print(f"\nToken check:")
    print(f"  Estimated tokens: {estimated_tokens}")
    print(f"  Trigger threshold: {trigger_threshold}")
    print(f"  Will compress: {estimated_tokens >= trigger_threshold}")
    
    if estimated_tokens < trigger_threshold:
        print(f"\n⚠ Not enough tokens to trigger compression!")
        print(f"   Need {trigger_threshold - estimated_tokens} more tokens")
        print(f"   This matches the diagnostic issue")
        return
    
    # Probe BEFORE
    constraint_probe = "What constraints are you operating under for this project?"
    constraints_before = agent.call(constraint_probe)
    
    client = _get_client()
    budget_before = _constraint_mentioned(budget_constraint, constraints_before, client, "gpt-4o")
    
    print(f"\nBEFORE compression:")
    print(f"  Budget mentioned: {budget_before}")
    
    # COMPRESS (should trigger)
    print(f"\nCompressing (should trigger)...")
    agent.compress(cp1_turn["turn_id"])
    
    # Check compressed context
    compressed = agent.context[0]["content"] if agent.context else ""
    has_task_context = "--- TASK CONTEXT" in compressed
    has_budget = "Budget: maximum $10K" in compressed or "$10K" in compressed
    
    print(f"\nCompressed context check:")
    print(f"  Has TASK CONTEXT: {has_task_context}")
    print(f"  Has budget constraint: {has_budget}")
    
    if has_task_context:
        start = compressed.find("--- TASK CONTEXT")
        end = compressed.find("---", start + 20)
        if end > start:
            task_section = compressed[start:min(start+400, end+3)]
            print(f"\nTASK CONTEXT section:")
            print("-" * 80)
            print(task_section)
            print("-" * 80)
    
    # Probe AFTER
    constraints_after = agent.call(constraint_probe)
    budget_after = _constraint_mentioned(budget_constraint, constraints_after, client, "gpt-4o")
    
    print(f"\nAFTER compression:")
    print(f"  Budget mentioned: {budget_after}")
    print(f"\nFull agent response:")
    print("-" * 80)
    print(constraints_after)
    print("-" * 80)
    
    # Analyze
    print(f"\n{'='*80}")
    print("ANALYSIS")
    print(f"{'='*80}")
    
    if has_task_context and not budget_after:
        print("\n⚠ ISSUE IDENTIFIED:")
        print("  - Budget constraint IS in TASK CONTEXT section")
        print("  - But agent response does NOT mention it")
        print("\n  Possible reasons:")
        print("  1. Agent sees explicit format and thinks it's 'already stated'")
        print("  2. Agent response style changes when seeing AUTHORITATIVE section")
        print("  3. Agent focuses on other constraints not in explicit format")
        
        # Check what agent actually said about budget
        budget_keywords = ["budget", "$10", "10K", "10,000", "cost"]
        found = [kw for kw in budget_keywords if kw.lower() in constraints_after.lower()]
        if found:
            print(f"\n  BUT: Budget keywords found: {found}")
            print("  This suggests agent DID mention budget, but not in the")
            print("  specific format the LLM-as-judge expects")
        else:
            print("\n  Agent truly didn't mention budget at all")
            print("  This confirms the 'already stated' hypothesis")
    
    elif has_task_context and budget_after:
        print("\n✓ Budget constraint IS mentioned")
        print("  This suggests the issue might be intermittent or context-dependent")

if __name__ == "__main__":
    if not os.environ.get("OPENAI_API_KEY"):
        print("ERROR: OPENAI_API_KEY not set")
        sys.exit(1)
    
    test_with_compression()
