#!/usr/bin/env python3
"""
growth_analysis.py - Measure code growth over time across all project repos.

For each repo, for each sample date, extracts the codebase at that point in
git history (using git archive — non-destructive, doesn't touch working trees)
and counts production vs test lines of code.

Output: CSV suitable for charting and paper analysis.

Usage:
    python3 growth_analysis.py [--output results.csv] [--dates 2025-11-17,2026-01-01,...]
"""

import argparse
import csv
import io
import os
import re
import subprocess
import sys
import tarfile
import tempfile
from pathlib import Path

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

ROOT = Path("/Volumes/Files/claude")

# Repos to analyze: (name, local_path)
# All user-produced repos, regardless of whether remote is GitHub or local Gitea.
# Excludes: FC-clone, JMRI, stable-audio-tools (upstream clones)
#           kicad-mcp-old (superseded), esp32-config/test-and-calibration-track/
#           track_geometry_car (archived, content moved to mr-esp32)
REPOS = [
    # Core infrastructure & tooling
    ("freecad-mcp",             ROOT / "freecad-mcp"),
    ("kicad-mcp",               ROOT / "kicad-mcp"),
    ("blender-mcp",             ROOT / "blender-mcp"),
    ("cnc-mcp",                 ROOT / "cnc-mcp"),
    ("FC-tools",                ROOT / "FC-tools"),
    ("FreeCAD-github",          ROOT / "FreeCAD-github"),   # automation scripts + macros
    ("tooling",                 ROOT / "tooling"),
    ("codebase-analytics",      ROOT / "codebase-analytics"),
    ("claude-journal",          ROOT / "claude-journal"),
    # Hardware projects
    ("mr-esp32",                ROOT / "mr-esp32"),
    # Media / ML
    ("curator",                 ROOT / "curator"),
    ("racing-tagger",           ROOT / "racing-tagger"),
    ("weathering",              ROOT / "weathering"),
    ("robo-classifier",         ROOT / "robo-classifier"),
    ("imageSearch",             ROOT / "imageSearch"),
    ("image-tiles",             ROOT / "image-tiles"),
    # Historical / mapping
    ("historicalResearch",      ROOT / "historicalResearch"),
    ("FreeCAD-github",          ROOT / "FreeCAD-github"),
    # Infrastructure & services
    ("mqtt-logger",             ROOT / "mqtt-logger"),
    ("infrastructure",          ROOT / "infrastructure"),
    ("webserver",               ROOT / "webserver"),
    # Model railroad support
    ("mr-docs",                 ROOT / "mr-docs"),
    ("number-boards",           ROOT / "number-boards"),
    # Misc
    ("COVA",                    ROOT / "COVA"),
    ("system-load-visualizer",  ROOT / "system-load-visualizer"),
]

# Deduplicate (FreeCAD-github appears twice above — remove duplicates preserving order)
seen = set()
REPOS = [(n, p) for n, p in REPOS if not (n in seen or seen.add(n))]

# Sample dates — first of each month since Claude install, plus start and today
DEFAULT_DATES = [
    "2025-11-17",   # Claude install date
    "2025-12-01",
    "2026-01-01",
    "2026-02-01",
    "2026-03-01",
    "2026-03-10",   # current
]

# Source file extensions to count
SRC_EXTENSIONS = {".py", ".js", ".ts", ".tsx", ".jsx",
                  ".cpp", ".h", ".c", ".ino", ".sh", ".lua", ".rs"}

# Paths to exclude (matched as substrings of relative path)
EXCLUDE_PATTERNS = [
    "/.git/", "/.claude/", "/node_modules/", "/__pycache__/",
    "/.pixi/", "/.pio/", "/build/", "/dist/", "/vendor/",
    "/.venv/", "/venv/", "/site-packages/",
]

EXCLUDE_SUFFIXES = [".min.js"]

# Test file/directory detection
TEST_PATTERN = re.compile(
    r'/(test|tests|spec|__tests__|conftest)[^/]*$'
    r'|/(test|tests|spec)/',
    re.IGNORECASE
)

# ---------------------------------------------------------------------------
# Core counting logic
# ---------------------------------------------------------------------------

def is_excluded(rel_path: str) -> bool:
    for pat in EXCLUDE_PATTERNS:
        if pat in rel_path:
            return True
    for suf in EXCLUDE_SUFFIXES:
        if rel_path.endswith(suf):
            return True
    return False


