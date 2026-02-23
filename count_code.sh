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
  "COVA"
  "cova-shared"
  "curator"
  "FC-tools"
  "freecad-mcp"
  "imageSearch"
  "infrastructure"
  "kicad-mcp"
  "KiCAD-mcp-extensions"
  "mcp-kicad-sch-api"
  "mqtt-logger"
  "mr-docs"
  "mr-esp32"
  "number-boards"
  "qwen-drawing-extractor"
  "racing-tagger"
  "robo-classifier"
  "sanborn-stitch"
  "system-load-visualizer"
  "tooling"
  "webserver"
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
    ! -path '*/.git/*' \
    ! -path '*/venv/*' \
    ! -path '*/.venv/*' \
    ! -path '*/.pixi/*' \
    ! -path '*/node_modules/*' \
    ! -path '*/__pycache__/*' \
    ! -path '*/build/*' \
    ! -path '*/dist/*' \
    ! -path '*/.pio/*' \
    ! -path '*/.cache/*' \
    ! -path '*/~*' \
    ! -path '*/.pytest_cache/*' \
    ! -path '*/.claude/worktrees/*' \
    ! -name 'test_*.py' \
    ! -name '*_test.py' \
    ! -name '*_test.js' \
    ! -name '*_test.cpp' \
    ! -path '*/tests/*' \
    ! -path '*/test/*' \
    2>/dev/null | xargs wc -l 2>/dev/null | tail -1 | awk '{print $1}')

  # Test code (test_*.py, *_test.py files and tests/ directories)
  tst=$(find "$proj_path" \
    \( -name 'test_*.py' -o -name '*_test.py' -o -name 'test_*.js' -o -name '*_test.cpp' -o \( \( -path '*/tests/*' -o -path '*/test/*' \) -a \( -name '*.py' -o -name '*.js' -o -name '*.cpp' \) \) \) \
    ! -path '*/.git/*' \
    ! -path '*/venv/*' \
    ! -path '*/.venv/*' \
    ! -path '*/.pixi/*' \
    ! -path '*/node_modules/*' \
    ! -path '*/__pycache__/*' \
    ! -path '*/.cache/*' \
    ! -path '*/~*' \
    ! -path '*/.pytest_cache/*' \
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
