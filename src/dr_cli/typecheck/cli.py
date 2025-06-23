#!/usr/bin/env python3
"""Advanced typecheck wrapper using mypy Python API.

Supports both regular mypy and dmypy daemon mode.
"""

import sys
import argparse
from pathlib import Path
from mypy import api
from .parser import MypyOutputParser
from .models import MypyResults


def run_dmypy_safe(args: list[str]) -> tuple[str, str, int]:
    """Run dmypy command safely, handling import errors."""
    try:
        return api.run_dmypy(args)
    except ImportError:
        print(
            "Error: dmypy not available. Install mypy to use daemon mode.",
            file=sys.stderr,
        )
        sys.exit(1)


def start_daemon() -> int:
    """Start dmypy daemon if not already running."""
    # Check daemon status
    _, _, status_code = run_dmypy_safe(["status"])

    if status_code != 0:
        print("Starting dmypy daemon...")
        stdout, stderr, code = run_dmypy_safe(["start"])
        if code != 0:
            print(f"Failed to start daemon: {stderr}", file=sys.stderr)
            return 1
    return 0


def restart_daemon() -> None:
    """Restart dmypy daemon by stopping and starting it."""
    print("Daemon crashed! Restarting...")
    run_dmypy_safe(["stop"])
    run_dmypy_safe(["start"])


def check_with_daemon(
    paths: list[str], retry_on_crash: bool = True, combined: bool = False
) -> int:
    """Check paths using dmypy daemon."""
    # Verify daemon is running
    start_code = start_daemon()
    if start_code == 1:
        return start_code

    if combined:
        # Collect outputs from each path
        outputs = []

        for path in paths:
            # Build command
            cmd = ["check"]
            if path != ".":
                cmd.extend(["--", path])
            else:
                cmd.append(".")

            # Run check
            stdout, stderr, exit_code = run_dmypy_safe(cmd)

            # Handle crashes
            if retry_on_crash and (
                "Daemon crashed" in stdout + stderr or "KeyError" in stdout + stderr
            ):
                restart_daemon()
                stdout, stderr, exit_code = run_dmypy_safe(cmd)

            # Collect output
            if stdout.strip():
                outputs.append(stdout.strip())

        # Parse and merge all outputs
        parser = MypyOutputParser()
        results_list = [parser.parse_output(output) for output in outputs]
        merged = MypyResults.merge(results_list)

        # Print combined output
        for diag in merged.diagnostics:
            level = diag.level.value
            loc = diag.location
            code = f" [{diag.error_code}]" if diag.error_code else ""
            col = f":{loc.column}" if loc.column else ""
            print(f"{loc.file}:{loc.line}{col}: {level}: {diag.message}{code}")
            for note in diag.notes:
                print(f"  note: {note}")

        # Print summary
        print(merged.format_summary())

        return 1 if merged.error_count > 0 else 0
    else:
        # Original behavior - run on all paths at once
        cmd = ["check"]
        if paths != ["."]:
            cmd.extend(["--", *paths])
        else:
            cmd.append(".")

        # Run check
        stdout, stderr, exit_code = run_dmypy_safe(cmd)

        # Handle crashes
        if retry_on_crash and (
            "Daemon crashed" in stdout + stderr or "KeyError" in stdout + stderr
        ):
            print("Retrying after daemon crash...")
            restart_daemon()
            stdout, stderr, exit_code = run_dmypy_safe(cmd)

        # Print output
        if stdout.strip():
            print(stdout.strip())
        if stderr.strip():
            print(stderr.strip(), file=sys.stderr)

        return 1 if exit_code != 0 else 0


def check_with_mypy(paths: list[str], combined: bool = False) -> int:
    """Check paths using regular mypy (no daemon)."""
    if combined:
        # Collect outputs from each path
        outputs = []

        for path in paths:
            # Run mypy
            stdout, stderr, exit_code = api.run([path])

            # Collect output
            if stdout.strip():
                outputs.append(stdout.strip())

        # Parse and merge all outputs
        parser = MypyOutputParser()
        results_list = [parser.parse_output(output) for output in outputs]
        merged = MypyResults.merge(results_list)

        # Print combined output
        for diag in merged.diagnostics:
            level = diag.level.value
            loc = diag.location
            code = f" [{diag.error_code}]" if diag.error_code else ""
            col = f":{loc.column}" if loc.column else ""
            print(f"{loc.file}:{loc.line}{col}: {level}: {diag.message}{code}")
            for note in diag.notes:
                print(f"  note: {note}")

        # Print summary
        print(merged.format_summary())

        return 1 if merged.error_count > 0 else 0
    else:
        # Original behavior - run on all paths at once
        stdout, stderr, exit_code = api.run(paths)

        # Print output
        if stdout.strip():
            print(stdout.strip())
        if stderr.strip():
            print(stderr.strip(), file=sys.stderr)

        return 1 if exit_code != 0 else 0


def main() -> None:
    """Run the typecheck script."""
    parser = argparse.ArgumentParser(description="Type check Python files with mypy")
    parser.add_argument(
        "paths", nargs="*", help="Paths to check (default: current directory)"
    )
    parser.add_argument(
        "--no-daemon", action="store_true", help="Use regular mypy instead of dmypy"
    )
    parser.add_argument(
        "--restart", action="store_true", help="Restart daemon before checking"
    )
    parser.add_argument("--stop", action="store_true", help="Stop daemon and exit")
    parser.add_argument(
        "--combined",
        action="store_true",
        help="Run each directory separately and combine results "
        "(default: True for multiple paths)",
    )
    parser.add_argument(
        "--no-combined",
        action="store_true",
        help="Disable combined mode even with multiple paths",
    )
    parser.add_argument(
        "--output-format",
        choices=["text", "jsonl"],
        default="text",
        help="Output format (default: text)",
    )
    parser.add_argument(
        "--output-file",
        type=Path,
        help="File to write output (JSONL format only)",
    )

    args = parser.parse_args()

    # Handle --stop
    if args.stop:
        print("Stopping dmypy daemon...")
        run_dmypy_safe(["stop"])
        return

    # Filter valid paths
    if args.paths:
        paths = [p for p in args.paths if Path(p).exists()]
        if not paths:
            print("No valid paths provided", file=sys.stderr)
            sys.exit(1)
    else:
        paths = ["."]

    # Handle --restart
    if args.restart and not args.no_daemon:
        print("Restarting dmypy daemon...")
        run_dmypy_safe(["stop"])

    # Determine if we should use combined mode
    # Default to combined when multiple paths provided
    combined = args.combined or (len(paths) > 1 and not args.no_combined)

    # Run type checking
    if args.no_daemon:
        errors = check_with_mypy(paths, combined=combined)
    else:
        errors = check_with_daemon(paths, combined=combined)

    # Exit with error count
    sys.exit(min(errors, 1))  # Exit 1 if any errors


if __name__ == "__main__":
    main()
