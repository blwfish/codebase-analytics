#!/usr/bin/env python3
"""
count_code.py - Analyze codebase across projects (current-tree snapshot).

Counts source code and test code separately, excluding dependencies, build
artifacts, and version control directories. Uses the shared engine in
codecount.py so this stays in sync with growth_analysis.py's historical
counts by construction.

Usage:
    ./count_code.sh [--project PROJECT_NAME] [--root ROOT_DIR]
"""

import argparse
import subprocess
from pathlib import Path

import codecount


def main() -> None:
    parser = argparse.ArgumentParser(description="Analyze codebase across projects")
    parser.add_argument("--project", default=None, help="Limit to a single project")
    parser.add_argument("--root", default=str(codecount.ROOT), help="Root directory to analyze")
    args = parser.parse_args()

    root_dir = Path(args.root)

    print("Analyzing code in:", args.root)
    print()
    print("PROJECT                        |   SOURCE |    TESTS |    TOTAL")
    print("-------------------------------|----------|----------|---------")

    total_src = 0
    total_tst = 0

    for name in codecount.PROJECTS:
        if args.project and name != args.project:
            continue

        proj_path = root_dir / name
        if not proj_path.is_dir():
            continue

        counts = codecount.count_tree(proj_path)
        src, tst = counts["prod"], counts["test"]
        total = src + tst

        if total > 0:
            print(f"{name:<30} | {src:>8} | {tst:>8} | {total:>8}")
            total_src += src
            total_tst += tst

    print("-------------------------------|----------|----------|---------")
    grand = total_src + total_tst
    print(f"{'TOTAL':<30} | {total_src:>8} | {total_tst:>8} | {grand:>8}")


if __name__ == "__main__":
    print(subprocess.run(["date"], capture_output=True, text=True).stdout, end="")
    main()
