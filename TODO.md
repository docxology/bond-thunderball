# TODO — thunderball (DISCO VOLANTE)

Thunderball is the BOND-suite film package for the *Thunderball* (1965)
underwater nuclear-recovery operation: six stdlib-only domain modules (Bühlmann
ZH-L16A dive planning, convoy-screen integrity, submersible logistics, passive
sonar, set-and-drift navigation, convoy interdiction) exposed through the frozen
`bond_api` `MissionProvider` protocol, plus a token-driven manuscript and five
generated figures. Measured this session on CPython 3.14.6 / macOS arm64:
**182 tests passing, 0 failed, 0 skipped, 100.00% line+branch coverage of
`src/`** against the 90% floor, working tree clean. All five findings in
`output/verify/thunderball.json` (2 SEVERE, 3 MODERATE) were re-checked against
today's code and **all five are closed** — see *Closed since the audit* below.
There is no `output/verify/thunderball.unresolved.json`, and `_unresolved.json`
carries no `thunderball` key, so **zero open items here are carried-over
unresolved audit findings**.

## Open work

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
- **Portable path dependency.** `pyproject.toml:33-34` pins `bond-api` to an absolute path on this machine (`/Users/4d/...`), so a fresh clone elsewhere will not resolve. Measured this session: **33** sibling packages carry the same absolute-path pin, so this is a fleet-wide convention — change it fleet-wide or not at all. *Done when:* a relative path or a uv workspace declaration replaces the absolute one across the fleet. *Demonstrate:* `uv sync --extra dev` succeeds from a clone at a different filesystem location.

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

The gate for this package. All commands run from
`projects/working/bond/thunderball/`.

```bash
uv sync --extra dev                                    # binds the bond-api path dep

uv run pytest tests/ --cov=src --cov-fail-under=90     # 182 passed, 100.00% cover
uv run ruff check src/ scripts/ tests/
uv run ruff format --check src/ scripts/ tests/
uv run mypy src/ scripts/

# Guardrail greps — each must print "Clean"
grep -rn "unittest.mock\|MagicMock\|@patch\|create_autospec" tests/ || echo Clean
grep -rnE "^(from|import) infrastructure" src/thunderball/ || echo Clean
grep -rnE "^(from|import) bond_api" src/thunderball/ | grep -v "mission.py" \
  || echo "Clean — only mission.py imports bond_api"

# Deterministic regeneration (must leave the tree clean)
uv run python scripts/z_generate_manuscript_variables.py \
  --now 2026-01-01T00:00:00+00:00
uv run python scripts/run_mission.py
```

Expected outcomes as measured on 2026-08-05, CPython 3.14.6 / macOS arm64:
182 passed, 0 failed, 0 skipped, 100.00% line+branch coverage of `src/` (floor
90%), ruff and mypy clean, all three guardrail greps `Clean`, `git status`
clean after regeneration. Regenerate `docs/_generated/COUNTS.md` from what you
measured after any test change — it is the only place in this package where a
coverage number or test count is quoted.

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
