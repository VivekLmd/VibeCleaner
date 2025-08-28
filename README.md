# VibeCleaner — Automated Code Quality & Cleanup Bot

**VibeCleaner** is an automated code quality and cleanup bot that works with **Claude Code** and **Codex** providing:
- Phase modes: **Discovery**, **Design**, **MVP**, **Production** (sticky).
- Provider routing (Claude/Codex) via `config/router.yaml`.
- Constraints awareness (`constraints-*.txt`) to avoid outdated package guesses.
- Simple *Swachh Code* hygiene scan before commits.
- PR template for AI changesets.

## Quick Start
- Prereqs: Python 3.10+, GitHub CLI (`gh`), and at least one provider CLI.
  - Claude Code CLI (default command `claude`)
  - Codex CLI (default command `codex`)
  - Override binaries via env: `VIBECLEANER_CLAUDE_CMD`, `VIBECLEANER_CODEX_CMD`

Install locally:
- `pip install .` or `pipx install .`

Initialize and plan:
- `vibecleaner init`
- `vibecleaner plan --ticket ticket_sample.md --mode design`
- `vibecleaner gen --ticket ticket_sample.md --mode mvp --out generated/`
- `vibecleaner review --in generated/ --mode production`
- `vibecleaner swachh`

Routing can be set per phase in `config/router.yaml` and overridden with `--provider`.
Pin project versions in `config/constraints-*.txt`; the prompt builder injects these to avoid version drift.

Visibility and reports: see `docs/VISIBILITY.md` for tracing, HTML reports, and optional OpenTelemetry export.

Operational cautions and safe-use guidelines: see `docs/CAUTIONS.md`.

By default, VibeCleaner runs in dry-run mode and will not perform external or destructive actions. Use `--apply` to opt in, and consider `--safe` for extra guardrails.

CI safeguard: PRs that add `--apply` usage must include the `approved` label or the phase-gate workflow will fail.

## Sci‑Fi Portal (Animated UI)
- Launch a local animated UI showing “robots” carrying files while runs progress:
  - `vibecleaner portal --port 8765`
  - Open `http://127.0.0.1:8765` in your browser
  - Enable `--trace` on your commands to stream live events to the portal
- Sound: click “Enable Sound” in the portal to play subtle servo blips (uses WebAudio; muted by default).

## License
- Licensed under the MIT License. See the `LICENSE` file for details. The software is provided “AS IS”, without warranty of any kind.

Notes:
- State is stored under your user config dir (e.g., `~/.config/vibecleaner` on Linux/macOS, `%APPDATA%\vibecleaner` on Windows).
- Set `VIBECLEANER_PROVIDER_TIMEOUT` (seconds) to cap provider CLI runtime.
