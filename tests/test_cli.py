"""Tests for typecheck CLI argument parsing and behavior."""

import pytest
from unittest.mock import patch, MagicMock

from dr_cli.typecheck.cli import main, check_with_daemon, check_with_mypy
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


@patch("dr_cli.typecheck.cli.api.run")
def test_check_with_mypy_returns_results(mock_api_run: MagicMock) -> None:
    """Test that check_with_mypy returns MypyResults and exit code."""
    # Mock mypy output with errors
    mock_api_run.return_value = (
        "test.py:1: error: Incompatible types [assignment]",
        "",
        1,
    )

    # Call function
    results, exit_code = check_with_mypy(["test.py"])

    # Verify results object
    assert isinstance(results, MypyResults)
    assert results.error_count == 1
    assert len(results.errors) == 1
    assert exit_code == 1

    # Test successful case
    mock_api_run.return_value = ("", "", 0)
    results, exit_code = check_with_mypy(["test.py"])

    assert isinstance(results, MypyResults)
    assert results.error_count == 0
    assert exit_code == 0


@patch("dr_cli.typecheck.cli.Path.exists")
@patch("dr_cli.typecheck.cli.check_with_mypy")
@patch("dr_cli.typecheck.cli.TextFormatter")
@patch("dr_cli.typecheck.cli.JsonlFormatter")
def test_formatter_selection(
    mock_jsonl_formatter: MagicMock,
    mock_text_formatter: MagicMock,
    mock_check_with_mypy: MagicMock,
    mock_path_exists: MagicMock,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test CLI formatter selection logic."""
    # Mock path exists to return True
    mock_path_exists.return_value = True

    # Mock check results
    mock_results = MagicMock()
    mock_check_with_mypy.return_value = (mock_results, 0)

    # Test text formatter selection (default)
    monkeypatch.setattr("sys.argv", ["typecheck", "--no-daemon", "test.py"])

    with pytest.raises(SystemExit):
        main()

    mock_text_formatter.assert_called_once()
    mock_text_formatter.return_value.format_results.assert_called_once_with(
        mock_results, None
    )

    # Reset mocks
    mock_text_formatter.reset_mock()
    mock_jsonl_formatter.reset_mock()

    # Test jsonl formatter selection
    monkeypatch.setattr(
        "sys.argv", ["typecheck", "--no-daemon", "--output-format", "jsonl", "test.py"]
    )

    with pytest.raises(SystemExit):
        main()

    mock_jsonl_formatter.assert_called_once()
    mock_jsonl_formatter.return_value.format_results.assert_called_once_with(
        mock_results, None
    )
