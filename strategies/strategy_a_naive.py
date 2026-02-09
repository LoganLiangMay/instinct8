"""
Strategy A: Naive Summarization

This strategy represents the simplest possible compression approach:
- Always calls the LLM with a generic summarization prompt
- No goal or constraint protection
- No token budget gating
- Serves as a lower-bound baseline for comparison
"""

import os
from typing import Any, Dict, List, Optional

from .strategy_base import CompressionStrategy
from .strategy_b_codex import (
    _create_llm_client,
    LLMClient,
    OpenAISummarizer,
    AnthropicSummarizer,
)


class StrategyA_NaiveSummarization(CompressionStrategy):
    """
    Naive summarization: always compress with a generic prompt.

    This strategy intentionally does NOT protect goals or constraints,
    making it the worst-case baseline for measuring goal drift.
    """

    def __init__(
        self,
        model: Optional[str] = None,
        backend: str = "auto",
    ):
        self.client = _create_llm_client(backend=backend, model=model)
        self.original_goal: Optional[str] = None
        self.constraints: List[str] = []

    def initialize(self, original_goal: str, constraints: List[str]) -> None:
        """Store goal and constraints (but never use them in compression)."""
        self.original_goal = original_goal
        self.constraints = constraints
        self.log(f"Initialized with goal: {original_goal}")

    def update_goal(self, new_goal: str, rationale: str = "") -> None:
        """No-op: naive strategy doesn't track goal updates."""
        self.log(f"Goal update received (ignored): {new_goal}")

    def compress(
        self,
        context: List[Dict[str, Any]],
        trigger_point: int,
    ) -> str:
        """
        Compress context with a generic summarization prompt.

        Always calls the LLM regardless of context size. Does not
        inject goal or constraint information into the output.
        """
        to_compress = context[:trigger_point]

        if not to_compress:
            return "Previous conversation summary:\n(No previous conversation)"

        conv_text = self.format_context(to_compress)

        prompt = (
            "Summarize this conversation in 3-4 sentences:\n\n"
            f"{conv_text}"
        )

        try:
            summary = self.client.complete(prompt, max_tokens=500)
        except Exception as e:
            self.log(f"Summarization failed: {e}")
            summary = "(summarization failed)"

        return f"Previous conversation summary:\n{summary}"

    def name(self) -> str:
        return "Strategy A - Naive Summarization"


def create_naive_strategy(backend: str = "openai") -> StrategyA_NaiveSummarization:
    """Create a naive summarization strategy."""
    return StrategyA_NaiveSummarization(backend=backend)
