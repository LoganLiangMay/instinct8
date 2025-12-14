"""
Evaluation Harness

This module provides the main evaluation loop for running compression strategies
against conversation templates and collecting metrics.

Usage:
    python -m evaluation.harness --strategy codex --template research-synthesis-001 --trials 5
"""

import json
import os
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional, Type
from pathlib import Path

from openai import OpenAI

from strategies.strategy_base import CompressionStrategy
from evaluation.metrics import MetricsCollector


@dataclass
class TrialResult:
    """Results from a single trial of a strategy on a template."""
    trial_id: int
    strategy_name: str
    template_id: str
    compression_points: List[Dict[str, Any]]
    summary: Dict[str, Any]
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "trial_id": self.trial_id,
            "strategy_name": self.strategy_name,
            "template_id": self.template_id,
            "compression_points": self.compression_points,
            "summary": self.summary,
            "timestamp": self.timestamp,
        }


@dataclass
class EvaluationResults:
    """Aggregated results from running a strategy across multiple trials."""
    strategy_name: str
    template_id: str
    num_trials: int
    trials: List[TrialResult]
    aggregate_summary: Dict[str, Any]
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "strategy": self.strategy_name,
            "template_id": self.template_id,
            "num_trials": self.num_trials,
            "trials": [t.to_dict() for t in self.trials],
            "aggregate_summary": self.aggregate_summary,
            "timestamp": self.timestamp,
        }


class MockAgent:
    """
    A mock agent for running evaluation trials.
    
    This simulates an agent with a context that can be compressed.
    It uses OpenAI to generate responses based on its current context.
    """
    
    def __init__(
        self,
        strategy: CompressionStrategy,
        system_prompt: str,
        original_goal: str,
        constraints: List[str],
        model: str = "gpt-4o",
    ):
        self.client = OpenAI()
        self.model = model
        self.strategy = strategy
        self.system_prompt = system_prompt
        self.original_goal = original_goal
        self.constraints = constraints
        
        # Initialize strategy
        self.strategy.initialize(original_goal, constraints)
        
        # Current context (list of turn dictionaries)
        self.context: List[Dict[str, Any]] = []
        
        # Track token usage (approximate)
        self.total_tokens = 0
    
    def add_turn(self, turn: Dict[str, Any]) -> None:
        """Add a turn to the conversation context."""
        self.context.append(turn)
        
        # Approximate token count
        content = turn.get("content", "")
        self.total_tokens += len(content) // 4  # ~4 chars per token
    
    def compress(self, trigger_point: int) -> str:
        """
        Compress the context using the configured strategy.
        
        Returns the compressed context string.
        """
        compressed = self.strategy.compress(self.context, trigger_point)
        
        # Reset context to just the compressed version
        old_tokens = self.total_tokens
        self.total_tokens = len(compressed) // 4
        
        # Keep compressed context as a single "summary" turn
        self.context = [{
            "id": 0,
            "role": "system",
            "content": compressed,
            "is_compression_point": False,
        }]
        
        return compressed
    
    def call(self, prompt: str) -> str:
        """
        Call the agent with a prompt and get a response.
        
        The agent responds based on its current context (which may be compressed).
        """
        # Build messages from context
        messages = []
        
        # Add context as system message
        context_text = self._format_current_context()
        
        messages.append({
            "role": "user",
            "content": f"Context:\n{context_text}\n\n---\n\nQuestion: {prompt}"
        })
        
        try:
            # Build messages with system prompt
            api_messages = []
            if self.system_prompt:
                api_messages.append({"role": "system", "content": self.system_prompt})
            api_messages.extend(messages)
            
            response = self.client.chat.completions.create(
                model=self.model,
                max_tokens=300,
                messages=api_messages,
            )
            content = response.choices[0].message.content
            return content if content else "(error: empty response)"
        except Exception as e:
            print(f"[agent] Error calling OpenAI: {e}")
            return f"(error: {e})"
    
    def _format_current_context(self) -> str:
        """Format the current context for prompting."""
        parts = []
        for turn in self.context:
            role = turn.get("role", "unknown")
            content = turn.get("content", "")
            parts.append(f"[{role}]: {content}")
        return "\n\n".join(parts)
    
    def get_token_count(self) -> int:
        """Get approximate token count of current context."""
        return self.total_tokens


def load_template(template_path: str) -> Dict[str, Any]:
    """Load a conversation template from JSON file."""
    with open(template_path, "r") as f:
        return json.load(f)


