#!/usr/bin/env python3
"""
Hierarchical Compression Evaluation Runner

Evaluate compression strategies on their ability to preserve information
at different hierarchy levels (domain -> category -> episode).

This evaluation tests:
1. Can the agent retrieve high-level summaries? (Domain recall)
2. Can the agent retrieve category-level patterns? (Category recall)
3. Can the agent retrieve specific episode details? (Episode recall)
4. Does the agent return the right level of detail? (Retrieval precision)
5. Can the agent synthesize across hierarchy levels? (Reasoning fidelity)

Usage:
    # Quick test with default settings
    python run_hierarchical_eval.py

    # Compare compression strategies
    python run_hierarchical_eval.py --compare

    # Full evaluation with multiple runs
    python run_hierarchical_eval.py --runs 3

    # Use specific strategy
    python run_hierarchical_eval.py --strategy amem
"""

import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from evaluation.hierarchical_metrics import (
    HierarchicalMetrics,
    HierarchicalMetricsCalculator,
    load_hierarchical_template,
    format_hierarchical_report,
)

# Try to import OpenAI for direct API calls
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    print("[warning] OpenAI not available. Running in mock mode.")


STRATEGIES = {
    "amem": "A-MEM (Agentic Memory)",
    "codex": "Codex (Checkpoint Summarization)",
    "no_compression": "No Compression (Full Context)",
    "recency": "Recency Only (Last N turns)",
    "first_last": "First + Last (Primacy + Recency)",
    "sliding_window": "Sliding Window (Token-based)",
}

# Codex's summarization prompt (from compact.rs)
CODEX_SUMMARIZATION_PROMPT = """You are performing a CONTEXT CHECKPOINT COMPACTION. Create a handoff summary for another LLM that will resume the task.

Include:
- Current progress and key decisions made
- Important context, constraints, or user preferences
- What remains to be done (clear next steps)
- Any critical data, examples, or references needed to continue

Be concise, structured, and focused on helping the next LLM seamlessly continue the work."""

# Codex's summary prefix (from compact.rs)
CODEX_SUMMARY_PREFIX = """Another language model started to solve this problem and produced a summary of its thinking process. You also have access to the state of the tools that were used by that language model. Use this to build on the work that has already been done and avoid duplicating work. Here is the summary produced by the other language model, use the information in this summary to assist with your own analysis:"""

# Codex constant: max tokens for user messages in compacted history
COMPACT_USER_MESSAGE_MAX_TOKENS = 20_000
APPROX_BYTES_PER_TOKEN = 4


