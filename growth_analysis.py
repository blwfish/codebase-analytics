#!/usr/bin/env python3
"""
growth_analysis.py - Measure code growth over time across all project repos.

For each repo, for each sample date, extracts the codebase at that point in
git history (using git archive — non-destructive, doesn't touch working trees)
and counts production vs test lines of code. Uses the shared counting engine
in codecount.py so this stays in sync with count_code.py's current-tree
snapshot by construction.

Output: CSV suitable for charting and paper analysis.

Usage:
    python3 growth_analysis.py [--output results.csv] [--dates 2025-11-17,2026-01-01,...]
"""

import argparse
import csv
from pathlib import Path

import codecount

# Sample dates — first of each month since Claude install, plus start and today
DEFAULT_DATES = [
    "2025-11-17",   # Claude install date
    "2025-12-01",
    "2026-01-01",
    "2026-02-01",
    "2026-03-01",
    "2026-03-10",
    "2026-04-01",
    "2026-04-07",   # current
]

# ---------------------------------------------------------------------------
# Main analysis
# ---------------------------------------------------------------------------

def zero_row(date_str: str, name: str) -> dict:
    return {"date": date_str, "repo": name,
            "prod_lines": 0, "test_lines": 0, "total_lines": 0,
            "py": 0, "cpp": 0, "h": 0, "js": 0, "ts": 0,
            "c": 0, "ino": 0, "sh": 0, "go": 0, "java": 0, "swift": 0,
            "other": 0}


def analyze(dates: list[str], output_path: str) -> None:
    headers = ["date", "repo", "prod_lines", "test_lines", "total_lines",
               "py", "cpp", "h", "js", "ts", "c", "ino", "sh",
               "go", "java", "swift", "other"]
    named_langs = {"py", "cpp", "h", "js", "ts", "c", "ino", "sh",
                    "go", "java", "swift"}
    rows = []

    for date_str in dates:
        print(f"\n=== {date_str} ===")
        for name in codecount.PROJECTS:
            repo_path = codecount.ROOT / name
            if not repo_path.is_dir():
                print(f"  {name}: directory not found, skipping")
                continue
            if not (repo_path / ".git").is_dir():
                print(f"  {name}: not a git repo, skipping")
                continue

            commit = codecount.git_commit_at(repo_path, date_str)
            if not commit:
                print(f"  {name}: no commits before {date_str}")
                rows.append(zero_row(date_str, name))
                continue

            try:
                tmpdir = codecount.git_archive_to_tmpdir(repo_path, commit)
            except Exception:
                rows.append(zero_row(date_str, name))
                continue

            try:
                counts = codecount.count_tree(Path(tmpdir.name))
                lang = counts["by_lang"]
                other = sum(v for k, v in lang.items() if k not in named_langs)
                row = {
                    "date": date_str,
                    "repo": name,
                    "prod_lines": counts["prod"],
                    "test_lines": counts["test"],
                    "total_lines": counts["prod"] + counts["test"],
                    "py":   lang.get("py", 0),
                    "cpp":  lang.get("cpp", 0),
                    "h":    lang.get("h", 0),
                    "js":   lang.get("js", 0),
                    "ts":   lang.get("ts", 0),
                    "c":    lang.get("c", 0),
                    "ino":  lang.get("ino", 0),
                    "sh":   lang.get("sh", 0),
                    "go":   lang.get("go", 0),
                    "java": lang.get("java", 0),
                    "swift": lang.get("swift", 0),
                    "other": other,
                }
                rows.append(row)
                print(f"  {name}@{commit[:8]}: prod={counts['prod']:,}  test={counts['test']:,}")
            finally:
                tmpdir.cleanup()

    # Write CSV
    with open(output_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        writer.writerows(rows)

    print(f"\nWrote {len(rows)} rows to {output_path}")

    # Print summary table
    print("\n--- Summary (total lines per date) ---")
    totals: dict[str, dict] = {}
    for row in rows:
        d = row["date"]
        if d not in totals:
            totals[d] = {"prod": 0, "test": 0, "projects": 0}
        totals[d]["prod"] += row["prod_lines"]
        totals[d]["test"] += row["test_lines"]
        if row["total_lines"] > 0:
            totals[d]["projects"] += 1

    print(f"{'Date':<15} {'Projects':>9} {'Production':>12} {'Test':>10} {'Total':>10} {'Test%':>7}")
    print("-" * 68)
    for d, t in sorted(totals.items()):
        total = t["prod"] + t["test"]
        pct = 100 * t["test"] / total if total else 0
        print(f"{d:<15} {t['projects']:>9} {t['prod']:>12,} {t['test']:>10,} {total:>10,} {pct:>6.1f}%")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Analyze codebase growth over time")
    parser.add_argument("--output", default="growth_results.csv",
                        help="Output CSV file (default: growth_results.csv)")
    parser.add_argument("--dates", default=",".join(DEFAULT_DATES),
                        help="Comma-separated list of dates (YYYY-MM-DD)")
    args = parser.parse_args()

    dates = [d.strip() for d in args.dates.split(",")]
    analyze(dates, args.output)