def is_test(rel_path: str) -> bool:
    return bool(TEST_PATTERN.search(rel_path))


def count_lines(path: Path) -> int:
    try:
        return path.read_bytes().count(b"\n")
    except (OSError, IOError):
        return 0


def count_tree(root: Path) -> dict:
    """Count production and test lines in a directory tree."""
    prod = 0
    test = 0
    by_lang: dict[str, int] = {}

    for f in root.rglob("*"):
        if not f.is_file():
            continue
        if f.suffix not in SRC_EXTENSIONS:
            continue

        rel = "/" + str(f.relative_to(root))
        if is_excluded(rel):
            continue

        lines = count_lines(f)
        lang = f.suffix.lstrip(".")

        if is_test(rel):
            test += lines
        else:
            prod += lines
            by_lang[lang] = by_lang.get(lang, 0) + lines

    return {"prod": prod, "test": test, "by_lang": by_lang}

# ---------------------------------------------------------------------------
# Git helpers
# ---------------------------------------------------------------------------

def git_commit_at(repo: Path, date_str: str) -> str | None:
    """Return the commit hash that was HEAD at end of date_str, or None."""
    try:
        result = subprocess.run(
            ["git", "rev-list", "-n", "1", f"--before={date_str} 23:59:59", "HEAD"],
            cwd=repo,
            capture_output=True, text=True, check=True
        )
        commit = result.stdout.strip()
        return commit if commit else None
    except subprocess.CalledProcessError:
        return None


def git_archive_to_tmpdir(repo: Path, commit: str) -> tempfile.TemporaryDirectory:
    """Extract commit tree to a temp directory using git archive. Returns TemporaryDirectory."""
    tmpdir = tempfile.TemporaryDirectory(prefix="growth_")
    try:
        archive = subprocess.run(
            ["git", "archive", "--format=tar", commit],
            cwd=repo,
            capture_output=True, check=True
        )
        with tarfile.open(fileobj=io.BytesIO(archive.stdout)) as tar:
            # Skip symlinks — they may point outside the temp dir (e.g. racing-tagger's
            # `common -> ../imageSearch/common`) and would double-count shared dirs anyway.
            members = [m for m in tar.getmembers() if not m.issym() and not m.islnk()]
            tar.extractall(tmpdir.name, members=members)
    except subprocess.CalledProcessError as e:
        stderr = e.stderr.decode(errors="replace")[:200]
        print(f"  WARNING: git archive failed for {repo.name}@{commit[:8]}: {stderr}",
              file=sys.stderr)
        tmpdir.cleanup()
        raise
    except Exception as e:
        print(f"  WARNING: archive extraction failed for {repo.name}@{commit[:8]}: {e}",
              file=sys.stderr)
        tmpdir.cleanup()
        raise
    return tmpdir

# ---------------------------------------------------------------------------
# Main analysis
# ---------------------------------------------------------------------------

def zero_row(date_str: str, name: str) -> dict:
    return {"date": date_str, "repo": name,
            "prod_lines": 0, "test_lines": 0, "total_lines": 0,
            "py": 0, "cpp": 0, "h": 0, "js": 0, "ts": 0,
            "c": 0, "ino": 0, "sh": 0, "other": 0}


def analyze(dates: list[str], output_path: str) -> None:
    headers = ["date", "repo", "prod_lines", "test_lines", "total_lines",
               "py", "cpp", "h", "js", "ts", "c", "ino", "sh", "other"]
    rows = []

    for date_str in dates:
        print(f"\n=== {date_str} ===")
        for name, repo_path in REPOS:
            if not repo_path.is_dir():
                print(f"  {name}: directory not found, skipping")
                continue
            if not (repo_path / ".git").is_dir():
                print(f"  {name}: not a git repo, skipping")
                continue

            commit = git_commit_at(repo_path, date_str)
            if not commit:
                print(f"  {name}: no commits before {date_str}")
                rows.append(zero_row(date_str, name))
                continue

            try:
                tmpdir = git_archive_to_tmpdir(repo_path, commit)
            except Exception:
                rows.append(zero_row(date_str, name))
                continue

            try:
                counts = count_tree(Path(tmpdir.name))
                lang = counts["by_lang"]
                other = sum(v for k, v in lang.items()
                            if k not in {"py", "cpp", "h", "js", "ts", "c", "ino", "sh"})
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
