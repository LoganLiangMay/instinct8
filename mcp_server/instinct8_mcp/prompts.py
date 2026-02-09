"""MCP prompt templates for instinct8.

These are discoverable templates that clients can use directly — a fallback
integration path when MCP sampling isn't available. The user/agent can
discover these prompts and run them through their own model manually.

Two prompts:
  1. selective-salience-extract — extract goal-critical info from context
  2. protected-core-compress   — compress with Protected Core pattern
"""

from __future__ import annotations

from typing import Any


def register_prompts(mcp_server: Any) -> None:
    """Register instinct8 prompt templates on the given FastMCP server."""

    @mcp_server.prompt()
    def selective_salience_extract(
        goal: str,
        constraints: str,
        conversation: str,
    ) -> str:
        """Extract goal-critical information from a conversation.

        Use this template to identify the exact quotes from a conversation
        that are critical for preserving the agent's goal and constraints.
        The output is a JSON list of verbatim quotes.

        Args:
            goal: The task's primary goal statement.
            constraints: Comma-separated list of hard constraints.
            conversation: The full conversation text to analyze.
        """
        return (
            "You are performing selective salience extraction for context compression.\n"
            "\n"
            "From the following conversation, extract ONLY the information that will "
            "directly impact the agent's ability to achieve the user's goal.\n"
            "\n"
            f"Original Goal: {goal}\n"
            f"Constraints: {constraints}\n"
            "\n"
            "Include:\n"
            "- Explicit goals and goal changes\n"
            "- Hard constraints (must/must not)\n"
            "- Key decisions with rationales\n"
            "- Critical facts or requirements\n"
            "- Important tool outputs that affect future actions\n"
            "\n"
            "Do NOT include:\n"
            "- Conversational scaffolding\n"
            "- Redundant explanations\n"
            "- Intermediate reasoning steps\n"
            "- Off-topic tangents\n"
            "\n"
            "CRITICAL: Quote exactly — do not summarize or paraphrase. "
            "Preserve the original wording.\n"
            "\n"
            "Conversation to analyze:\n"
            f"{conversation}\n"
            "\n"
            'Output format (JSON):\n'
            '{\n'
            '  "salient_items": [\n'
            '    "exact quote 1",\n'
            '    "exact quote 2"\n'
            '  ]\n'
            '}'
        )

    @mcp_server.prompt()
    def protected_core_compress(
        goal: str,
        constraints: str,
        decisions: str,
        conversation: str,
    ) -> str:
        """Compress a conversation while preserving a Protected Core.

        Use this template to compress a long conversation into a shorter form
        that keeps the goal, constraints, and key decisions intact at the top.

        Args:
            goal: The task's primary goal statement.
            constraints: Comma-separated list of hard constraints.
            decisions: Key decisions made so far (one per line).
            conversation: The full conversation text to compress.
        """
        constraint_lines = "\n".join(
            f"  - {c.strip()}" for c in constraints.split(",") if c.strip()
        )
        decision_lines = "\n".join(
            f"  - {d.strip()}" for d in decisions.split("\n") if d.strip()
        ) if decisions.strip() else "  (none yet)"

        return (
            "You are compressing a conversation while preserving critical goal information.\n"
            "\n"
            "== PROTECTED CORE (copy this verbatim to your output) ==\n"
            "PROTECTED CORE (AUTHORITATIVE - Never forget these):\n"
            "================================================\n"
            f"Goal: {goal}\n"
            "\n"
            "Hard Constraints (MUST FOLLOW):\n"
            f"{constraint_lines}\n"
            "\n"
            "Key Decisions Made:\n"
            f"{decision_lines}\n"
            "================================================\n"
            "\n"
            "== TASK ==\n"
            "Summarize the following conversation into a concise summary. Focus on:\n"
            "- What progress has been made\n"
            "- Key decisions and their outcomes\n"
            "- Important context and information discovered\n"
            "- What remains to be done\n"
            "\n"
            "Do NOT include the goal or constraints in the summary — those are in the Protected Core above.\n"
            "Be concise and structured.\n"
            "\n"
            "Conversation to compress:\n"
            f"{conversation}\n"
            "\n"
            "Output the PROTECTED CORE block above verbatim, followed by your summary "
            "under a '--- Previous Conversation Summary ---' header."
        )
