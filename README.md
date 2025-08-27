# VibeOps — Practical Vibe Coding Toolkit (Claude + Codex)

**VibeOps** orchestrates vibe coding across **Claude Code** and **Codex** with:
- Phase modes: **Discovery**, **Design**, **MVP**, **Production** (sticky).
- Provider routing (Claude/Codex) via `config/router.yaml`.
- Constraints awareness (`constraints-*.txt`) to avoid outdated package guesses.
- Simple *Swachh Code* hygiene scan before commits.
- PR template for AI changesets.

## Quick Start
- Prereqs: Python 3.10+, GitHub CLI (`gh`), and at least one provider CLI.
  - Claude Code CLI (default command `claude`)
  - Codex CLI (default command `codex`)
  - Override binaries via env: `VIBEOPS_CLAUDE_CMD`, `VIBEOPS_CODEX_CMD`

Install locally:
- `pip install .` or `pipx install .`

Initialize and plan:
- `vibeops init`
- `vibeops plan --ticket ticket_sample.md --mode design`
- `vibeops gen --ticket ticket_sample.md --mode mvp --out generated/`
- `vibeops review --in generated/ --mode production`
- `vibeops swachh`

Routing can be set per phase in `config/router.yaml` and overridden with `--provider`.
Pin project versions in `config/constraints-*.txt`; the prompt builder injects these to avoid version drift.

Visibility and reports: see `docs/VISIBILITY.md` for tracing, HTML reports, and optional OpenTelemetry export.

Operational cautions and safe-use guidelines: see `docs/CAUTIONS.md`.

By default, VibeOps runs in dry-run mode and will not perform external or destructive actions. Use `--apply` to opt in, and consider `--safe` for extra guardrails.

CI safeguard: PRs that add `--apply` usage must include the `approved` label or the phase-gate workflow will fail.

## License
- Licensed under the MIT License. See the `LICENSE` file for details. The software is provided “AS IS”, without warranty of any kind.

Notes:
- State is stored under your user config dir (e.g., `~/.config/vibeops` on Linux/macOS, `%APPDATA%\vibeops` on Windows).
- Set `VIBEOPS_PROVIDER_TIMEOUT` (seconds) to cap provider CLI runtime.