class SimpleOpenAIAgent:
    """Simple OpenAI-based agent for hierarchical evaluation."""

    def __init__(self, model: str = "gpt-4o-mini", strategy: str = "no_compression"):
        self.model = model
        self.strategy = strategy
        self.conversation_history: List[Dict[str, str]] = []
        self.system_prompt = ""
        self.client = OpenAI() if OPENAI_AVAILABLE else None
        self.max_context_turns = 40  # For sliding window

        # A-MEM hierarchical memory
        self.episode_summaries: List[str] = []  # Compressed episode summaries
        self.category_summaries: Dict[str, str] = {}  # Category-level summaries
        self.domain_summary: str = ""  # High-level domain summary
        self.compression_count = 0  # Track which compression point we're at

        # Codex-style compression
        self.codex_summary: str = ""  # Rolling summary from previous compressions

    def set_system_prompt(self, prompt: str) -> None:
        """Set the system prompt."""
        self.system_prompt = prompt

    def add_turn(self, role: str, content: str) -> None:
        """Add a turn to the conversation history."""
        self.conversation_history.append({"role": role, "content": content})

    def _generate_summary(self, content: str, summary_type: str) -> str:
        """Generate a summary using the LLM."""
        if not self.client:
            return f"[Summary of {summary_type}]"

        prompts = {
            "episode": """Summarize this episode of conversation into a concise paragraph.
Focus on: key decisions made, specific technical details, constraints identified, and outcomes.
Keep specific facts like names, numbers, formats, and technical choices.

Conversation:
{content}

Summary (2-3 sentences, preserve specific details):""",

            "category": """Synthesize these episode summaries into a category-level summary.
Focus on: patterns across episodes, recurring themes, key architectural decisions.

Episodes:
{content}

Category Summary (2-3 sentences):""",

            "domain": """Create a high-level domain summary from these category summaries.
Focus on: overall system architecture, main goals, critical constraints.

Categories:
{content}

Domain Summary (2-3 sentences):"""
        }

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompts[summary_type].format(content=content)}],
                max_tokens=300,
                temperature=0.0,
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"[error] Summary generation failed: {e}")
            return f"[Summary error: {e}]"

    def compress(self) -> None:
        """Apply compression strategy."""
        if self.strategy == "no_compression":
            # Keep everything
            pass
        elif self.strategy == "recency":
            # Keep only last N turns
            if len(self.conversation_history) > 20:
                self.conversation_history = self.conversation_history[-20:]
        elif self.strategy == "first_last":
            # Keep first 5 + last 15 turns
            if len(self.conversation_history) > 20:
                first = self.conversation_history[:5]
                last = self.conversation_history[-15:]
                self.conversation_history = first + last
        elif self.strategy == "sliding_window":
            # Keep last 30 turns
            if len(self.conversation_history) > 30:
                self.conversation_history = self.conversation_history[-30:]
        elif self.strategy == "amem":
            # A-MEM: Hierarchical compression with LLM-generated summaries
            self._compress_amem()
        elif self.strategy == "codex":
            # Codex: Flat checkpoint summarization
            self._compress_codex()

    def _compress_amem(self) -> None:
        """A-MEM style hierarchical compression."""
        self.compression_count += 1

        # Get the recent episode (last ~10 turns before this compression point)
        # We keep some recent context and summarize the rest
        episode_turns = self.conversation_history[-10:] if len(self.conversation_history) >= 10 else self.conversation_history

        # Format episode content for summarization
        episode_content = "\n".join([
            f"{t['role'].upper()}: {t['content']}" for t in episode_turns
        ])

        # Generate episode summary
        print(f"    [A-MEM] Generating episode {self.compression_count} summary...")
        episode_summary = self._generate_summary(episode_content, "episode")
        self.episode_summaries.append(f"Episode {self.compression_count}: {episode_summary}")

        # Every 2 episodes, create/update category summary
        if self.compression_count % 2 == 0:
            category_idx = self.compression_count // 2
            category_name = "data_processing" if category_idx == 1 else "model_training"

            # Summarize the last 2 episodes into a category
            recent_episodes = self.episode_summaries[-2:]
            category_content = "\n\n".join(recent_episodes)

            print(f"    [A-MEM] Generating category '{category_name}' summary...")
            self.category_summaries[category_name] = self._generate_summary(category_content, "category")

        # After all 4 episodes, create domain summary
        if self.compression_count == 4:
            domain_content = "\n\n".join([
                f"{name}: {summary}" for name, summary in self.category_summaries.items()
            ])
            print(f"    [A-MEM] Generating domain summary...")
            self.domain_summary = self._generate_summary(domain_content, "domain")

        # Replace old history with compressed summaries + recent turns
        self._rebuild_compressed_history()

    def _rebuild_compressed_history(self) -> None:
        """Rebuild conversation history with compressed summaries."""
        # Build hierarchical context prefix
        context_parts = []

        if self.domain_summary:
            context_parts.append(f"[DOMAIN CONTEXT]\n{self.domain_summary}")

        if self.category_summaries:
            cat_text = "\n".join([f"- {name}: {summary}" for name, summary in self.category_summaries.items()])
            context_parts.append(f"[CATEGORY CONTEXT]\n{cat_text}")

        if self.episode_summaries:
            # Only include episode summaries not yet rolled into categories
            unrolled_start = (self.compression_count // 2) * 2
            unrolled = self.episode_summaries[unrolled_start:]
            if unrolled:
                context_parts.append(f"[EPISODE CONTEXT]\n" + "\n".join(unrolled))

        # Create compressed context message
        if context_parts:
            compressed_context = "\n\n".join(context_parts)

            # Keep only last 5 turns as recent context + compressed summary
            recent_turns = self.conversation_history[-5:] if len(self.conversation_history) > 5 else []

            # Rebuild history: compressed context + recent turns
            self.conversation_history = [
                {"role": "assistant", "content": f"[Compressed Memory]\n{compressed_context}"}
            ] + recent_turns

    def _compress_codex(self) -> None:
        """Codex-style checkpoint summarization (from compact.rs).

        Algorithm:
        1. Format conversation history for summarization
        2. Call LLM with Codex's summarization prompt
        3. Collect recent user messages (up to 20k tokens)
        4. Rebuild history: [system_prompt] + [user_messages] + [summary_prefix + summary]
        """
        self.compression_count += 1
        print(f"    [Codex] Compression point {self.compression_count}...")

        if not self.conversation_history:
            return

        # Format entire conversation for summarization
        conv_text = "\n".join([
            f"{t['role'].upper()}: {t['content']}" for t in self.conversation_history
        ])

        # Include previous summary if exists (rolling compression)
        if self.codex_summary:
            conv_text = f"[Previous Summary]\n{self.codex_summary}\n\n[Recent Conversation]\n{conv_text}"

        # Generate summary using Codex's prompt
        print(f"    [Codex] Generating checkpoint summary...")
        summary = self._generate_codex_summary(conv_text)
        self.codex_summary = summary

        # Collect user messages (up to COMPACT_USER_MESSAGE_MAX_TOKENS)
        user_messages = self._collect_user_messages()
        selected_messages = self._select_user_messages_codex(user_messages)

        # Rebuild compacted history
        self._rebuild_codex_history(selected_messages, summary)

    def _generate_codex_summary(self, conv_text: str) -> str:
        """Generate summary using Codex's summarization prompt."""
        if not self.client:
            return f"[Codex summary of conversation]"

        try:
            prompt = f"{CODEX_SUMMARIZATION_PROMPT}\n\nConversation to summarize:\n\n{conv_text}"
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=500,
                temperature=0.0,
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"    [Codex] Summary generation failed: {e}")
            return f"[Summary error: {e}]"

    def _collect_user_messages(self) -> List[str]:
        """Collect all user messages from conversation history."""
        messages = []
        for turn in self.conversation_history:
            if turn.get("role") == "user":
                content = turn.get("content", "")
                # Filter out previous summaries (same as Codex's is_summary_message)
                if not content.startswith(CODEX_SUMMARY_PREFIX[:50]):
                    messages.append(content)
        return messages

    def _select_user_messages_codex(self, user_messages: List[str]) -> List[str]:
        """Select user messages up to COMPACT_USER_MESSAGE_MAX_TOKENS (most recent first)."""
        selected: List[str] = []
        remaining_tokens = COMPACT_USER_MESSAGE_MAX_TOKENS

        # Process messages from most recent to oldest
        for message in reversed(user_messages):
            if remaining_tokens <= 0:
                break

            # Approximate token count (bytes / 4)
            byte_len = len(message.encode('utf-8'))
            tokens = (byte_len + APPROX_BYTES_PER_TOKEN - 1) // APPROX_BYTES_PER_TOKEN

            if tokens <= remaining_tokens:
                selected.append(message)
                remaining_tokens -= tokens
            else:
                # Truncate to fit
                max_chars = remaining_tokens * APPROX_BYTES_PER_TOKEN
                truncated = message[:max_chars] + "...[truncated]"
                selected.append(truncated)
                break

        # Reverse to restore chronological order
        selected.reverse()
        return selected

    def _rebuild_codex_history(self, user_messages: List[str], summary: str) -> None:
        """Rebuild history in Codex's compacted format."""
        new_history = []

        # Add selected user messages
        if user_messages:
            user_context = "--- Previous User Messages ---\n" + "\n\n".join([
                f"User message {i+1}: {msg}" for i, msg in enumerate(user_messages)
            ])
            new_history.append({"role": "user", "content": user_context})

        # Add summary with Codex's prefix
        summary_content = f"--- Conversation Summary ---\n{CODEX_SUMMARY_PREFIX}\n\n{summary}"
        new_history.append({"role": "assistant", "content": summary_content})

        self.conversation_history = new_history

    def respond(self, prompt: str) -> str:
        """Generate a response to the prompt."""
        if not self.client:
            return f"[Mock response to: {prompt[:50]}...]"

        # Build messages
        messages = []
        if self.system_prompt:
            messages.append({"role": "system", "content": self.system_prompt})

        # Add conversation history
        messages.extend(self.conversation_history)

        # Add current prompt
        messages.append({"role": "user", "content": prompt})

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=500,
                temperature=0.0,
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"[error] API call failed: {e}")
            return f"[Error: {e}]"


