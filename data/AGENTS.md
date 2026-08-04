# AGENTS.md — data/

- Claims in `claim_ledger.yaml` must trace to a deterministic `src/`
  derivation and a manuscript `{{TOKEN}}` from
  `src/thunderball/manuscript_variables.py`.
- Only add a claim when the value is actually computed by code; never
  hand-author a numeric that the domain modules should produce.
- Keep the `token` field consistent with the manuscript token map.
