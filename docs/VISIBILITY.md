# Visibility and Tracing

VibeOps can record a per-run visibility trail consisting of structured events and, when tracing is enabled, provider prompts and responses.

## Enable Tracing
- CLI: pass `--trace` to `vibeops plan|gen|review ...`
- Env: set `VIBEOPS_TRACE=1`

## Artifacts
Artifacts live under the platform user config path (e.g., `~/.config/vibeops` or `%APPDATA%\vibeops`):

- `runs/<run_id>/run.json` — run context (cmd, mode, provider, timestamps)
- `runs/<run_id>/events.jsonl` — JSON lines event log
- `runs/<run_id>/codex/prompt.txt`, `runs/<run_id>/codex/response.txt` (or `claude/...`) — when tracing is on

## Events
Events are appended to `events.jsonl` with fields such as `event`, `ts`, `provider`, `duration_ms`, and return codes. Providers emit `provider_call_start` and `provider_call_end`. The CLI emits `run_start` and `run_end`.

## Configuration
- `VIBEOPS_CLAUDE_CMD`, `VIBEOPS_CODEX_CMD` — override provider binaries
- `VIBEOPS_PROVIDER_TIMEOUT` — seconds to cap provider runtime
- `VIBEOPS_RUN_ID` — set a custom run id (optional)

## HTML Reports
- Generate a static HTML report for a run:
  - Latest run: `vibeops report --latest`
  - Specific run id: `vibeops report --run <id>`
  - Custom output path: `vibeops report --run <id> --out /path/to/report.html`

### Bundle Multiple Reports
- Build an index and per-run reports under `./reports/` for publishing:
  - Latest N runs: `vibeops reports-bundle --latest-count 5`
  - Specific runs: `vibeops reports-bundle --runs id1,id2,id3 --out reports`

To publish on GitHub Pages:
- Commit the `reports/` directory and enable Pages for your repo (e.g., deploy from `docs/` or `gh-pages` branch). You can rename `reports/` to `docs/` if using the main branch Pages source.

## OpenTelemetry Export (optional)
- Export a run as a trace to an OTLP collector (respects `OTEL_EXPORTER_OTLP_*` env):
  - Install deps: `pip install opentelemetry-sdk opentelemetry-exporter-otlp`
  - Export latest: `vibeops otel-export --latest`
  - Export specific: `vibeops otel-export --run <id>`
