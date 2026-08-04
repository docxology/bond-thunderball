# scripts — Mission CLIs for Thunderball (DISCO VOLANTE)

Thin orchestrators. Each script bootstraps `sys.path` via `_bootstrap.py`,
then delegates to `src/` and `bond_api`. No business logic lives here.

| Script | Phase | Delegates to |
|---|---|---|
| `brief.py` | brief | `thunderball.mission.PROVIDER.brief()` |
| `recon.py` | recon | `PROVIDER.recon(ReconRequest)` |
| `plan.py` | plan | `PROVIDER.plan(brief)` |
| `execute.py` | execute | `PROVIDER.execute(plan)` |
| `debrief.py` | debrief | `PROVIDER.debrief(outcome)` |
| `run_mission.py` | all five | `bond_api.protocol.run_mission` |
| `render_figures.py` | figures | `thunderball.figures.render_all_figures` |
| `z_generate_manuscript_variables.py` | tokens | `thunderball.manuscript_variables.generate_variables` |

Run from the package root (`uv run python scripts/<name>.py`).

`z_generate_manuscript_variables.py` writes `output/data/manuscript_variables.json`
and renders the concept figures; `--now` pins `GENERATION_TIMESTAMP` for
byte-identical regeneration.
