# TODO — thunderball (DISCO VOLANTE)

Thunderball is the BOND-suite film package for the *Thunderball* (1965)
underwater nuclear-recovery operation: six stdlib-only domain modules (Bühlmann
ZH-L16A dive planning, convoy-screen integrity, submersible logistics, passive
sonar, set-and-drift navigation, convoy interdiction) exposed through the frozen
`bond_api` `MissionProvider` protocol, plus a token-driven manuscript and five
generated figures. The live test count and coverage live in
[`docs/_generated/COUNTS.md`](docs/_generated/COUNTS.md); the figures quoted in
the round logs below are historical measurements, not current ones. All five
findings in `output/verify/thunderball.json` (an untracked local artifact; 2
SEVERE, 3 MODERATE) were re-checked against
today's code and **all five are closed** — see *Closed since the audit* below.
There is no `output/verify/thunderball.unresolved.json`, and `_unresolved.json`
carries no `thunderball` key, so **zero open items here are carried-over
unresolved audit findings**.

## Open work

**Status (2026-10-25):** every item below **except V3** was closed in the
Round-2 pass — C1, V1, V2, V4, and D1 are fixed, and V5 was resolved as the
documented compendium boundary (see *Round-2* and *Left for a future round*
below). The tables are kept for their reasoning, not as open work. V3 is the
one item still open, and it is a fleet-wide convention question, not a
thunderball-local fix.

### Correctness

| # | Item |
|---|---|
| **C1** | **Stale hardcoded token count in agent-facing doc.** `AGENTS.md:30` reads "Plus `manuscript_variables.py` (53 computed manuscript tokens)". `generate_variables()` returns **55** today, and `docs/_generated/COUNTS.md:52` records 55. The number was correct when written and decayed silently when two tokens were added; nothing gates it. **Done when:** `AGENTS.md:30` either quotes 55 or (preferred, matching the README/COUNTS convention that a count lives in exactly one generated place) drops the parenthetical entirely and points at `docs/_generated/COUNTS.md`. **Demonstrate:** `uv run python -c "from pathlib import Path; from thunderball.manuscript_variables import generate_variables; print(len(generate_variables(project_root=Path('.'))))"` prints 55, and `grep -n '53' AGENTS.md` returns nothing. |

Nothing else in `src/` is known-wrong. The five audit findings were each
re-derived against the current source this session (code read, not assumed) and
the corresponding gates re-run.

### Verification

Claims that hold today but are not bound by a test that could fail.

