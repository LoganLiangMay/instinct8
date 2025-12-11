"""
Strategy B: Codex-Style Checkpoint

This strategy mirrors OpenAI Codex's compaction algorithm from compact.rs.

Algorithm:
1. Send conversation history + summarization prompt to LLM
2. Get summary from LLM response
3. Rebuild history as: [initial_context] + [user_messages] + [summary]
4. User messages are truncated to max 20k tokens (most recent first)

Key Characteristics:
- System prompt is preserved (part of initial_context)
- Last N user messages are kept raw
- Middle conversation is summarized
- No explicit goal protection (goals may be lost in summarization)
"""

from typing import Any, Dict, List, Optional
from anthropic import Anthropic

from .strategy_base import CompressionStrategy


# Codex's summarization prompt (from templates/compact/prompt.md)
CODEX_SUMMARIZATION_PROMPT = """You are performing a CONTEXT CHECKPOINT COMPACTION. Create a handoff summary for another LLM that will resume the task.

Include:
- Current progress and key decisions made
- Important context, constraints, or user preferences
- What remains to be done (clear next steps)
- Any critical data, examples, or references needed to continue

Be concise, structured, and focused on helping the next LLM seamlessly continue the work."""

# Codex's summary prefix (from templates/compact/summary_prefix.md)
CODEX_SUMMARY_PREFIX = """Another language model started to solve this problem and produced a summary of its thinking process. You also have access to the state of the tools that were used by that language model. Use this to build on the work that has already been done and avoid duplicating work. Here is the summary produced by the other language model, use the information in this summary to assist with your own analysis:"""

# Codex constant: max tokens for user messages in compacted history
COMPACT_USER_MESSAGE_MAX_TOKENS = 20_000

# Approximate bytes per token (from truncate.rs)
APPROX_BYTES_PER_TOKEN = 4


