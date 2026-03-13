# AI-Assisted Development Journal

**Purpose:** Track productivity, patterns, and learning from Claude-assisted development over time. Understand what works, what's slow, and how this mode of work evolves.

**Scope:** Lines of code, time allocation, quality observations, domain-specific insights, lessons learned.

---

## Entry 1: Nov 2025 – Feb 2026 (3 months, initial period)

**Dates:** November 2025 – February 23, 2026
**Duration:** ~3 months

**Audit Note:** Carefully counted to exclude dependencies (venv, .pixi, node_modules), build artifacts (build/, dist/, .pio), and version control (.git, .pytest_cache, .claude/worktrees). Separated source code from test code. See methodology in project file.

### Output Summary
- **Total LOC:** 168,077 lines
  - **Source code:** 130,689 lines
  - **Test code:** 37,388 lines (22% of total)
- **Projected annual rate:** ~630k LOC/year (source + tests)
- **Breakdown by project (source code):**
  - mr-esp32: 37,557 lines (C/C++ firmware + Python, includes 27k tests)
  - webserver: 30,966 lines (infrastructure/web UI)
  - curator: 15,751 lines (Python, media curation)
  - freecad-mcp: 10,306 lines (Python, CAM/terrain operations, includes 3.7k tests)
  - mcp-kicad-sch-api: 9,896 lines (KiCAD automation)
  - kicad-mcp: 8,581 lines (KiCAD MCP, includes 2.3k tests)
  - Other projects: ~17.5k lines

### Work Type Breakdown
- **Greenfield development:** ~85% (new systems, MCPs, infrastructure)
- **Integration & debugging:** ~10% (FreeCAD/OCCT interface work, CAM tooling)
- **Maintenance/refactoring:** ~5% (bug fixes, code cleanup)

### Activity Time Allocation (estimated)
- **Coding/implementation:** ~60%
- **Integration/debugging/research:** ~25% (including FreeCAD/OCCT interface exploration)
- **Design/architecture/direction:** ~10% (human-driven)
- **Testing/validation:** ~5%

### Key Domains & Complexity
1. **ESP32 firmware** (mr-esp32): Real-time constraints, hardware integration, WiFi management, sensor I/O
2. **FreeCAD MCP** (freecad-mcp): CAD geometry, CAM operations (OCL surface machining), terrain generation
3. **KiCAD automation** (kicad-mcp, mcp-kicad-sch-api): PCB design, netlist handling, footprint placement
4. **Media processing** (curator, racing-tagger): Image analysis, metadata curation, data pipelines
5. **Infrastructure** (mqtt-logger, webserver): System monitoring, data logging, web UIs

### What Worked Well ✓
- **Clear direction + rapid iteration:** User-driven prioritization (what to build, in what order) dramatically reduces wasted effort.
- **Leveraging existing libraries:** Building *on top of* FreeCAD, KiCAD, etc. rather than from scratch multiplies productivity.
- **Pair programming on complex integration:** Hunting down OCCT/FreeCAD interface quirks, CAM algorithm debugging—two eyes caught subtle issues faster than one.
- **MCP architecture:** Decoupling Claude from application logic (FreeCAD, KiCAD) allows rapid iteration on new functionality without touching core systems.
- **Sustained context:** No context-switching overhead; continuous domain focus enables deep problem-solving.
- **Production-quality threshold:** Code shipped is evaluated and approved before commit, filtering out low-quality output.

### What Was Slow / Challenging ⚠
- **Obscure library interfaces:** FreeCAD/OCCT have poorly documented corners; required significant exploration and trial-and-error.
- **Integration overhead:** ~10-15% of time spent on "glue" work that doesn't produce visible code (interface mapping, workarounds for bugs in upstream libraries).
- **Hardware constraints:** ESP32 memory and timing constraints required careful optimization; not all straightforward implementations fit.
- **CAM algorithm research:** Terrain generation, OCL surface machining—required understanding domain-specific algorithms (not just coding).

### Quality Observations
- **Test coverage:** freecad-mcp has 54 tests; most projects include reasonable test suites.
- **Bug rate:** Low defect rate in shipped code; most bugs caught during integration/review phase.
- **Code maintainability:** Production code across projects follows consistent patterns, well-structured, documented.
- **Refactoring:** Minimal technical debt accrued; most code is clean on first pass (suggesting good initial design).

### Lessons Learned 📚
1. **Greenfield ≠ all software:** This 500k/year rate applies to building new systems where the problem space is understood. Maintenance work in regulated industries (health, nuclear, finance) with 15+ years of legacy debt is fundamentally different. Pair programming may help there too, but different constraints apply.

