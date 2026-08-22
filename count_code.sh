#!/bin/bash
#
# count_code.sh - Analyze codebase across projects
#
# Thin wrapper: the counting logic lives in count_code.py / codecount.py
# (shared with growth_analysis.py) so the two tools can't drift apart.
#
# Usage: ./count_code.sh [--project PROJECT_NAME] [--root ROOT_DIR]
#
exec python3 "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/count_code.py" "$@"
