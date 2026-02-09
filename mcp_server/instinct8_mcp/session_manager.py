"""In-memory session state management for instinct8 MCP server.

All state lives on the user's machine — nothing is sent remotely.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass
class Decision:
    """A key decision recorded during the session."""

    decision: str
    rationale: str
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class ProtectedCore:
    """Goal + constraints that are NEVER compressed, only re-asserted."""

    original_goal: str
    current_goal: str
    hard_constraints: list[str]
    key_decisions: list[Decision] = field(default_factory=list)
    timestamp_updated: str = field(default_factory=lambda: datetime.now().isoformat())

    def render(self) -> str:
        """Render the protected core as a text block for context assembly."""
        decisions_str = "\n".join(
            f"  - {d.decision} (Rationale: {d.rationale})"
            for d in self.key_decisions
        ) if self.key_decisions else "  (none yet)"

        return (
            "PROTECTED CORE (AUTHORITATIVE - Never forget these):\n"
            "================================================\n"
            f"Original Goal: {self.original_goal}\n"
            f"Current Goal: {self.current_goal}\n"
            "\n"
            "Hard Constraints (MUST FOLLOW):\n"
            + "\n".join(f"  - {c}" for c in self.hard_constraints)
            + "\n\n"
            "Key Decisions Made:\n"
            f"{decisions_str}\n"
            "\n"
            f"Last Updated: {self.timestamp_updated}\n"
            "================================================\n"
            "\n"
            "INSTRUCTION: Always prioritize the CURRENT GOAL and HARD CONSTRAINTS above all else.\n"
            "If there's any ambiguity, refer back to this Protected Core as the source of truth."
        )


@dataclass
class SessionState:
    """Complete session state — lives entirely in-memory on user's machine."""

    protected_core: ProtectedCore
    salience_set: list[str] = field(default_factory=list)
    compression_count: int = 0
    total_tokens_saved: int = 0
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> dict[str, Any]:
        """Serialize session state for the session://current resource."""
        return {
            "protected_core": {
                "original_goal": self.protected_core.original_goal,
                "current_goal": self.protected_core.current_goal,
                "hard_constraints": self.protected_core.hard_constraints,
                "key_decisions": [
                    {"decision": d.decision, "rationale": d.rationale, "timestamp": d.timestamp}
                    for d in self.protected_core.key_decisions
                ],
            },
            "salience_set": self.salience_set,
            "compression_count": self.compression_count,
            "total_tokens_saved": self.total_tokens_saved,
            "created_at": self.created_at,
        }


class SessionManager:
    """Manages session lifecycle. One active session at a time."""

    def __init__(self) -> None:
        self._session: SessionState | None = None

    @property
    def session(self) -> SessionState | None:
        return self._session

    @property
    def has_session(self) -> bool:
        return self._session is not None

    def initialize(self, goal: str, constraints: list[str]) -> SessionState:
        """Create a new session with the given goal and constraints."""
        core = ProtectedCore(
            original_goal=goal,
            current_goal=goal,
            hard_constraints=list(constraints),
        )
        self._session = SessionState(protected_core=core)
        return self._session

    def require_session(self) -> SessionState:
        """Return active session or raise."""
        if self._session is None:
            raise ValueError(
                "No active session. Call initialize_session first."
            )
        return self._session

    def update_goal(self, new_goal: str, rationale: str = "") -> None:
        """Update the current goal in the protected core."""
        session = self.require_session()
        session.protected_core.key_decisions.append(
            Decision(
                decision=f"Goal updated to: {new_goal}",
                rationale=rationale or "Goal evolution during task execution",
            )
        )
        session.protected_core.current_goal = new_goal
        session.protected_core.timestamp_updated = datetime.now().isoformat()

    def add_decision(self, decision: str, rationale: str) -> None:
        """Record a key decision in the protected core."""
        session = self.require_session()
        session.protected_core.key_decisions.append(
            Decision(decision=decision, rationale=rationale)
        )

    def update_salience(self, items: list[str]) -> None:
        """Replace the salience set with a new deduplicated set."""
        session = self.require_session()
        session.salience_set = items

    def record_compression(self, tokens_saved: int) -> None:
        """Record that a compression occurred."""
        session = self.require_session()
        session.compression_count += 1
        session.total_tokens_saved += tokens_saved

    def reset(self) -> None:
        """Destroy the current session."""
        self._session = None