| # | Item |
|---|---|
| **V1** | **No gate against a hardcoded count decaying in prose.** C1 exists because no test compares a number written in `AGENTS.md` / `README.md` / `docs/*.md` against the value it names. `tests/test_manuscript_variables.py` gates the *manuscript* rigorously (both directions, plus `test_manuscript_token_gate_actually_scans_something` at line 246 guarding against a vacuous scan) — but the agent-facing docs outside `manuscript/` are ungated. **Done when:** a test asserts that no `.md` outside `manuscript/` states a token count, test count, or coverage percentage other than by reference to `docs/_generated/COUNTS.md` — or the counts are removed from prose so the assertion is trivially safe and stays that way. **Demonstrate:** add the token to `AGENTS.md`, run `uv run pytest tests/ -q`, see it fail; revert, see it pass. Do not ship a gate that passes without ever scanning a file — pin it the way line 246 pins the manuscript gate. |
| **V2** | **Three of the five figures assert only that a non-empty PNG appeared.** `tests/test_figures.py:20` (`plot_ndl_curve`), `:35` (`plot_submersible_range`), `:42` (`plot_transmission_loss`) check `os.path.exists` and `getsize > 0` and nothing about what is drawn. The convoy rosette (`:66`) and drift geometry (`:83`) *are* content-bound — those two were hardened after a real regression where the polar plot sampled `coverage_fraction()` one bearing at a time and rendered identically for every screen. The same defect class is still open for the other three: `plot_ndl_curve` could plot a constant and pass. **Done when:** each of the three renders differently for two inputs the underlying domain function distinguishes (e.g. `plot_transmission_loss(f_khz=1.0)` vs `f_khz=100.0` — Thorp absorption differs by orders of magnitude, so identical bytes prove the figure ignores its argument). **Demonstrate:** `uv run pytest tests/test_figures.py -q`, then stub the plotted series to a constant in `src/thunderball/figures.py:73` and confirm the new test fails. |
| **V3** | **`requires-python = ">=3.10"` is an untested declaration.** `pyproject.toml:16` claims 3.10+; `docs/_generated/COUNTS.md:58` records that every measurement was taken on CPython 3.14.6 / macOS arm64, which is the only interpreter any gate has ever run. `[tool.mypy] python_version = "3.10"` (`pyproject.toml:69`) type-checks *against* 3.10 but never executes on it. **Done when:** either the suite runs on 3.10 (a CI matrix is outside this package — a local `uv run --python 3.10 pytest tests/ -q` would at least bind the floor once) or `pyproject.toml` narrows the floor to a version that has actually been exercised. **Demonstrate:** `uv run --python 3.10 pytest tests/ --cov=src --cov-fail-under=90 -q` green, and record the interpreter in `docs/_generated/COUNTS.md`. |
| **V4** | **No lint gate on `manuscript/`.** Prose is checked only by the token cross-reference. A broken `@fig:` reference, a dangling heading anchor, or a bib key with no entry in `manuscript/references.bib` passes every gate in this package. Confirmed by grep: no markdownlint, no doc linter, nothing in `scripts/` or `tests/` reads the manuscript except `test_manuscript_variables.py`. **Done when:** a markdown/reference linter runs over `manuscript/*.md` and fails on an unresolved `@fig:`/`@tbl:` label or a citation key absent from `references.bib`. **Demonstrate:** introduce `@fig:nonexistent` in `manuscript/03_results.md`, run the gate, see it fail. |
| **V5** | **No rendered-PDF check.** Nothing in this package renders the manuscript (confirmed: `scripts/` has no render/pandoc/latex entry point), so a LaTeX-level break surfaces only at compendium build time, outside this tree. **Done when:** either a render smoke test exists here, or `README.md`/`AGENTS.md` states plainly that rendering is the compendium's responsibility so the gap is a known boundary rather than an assumed gate. **Demonstrate:** whichever path is chosen, `uv run pytest tests/ -q` stays green and the claim in prose matches what runs. |

### Documentation

| # | Item |
|---|---|
| **D1** | **`wall_time_s=0.0` has no recorded rationale.** `src/thunderball/mission.py:384` hardcodes zero into every `Provenance` record. This is almost certainly deliberate — `AGENTS.md:47` makes "no wall-clock in results" a determinism guardrail, and a real elapsed time would make `execute()` non-reproducible — but that reasoning appears nowhere near the code (grep for `wall_time_s` finds exactly one hit, this line, with no comment). A future maintainer reading a field named "wall time" that is always zero will read it as a stub and "fix" it, breaking determinism. **Done when:** a one-line comment at the assignment states that zero is required by the determinism guardrail and names it. **Demonstrate:** `grep -n -B2 "wall_time_s" src/thunderball/mission.py` shows the rationale; `uv run pytest tests/ -q` unchanged. |

### Extension

Genuine future work; none of it is a defect.

**Model fidelity**

- **Gradient factors.** The ZH-L16A implementation (`src/thunderball/dive_planner.py`) is the raw M-value line with no GF-low/GF-high conservatism. Adding them moves the no-stop limits toward what a modern dive computer shows and gives the deco scheduler a tunable knob. *Done when:* `plan_dive` accepts GF parameters and a test shows a stricter GF yields a strictly shorter NDL at fixed depth.
- **Mixed gas.** Air only — `F_N2` is a module constant in `dive_planner.py`. Trimix/nitrox needs a per-gas fraction on the profile, helium compartment half-times and coefficients, and an updated alveolar term. *Done when:* an EAN32 plan at 30 m yields a longer NDL than air at the same depth.
- **Repetitive dives.** `plan_dive` always starts from a surface-saturated diver. A surface-interval model plus residual-nitrogen carry-over would let a multi-dive recovery day be planned. *Done when:* a second dive after a short interval yields a shorter NDL than the first.
- **Ascent-rate violations.** `plan_decompression` models ascent loading but neither flags nor penalises an over-fast ascent. *Done when:* an ascent above the rate limit is reported in the returned plan.
- **Detection probability.** `sonar_detection` returns a range, not a probability. A Marcum-Q layer over the signal excess would give P(detection) and a false-alarm rate. *Done when:* a `p_detect` function is monotone in signal excess and tested at the 0.5 crossing.
- **Sound-speed structure.** Spherical spreading only — no profile, no multipath, no convergence zones, no bottom interaction.
- **Non-uniform currents.** One set/drift vector for the whole water column (`current_navigation.py`). Depth shear or a tidal series would make the drift assessment meaningfully harder.
- **Multi-track interdiction.** One threat track, one CPA (`interdiction_analysis.py`). Multiple tracks need association and per-sector threat allocation.