class MockAgent:
    """Mock agent for testing without API calls."""

    def __init__(self, strategy: str = "mock"):
        self.strategy = strategy
        self.conversation_history: List[Dict[str, str]] = []

    def set_system_prompt(self, prompt: str) -> None:
        """Set the system prompt."""
        pass

    def add_turn(self, role: str, content: str) -> None:
        """Add a turn to the conversation history."""
        self.conversation_history.append({"role": role, "content": content})

    def compress(self) -> None:
        """Simulate compression (no-op for mock)."""
        pass

    def respond(self, prompt: str) -> str:
        """Generate a mock response."""
        return f"[Mock response to: {prompt[:50]}...]"


def create_agent(strategy: str, model: str = "gpt-4o-mini"):
    """Create an agent with the specified strategy."""
    if not OPENAI_AVAILABLE:
        return MockAgent(strategy)

    return SimpleOpenAIAgent(model=model, strategy=strategy)


def simulate_conversation(
    agent,
    template: Dict[str, Any],
    verbose: bool = True,
) -> Dict[str, str]:
    """
    Simulate the conversation from the template, triggering compression at markers.

    Args:
        agent: The agent to use
        template: The loaded template
        verbose: Whether to print progress

    Returns:
        Dictionary mapping probe_id/test_id to agent responses
    """
    responses = {}
    compression_points_hit = 0

    # Set system prompt from template
    system_prompt = template.get("initial_setup", {}).get("system_prompt", "")
    if hasattr(agent, "set_system_prompt"):
        agent.set_system_prompt(system_prompt)

    turns = template.get("turns", [])
    total_turns = len(turns)

    for i, turn in enumerate(turns):
        turn_id = turn.get("turn_id", i + 1)
        role = turn.get("role", "user")
        content = turn.get("content", "")

        # Add turn to agent history
        agent.add_turn(role, content)

        # Check if this is a compression point
        if turn.get("is_compression_point"):
            compression_points_hit += 1
            if verbose:
                print(f"  [Compression point {compression_points_hit} at turn {turn_id}]")
            agent.compress()

        # If this is a probe or behavioral test, get agent response
        probe_id = turn.get("probe_id")
        test_id = turn.get("test_id")

        if probe_id or test_id:
            if verbose:
                id_str = probe_id or test_id
                print(f"  Turn {turn_id}/{total_turns}: Probing ({id_str})...")

            response = agent.respond(content)

            if probe_id:
                responses[probe_id] = response
            if test_id:
                responses[test_id] = response

        elif role == "assistant":
            # For assistant turns in Phase 1, we add the template's response
            # (simulating the agent following the template)
            pass

        elif verbose and turn_id % 10 == 0:
            print(f"  Turn {turn_id}/{total_turns}...")

    return responses


