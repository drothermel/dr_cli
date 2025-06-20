#!/usr/bin/env python3
"""
Advanced typecheck wrapper using mypy Python API.
Supports both regular mypy and dmypy daemon mode.
"""

import os
import sys
import argparse
from mypy import api


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


def check_with_daemon(paths: list[str], retry_on_crash: bool = True) -> int:
    """Check paths using dmypy daemon."""

    # Verify daemon is running
    start_code = start_daemon()
    if start_code == 1:
        return start_code

    # Run on all paths with retries
    total_errors = 0
    for path in paths:
        print(f">> Checking: {path}")

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
            print(f"Retrying {path}...")
            restart_daemon()
            stdout, stderr, exit_code = run_dmypy_safe(cmd)

        # Print output
        if stdout.strip():
            print(stdout.strip())
        if stderr.strip():
            print(stderr.strip(), file=sys.stderr)

        if exit_code != 0:
            total_errors += 1
    return total_errors


def check_with_mypy(paths: list[str]) -> int:
    """Check paths using regular mypy (no daemon)."""
    total_errors = 0

    for path in paths:
        print(f"\nChecking {path}...")

        # Run mypy
        stdout, stderr, exit_code = api.run([path])

        # Print output
        if stdout.strip():
            print(stdout.strip())
        if stderr.strip():
            print(stderr.strip(), file=sys.stderr)

        if exit_code != 0:
            total_errors += 1

    return total_errors


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

    args = parser.parse_args()

    # Handle --stop
    if args.stop:
        print("Stopping dmypy daemon...")
        run_dmypy_safe(["stop"])
        return

    # Filter valid paths
    if args.paths:
        paths = [p for p in args.paths if os.path.exists(p)]
        if not paths:
            print("No valid paths provided", file=sys.stderr)
            sys.exit(1)
    else:
        paths = ["."]

    # Handle --restart
    if args.restart and not args.no_daemon:
        print("Restarting dmypy daemon...")
        run_dmypy_safe(["stop"])

    # Run type checking
    errors = check_with_mypy(paths) if args.no_daemon else check_with_daemon(paths)

    # Exit with error count
    sys.exit(min(errors, 1))  # Exit 1 if any errors


if __name__ == "__main__":
    main()
