#!/bin/bash
#
# count_code.sh - Analyze codebase across projects
#
# Counts source code and test code separately, excluding dependencies,
# build artifacts, and version control directories.
#
# Usage: ./count_code.sh [--project PROJECT_NAME]
#

set -e

# Configuration
PROJECTS=(
  "blender-mcp"
  "claude-journal"
  "COVA"
  "cova-shared"
  "curator"
  "FC-tools"
  "freecad-mcp"
  "freecad-mr-generators"
  "imageSearch"
  "infrastructure"
  "kicad-mcp"
  "mcp-kicad-sch-api"
  "mqtt-logger"
  "mr-docs"
  "mr-esp32"
  "needlestack"
  "number-boards"
  "Poirot2"
  "racing-tagger"
  "robo-classifier"
  "system-load-visualizer"
  "tooling"
  "voice-jmri"
  "vrf-monitor"
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
  ! -path '*/.pio/*'
  ! -path '*/.pioenvs/*'
  ! -path '*/libdeps/*'
  ! -path '*/.cache/*'
  ! -path '*/~*'
  ! -path '*/.pytest_cache/*'
  ! -path '*/.claude/worktrees/*'
  ! -path '*/actions-runner*/*'
  ! -path '*/td-scan/repos/*'
)

echo "Analyzing code in: $ROOT_DIR"
echo ""
echo "PROJECT | SOURCE | TESTS | TOTAL"
echo "---|---|---|---"

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
  src=$(find "$proj_path" -type f \( -name '*.py' -o -name '*.cpp' -o -name '*.c' -o -name '*.h' -o -name '*.js' -o -name '*.ts' -o -name '*.tsx' -o -name '*.java' -o -name '*.rs' -o -name '*.go' \) \
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
    ! -path '*/tests/*' \
    ! -path '*/test/*' \
    2>/dev/null | xargs wc -l 2>/dev/null | tail -1 | awk '{print $1}')

  # Test code (test_*.py, *_test.py files and tests/ directories)
  tst=$(find "$proj_path" \
    \( -name 'test_*.py' -o -name '*_test.py' -o -name 'test_*.js' -o -name '*_test.js' -o -name 'test_*.ts' -o -name '*_test.ts' -o -name 'test_*.tsx' -o -name '*_test.tsx' -o -name 'test_*.cpp' -o -name '*_test.cpp' -o -name 'test_*.rs' -o -name '*_test.rs' -o -name '*_test.go' -o \( \( -path '*/tests/*' -o -path '*/test/*' \) -a \( -name '*.py' -o -name '*.js' -o -name '*.ts' -o -name '*.tsx' -o -name '*.cpp' -o -name '*.rs' -o -name '*.go' \) \) \) \
    "${EXCLUDES[@]}" \
    2>/dev/null | xargs wc -l 2>/dev/null | tail -1 | awk '{print $1}')

  [ -z "$src" ] && src=0
  [ -z "$tst" ] && tst=0

  total=$((src + tst))

  if [ $total -gt 0 ]; then
    printf "%-30s | %8d | %8d | %8d\n" "$proj" "$src" "$tst" "$total"
    TOTAL_SRC=$((TOTAL_SRC + src))
    TOTAL_TST=$((TOTAL_TST + tst))
  fi
done

echo "---|---|---|---"
GRAND=$((TOTAL_SRC + TOTAL_TST))
printf "%-30s | %8d | %8d | %8d\n" "TOTAL" "$TOTAL_SRC" "$TOTAL_TST" "$GRAND"