**Integration**

- **Persistent provenance — now unblocked.** The old blocker ("once that dependency ships") is resolved: `bond_utilities.mission_io.record_provenance_outcome` exists today at `../bond-utilities/src/bond_utilities/mission_io.py:153` with signature `(mission_id, seed, version, input_payload, outcome, path, fmt=None, codename=None, started_at=None, now=None)`. Two things still stand between here and binding it: `pyproject.toml:17-22` declares only `bond-api` as a dependency (bond-utilities would have to be added), and **no film package in the fleet binds it yet** (`grep -rln record_provenance_outcome */src/*/mission.py` returns nothing), so this is a fleet convention decision, not a thunderball-local one. The integration point is the `Provenance(...)` construction at `src/thunderball/mission.py:380-385`. *Done when:* `execute()` writes a provenance record to disk and a test reads it back; determinism must survive (see D1 — `now` is injectable for exactly this reason). *Demonstrate:* `uv run pytest tests/test_mission.py -q`.
- **Portable path dependency — closed 2026-11-03.** `pyproject.toml` declared `bond-api` by an absolute path on the author's machine, so a fresh clone elsewhere would not resolve; it now declares the sibling-relative form (`bond-api = { path = "../bond-api" }`) and `uv.lock` was regenerated from that declaration. **The "33 siblings" figure this item carried was not reproducible:** measured across all 34 `bond-*` repositories at that date, **15** pinned the absolute path in `pyproject.toml`, **one more** recorded it only in `uv.lock`, and **30** committed a `uv.lock` whose `requires-python` contradicted the package's own declaration — those are the ones being repointed, and this package is done. *Closure measured 2026-11-03:* `uv sync --extra dev` succeeds from a relocated copy and the suite is **210 passed**.
  *Open, and not closed by this change:* the sibling-relative form is correct for a human suite checkout and **still unresolvable for Dependabot**, which clones one repository. Whether that matters depends on whether the code imports `bond_api` at all — that measurement is still outstanding, so this item's Dependabot half stays open.

## Known limitations (not bugs)

Deliberate scope boundaries. Recording them here so they are not re-opened as
work items.

- **Not a certified dive planner.** Air only, no gradient factors, no repetitive
  dives, no gas sharing. The model is representative. Documented in
  `manuscript/07_scope_and_related_work.md` and `README.md:103-109`.
- **Multi-diver teams and gas sharing** are out of scope.
- **Weapon-target assignment and escort-manoeuvre wargaming** are out of scope.
- **`largest_gap` deliberately does not read a half-angle.** It returns escort
  *spacing*, which is not the unwatched arc — the two are different quantities
  and the flagship screen (8 escorts at 45°, 30° half-angle) has 45° spacing and
  0° uncovered. This split was the fix for the SEVERE audit finding; the
  half-angle-aware quantity is `largest_uncovered_sector`
  (`src/thunderball/convoy_integrity.py:169`), and its docstring and
  `largest_gap`'s (`:94`) cross-reference each other so the distinction cannot
  be lost again. Do not "simplify" them back together.
