# TODO — Thunderball (DISCO VOLANTE)

Remaining work only. Anything already shipped is described in `README.md`,
`AGENTS.md`, and `docs/architecture.md`, not here.

## Status

Phases 2 (build), 4 (deep improvement), and 5 (review + documentation truth)
are complete and gated: pytest at the 90% line+branch floor, ruff, mypy, zero
mocks, zero exemplar-lineage strings, git clean. Measured counts live in
`docs/_generated/COUNTS.md`.

## Open — model fidelity

- [ ] **Gradient factors.** The ZH-L16A implementation is the raw M-value line
      with no GF-low/GF-high conservatism. Adding gradient factors would move
      the no-stop limits toward what a modern dive computer shows and give the
      deco scheduler a tunable conservatism knob.
- [ ] **Mixed gas.** Air only. Trimix/nitrox needs a per-gas fraction on the
      profile, helium compartment half-times and coefficients, and an updated
      alveolar term. Currently `F_N2` is a module constant.
- [ ] **Repetitive dives.** `plan_dive` always starts from a surface-saturated
      diver. A surface-interval model and residual-nitrogen carry-over would let
      a multi-dive recovery day be planned.
- [ ] **Ascent-rate violations.** `plan_decompression` models ascent loading but
      does not flag or penalise an over-fast ascent.
- [ ] **Detection probability.** `sonar_detection` returns a range, not a
      probability. A Marcum-Q layer over the signal excess would give a
      probability of detection and a false-alarm rate.
- [ ] **Sound-speed structure.** Spherical spreading only — no profile, no
      multipath, no convergence zones, no bottom interaction.
- [ ] **Non-uniform currents.** One set/drift vector for the whole water column.
      Depth shear or a tidal time series would make the drift assessment
      meaningfully harder and more realistic.
- [ ] **Multi-track interdiction.** One threat track, one CPA. Multiple tracks
      would need association and a per-sector threat allocation.

## Open — integration

- [ ] **Persistent provenance.** Bind
      `bond_utilities.mission_io.record_provenance_outcome` once that dependency
      ships, so outcomes are recorded rather than only returned. The integration
      point is `MissionProvider.execute()`'s `Provenance` construction.
- [ ] **Portable path dependency.** `[tool.uv.sources]` in `pyproject.toml`
      pins `bond-api` to an absolute path on this machine. A relative path or a
      workspace declaration would make a fresh clone elsewhere resolve. This is
      a fleet-wide convention, so change it fleet-wide or not at all.

## Open — verification

- [ ] **No lint gate on `manuscript/`.** Prose is checked only by the token
      cross-reference test. A markdown linter would catch broken figure
      references and heading-anchor drift.
- [ ] **No rendered-PDF check.** The manuscript's tokens and citations are
      verified, but nothing in this package renders it, so a LaTeX-level break
      (an unresolved `@fig:` reference, a missing bib key) would only surface at
      compendium build time.
- [ ] **Figure content is unasserted beyond variation.** `test_figures.py`
      checks that PNGs are written, are non-empty, and that the convoy rosette
      differs between screens — it does not verify what is drawn.

## Not planned

These are deliberate scope boundaries, documented in
`manuscript/07_scope_and_related_work.md`; do not open them as work items
without a reason:

- Multi-diver teams and gas sharing.
- Weapon-target assignment or escort-manoeuvre wargaming.
- Any claim that the dive planner is fit to plan a real dive.