2. **LOC is incomplete:** Metric excludes research, debugging, exploration time, and integration overhead. Real work is ~20–30% higher than code committed.

3. **Domain expertise multiplies AI efficiency:** User understanding of what to build, how systems should integrate, and technical constraints shapes what's possible. Average developer + Claude ≠ this productivity.

4. **Composition > reimplementation:** Building MCPs and tools *on top of* existing systems (FreeCAD, KiCAD) is far more productive than reimplementing from scratch. Leverage matters.

5. **User as director is critical:** The human choosing what to pursue, setting priorities, and evaluating output is the force multiplier. AI execution without direction wastes time.

6. **Pair programming on complex work:** Debugging twisted legacy interfaces, exploring CAM algorithms, refactoring—two minds are better. The "second eyes" aspect of AI assistance may be most valuable for hard, error-prone work, not just greenfield.

### Next Steps / Open Questions
- How does productivity change as complexity increases?
- Where does AI assistance *not* help (or slow things down)?
- How does this scale to team environments (multiple humans + Claude)?
- Do different problem domains have dramatically different productivity curves?

### Collaboration Model: Distinguished Engineer + AI Executor

This work demonstrates a specific collaboration pattern that appears highly effective:

**The Human (Distinguished Engineer, 25+ years experience):**
- Sets vision and direction (what systems to build, architectural principles)
- Makes strategic decisions (monorepo vs. separate repos, rewrite vs. patch, platform vs. one-off)
- Understands system behavior at architectural level (can reason about churn patterns without reading implementation)
- Evaluates quality and fitness-for-purpose
- Steers execution through prioritization and feedback
- Role: "Jedi ambassador" — mastery + mentorship mode

**The AI (Claude):**
- Executes implementation at scale (10k-40k LOC per project)
- Handles mechanical complexity (C++, Python, JavaScript across domains)
- Performs research and exploration (FreeCAD/OCCT interfaces, CAM algorithms)
- Catches bugs through careful implementation
- Serves as "second eyes" on complex integration work
- Role: Capable executor with domain-specific depth

**Why this works:**
1. **Clear division of labor:** Human thinks architecturally; AI codes mechanically
2. **Shared understanding:** Human can reason about system without writing it
3. **Quality multiplication:** Human evaluation + AI execution produces production-quality code
4. **Efficiency:** No time lost to context-switching between vision and implementation
5. **Scale:** Human expertise amplified across multiple sophisticated systems

**Evidence of effectiveness:**
- 168k LOC across 19 projects in 3 months, all production-quality
- Human understands architectural patterns (monorepo tightly-coupled-by-design, socket_server rewrite rationale, hardware expansion model)
- Churn analysis reveals architectural insights (socket_server healing post-rewrite, mr-esp32 growth patterns match product expansion)
- Strategic decisions (FreeCAD bug fix, KiCAD MCP development, socket_server amputation) all executed cleanly

**Note:** This model is NOT "human becomes obsolete" or "AI writes code autonomously." It's the opposite: human expertise becomes the limiting factor, not the bottleneck. The 25 years of engineering judgment shape everything; the AI just enables it to be applied across more systems.

---

## Entry 2: Feb 2026 – [ongoing]

**Dates:** February 24, 2026 –
**Duration:** [in progress]

**Audit Note:** LOC count to be run at close of entry period using `count_code.sh`.

### Output Summary
- **Total LOC:** [to be counted]
- **Breakdown by project:** [to be counted]

### Work Type Breakdown
- **Greenfield:** [to be assessed]
- **Integration & debugging:** [to be assessed]
- **Maintenance/refactoring:** [to be assessed]

### Session Notes

#### 2026-02-25 — mr-esp32: MQTT fix + audio architecture design

**Code shipped:**
- `shared/src/e32sl_mqtt.cpp` — WiFi-aware MQTT reconnect. Root cause of persistent
  `exceeded timeout` disconnects on audio-node: when WiFi drops briefly and ESP32's
  background task reconnects silently, the existing MQTT TCP connection is dead at
  the network level but `mqttClient.connected()` still returns true (half-open TCP).
  PINGREQs appear to be sent but never reach the broker; after 90s (1.5× keepalive)
  broker fires `exceeded timeout`. Fix: detect WiFi down→up transition in
  `e32sl_mqtt_process()` and explicitly disconnect the stale socket before reconnecting.
  Also reduced keepalive 60s→30s (broker timeout now 45s). Boot false-positive fixed
  by initializing `wifiWasUp` from actual `WiFi.status()` at init time.
  Commits: `7defa7e`, `cec734a` (mr-esp32). Affects all 8+ deployed boards.