def run_single_trial(
    strategy: CompressionStrategy,
    template: Dict[str, Any],
    trial_id: int,
) -> TrialResult:
    """
    Run a single trial of a strategy on a template.
    
    Returns TrialResult with metrics at each compression point.
    """
    print(f"\n=== Trial {trial_id} ===")
    
    # Extract template info
    initial_setup = template["initial_setup"]
    original_goal = initial_setup["original_goal"]
    constraints = initial_setup["hard_constraints"]
    system_prompt = initial_setup["system_prompt"]
    turns = template["turns"]
    probing_tasks = template.get("probing_tasks", {})
    
    # Create agent with strategy
    agent = MockAgent(
        strategy=strategy,
        system_prompt=system_prompt,
        original_goal=original_goal,
        constraints=constraints,
    )
    
    # Create metrics collector
    collector = MetricsCollector(
        original_goal=original_goal,
        constraints=constraints,
    )
    
    # Run through template turns
    compression_point_counter = 0
    
    for turn in turns:
        turn_id = turn["turn_id"]
        print(f"  Turn {turn_id}...", end="")
        
        # Add turn to agent context
        agent.add_turn({
            "id": turn_id,
            "role": turn["role"],
            "content": turn["content"],
            "is_compression_point": turn.get("is_compression_point", False),
            "tool_call": turn.get("tool_call"),
            "decision": turn.get("decision"),
        })
        
        # Check if this is a compression point
        if turn.get("is_compression_point", False):
            compression_point_counter += 1
            print(f" [COMPRESSION POINT {compression_point_counter}]")
            
            # Get tokens before compression
            tokens_before = agent.get_token_count()
            
            # Probe BEFORE compression
            goal_before = agent.call(probing_tasks.get(
                "goal_probe",
                "In one sentence, what is your current goal?"
            ))
            constraints_before = agent.call(probing_tasks.get(
                "constraint_probe",
                "What constraints are you operating under?"
            ))
            
            # Compress
            agent.compress(turn_id)
            
            # Get tokens after compression
            tokens_after = agent.get_token_count()
            
            # Probe AFTER compression
            goal_after = agent.call(probing_tasks.get(
                "goal_probe",
                "In one sentence, what is your current goal?"
            ))
            constraints_after = agent.call(probing_tasks.get(
                "constraint_probe",
                "What constraints are you operating under?"
            ))
            
            # Behavioral test
            behavioral_test = probing_tasks.get("behavioral_test", {})
            behavioral_prompt = behavioral_test.get(
                "prompt",
                "What should we do next?"
            )
            behavioral_after = agent.call(behavioral_prompt)
            
            # Collect metrics
            metrics = collector.collect_at_compression_point(
                compression_point_id=compression_point_counter,
                turn_id=turn_id,
                tokens_before=tokens_before,
                tokens_after=tokens_after,
                goal_stated_before=goal_before,
                goal_stated_after=goal_after,
                constraints_stated_before=constraints_before,
                constraints_stated_after=constraints_after,
                behavioral_response_after=behavioral_after,
                behavioral_test_context=behavioral_prompt,
            )
            
            print(f"    Goal drift: {metrics.goal_drift:.2f}")
            print(f"    Constraint loss: {metrics.constraint_loss:.2f}")
            print(f"    Compression ratio: {metrics.compression_ratio:.2f}")
        else:
            print(" ok")
    
    # Get results
    results = collector.get_results()
    
    return TrialResult(
        trial_id=trial_id,
        strategy_name=strategy.name(),
        template_id=template["template_id"],
        compression_points=results["compression_points"],
        summary=results["summary"],
    )


def run_baseline_evaluation(
    template_path: str,
    num_trials: int = 5,
    output_path: str = "results/baseline_results.json",
) -> EvaluationResults:
    """
    Run baseline evaluation using Codex strategy.
    
    Args:
        template_path: Path to the conversation template JSON
        num_trials: Number of trials to run
        output_path: Path to save results
    
    Returns:
        EvaluationResults with all trials and aggregate metrics
    """
    print(f"\n{'='*60}")
    print(f"BASELINE EVALUATION")
    print(f"Strategy: Codex-Style Checkpoint (Strategy B)")
    print(f"Template: {template_path}")
    print(f"Trials: {num_trials}")
    print(f"{'='*60}")
    
    # Load template
    template = load_template(template_path)
    
    # Run trials
    trials: List[TrialResult] = []
    
    for trial_id in range(1, num_trials + 1):
        # Create fresh strategy instance for each trial
        from strategies.strategy_b_codex import StrategyB_CodexCheckpoint
        strategy = StrategyB_CodexCheckpoint(
            system_prompt=template["initial_setup"]["system_prompt"]
        )
        
        result = run_single_trial(strategy, template, trial_id)
        trials.append(result)
    
    # Calculate aggregate summary
    aggregate = _calculate_aggregate_summary(trials)
    
    # Create results
    results = EvaluationResults(
        strategy_name="Strategy B - Codex-Style Checkpoint",
        template_id=template["template_id"],
        num_trials=num_trials,
        trials=trials,
        aggregate_summary=aggregate,
    )
    
    # Save results
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(results.to_dict(), f, indent=2)
    
    print(f"\n{'='*60}")
    print(f"RESULTS SAVED TO: {output_path}")
    print(f"{'='*60}")
    
    # Print summary
    print("\nAGGREGATE SUMMARY:")
    for key, value in aggregate.items():
        if isinstance(value, float):
            print(f"  {key}: {value:.3f}")
        else:
            print(f"  {key}: {value}")
    
    return results


def _calculate_aggregate_summary(trials: List[TrialResult]) -> Dict[str, Any]:
    """Calculate aggregate statistics across all trials."""
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
    
    parser = argparse.ArgumentParser(description="Run compression strategy evaluation")
    parser.add_argument(
        "--template",
        type=str,
        default="templates/research-synthesis-001.json",
        help="Path to conversation template",
    )
    parser.add_argument(
        "--trials",
        type=int,
        default=5,
        help="Number of trials to run",
    )
    parser.add_argument(
        "--output",
        type=str,
        default="results/baseline_results.json",
        help="Path to save results",
    )
    
    args = parser.parse_args()
    
    run_baseline_evaluation(
        template_path=args.template,
        num_trials=args.trials,
        output_path=args.output,
    )

