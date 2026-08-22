#!/bin/bash
#
# count_code.sh - Analyze codebase across projects
#
# Counts source code and test code separately, excluding dependencies,
# build artifacts, and version control directories.
#
# Usage: ./count_code.sh [--project PROJECT_NAME]
#

date

set -e

# Configuration
PROJECTS=(
  "blender-mcp"
  "bwf-pack"
  "claude-journal"
  "COVA"
  "cova-shared"
  "curator"
  "dji-repack"
  "FC-tools"
  "freecad-mcp"
  "freecad-mr-generators"
  "heimdall"
  "infrastructure"
  "kicad-mcp"
  "lo-mcp"
  "mcp-jobs"
  "mcp-kicad-sch-api"
  "mneme"
  "mqtt-logger"
  "mr-docs"
  "mr-esp32"
  "mrh-archive"
  "needlestack"
  "nikon-fleet"
  "number-boards"
  "Poirot2"
  "racing-tagger"
  "robo-classifier"
  "system-load-visualizer"
  "tooling"
  "voice-jmri"
  "vrf-monitor"
  "writer"
)

# Root directory to analyze (default: parent of this script)
ROOT_DIR="${ROOT_DIR:-.}"

# Parse arguments
FILTER_PROJECT=""
while [[ $# -gt 0 ]]; do
  case $1 in
    --project)
      FILTER_PROJECT="$2"
      shift 2
      ;;
    --root)
      ROOT_DIR="$2"
      shift 2
      ;;
    *)
      echo "Unknown option: $1"
      exit 1
      ;;
  esac
done

# Shared path exclusions — dependency, build, tooling, and CI dirs that are
# never our own code. Used by BOTH the source and test passes so the two filters
# can't drift apart (they previously did: only the source pass excluded build/
# dist, and NEITHER excluded the self-hosted actions-runner* installs, which bury
# the real line count under bundled runner + downloaded-action JS).
# target/ (Cargo's build dir, also Maven's) was missing too: `cargo doc`
# dumps hundreds of generated .js files under target/doc/, which the .js
# extension match then silently counted as source — inflated nikon-fleet's
# reported total by ~6x (926 "source" files vs. ~15 real ones) before this
# was added.
# NOTE: this walks the filesystem and does NOT consult .gitignore, so gitignoring
# a dir (e.g. actions-runner*) does nothing here — it must be listed below.
EXCLUDES=(
  ! -path '*/.git/*'
  ! -path '*/venv/*'
  ! -path '*/.venv/*'
  ! -path '*/.pixi/*'
  ! -path '*/node_modules/*'
  ! -path '*/__pycache__/*'
  ! -path '*/build/*'
  ! -path '*/dist/*'
  ! -path '*/.build/*'
  ! -path '*/target/*'
  ! -path '*/.pio/*'
  ! -path '*/.pioenvs/*'
  ! -path '*/libdeps/*'
  ! -path '*/.cache/*'
  ! -path '*/~*'
  ! -path '*/.pytest_cache/*'
  ! -path '*/.claude/worktrees/*'
  ! -path '*/.claude/skills/*'
  ! -path '*/actions-runner*/*'
  ! -path '*/td-scan/repos/*'
)

# Rust doesn't have a separate-file test convention like the other
# languages here — idiomatic Rust unit tests live inline, in a
# `#[cfg(test)] mod tests { ... }` block at the bottom of the SAME file as
# the code under test (see e.g. nikon-fleet/src/*.rs). The name/path-based
# src vs. test split above only catches separately-named integration-test
# files (test_*.rs, *_test.rs, tests/) — it's structurally blind to this
# in-file pattern, which is how most Rust unit tests are actually written,
# so it was counting them as source. This walks each source-classified .rs
# file and, for any that contain a top-level `#[cfg(test)]` line, moves
# everything from that line to EOF from src to tst.
#
# Heuristic, not a real parser: matches only an exact `#[cfg(test)]` line
# (trimmed), so a comment that merely mentions the attribute in prose
# doesn't false-positive-trigger it. Takes the FIRST such line and treats
# everything after it as test code, which assumes — true of every Rust
# file in this codebase so far — that once a #[cfg(test)] block starts,
# no more production code follows it in that file. A file with a
# #[cfg(test)]-gated helper in the middle, followed by more real source,
# would undercount source lines; that pattern hasn't been observed here.
rust_inline_test_lines() {
  awk '
    /^[ \t]*#\[cfg\(test\)\][ \t]*$/ { if (!found) { found = 1; split_at = NR } }
    END { if (found) print NR - split_at + 1; else print 0 }
  ' "$1"
}