- `tools/test_health_watcher.py`, `tools/health_watcher.py` — three test failures
  fixed (SQL binding, heap drift computation, disconnect threshold logic).
- `tools/health_schema.py`, `tools/test_health_schema.py` — new: canonical health
  payload field sets + 11 cross-validation tests including firmware grep via content
  sentinel. Caught a real firmware/watcher mismatch on first run.
- `mr-docs/audio-architecture.md` — comprehensive audio architecture specification
  (393 lines) covering hardware platform, two-core software architecture, full
  capability inventory, phased sound sequences, board-config I2S integration,
  audio-server extensions, layout coordinator design, and four deployment scenarios.

**Notable technical depth:**
- The MQTT half-open TCP bug is the kind of embedded networking issue that requires
  correlating broker-side logs against board-side serial output to even form the
  hypothesis. Standard hobbyist debugging (look at the serial port) would never
  surface it — the board looks fine.
- The audio architecture exercise covered four distinct layout scenarios and converged
  on a general-purpose scene audio engine. The design surface included: live DSP
  (delay line echo), multi-core audio mixing, spatial panning with dead-reckoning,
  phased sound sequences (coaling tower, ashpit, water column, coal delivery chain),
  TTS generation with hall IR reverb, procedural ambient samplers, and intra-board
  trigger rules. None of this was prompted by a specific implementation request —
  it emerged from working through what each scene actually requires.
- "Sounds nobody else models" identified as a design principle: the coal delivery
  chain, the ashpit, the turntable bearing rumble, the Poague water column recording
  opportunity.

**What worked well:**
- Test-first caught the health watcher bugs immediately; ROI on that test investment
  was described as "basically instantaneous."
- Schema cross-validation (firmware grep via content sentinel) caught a real
  mismatch on first run: "another immediate payback."
- Architecture design via scenario analysis: working through concrete use cases
  produced a more grounded spec than abstract capability planning would have.

**What was slow / challenging:**
- Root cause analysis of MQTT disconnects required reading three log sources
  (Mosquitto, ESP32 serial, loop() source code) and understanding TCP half-open
  state in an embedded WiFi context. Several dead ends ruled out (I2S 50ms timeout,
  vibration calibration, HTTP fetches at playback time) before the WiFi layer
  was identified.

#### 2026-02-26/27 — mr-esp32: Heap fragmentation diagnosis + monorepo-wide fix

**Code shipped:**
- `board-config/firmware/` (8 files) — eliminated all Arduino `String` allocations
  in MQTT hot paths. Replaced `String topic = mqttPrefix + "/config/" + boardName + ...`
  with `static char cachedPrefix[]` + `buildTopic(buf, size, suffix)`. Rewrote
  `mqttCallback()` and `processMessage()` with cached topic prefixes and `strcmp`
  dispatch. OTA deployed to 5 production boards same session.
- `audio-node/firmware/src/main.cpp` — same pattern: cached `cmcaBase[96]`,
  per-channel parsing via `strchr()`+`atoi()` instead of `String::substring()`.
- `rt/firmware/src/main.cpp` — replaced `static String topicBase()` (new String
  every call) with `static char cachedTopicBase[96]` + `buildRtTopic()`.
- `hammer/firmware/src/main.cpp` — same pattern.
- `speed-cal/firmware/src/mqtt_manager.cpp` — all 11 publish functions routed
  through `publishToTopic()` helper using stack buffers.
- `dynamometer/firmware/src/mqtt_manager.cpp` — `serialized(String(float, N))`
  replaced with `snprintf(fbuf, ...)` + `serialized(fbuf)` (9 instances).
- `tools/health_watcher.py` — skip LLM summary when API key not set; update to
  paho-mqtt v2 callback API.
- 16 files changed, 575 insertions, 468 deletions across 6 projects.

**The diagnosis story:**

Enhanced health monitoring code was deployed to the board-config fleet the
evening of Feb 25. The next morning (Feb 26), the health watcher showed
`heap_min` had drifted 17-22% below baseline across all 5 boards after ~12
hours of idle operation. This was the first time heap drift was visible — the
`heap_min` metric didn't exist 24 hours earlier.

