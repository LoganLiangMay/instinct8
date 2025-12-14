#!/usr/bin/env python3
"""Test if LLM-as-judge is correctly identifying budget constraint mentions."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from evaluation.metrics import _constraint_mentioned, _get_client

budget_constraint = "Budget: maximum $10K implementation cost"

test_responses = [
    # Response 1: Generic budget mention (no specific amount)
    "Budget: Constraints on budget impact infrastructure choices",
    
    # Response 2: Specific amount mentioned
    "We have a budget of $10,000 for implementation costs",
    
    # Response 3: Paraphrased
    "The budget is limited to 10K dollars for the project",
    
    # Response 4: Very generic
    "Budget constraints affect our choices",
    
    # Response 5: What agent might say when seeing explicit format
    "The constraints are listed in the TASK CONTEXT section above, including budget limitations",
    
    # Response 6: Mentions budget but not the amount
    "Budget is a key constraint, along with timeline and technical requirements",
]

print("=" * 80)
print("TESTING LLM-AS-JUDGE ON BUDGET CONSTRAINT")
print("=" * 80)
print(f"\nConstraint to detect: {budget_constraint}\n")

client = _get_client()

for i, response in enumerate(test_responses, 1):
    print(f"Test {i}:")
    print(f"  Response: {response[:80]}...")
    mentioned = _constraint_mentioned(budget_constraint, response, client, "gpt-4o")
    status = "✓" if mentioned else "✗"
    print(f"  Result: {status} {'Mentioned' if mentioned else 'NOT mentioned'}")
    print()

print("=" * 80)
print("ANALYSIS")
print("=" * 80)
print("\nThe LLM-as-judge requires the agent to mention:")
print("  1. Budget/cost concept")
print("  2. The specific amount ($10K or equivalent)")
print("  3. Implementation cost context")
print("\nIf the agent only says 'budget' generically without the amount,")
print("the judge will say it's NOT mentioned.")

