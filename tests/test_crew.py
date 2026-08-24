"""Tests for the feature crew orchestration."""

from unittest.mock import MagicMock, patch

import pytest

from feature_crew.crew import Crew
from feature_crew.models import CodeArtifact, Plan, Review


@pytest.fixture
def sample_plan() -> Plan:
    return Plan(
        summary="Add a sum utility.",
        tasks=["Create sum function", "Add docstring"],
    )


@pytest.fixture
def sample_code() -> CodeArtifact:
    return CodeArtifact(
        filename="sum_utils.py",
        code="def sum_list(values: list[int]) -> int:\n    return sum(values)\n",
    )


@pytest.fixture
def sample_review_pass() -> Review:
    return Review(passed=True, feedback="Looks good.")


def test_crew_run_returns_plan_code_review(
    sample_plan: Plan,
    sample_code: CodeArtifact,
    sample_review_pass: Review,
) -> None:
    with (
        patch("feature_crew.crew.create_planner", return_value=MagicMock()) as mock_planner,
        patch("feature_crew.crew.create_coder", return_value=MagicMock()) as mock_coder,
        patch("feature_crew.crew.create_reviewer", return_value=MagicMock()) as mock_reviewer,
    ):
        crew = Crew()
        crew.planner.invoke.return_value = sample_plan
        crew.coder.invoke.return_value = sample_code
        crew.reviewer.invoke.return_value = sample_review_pass

        plan, code, review = crew.run("Add a sum utility")

        assert plan == sample_plan
        assert code == sample_code
        assert review == sample_review_pass
        mock_planner.assert_called_once_with(None)
        mock_coder.assert_called_once_with(None)
        mock_reviewer.assert_called_once_with(None)


def test_crew_accepts_model() -> None:
    crew = Crew(model="deepseek-v4-flash")
    assert crew.model == "deepseek-v4-flash"
