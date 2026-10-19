#!/usr/bin/env python3
"""
check_repo_clean.py — CI gate: fail if forbidden file types are tracked by Git.

Usage:
    python scripts/check_repo_clean.py

Exit codes:
    0 — no forbidden files found
    1 — one or more forbidden files are tracked (CI should block the build)

Add to CI (GitHub Actions example):
    - name: Check repo for sensitive files
      run: python scripts/check_repo_clean.py
"""

import subprocess
import sys

# Patterns that must never be tracked in Git.
# Extend this list as the project grows.
FORBIDDEN_PATTERNS = [
    ".sql",
    ".dump",
    ".pem",
    ".key",
    ".crt",
    ".p12",
    ".pfx",
    ".pdf",
    ".env",
]

# Allowed exceptions (exact filenames that may look like forbidden but are safe).
ALLOWED_EXCEPTIONS = {
    ".env.example",
}


def get_tracked_files() -> list[str]:
    """Return all files currently tracked by Git."""
    result = subprocess.run(
        ["git", "ls-files"],
        capture_output=True,
        text=True,
        check=True,
    )
    return result.stdout.splitlines()


def check_for_forbidden(tracked_files: list[str]) -> list[str]:
    """Return a list of tracked files that match forbidden patterns."""
    violations = []
    for filepath in tracked_files:
        # Skip allowed exceptions
        filename = filepath.split("/")[-1]
        if filename in ALLOWED_EXCEPTIONS:
            continue
        for pattern in FORBIDDEN_PATTERNS:
            if filepath.endswith(pattern):
                violations.append(filepath)
                break
    return violations


def main() -> int:
    try:
        tracked = get_tracked_files()
    except subprocess.CalledProcessError as exc:
        print(f"ERROR: could not run `git ls-files`: {exc}", file=sys.stderr)
        return 1

    violations = check_for_forbidden(tracked)

    if violations:
        print("=" * 60, file=sys.stderr)
        print("FAIL: Forbidden file types found in Git tracking!", file=sys.stderr)
        print("Remove them with: git rm --cached <file>", file=sys.stderr)
        print("=" * 60, file=sys.stderr)
        for v in violations:
            print(f"  TRACKED: {v}", file=sys.stderr)
        print(file=sys.stderr)
        print(
            f"Found {len(violations)} violation(s). "
            "Update .gitignore and run `git rm --cached` to fix.",
            file=sys.stderr,
        )
        return 1

    print(f"OK: No forbidden file types found in {len(tracked)} tracked files.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
