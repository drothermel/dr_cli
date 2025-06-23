"""Tests for typecheck CLI argument parsing and behavior."""

import pytest
from unittest.mock import patch, MagicMock

from dr_cli.typecheck.cli import main, check_with_daemon
from dr_cli.typecheck.models import MypyResults


def test_cli_argument_parsing(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """Test parsing of new --output-format and --output-file arguments."""
    # Test default values
    monkeypatch.setattr("sys.argv", ["typecheck", "--stop"])
    main()

    # Test --output-format choices
    monkeypatch.setattr("sys.argv", ["typecheck", "--output-format", "text", "--stop"])
    main()

    monkeypatch.setattr("sys.argv", ["typecheck", "--output-format", "jsonl", "--stop"])
    main()

    # Test --output-file with Path
    test_file = "test_output.jsonl"
    monkeypatch.setattr("sys.argv", ["typecheck", "--output-file", test_file, "--stop"])
    main()


@patch("dr_cli.typecheck.cli.run_dmypy_safe")
@patch("dr_cli.typecheck.cli.start_daemon")
def test_check_with_daemon_returns_results(
    mock_start_daemon: MagicMock, mock_run_dmypy: MagicMock
) -> None:
    """Test that check_with_daemon returns MypyResults and exit code."""
    # Mock successful daemon start
    mock_start_daemon.return_value = 0

    # Mock dmypy output with errors
    mock_run_dmypy.return_value = (
        "test.py:1: error: Incompatible types [assignment]",
        "",
        1,
    )

    # Call function
    results, exit_code = check_with_daemon(["test.py"])

    # Verify results object
    assert isinstance(results, MypyResults)
    assert results.error_count == 1
    assert len(results.errors) == 1
    assert exit_code == 1

    # Test successful case
    mock_run_dmypy.return_value = ("", "", 0)
    results, exit_code = check_with_daemon(["test.py"])

    assert isinstance(results, MypyResults)
    assert results.error_count == 0
    assert exit_code == 0
