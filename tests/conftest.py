"""Pytest configuration and fixtures for context compression tests."""

import pytest
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


@pytest.fixture
def sample_conversation():
    """Sample conversation for testing compression strategies."""
    return [
        {"role": "user", "content": "Help me build a REST API with FastAPI."},
        {"role": "assistant", "content": "I'll help you build a FastAPI REST API. Let's start with the basic structure."},
        {"role": "user", "content": "It needs authentication with JWT tokens."},
        {"role": "assistant", "content": "I'll add JWT authentication. We'll use python-jose for token handling."},
    ]


@pytest.fixture
def sample_goal():
    """Sample goal for testing goal coherence metrics."""
    return {
        "objective": "Build a REST API with FastAPI and JWT authentication",
        "constraints": [
            "Must use FastAPI framework",
            "Must implement JWT token authentication",
            "Must follow REST best practices",
        ],
    }


@pytest.fixture
def mock_llm_response():
    """Mock LLM response for testing without API calls."""
    return {
        "content": "Here's the implementation...",
        "model": "gpt-4o-mini",
        "usage": {"prompt_tokens": 100, "completion_tokens": 50},
    }