Root cause: Arduino `String` class. Every MQTT callback invocation constructed
3-7 temporary `String` objects for topic comparison (`String(topic).startsWith(prefix + "/config/" + ...)`)
and every publish built topic strings the same way. Each `String` allocates on
the heap, copies, then frees — but the freed blocks leave holes that can't be
coalesced. Over hours, the heap fragments: `heap_free` stays stable (memory is
returned) but `heap_min` drops monotonically (the worst-case fragmentation
worsens). Eventually a large allocation fails and the board crashes.

The fix is mechanical but pervasive: replace all `String` in MQTT paths with
`static char[]` cached at startup + `snprintf()` into stack buffers +
`strcmp()`/`strncmp()` for dispatch. Zero heap allocation per message.

After fixing board-config, a monorepo sweep found the identical anti-pattern in
all 5 other MQTT-enabled projects. All fixed, 134 native tests passing
(audio-node 50, rt 25, hammer 9, board-config 50). Board-config OTA deployed
to fleet; other projects awaiting next physical flash.

**Observability investment thesis — now with 4 data points:**

Every investment in observability/debugging infrastructure in this project has
paid off almost immediately:

1. **FreeCAD MCP ring buffer** — first run after adding it surfaced a framing bug
2. **Board-config health monitoring** — first morning report revealed heap
   fragmentation across all 5 boards (this session)
3. **e32sl_mqtt WiFi-state tracking** — immediately explained persistent MQTT
   disconnects on audio-node (Feb 25 session)
4. **Health schema cross-validation tests** — caught a field name mismatch on
   first run

The pattern is consistent enough to be a principle: *instrument first, then
problems become self-reporting*. The marginal cost of adding a metric is
trivial compared to diagnosing a blind production issue. In embedded systems
where you can't attach a debugger to a deployed device and the failure mode
might be "crashes after 18 hours," observability is prerequisite infrastructure.

This is amplified in AI-assisted development. When Claude can see structured
health data (`heap_min` drifting 17-22%), it goes directly from symptom to
root cause to fleet-wide fix in one session. Without the metric, the symptom
would have been "board X crashed sometime last night" — and the investigation
would have started from zero.

**What worked well:**
- Diagnosis to fleet-wide OTA in a single conversation (~2 hours)
- Monorepo structure made the cross-project sweep natural — same pattern,
  same fix, applied 6 times
- OTA deployment via ElegantOTA v3 programmatic API: no physical access needed
- 134 tests provided confidence the mechanical String→char[] replacement didn't
  break anything

**What was slow / challenging:**
- speed-cal and dynamometer had pre-existing build failures (shared library API
  drift) unrelated to this fix — couldn't verify those two builds

### What Worked Well ✓

### What Was Slow / Challenging ⚠

### Quality Observations

### Lessons Learned 📚

### Next Steps / Open Questions

---

## Observations Over Time
(To be updated as patterns emerge across multiple entries)

### Observability as a Development Accelerator

Four instances in three days (Feb 25-27, 2026) confirm a strong pattern:
debugging infrastructure pays for itself almost immediately. This appears to be
a general principle rather than coincidence — instrumented systems surface
problems that uninstrumented systems hide until they cause user-visible failures.

The ROI is especially high in:
- **Embedded systems** where you can't attach a debugger post-deployment
- **Fleet deployments** where one fix applies to many devices
- **AI-assisted workflows** where structured data enables faster diagnosis

- Productivity trends
- Domain-specific insights
- Technique evolution
- Changing challenges
(To be updated as patterns emerge across multiple entries)

- Productivity trends
- Domain-specific insights
- Technique evolution
- Changing challenges

---

## Methodology Notes

### Counting Criteria (consistent across all entries)

**Included (counted as source code):**
- `.py`, `.cpp`, `.c`, `.h`, `.js`, `.ts`, `.tsx`, `.java`, `.rs`, `.go` files
- Application code, library code, MCP handlers, firmware
- Infrastructure-as-code

**Included (counted separately as test code):**
- Files matching `test_*.py`, `*_test.py`, `*_test.js`, `*_test.cpp`
- Files in `tests/` or `test/` directories
- Pytest fixtures, test utilities

**Excluded (not counted):**
- `venv/`, `.venv/`, `.pixi/`, `node_modules/` (dependencies)
- `.git/`, `.pytest_cache/`, `__pycache__/` (version control & caches)
- `build/`, `dist/`, `.pio/`, `~*` (build artifacts, temp files)
- `.claude/worktrees/` (git worktrees)
- `.cache/` directories (runtime caches)
- Configuration files (YAML, JSON, TOML unless they're data/specs)
- Documentation (Markdown, etc.)

This provides an honest baseline that can be tracked over time and compared across project domains.
