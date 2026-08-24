"""Tests for the CLI entry point."""

from unittest.mock import MagicMock, patch

from feature_crew.cli import main
from feature_crew.models import CodeArtifact, Plan, Review


def test_cli_exits_without_server_url(monkeypatch) -> None:
    monkeypatch.delenv("MARVINCODE_SERVER_URL", raising=False)
    assert main(["--description", "Add a feature"]) == 1


def test_cli_prints_output_and_returns_zero_on_pass(
    monkeypatch,
    capsys,
) -> None:
    monkeypatch.setenv("MARVINCODE_SERVER_URL", "http://127.0.0.1:4097")

    plan = Plan(summary="Add a sum utility.", tasks=["Create sum function"])
    code = CodeArtifact(filename="sum.py", code="def total(xs): return sum(xs)")
    review = Review(passed=True, feedback="Looks good.")

    with patch("feature_crew.cli.Crew") as mock_crew_cls:
        mock_crew = MagicMock()
        mock_crew.run.return_value = (plan, code, review)
        mock_crew_cls.return_value = mock_crew

        result = main(["--description", "Add a sum utility"])

    assert result == 0
    captured = capsys.readouterr()
    assert "Add a sum utility" in captured.out
    assert "sum.py" in captured.out
    assert "Looks good" in captured.out
    mock_crew_cls.assert_called_once_with(model=None)


def test_cli_returns_two_on_review_failure(
    monkeypatch,
    capsys,
) -> None:
    monkeypatch.setenv("MARVINCODE_SERVER_URL", "http://127.0.0.1:4097")

    plan = Plan(summary="Add a sum utility.", tasks=["Create sum function"])
    code = CodeArtifact(filename="sum.py", code="def total(xs): return sum(xs)")
    review = Review(passed=False, feedback="Missing type hints.")

    with patch("feature_crew.cli.Crew") as mock_crew_cls:
        mock_crew = MagicMock()
        mock_crew.run.return_value = (plan, code, review)
        mock_crew_cls.return_value = mock_crew

        result = main(["--description", "Add a sum utility"])

    assert result == 2


def test_cli_accepts_server_flag(monkeypatch, capsys) -> None:
    monkeypatch.delenv("MARVINCODE_SERVER_URL", raising=False)

    plan = Plan(summary="Add a sum utility.", tasks=["Create sum function"])
    code = CodeArtifact(filename="sum.py", code="def total(xs): return sum(xs)")
    review = Review(passed=True, feedback="Looks good.")

    with patch("feature_crew.cli.Crew") as mock_crew_cls:
        mock_crew = MagicMock()
        mock_crew.run.return_value = (plan, code, review)
        mock_crew_cls.return_value = mock_crew

        result = main(
            [
                "--description",
                "Add a sum utility",
                "--server",
                "http://127.0.0.1:9999",
            ]
        )

    assert result == 0
    mock_crew_cls.assert_called_once_with(model=None)