echo "Analyzing code in: $ROOT_DIR"
echo ""
echo "PROJECT                        |   SOURCE |    TESTS |    TOTAL"
echo "-------------------------------|----------|----------|---------"

TOTAL_SRC=0
TOTAL_TST=0

# Process each project
for proj in "${PROJECTS[@]}"; do

  # If filtering by project, skip others
  if [ -n "$FILTER_PROJECT" ] && [ "$proj" != "$FILTER_PROJECT" ]; then
    continue
  fi

  proj_path="$ROOT_DIR/$proj"

  if [ ! -d "$proj_path" ]; then
    continue
  fi

  # Source code (exclude test files and test directories)
  src=$(find "$proj_path" -type f \( -name '*.py' -o -name '*.cpp' -o -name '*.c' -o -name '*.h' -o -name '*.js' -o -name '*.ts' -o -name '*.tsx' -o -name '*.java' -o -name '*.rs' -o -name '*.go' -o -name '*.swift' \) \
    "${EXCLUDES[@]}" \
    ! -name 'test_*.py' \
    ! -name '*_test.py' \
    ! -name 'test_*.js' \
    ! -name '*_test.js' \
    ! -name 'test_*.ts' \
    ! -name '*_test.ts' \
    ! -name 'test_*.tsx' \
    ! -name '*_test.tsx' \
    ! -name 'test_*.cpp' \
    ! -name '*_test.cpp' \
    ! -name 'test_*.rs' \
    ! -name '*_test.rs' \
    ! -name '*_test.go' \
    ! -name '*Tests.swift' \
    ! -path '*/tests/*' \
    ! -path '*/test/*' \
    ! -path '*/Tests/*' \
    2>/dev/null | xargs wc -l 2>/dev/null | tail -1 | awk '{print $1}')

  # Test code (test_*.py, *_test.py files, *Tests.swift files, and tests/ directories)
  tst=$(find "$proj_path" \
    \( -name 'test_*.py' -o -name '*_test.py' -o -name 'test_*.js' -o -name '*_test.js' -o -name 'test_*.ts' -o -name '*_test.ts' -o -name 'test_*.tsx' -o -name '*_test.tsx' -o -name 'test_*.cpp' -o -name '*_test.cpp' -o -name 'test_*.rs' -o -name '*_test.rs' -o -name '*_test.go' -o -name '*Tests.swift' -o \( \( -path '*/tests/*' -o -path '*/test/*' -o -path '*/Tests/*' \) -a \( -name '*.py' -o -name '*.js' -o -name '*.ts' -o -name '*.tsx' -o -name '*.cpp' -o -name '*.rs' -o -name '*.go' -o -name '*.swift' \) \) \) \
    "${EXCLUDES[@]}" \
    2>/dev/null | xargs wc -l 2>/dev/null | tail -1 | awk '{print $1}')

  [ -z "$src" ] && src=0
  [ -z "$tst" ] && tst=0

  # Reclassify inline #[cfg(test)] blocks (see rust_inline_test_lines above)
  # out of src and into tst. Scans exactly the .rs files the source pass
  # counted — same name/path filters — so this can't drift from it.
  rs_inline_tst=0
  while IFS= read -r rf; do
    n=$(rust_inline_test_lines "$rf")
    rs_inline_tst=$((rs_inline_tst + n))
  done < <(find "$proj_path" -type f -name '*.rs' \
    "${EXCLUDES[@]}" \
    ! -name 'test_*.rs' \
    ! -name '*_test.rs' \
    ! -path '*/tests/*' \
    ! -path '*/test/*' \
    ! -path '*/Tests/*' \
    2>/dev/null)
  src=$((src - rs_inline_tst))
  tst=$((tst + rs_inline_tst))

  total=$((src + tst))

  if [ $total -gt 0 ]; then
    printf "%-30s | %8d | %8d | %8d\n" "$proj" "$src" "$tst" "$total"
    TOTAL_SRC=$((TOTAL_SRC + src))
    TOTAL_TST=$((TOTAL_TST + tst))
  fi
done

echo "-------------------------------|----------|----------|---------"
GRAND=$((TOTAL_SRC + TOTAL_TST))
printf "%-30s | %8d | %8d | %8d\n" "TOTAL" "$TOTAL_SRC" "$TOTAL_TST" "$GRAND"
