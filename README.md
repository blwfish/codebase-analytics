# Codebase Analytics

Tools and tracking for understanding productivity and code volume across the `/Volumes/Files/claude` project tree.

## Contents

- **`count_code.sh`** — Analyze source code and test code across all projects
- **`DEVELOPMENT_JOURNAL.md`** — Longitudinal tracking of AI-assisted development productivity
- **`CHURN_ANALYSIS.md`** — Guide to analyzing git history with Code Maat (hotspots, coupling, knowledge silos)

## Quick Start

Count all code in the parent directory:
```bash
./count_code.sh
```

Count a specific project:
```bash
./count_code.sh --project mr-esp32
```

Analyze from a different root:
```bash
./count_code.sh --root /path/to/codebase
```

## Methodology

Counting rules live in one place — `codecount.py` — shared by `count_code.py`
(current-tree snapshot, invoked via `count_code.sh`) and `growth_analysis.py`
(historical trend via `git archive`), so the two can't drift apart.

### What Gets Counted (Source Code)
- `.py`, `.c`, `.cpp`, `.h`, `.js`, `.ts`, `.tsx`, `.jsx`, `.java`, `.rs`, `.go`, `.swift`, `.ino`, `.sh`, `.lua` files
- Application code, libraries, MCPs, firmware, infrastructure-as-code

### What Gets Counted (Test Code)
- Files matching `test_*.EXT` / `*_test.EXT` (py/js/ts/tsx/cpp/rs/go), `*Tests.swift`, `conftest*.py`
- Code in `tests/`, `test/`, or `Tests/` directories
- Rust unit tests written inline in a `#[cfg(test)]` block are reclassified out of
  source and into test line counts (Rust has no separate-file test convention)

### What's Excluded
- **Dependencies:** `venv/`, `.venv/`, `.pixi/`, `node_modules/`, `vendor/`, `site-packages/`
- **Build artifacts:** `build/`, `dist/`, `.build/`, `target/`, `.pio/`, `.pioenvs/`, `libdeps/`, `~*`
- **Version control & caches:** `.git/`, `.pytest_cache/`, `__pycache__/`, `.cache/`
- **Worktrees & tooling:** `.claude/worktrees/`, `.claude/skills/`, `actions-runner*/`
- **Configuration & docs:** YAML, JSON, Markdown (unless they're code or specs)

This approach gives an honest count of actual source code without inflating numbers with dependencies or build outputs.

## Projects Analyzed

| Project | Purpose |
|---------|---------|
| `blender-mcp` | Blender MCP server integration |
| `COVA` | Core visualization/analysis framework |
| `cova-shared` | Shared COVA utilities |
| `curator` | Media curation pipeline |
| `FC-tools` | FreeCAD tooling |
| `freecad-mcp` | FreeCAD MCP server with CAM operations |
| `imageSearch` | Image search/analysis tools |
| `infrastructure` | System infrastructure configs |
| `kicad-mcp` | KiCAD MCP server |
| `KiCAD-mcp-extensions` | KiCAD MCP extensions |
| `mcp-kicad-sch-api` | KiCAD schematic API |
| `mqtt-logger` | MQTT logging service |
| `mr-docs` | Model railroad documentation |
| `mr-esp32` | Model railroad ESP32 projects (monorepo) |
| `number-boards` | Number board generation |
| `qwen-drawing-extractor` | Drawing extraction with Qwen |
| `racing-tagger` | Racing photo tagging |
| `robo-classifier` | Robot classifier |
| `sanborn-stitch` | Sanborn map stitching |
| `siril-mcp` | Siril (astrophotography) MCP server |
| `system-load-visualizer` | System load visualization |
| `tooling` | General tooling |
| `webserver` | Web infrastructure |

## Usage Notes

- Counts are intentionally separated: source code + test code
- Test code percentage indicates testing coverage effort
- Projects with 0 tests may still have quality code (not all projects need test suites)
- Projected annual rates assume consistent productivity across the 3-month baseline

## Future Enhancements

- Language breakdown (Python vs. C/C++ vs. JavaScript, etc.)
- Complexity metrics (functions per file, average file size)
- Churn analysis (how often files change)
- Test coverage percentage by project
- Integration/debugging overhead estimation
