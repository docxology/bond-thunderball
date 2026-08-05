# Thunderball — DISCO VOLANTE (package standalone note)

This package is one film in the PROJECT BOND suite
(`projects/working/bond/`). It is a **local-only** working tree: no remote,
never push.

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

## Not a standalone fork

Unlike a forked exemplar, this package is not published to GitHub or Zenodo
and carries no external DOI. Citation sidecars (`CITATION.cff`, `.zenodo.json`,
`codemeta.json`) document the intended metadata surface for the fork contract
but are not resolvable publication records.
