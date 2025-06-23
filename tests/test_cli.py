"""Tests for typecheck CLI argument parsing and behavior."""

import pytest

from dr_cli.typecheck.cli import main


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
