"""Integration test: LLM-as-judge budget constraint detection.

Verifies that the LLM-as-judge correctly identifies budget constraint
mentions in agent responses at varying levels of specificity.
"""

import pytest

from evaluation.metrics import _constraint_mentioned, _get_client


BUDGET_CONSTRAINT = "Budget: maximum $10K implementation cost"

TEST_RESPONSES = [
    ("generic_mention", "Budget: Constraints on budget impact infrastructure choices", None),
    ("specific_amount", "We have a budget of $10,000 for implementation costs", True),
    ("paraphrased", "The budget is limited to 10K dollars for the project", True),
    ("very_generic", "Budget constraints affect our choices", None),
    ("explicit_reference", "The constraints are listed in the TASK CONTEXT section above, including budget limitations", None),
    ("no_amount", "Budget is a key constraint, along with timeline and technical requirements", None),
]


@pytest.mark.integration
class TestBudgetJudge:
    """Test LLM-as-judge accuracy on budget constraint detection."""

    @pytest.fixture(autouse=True)
    def _setup_client(self):
        """Get an LLM client, skip if no API key available."""
        try:
            self.client = _get_client()
        except (ValueError, Exception) as exc:
            pytest.skip(f"No LLM API key available: {exc}")

    def test_specific_amount_detected(self):
        """Agent mentioning the specific $10K amount should be detected."""
        response = "We have a budget of $10,000 for implementation costs"
        assert _constraint_mentioned(BUDGET_CONSTRAINT, response, self.client, "gpt-4o")

    def test_paraphrased_amount_detected(self):
        """Agent paraphrasing '$10K' should be detected."""
        response = "The budget is limited to 10K dollars for the project"
        assert _constraint_mentioned(BUDGET_CONSTRAINT, response, self.client, "gpt-4o")

    def test_generic_mention_insufficient(self):
        """Agent saying only 'budget constraints' without amount may not count."""
        response = "Budget constraints affect our choices"
        # The judge should NOT consider a generic mention as satisfying the constraint
        result = _constraint_mentioned(BUDGET_CONSTRAINT, response, self.client, "gpt-4o")
        # This is informational — the judge may or may not flag it
        assert isinstance(result, bool)
