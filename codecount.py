"""
codecount.py - Shared code-counting engine.

Single source of truth for: which projects are tracked, which file
extensions count as source, which paths are excluded, and what counts as
test vs. production code. Used by both count_code.py (current-tree
snapshot) and growth_analysis.py (historical trend via `git archive`) so
the two tools can't drift apart the way count_code.sh and growth_analysis.py
previously did.
"""

import io
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

# Canonical project list — the count_code.sh list (its curated, actively
# maintained set). growth_analysis.py's REPOS list previously covered 8
# projects not on this list (cnc-mcp, codebase-analytics, FreeCAD-github,
# historicalResearch, image-tiles, imageSearch, weathering, webserver) —
# those are no longer tracked by either tool now that they share this list.
# Every project resolves as ROOT / name.
PROJECTS = [
    "blender-mcp",
    "bwf-pack",
    "claude-journal",
    "COVA",
    "cova-shared",
    "curator",
    "dji-repack",
    "FC-tools",
    "freecad-mcp",
    "freecad-mr-generators",
    "heimdall",
    "infrastructure",
    "jmri-mcp",
    "kicad-mcp",
    "lo-mcp",
    "mcp-agent-notes",
    "mcp-events",
    "mcp-jobs",
    "mcp-kicad-sch-api",
    "mneme",
    "mqtt-logger",
    "mr-docs",
    "mr-esp32",
    "mrh-archive",
    "needlestack",
    "nikon-fleet",
    "number-boards",
    "Poirot2",
    "racing-tagger",
    "robo-classifier",
    "siril-mcp",
    "system-load-visualizer",
    "tooling",
    "voice-jmri",
    "vrf-monitor",
    "writer",
]

# Source file extensions to count — union of both tools' previous sets.
SRC_EXTENSIONS = {".py", ".c", ".cpp", ".h", ".js", ".ts", ".tsx", ".jsx",
                   ".java", ".rs", ".go", ".swift", ".ino", ".sh", ".lua"}

# Paths to exclude (matched as substrings of the "/"-prefixed relative path).
# Union of both tools' previous exclude lists.
EXCLUDE_PATTERNS = [
    "/.git/", "/.claude/worktrees/", "/.claude/skills/",
    "/node_modules/", "/__pycache__/",
    "/.pixi/", "/.pio/", "/.pioenvs/", "/libdeps/",
    "/build/", "/dist/", "/.build/", "/target/",
    "/.venv/", "/venv/", "/site-packages/", "/vendor/",
    "/.cache/", "/.pytest_cache/", "/~",
    "/actions-runner", "/td-scan/repos/",
]

EXCLUDE_SUFFIXES = [".min.js"]

# Extensions that follow the test_*.EXT / *_test.EXT naming convention.
TEST_NAME_EXTS = {"py", "js", "ts", "tsx", "cpp", "rs", "go"}

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
    """Precise name/path-based test detection (ported from count_code.sh),
    plus an explicit conftest*.py check — count_code.sh had no such check,
    so root-level conftest.py files (e.g. heimdall/conftest.py,
    mr-esp32/shared/test_hw/conftest.py) were silently counted as
    production source."""
    name = rel_path.rsplit("/", 1)[-1]
    if "." not in name:
        return False
    stem, ext = name.rsplit(".", 1)

    if ext in TEST_NAME_EXTS and (stem.startswith("test_") or stem.endswith("_test")):
        return True
    if ext == "py" and stem.startswith("conftest"):
        return True
    if ext == "swift" and name.endswith("Tests.swift"):
        return True
    if f".{ext}" in SRC_EXTENSIONS and re.search(r'/(test|tests|Tests)/', rel_path):
        return True
    return False


def count_lines(path: Path) -> int:
    try:
        return path.read_bytes().count(b"\n")
    except (OSError, IOError):
        return 0


# Matches a top-level `#[cfg(test)]` line (trimmed) — see rust_inline_test_lines.
_RUST_CFG_TEST_RE = re.compile(r'^[ \t]*#\[cfg\(test\)\][ \t]*$')


def rust_inline_test_lines(path: Path) -> int:
    """Rust doesn't have a separate-file test convention like the other
    languages here — idiomatic Rust unit tests live inline, in a
    `#[cfg(test)] mod tests { ... }` block at the bottom of the SAME file as
    the code under test. The name/path-based split in is_test() only catches
    separately-named integration-test files — it's structurally blind to
    this in-file pattern, which is how most Rust unit tests are actually
    written. This scans a source-classified .rs file and, for the first
    top-level `#[cfg(test)]` line found, returns the line count from there
    to EOF (heuristic: assumes no more production code follows the first
    such block in the file, true of every Rust file observed here so far)."""
    try:
        lines = path.read_text(errors="replace").splitlines()
    except (OSError, IOError):
        return 0
    for i, line in enumerate(lines):
        if _RUST_CFG_TEST_RE.match(line):
            return len(lines) - i
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
            continue

        if lang == "rs":
            rs_test = rust_inline_test_lines(f)
            if rs_test:
                prod += lines - rs_test
                test += rs_test
                by_lang[lang] = by_lang.get(lang, 0) + (lines - rs_test)
                continue

        prod += lines
        by_lang[lang] = by_lang.get(lang, 0) + lines

    return {"prod": prod, "test": test, "by_lang": by_lang}

# ---------------------------------------------------------------------------
# Git helpers (for historical / as-of-date analysis)
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
