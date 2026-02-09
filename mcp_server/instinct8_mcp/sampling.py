"""Wrapper for MCP sampling/createMessage requests.

The key insight: the MCP server never calls an LLM directly. Instead it
constructs prompts and asks the *client* (Claude Code, Cursor, etc.) to run
them through whatever model the user already has configured. This means:

  - Zero API keys needed inside instinct8
  - Zero heavy dependencies (no openai, no anthropic, no torch)
  - The user's existing billing / credentials handle everything
"""

from __future__ import annotations

import json
import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from mcp.server.session import ServerSession

logger = logging.getLogger(__name__)


async def sample_json(
    session: ServerSession,
    prompt: str,
    *,
    max_tokens: int = 2000,
    system_hint: str | None = None,
) -> dict:
    """Send a sampling request and parse the JSON response.

    Raises ``ValueError`` if the client returns non-JSON.
    """
    text = await sample_text(session, prompt, max_tokens=max_tokens, system_hint=system_hint)
    try:
        return json.loads(text)
    except json.JSONDecodeError as exc:
        # Try to extract JSON from markdown fences
        stripped = _extract_json_block(text)
        if stripped is not None:
            return json.loads(stripped)
        raise ValueError(f"Client returned non-JSON response: {text[:200]}") from exc


async def sample_text(
    session: ServerSession,
    prompt: str,
    *,
    max_tokens: int = 2000,
    system_hint: str | None = None,
) -> str:
    """Send a sampling request and return the raw text response.

    Uses MCP ``sampling/createMessage`` so the client's own model runs the
    prompt — instinct8 never makes LLM calls itself.
    """
    from mcp.types import SamplingMessage, TextContent

    messages = [
        SamplingMessage(
            role="user",
            content=TextContent(type="text", text=prompt),
        )
    ]

    logger.debug("Sending sampling request (%d chars)", len(prompt))
    result = await session.create_message(
        messages,
        max_tokens=max_tokens,
        system_prompt=system_hint,
    )

    # Extract text from the result
    if hasattr(result.content, "text"):
        return result.content.text
    # Handle list-of-content-blocks
    if isinstance(result.content, list):
        parts = [
            block.text for block in result.content if hasattr(block, "text")
        ]
        return "\n".join(parts)
    return str(result.content)


async def sample_score(
    session: ServerSession,
    prompt: str,
    *,
    max_tokens: int = 10,
) -> float:
    """Send a sampling request expecting a single numeric score back."""
    text = await sample_text(session, prompt, max_tokens=max_tokens)
    text = text.strip()
    try:
        return float(text)
    except ValueError:
        # Try to find a number in the response
        import re
        match = re.search(r"(\d+\.?\d*)", text)
        if match:
            return float(match.group(1))
        raise ValueError(f"Client returned non-numeric response: {text!r}")


def _extract_json_block(text: str) -> str | None:
    """Extract JSON from markdown code fences if present."""
    import re
    match = re.search(r"```(?:json)?\s*\n?(.*?)\n?```", text, re.DOTALL)
    if match:
        return match.group(1).strip()
    # Try bare braces
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if match:
        return match.group(0)
    return None
