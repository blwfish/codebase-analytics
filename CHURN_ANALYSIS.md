# Code Churn Analysis with Code Maat

**Purpose:** Identify architectural hotspots, coupling problems, and code quality issues through git history analysis.

## Installation

Code Maat is a command-line tool written in Clojure. Install via Homebrew (macOS):

```bash
brew install code-maat
```

Or download from [github.com/adamtornhill/code-maat](https://github.com/adamtornhill/code-maat)

Verify installation:
```bash
maat --version
```

## Quick Start

Analyze a repository to find hotspots (files with high churn):

```bash
cd /path/to/repo
maat --log-file <(git log --format="%H|%an|%ad|%s" --date=short) \
     --analysis hotspots \
     --output-file hotspots.csv
```

This produces a CSV with columns:
- **File:** Source code file
- **Revisions:** Number of commits touching this file
- **Added:** Lines added (total over history)
- **Deleted:** Lines deleted (total over history)

Higher revision count = "hotter" file (more churn).

## Analyses Available

### 1. Hotspots (Churn)
Files with high change frequency—potential problem areas.

```bash
maat --log-file <(git log --format="%H|%an|%ad|%s" --date=short) \
     --analysis hotspots \
     --output-file hotspots.csv
```

**Interpret:** Files with 20+ revisions in 3 months = active development or unstable architecture.

### 2. Coupling (Temporal)
Files that frequently change together—architectural coupling.

```bash
maat --log-file <(git log --format="%H|%an|%ad|%s" --date=short) \
     --analysis coupling \
     --output-file coupling.csv
```

**Interpret:** High coupling indicates tightly-coupled modules; consider refactoring boundaries.

### 3. Author Activity
Which authors touched which files—knowledge silos.

```bash
maat --log-file <(git log --format="%H|%an|%ad|%s" --date=short) \
     --analysis authors \
     --output-file authors.csv
```

**Interpret:** Single author on critical module = knowledge risk.

### 4. Communication Patterns
How many developers work on the same files—team coordination cost.

```bash
maat --log-file <(git log --format="%H|%an|%ad|%s" --date=short) \
     --analysis communication \
     --output-file communication.csv
```

**Interpret:** Many authors on same files = coordination overhead, merge conflicts.

## Example Workflow

### Analyze freecad-mcp
```bash
cd /Volumes/Files/claude/freecad-mcp
maat --log-file <(git log --format="%H|%an|%ad|%s" --date=short) \
     --analysis hotspots \
     --output-file /tmp/freecad-mcp-hotspots.csv

# View results
head -20 /tmp/freecad-mcp-hotspots.csv
```

### Analyze FreeCAD itself
```bash
cd /path/to/FreeCAD
maat --log-file <(git log --format="%H|%an|%ad|%s" --date=short) \
     --min-revisions 5 \
     --analysis hotspots \
     --output-file /tmp/freecad-hotspots.csv

# Sort by revisions (churn)
sort -t, -k2 -rn /tmp/freecad-hotspots.csv | head -20
```

### Analyze JMRI
```bash
cd /path/to/JMRI
maat --log-file <(git log --format="%H|%an|%ad|%s" --date=short) \
     --analysis hotspots \
     --output-file /tmp/jmri-hotspots.csv
```

## Interpreting Results

### High Churn Signals

**Red flags:**
- **Same file in top 5 hotspots for months:** Architectural problem
- **High revisions + high added/deleted:** Code rewriting = instability
- **Single author on hot file:** Knowledge silo + risk

**Green patterns:**
- **High revisions but low add/delete ratio:** Stabilizing (good)
- **Multiple authors over time:** Healthy knowledge distribution
- **Hot files in test/ directory:** Natural (tests evolve with features)

### Example Interpretation

If you see:
```
file,revisions,added,deleted
src/core/engine.py,47,2340,1890
src/api/handlers.py,12,340,280
src/util/helpers.py,3,100,50
```

**Analysis:**
- `engine.py` is churning hard (47 revisions, lots of rewrites)
  - Could indicate: algorithmic instability, poor initial design, or active refactoring
  - **Action:** Review recent commits; is it converging or diverging?

- `handlers.py` is moderate (12 revisions, reasonable changes)
  - Likely API evolution (expected)
  - **Action:** Check coupling; are API changes breaking other modules?

- `helpers.py` is stable (3 revisions, minimal changes)
  - **Action:** Low priority; good design

## Comparing Across Projects

Run the same analysis on your projects and FreeCAD/JMRI:

```bash
for repo in freecad-mcp mr-esp32 curator /path/to/FreeCAD /path/to/JMRI; do
  echo "=== $(basename $repo) ==="
  cd "$repo"
  maat --log-file <(git log --format="%H|%an|%ad|%s" --date=short --since="3 months ago") \
       --min-revisions 5 \
       --analysis hotspots \
       --output-file /tmp/$(basename $repo)-hotspots.csv
  echo "Top hotspots:"
  head -5 /tmp/$(basename $repo)-hotspots.csv
done
```

## Advanced: Temporal Analysis

See how churn changes over time:

```bash
# Last 6 months
maat --log-file <(git log --format="%H|%an|%ad|%s" --date=short --since="6 months ago") \
     --analysis hotspots \
     --output-file hotspots-6mo.csv

# Last 3 months
maat --log-file <(git log --format="%H|%an|%ad|%s" --date=short --since="3 months ago") \
     --analysis hotspots \
     --output-file hotspots-3mo.csv

# Compare: is the same file still hot? Or has it stabilized?
diff hotspots-6mo.csv hotspots-3mo.csv
```

## Limitations

- **New code:** Churn metrics require history; new files (< few commits) don't surface
- **Renames:** Churn doesn't track file renames across history (git log --follow helps but isn't perfect)
- **Merges:** High-churn branches merged to main appear as single large commit
- **Refactoring:** Large refactors show as high churn even if functionality unchanged

## Further Reading

- Adam Tornhill: [Code as a Crime Scene](https://pragprog.com/titles/atcrime/code-as-a-crime-scene/)
- Microsoft Research: [Use of Relative Code Churn Measures to Predict System Defect Density](https://www.microsoft.com/en-us/research/publication/use-of-relative-code-churn-measures-to-predict-system-defect-density/)
- Code Maat docs: [github.com/adamtornhill/code-maat](https://github.com/adamtornhill/code-maat)

## Integration with Development Journal

After running churn analysis on your projects, document findings in `DEVELOPMENT_JOURNAL.md`:

**New section to add each entry:**
```markdown
### Churn Analysis

**Hotspots (3-month window):**
- File X: N revisions (stable/unstable/converging)
- File Y: M revisions
...

**Key observations:**
- Which modules are stabilizing?
- Which show signs of architectural debt?
- Any knowledge silos?
```

This helps track whether code quality (via churn patterns) improves or degrades over time.
