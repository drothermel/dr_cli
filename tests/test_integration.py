"""Integration tests for complete JSONL workflow."""

import json
from pathlib import Path


from dr_cli.typecheck.formatters import JsonlFormatter
from dr_cli.typecheck.models import MypyResults


def test_jsonl_output_e2e(multi_file_results: MypyResults, tmp_path: Path) -> None:
    """Test complete JSONL workflow with sample mypy output."""
    # Create output file path
    output_file = tmp_path / "errors.jsonl"

    # Use JsonlFormatter to write results
    formatter = JsonlFormatter()
    formatter.format_results(multi_file_results, str(output_file))

    # Verify file was created
    assert output_file.exists()

    # Read and verify JSONL content
    lines = output_file.read_text().strip().split("\n")

    # Should have 2 error lines (excluding the warning)
    assert len(lines) == 2

    # Parse each line as JSON
    error_data = []
    for line in lines:
        data = json.loads(line)
        error_data.append(data)

    # Verify structure and content
    assert error_data[0]["file"] == "test.py"
    assert error_data[0]["line"] == 1
    assert error_data[0]["level"] == "error"
    assert "assignment" in error_data[0]["error_code"]

    assert error_data[1]["file"] == "other.py"
    assert error_data[1]["line"] == 10
    assert error_data[1]["level"] == "error"
    assert "name-defined" in error_data[1]["error_code"]

    # Verify line count matches errors
    assert len(lines) == multi_file_results.error_count