class StrategyB_CodexCheckpoint(CompressionStrategy):
    """
    Codex-style compression: rolling summarization with system prompt preservation.
    
    This implementation mirrors the behavior of compact.rs from OpenAI Codex.
    """
    
    def __init__(self, system_prompt: str = "", model: str = "claude-sonnet-4-20250514"):
        """
        Initialize the Codex-style strategy.
        
        Args:
            system_prompt: The system prompt to preserve across compressions
            model: Claude model to use for summarization
        """
        self.client = Anthropic()
        self.model = model
        self.system_prompt = system_prompt
        self.original_goal: Optional[str] = None
        self.constraints: List[str] = []
    
    def initialize(self, original_goal: str, constraints: List[str]) -> None:
        """
        Store initial goal and constraints.
        
        Note: Codex doesn't explicitly protect these. They're only preserved
        if the LLM includes them in its summary.
        """
        self.original_goal = original_goal
        self.constraints = constraints
        self.log(f"Initialized with goal: {original_goal}")
        self.log(f"Constraints: {constraints}")
    
    def update_goal(self, new_goal: str, rationale: str = "") -> None:
        """
        Codex doesn't track goal updates explicitly.
        
        Goal changes are just part of the conversation history and may
        or may not be captured in the summary.
        """
        self.log(f"Goal update received (not explicitly tracked): {new_goal}")
        # Codex doesn't do anything special here - goal is in conversation
    
    def compress(
        self,
        context: List[Dict[str, Any]],
        trigger_point: int,
    ) -> str:
        """
        Compress context using Codex's algorithm.
        
        Steps:
        1. Format conversation history as text
        2. Call LLM with summarization prompt
        3. Extract summary from response
        4. Rebuild context: [system_prompt] + [user_messages] + [summary]
        
        Args:
            context: List of conversation turns
            trigger_point: Which turn to compress up to
        
        Returns:
            Compressed context string
        """
        self.log(f"Compressing {len(context)} turns up to point {trigger_point}")
        
        # Get the conversation up to trigger point
        to_compress = context[:trigger_point]
        
        if not to_compress:
            self.log("Nothing to compress")
            return self._format_empty_context()
        
        # Format conversation for summarization
        conv_text = self.format_context(to_compress)
        
        # Get summary from LLM
        summary = self._summarize(conv_text)
        
        # Collect user messages (up to 20k tokens, most recent first)
        user_messages = self._collect_user_messages(to_compress)
        selected_messages = self._select_user_messages(user_messages)
        
        # Build compacted context
        compressed = self._build_compacted_context(selected_messages, summary)
        
        original_chars = len(conv_text)
        compressed_chars = len(compressed)
        self.log(f"Compressed {original_chars} chars -> {compressed_chars} chars")
        
        return compressed
    
    def name(self) -> str:
        return "Strategy B - Codex-Style Checkpoint"
    
    def _summarize(self, conv_text: str) -> str:
        """
        Call Claude to summarize the conversation.
        
        Uses Codex's exact summarization prompt.
        """
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=500,
                messages=[
                    {
                        "role": "user",
                        "content": f"{CODEX_SUMMARIZATION_PROMPT}\n\nConversation to summarize:\n\n{conv_text}"
                    }
                ]
            )
            return response.content[0].text
        except Exception as e:
            self.log(f"Summarization failed: {e}")
            return "(summarization failed)"
    
    def _collect_user_messages(self, turns: List[Dict[str, Any]]) -> List[str]:
        """
        Collect all user messages from turns.
        
        Mirrors collect_user_messages() from compact.rs.
        Filters out messages that look like previous summaries.
        """
        messages = []
        for turn in turns:
            if turn.get("role") == "user":
                content = turn.get("content", "")
                # Filter out previous summaries (same as is_summary_message in Rust)
                if not content.startswith(f"{CODEX_SUMMARY_PREFIX}\n"):
                    messages.append(content)
        return messages
    
    def _select_user_messages(self, user_messages: List[str]) -> List[str]:
        """
        Select user messages up to COMPACT_USER_MESSAGE_MAX_TOKENS.
        
        Mirrors build_compacted_history_with_limit() from compact.rs.
        Selects most recent messages first, then reverses.
        """
        selected: List[str] = []
        remaining_tokens = COMPACT_USER_MESSAGE_MAX_TOKENS
        
        # Process messages from most recent to oldest
        for message in reversed(user_messages):
            if remaining_tokens <= 0:
                break
            
            tokens = self._approx_token_count(message)
            
            if tokens <= remaining_tokens:
                selected.append(message)
                remaining_tokens -= tokens
            else:
                # Truncate this message to fit remaining budget
                truncated = self._truncate_text(message, remaining_tokens)
                selected.append(truncated)
                break
        
        # Reverse to restore chronological order
        selected.reverse()
        return selected
    
    def _approx_token_count(self, text: str) -> int:
        """
        Approximate token count using bytes/4 heuristic.
        
        Mirrors approx_token_count() from truncate.rs.
        """
        byte_len = len(text.encode('utf-8'))
        return (byte_len + APPROX_BYTES_PER_TOKEN - 1) // APPROX_BYTES_PER_TOKEN
    
    def _truncate_text(self, text: str, max_tokens: int) -> str:
        """
        Truncate text to fit within token budget.
        
        Simple truncation with marker.
        """
        max_bytes = max_tokens * APPROX_BYTES_PER_TOKEN
        if len(text.encode('utf-8')) <= max_bytes:
            return text
        
        # Truncate to approximate byte limit
        truncated = text[:max_bytes // 2]  # Keep first half
        return f"{truncated}...[truncated]"
    
    def _build_compacted_context(
        self,
        user_messages: List[str],
        summary: str,
    ) -> str:
        """
        Build the final compacted context.
        
        Structure mirrors Codex's build_compacted_history():
        1. System prompt (initial context)
        2. Selected user messages
        3. Summary with prefix
        """
        parts = []
        
        # Add system prompt if present
        if self.system_prompt:
            parts.append(f"System: {self.system_prompt}")
        
        # Add selected user messages
        if user_messages:
            parts.append("\n--- Previous User Messages ---")
            for i, msg in enumerate(user_messages, 1):
                parts.append(f"User message {i}: {msg}")
        
        # Add summary with Codex's prefix
        parts.append("\n--- Conversation Summary ---")
        parts.append(f"{CODEX_SUMMARY_PREFIX}\n\n{summary}")
        
        return "\n\n".join(parts)
    
    def _format_empty_context(self) -> str:
        """Return context when there's nothing to compress."""
        if self.system_prompt:
            return f"System: {self.system_prompt}\n\n(No previous conversation)"
        return "(No previous conversation)"


# Convenience function for quick testing
def create_codex_strategy(system_prompt: str = "") -> StrategyB_CodexCheckpoint:
    """Create a Codex-style compression strategy."""
    return StrategyB_CodexCheckpoint(system_prompt=system_prompt)