- **The `[@usnavydiving2016]` no-stop-band check is a cross-model agreement
  check, not a validation against ZH-L16A tables.** The Navy manual publishes
  limits from its own EL/VVAL-18 lineage, not Bühlmann. The audit forced this
  claim to be softened from "validated against published ZH-L16A bands" to the
  honest scope now stated in `manuscript/06_reproducibility.md:40-44`,
  `manuscript/04_conclusion.md:34-36`, and
  `manuscript/07_scope_and_related_work.md:38-41`. The bands are wide by design;
  passing them is weak evidence, and the prose now says so.
- **`time_to_minimum_separation` returns `inf` whenever the CPA lies outside the
  limit** (`src/thunderball/interdiction_analysis.py:160-161`). That is correct,
  not a missing branch: the CPA *is* the smallest range the threat ever
  achieves, so a CPA outside the limit means the limit is never reached.
- **Determinism is asserted only on the platform the suite runs on.** See V3 —
  recorded there as open work because the declared floor is broader than what
  has been exercised, not because the current numbers are suspect.

## Verification

The gate for this package. All commands run from this repository's root.

In a standalone clone `uv sync` cannot resolve the `bond-api` path dependency
(see `STANDALONE.md`); install the third-party dependencies directly and prefix
the commands below with `PYTHONPATH=src` instead.

```bash
uv sync --extra dev                                    # binds the bond-api path dep

uv run pytest tests/ --cov=src --cov-fail-under=90     # live numbers: docs/_generated/COUNTS.md
uv run ruff check src/ scripts/ tests/
uv run ruff format --check src/ scripts/ tests/
uv run mypy src/ scripts/

# Guardrail greps — each must print "Clean"
grep -rn --include='*.py' "unittest.mock\|MagicMock\|@patch\|create_autospec" tests/ || echo Clean
grep -rnE "^(from|import) infrastructure" src/thunderball/ || echo Clean
grep -rnE "^(from|import) bond_api" src/thunderball/ | grep -v "mission.py" \
  || echo "Clean — only mission.py imports bond_api"

# Deterministic regeneration (must leave the tree clean)
uv run python scripts/z_generate_manuscript_variables.py \
  --now 2026-01-01T00:00:00+00:00
uv run python scripts/run_mission.py
```

Expected outcome: the coverage gate green with zero failures and skips, ruff
and mypy clean, all three guardrail greps `Clean`, and `git status` clean after
regeneration. The last measured numbers are in `docs/_generated/COUNTS.md`;
regenerate that file from what you measured after any test change — it is the
only place in this package where a coverage number or test count is quoted.

## Closed since the audit

Recorded so nobody re-opens them from a stale
`output/verify/thunderball.json`. Each was re-verified against today's source
this session.

| Audit finding | Where it now stands |
|---|---|
| SEVERE — `largest_gap` reported as "the largest uncovered sector" when it never reads `half_angle_deg` | Split into two functions with cross-referencing docstrings; `largest_uncovered_sector` is the half-angle-aware quantity, and the manuscript now reports `RESULT_UNCOVERED_SECTOR_DEG` (`manuscript/03_results.md:30`, `manuscript/04_conclusion.md:13`) |
| SEVERE — "checked in both directions" claimed but only the forward direction implemented | `tests/test_manuscript_variables.py:149` `test_no_generated_token_is_orphaned` asserts `set(variables) - referenced == ∅`; `:246` guards both directions against being vacuous |
| MODERATE — `time_to_minimum_separation` docstring inverted, finite branch meaningless | Rewritten as the hyperbolic range profile (`interdiction_analysis.py:137-169`); oracle test steps the real tracks forward to the returned time |
| MODERATE — drift computed over the gas-limited rather than planned bottom time | `manuscript_variables.py:156-157` now passes `dive.bottom_minutes / 60.0` into `assess_navigation`; `tests/test_manuscript_variables.py:230-244` asserts the two durations are distinguishable and that the token matches the planned one |
| MODERATE — ZH-L16A bands attributed to `[@usnavydiving2016]` | Corrected in three files; the honest scope is now a Known limitation above |

## Closed outside the audit

