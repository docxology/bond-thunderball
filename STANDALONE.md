# Thunderball — DISCO VOLANTE (package standalone note)

This package is one film in the PROJECT BOND suite; its original home was
`projects/working/bond/thunderball/` in the suite monorepo. This repository is
the standalone copy, and its canonical remote is
<https://github.com/docxology/bond-thunderball> (`origin`, default branch
`main`).

## Identity

- Film: Thunderball (1965) · mission codename **DISCO VOLANTE**.
- Protocol: frozen `bond_api` `MissionProvider` (`src/thunderball/mission.py`,
  slug `thunderball`).
- Domain core (six pure, stdlib-only modules): dive planning (Bühlmann
  ZH-L16A), convoy integrity, submersible logistics, passive-sonar detection,
  set-and-drift navigation, and convoy interdiction.

## Relationship to the BOND suite

The orchestrator discovers this package by slug via `bond_api.discovery`
(`load_provider("thunderball", ...)`). It depends on `bond-api` as a local
path dependency; the pure domain modules import neither infrastructure nor
`bond_api`, so they remain usable in isolation.

That dependency is pinned in `[tool.uv.sources]` to the suite's absolute
monorepo path (`/Users/4d/Documents/GitHub/template/...`), which does not exist
in this checkout, so `uv sync` and `uv lock` cannot resolve `bond-api` here
(`uv lock --check` fails with "Distribution not found"). The pin is suite
provenance and is deliberately not repointed. The domain core stays importable
without `bond_api`, so the suite runs against `PYTHONPATH=src` with numpy,
matplotlib, pyyaml, and pytest installed directly — that is how this repository
is verified standalone.

## Not a standalone fork

Unlike a forked exemplar, this package is not deposited on Zenodo and carries
no external DOI; the GitHub repository above is its only publication surface.
Citation sidecars (`CITATION.cff`, `.zenodo.json`, `codemeta.json`) document the
intended metadata surface for the fork contract but are not resolvable
publication records.