def run_hierarchical_evaluation(
    strategy: str = "amem",
    model: str = "gpt-4o-mini",
    template_path: Optional[str] = None,
    output_dir: str = "results",
    verbose: bool = True,
) -> HierarchicalMetrics:
    """
    Run hierarchical compression evaluation.

    Args:
        strategy: Compression strategy to evaluate
        model: LLM model to use
        template_path: Path to template (uses default if None)
        output_dir: Directory to save results
        verbose: Whether to print progress

    Returns:
        HierarchicalMetrics with all calculated scores
    """
    # Load template
    if template_path is None:
        template_path = project_root / "templates" / "hierarchical-eval-60-turn.json"

    if verbose:
        print("\n" + "=" * 60)
        print("HIERARCHICAL COMPRESSION EVALUATION")
        print("=" * 60)
        print(f"Strategy:    {STRATEGIES.get(strategy, strategy)}")
        print(f"Model:       {model}")
        print(f"Template:    {Path(template_path).name}")
        print("=" * 60)
        print("\nLoading template...")

    template = load_hierarchical_template(str(template_path))

    if verbose:
        metadata = template.get("metadata", {})
        print(f"  Task: {metadata.get('task_type', 'unknown')}")
        print(f"  Turns: {metadata.get('num_turns', 'unknown')}")
        print(f"  Compression points: {metadata.get('num_compression_points', 'unknown')}")
        print("\nPhase 1: Building hierarchy (turns 1-40)...")

    # Create agent
    agent = create_agent(strategy, model)

    # Simulate conversation and collect probe responses
    responses = simulate_conversation(agent, template, verbose)

    if verbose:
        print(f"\nCollected {len(responses)} probe/test responses")
        print("\nPhase 3: Calculating hierarchical metrics...")

    # Calculate metrics
    calculator = HierarchicalMetricsCalculator(template)

    # Add probe results
    for probe_id, response in responses.items():
        if probe_id.startswith("domain_") or probe_id.startswith("category_") or \
           probe_id.startswith("episode_") or probe_id.startswith("reasoning_"):
            calculator.add_probe_result(probe_id, response)
        elif probe_id.startswith("decision_"):
            calculator.add_behavioral_result(probe_id, response)

    metrics = calculator.calculate()

    # Save results
    os.makedirs(output_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"hierarchical_{strategy}_{timestamp}.json"
    filepath = os.path.join(output_dir, filename)

    output = {
        "metadata": {
            "evaluation_type": "hierarchical",
            "strategy": strategy,
            "model": model,
            "template": str(template_path),
            "timestamp": timestamp,
        },
        **metrics.to_dict(),
    }

    with open(filepath, "w") as f:
        json.dump(output, f, indent=2)

    if verbose:
        print("\n" + format_hierarchical_report(metrics))
        print(f"\nResults saved to: {filepath}")

    return metrics


def run_comparison(
    strategies: Optional[List[str]] = None,
    model: str = "gpt-4o-mini",
    output_dir: str = "results",
    verbose: bool = True,
) -> Dict[str, HierarchicalMetrics]:
    """
    Compare multiple compression strategies on hierarchical evaluation.

    Args:
        strategies: List of strategies to compare (default: amem, recency, first_last)
        model: LLM model to use
        output_dir: Directory to save results
        verbose: Whether to print progress

    Returns:
        Dictionary mapping strategy name to metrics
    """
    if strategies is None:
        strategies = ["amem", "recency", "first_last"]

    if verbose:
        print("\n" + "=" * 60)
        print("HIERARCHICAL EVALUATION - STRATEGY COMPARISON")
        print("=" * 60)
        print(f"Strategies: {', '.join(strategies)}")
        print("=" * 60)

    all_metrics = {}

    for strategy in strategies:
        if verbose:
            print(f"\n--- Evaluating: {STRATEGIES.get(strategy, strategy)} ---")

        metrics = run_hierarchical_evaluation(
            strategy=strategy,
            model=model,
            output_dir=output_dir,
            verbose=verbose,
        )
        all_metrics[strategy] = metrics

    # Save comparison summary
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    summary_path = os.path.join(output_dir, f"hierarchical_comparison_{timestamp}.json")

    summary = {
        "timestamp": timestamp,
        "strategies": {
            name: {
                "weighted_score": m.weighted_score,
                "domain_recall": m.domain_recall,
                "category_recall": m.category_recall,
                "episode_recall": m.episode_recall,
                "retrieval_precision": m.retrieval_precision,
                "reasoning_fidelity": m.reasoning_fidelity,
                "hierarchy_drift": m.hierarchy_drift,
                "behavioral_alignment": m.behavioral_alignment,
            }
            for name, m in all_metrics.items()
        },
    }

    with open(summary_path, "w") as f:
        json.dump(summary, f, indent=2)

    # Print comparison table
    if verbose:
        print("\n" + "=" * 80)
        print("COMPARISON SUMMARY")
        print("=" * 80)
        print(f"{'Strategy':<20} {'Weighted':>10} {'Domain':>10} {'Category':>10} {'Episode':>10} {'Drift':>10}")
        print("-" * 80)

        for name, m in all_metrics.items():
            print(
                f"{STRATEGIES.get(name, name)[:19]:<20} "
                f"{m.weighted_score:>9.1%} "
                f"{m.domain_recall:>9.1%} "
                f"{m.category_recall:>9.1%} "
                f"{m.episode_recall:>9.1%} "
                f"{m.hierarchy_drift:>+9.1%}"
            )

        print("-" * 80)
        print(f"\nComparison saved to: {summary_path}")

        # Highlight best performer
        best = max(all_metrics.items(), key=lambda x: x[1].weighted_score)
        print(f"\nBest overall: {STRATEGIES.get(best[0], best[0])} ({best[1].weighted_score:.1%})")

        # Note hierarchy drift
        lowest_drift = min(all_metrics.items(), key=lambda x: abs(x[1].hierarchy_drift))
        print(f"Lowest hierarchy drift: {STRATEGIES.get(lowest_drift[0], lowest_drift[0])} ({lowest_drift[1].hierarchy_drift:+.1%})")

    return all_metrics


def main():
    parser = argparse.ArgumentParser(
        description="Hierarchical Compression Evaluation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_hierarchical_eval.py                    # Quick evaluation
  python run_hierarchical_eval.py --compare          # Compare strategies
  python run_hierarchical_eval.py --strategy recency # Specific strategy
  python run_hierarchical_eval.py --model gpt-4o     # Different model

This evaluation tests compression strategies on their ability to preserve
information at different hierarchy levels:
  - Domain: High-level system overview
  - Category: Mid-level patterns and decisions
  - Episode: Specific details from individual episodes

Key metrics:
  - Domain/Category/Episode Recall: What % of information is preserved at each level
  - Retrieval Precision: Does the agent return the right level of detail
  - Reasoning Fidelity: Can the agent synthesize across levels
  - Hierarchy Drift: How much worse is deeper retrieval vs. shallow
        """,
    )

    parser.add_argument(
        "--strategy", "-s",
        type=str,
        default="amem",
        choices=list(STRATEGIES.keys()),
        help="Compression strategy to evaluate",
    )
    parser.add_argument(
        "--model", "-m",
        type=str,
        default="gpt-4o-mini",
        help="Model to use (default: gpt-4o-mini)",
    )
    parser.add_argument(
        "--template", "-t",
        type=str,
        default=None,
        help="Path to template file (default: hierarchical-eval-60-turn.json)",
    )
    parser.add_argument(
        "--compare", "-c",
        action="store_true",
        help="Compare multiple strategies",
    )
    parser.add_argument(
        "--strategies",
        type=str,
        nargs="+",
        default=None,
        help="Strategies to compare (with --compare)",
    )
    parser.add_argument(
        "--output", "-o",
        type=str,
        default="results",
        help="Output directory (default: results)",
    )
    parser.add_argument(
        "--quiet", "-q",
        action="store_true",
        help="Minimal output",
    )

    args = parser.parse_args()
    verbose = not args.quiet

    if args.compare:
        run_comparison(
            strategies=args.strategies,
            model=args.model,
            output_dir=args.output,
            verbose=verbose,
        )
    else:
        run_hierarchical_evaluation(
            strategy=args.strategy,
            model=args.model,
            template_path=args.template,
            output_dir=args.output,
            verbose=verbose,
        )


if __name__ == "__main__":
    main()