| Finding | Where it now stands |
|---|---|
| **Byte-identical regeneration was false.** `manuscript_variables.py` defaulted `GENERATION_TIMESTAMP` to `datetime.now(timezone.utc)`, so every run of `scripts/z_generate_manuscript_variables.py` rewrote `output/data/manuscript_variables.json` with different bytes (two runs a second apart hashed `ef72f22d…` and `06dde2df…`) while the manuscript, `AGENTS.md`, and `docs/architecture.md` all claimed no wall-clock dependence. The existing token tests injected a fixed `now`, so they could never see it. | The stamp now comes from the committed `paper.date` in `manuscript/config.yaml` via `manuscript_variables.generation_timestamp()`; `--now` remains an explicit override and is no longer needed for determinism. `tests/test_regeneration_determinism.py` runs the real CLI twice, 1.05 s apart, with no override and compares every written byte of the JSON and all five PNGs — proven failable by temporarily restoring the wall clock (3 tests red). Prose in `manuscript/06_reproducibility.md`, `AGENTS.md`, `docs/architecture.md`, `docs/agent_instructions.md`, `docs/testing_philosophy.md`, `scripts/README.md`, and `scripts/CONVENTIONS.md` updated to state what actually runs. |
## Round-2 (2026-08-06)

Deep-improvement pass: hostile review of the code plus a manuscript depth pass.
Baseline this session (before edits) was **192 passed, 0 failed, 0 skipped,
100.00% line+branch coverage of `src/`** on CPython 3.14.6 / macOS arm64, with
ruff and mypy clean — the pre-existing suite was already fully green. The work
here closed four open TODO items (C1, V1, V2, V4), opened V5 to done, closed
D1, and added a NaN-hardening defect fix plus a cross-module drift guard.

### Findings → fixes (each with a regression or negative-control test)

| Finding | Fix | Test evidence |
|---|---|---|
| **NaN accepted by every domain validator.** `_require_positive`/`_require_nonneg` in `dive_planner`, `submersible_logistics`, `sonar_detection`, `current_navigation`, and `interdiction_analysis` let `float('nan')` through (`nan <= 0` is false, so the guard never fired), silently propagating NaN into bottom times, ranges, and verdicts. `inf` was likewise accepted for positive-only quantities. | All five validators reject NaN (and non-finite for positive quantities). `inf` remains legal in the one place it is meaningful: `interdiction_status(inf, ...)`, since `time_to_minimum_separation` returns `inf` for "never". | `tests/test_nan_rejection.py` (11 tests): NaN/`inf` raise `ValueError` across all five modules; `test_interdiction_status_accepts_inf_min_sep` pins that the hardening does not regress the legal-`inf` path. |
| **C1 — stale token count in AGENTS.md** (`53` vs the live 55). | Removed the number; `AGENTS.md` now points at `docs/_generated/COUNTS.md` (the one generated place a count may live). | V1 gate (below) fails if any number is re-introduced. |
| **V1 — no gate against a hardcoded count decaying in prose.** | `tests/test_manuscript_lint.py::test_no_measured_metric_decays_in_agent_facing_prose` scans `AGENTS.md`, `README.md`, and all `docs/*.md` (excluding COUNTS.md) for token/test/coverage counts and fails on any. Pinned non-vacuous (asserts ≥6 docs scanned). | **Failable**: re-adding `62 computed manuscript tokens` to AGENTS.md makes the gate fail; reverting passes. |
| **V2 — three figures asserted only non-empty PNGs.** `plot_ndl_curve`, `plot_submersible_range`, `plot_transmission_loss` could draw a constant and pass. | Hardened so each renders differently for two inputs the domain distinguishes. | `tests/test_figures.py::test_ndl_curve_depends_on_the_model_it_is_given`, `..._depends_on_energy`, `..._depends_on_frequency` assert different bytes. |
| **V4 — no lint gate on the manuscript.** A dangling `@fig:`/`@sec:` label or a bib key with no entry passed every gate. | `tests/test_manuscript_lint.py::test_manuscript_crossref_labels_resolve` (referenced label ⊆ defined) and `..._citation_keys_resolve` (cited key ⊆ `references.bib`). Both pinned non-vacuous. | **Failable**: adding `@fig:nonexistent` and `[@no_such_bib_key]` to `03_results.md` makes both fail; reverting passes. Confirmed red then green. |
| **Cross-module drift: `figures.FLAGSHIP_DIVE` was a hardcoded literal** (`12, 207, 20, 40`) duplicating `config.yaml`, so the drift figure's default bottom time could silently move off the manuscript's if config changed. | `tests/test_figures.py::test_figures_flagship_dive_binds_to_config` asserts `FLAGSHIP_DIVE` equals the config recovery params and that `_flagship_bottom_hours()` matches the manuscript's `RESULT_DIVE_BOTTOM_MIN`. | Test added; passes with the current (agreeing) values. |
| **D1 — `wall_time_s=0.0` had no rationale** and read as a stub. | Added a comment at the assignment in `mission.py` stating it is pinned by the determinism guardrail (no wall-clock in artifacts), so a maintainer will not "fix" it into non-reproducibility. | `grep -n -B2 wall_time_s src/thunderball/mission.py` shows the rationale. |
| **V5 — no rendered-PDF check / responsibility undefined.** | Documented that rendering to a compiled PDF is the suite compendium's responsibility, outside this package — the "known boundary" branch of V5's done-when. | `README.md` "Scope note" carries the statement; `uv run pytest tests/ -q` stays green. |

