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

    # Should have metadata + 2 error lines (excluding the warning)
    assert len(lines) == 3

    # First line should be metadata
    metadata = json.loads(lines[0])
    assert metadata["type"] == "metadata"
    assert metadata["error_count"] == 2

    # Parse error lines as JSON
    error_data = []
    for line in lines[1:]:  # Skip metadata line
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

    # Verify line count matches errors (metadata + errors)
    assert len(lines) == multi_file_results.error_count + 1  # +1 for metadata


def test_error_handling(tmp_path: Path) -> None:
    """Test error conditions and edge cases."""
    from dr_cli.typecheck.models import MypyResults
    from dr_cli.typecheck.formatters import JsonlFormatter

    # Test empty results
    empty_results = MypyResults(diagnostics=[], standalone_notes=[], files_checked=0)
    formatter = JsonlFormatter()

    output_file = tmp_path / "empty.jsonl"
    formatter.format_results(empty_results, str(output_file))

    # Should still create file with just metadata
    assert output_file.exists()
    content = output_file.read_text().strip()
    lines = content.split("\n") if content else []

    # Should have just metadata line
    assert len(lines) == 1
    metadata = json.loads(lines[0])
    assert metadata["error_count"] == 0

    # Test invalid file path (simulate permission error)
    import stat

    readonly_dir = tmp_path / "readonly"
    readonly_dir.mkdir()
    readonly_dir.chmod(stat.S_IRUSR | stat.S_IXUSR)  # Read and execute only

    bad_file = readonly_dir / "cannot_write.jsonl"
    # This should fall back to stdout without raising an exception
    formatter.format_results(empty_results, str(bad_file))


def test_multi_directory_jsonl(multi_file_results: MypyResults, tmp_path: Path) -> None:
    """Test JSONL output with merged results from multiple directories."""
    from dr_cli.typecheck.formatters import JsonlFormatter

    formatter = JsonlFormatter()
    output_file = tmp_path / "merged_errors.jsonl"

    # Use the multi_file_results which simulates merged results
    formatter.format_results(multi_file_results, str(output_file))

    # Verify file content
    lines = output_file.read_text().strip().split("\n")

    # Should have metadata + 2 errors (excluding warning)
    assert len(lines) == 3  # metadata + 2 errors

    # Check metadata
    metadata = json.loads(lines[0])
    assert metadata["error_count"] == 2

    # Check that we have errors from multiple files
    error_data = [json.loads(line) for line in lines[1:]]
    files_with_errors = {error["file"] for error in error_data}
    assert len(files_with_errors) == 2  # test.py and other.py
    assert "test.py" in files_with_errors
    assert "other.py" in files_with_errors