### Manuscript improvements

- **New section `manuscript/08_discussion.md`** — "Discussion and Uncertainty": an
  honest per-capability statement of where each of the six models' idealising
  assumptions break and how the reported precision differs from accuracy,
  referencing live `{{RESULT_*}}`/`{{CONFIG_*}}` tokens throughout. Argues the
  central result (decompression, not gas, binds — `RESULT_DIVE_BINDING_CONSTRAINT`)
  is the *most robust* finding because the two limits are more than a factor of
  two apart, not a borderline tie.
- **Verdict summary table** added at the top of `manuscript/03_results.md` —
  one row per capability, every cell a live token (NDL, air limit, binding
  constraint, convoy score, sonar range, drift, interdiction status).
- **`01_introduction.md`** roadmap now cites `@sec:discussion`; `03_results.md`
  and `05_experimental_setup.md` unchanged elsewhere.
- No hand-authored numbers introduced: all new prose sits on pre-existing
  tokens (55, unchanged), so both manuscript cross-reference gates still hold.
- `docs/_generated/COUNTS.md` regenerated from the measured run (210 tests, per-file
  table, 55 tokens, new gate rows).

### Gate numbers (final, measured this session)

- `uv run pytest tests/ --cov=src --cov-fail-under=90`: **210 passed, 0 failed, 0 skipped, 100.00%** coverage of `src/` (floor 90%).
- `uv run ruff check src/ scripts/ tests/`: clean.
- `uv run ruff format --check src/ scripts/ tests/`: clean.
- `uv run mypy src/ scripts/`: clean (20 source files).
- All three guardrail greps (mock / infrastructure / bond-api-only-in-mission): Clean.
- Deterministic regeneration (`scripts/z_generate_manuscript_variables.py` +
  `run_mission.py`): leaves no tracked tree dirty; `test_regeneration_determinism.py` passes.

### Left for a future round

- **V3 — the `>=3.10` floor remains untested.** Attempted
  `uv run --python 3.10 pytest tests/ --cov=src --cov-fail-under=90 -q`; the
  pure-domain tests that don't import `bond_api` ran on 3.10, but collection
  aborted at `test_mission.py` with `ModuleNotFoundError: No module named
  'bond_api'` because the path dependency is not installed into an ad-hoc 3.10
  interpreter. Binding it properly needs a full `uv sync --python 3.10`
  (network + building the bond-api path dep for a second interpreter), which is
  a fleet-wide convention decision rather than a thunderball-local fix. Note:
  forcing `--python 3.10` re-targets the project `.venv`; recover with
  `rm -rf .venv && uv sync --extra dev --python 3.14`.
- **Persistent provenance binding** (`bond_utilities.mission_io.record_provenance_outcome`)
  and **portable path dependency** remain fleet-convention items (see "Integration"
  above); unchanged in this round.
- New model refinements (gradient factors, probabilistic sonar, depth-sheared
  current, multi-track interdiction) remain extension work, now each tied in
  `08_discussion.md` to the uncertainty it would reduce.

