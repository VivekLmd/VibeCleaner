## Contributing

Thanks for your interest in contributing to VibeOps!

### Getting Started
- Prereqs: Python 3.10+, Git, and optionally provider CLIs (`claude`, `codex`).
- Install locally: `pip install -e .`
- Verify CLI: `vibeops --help`

### Development Workflow
- Create a branch for your change.
- Keep PRs small and focused; include a brief rationale and test plan.
- Run hygiene checks before pushing: `vibeops swachh`
- If adding commands/features, update `README.md` and `docs/`.

### Testing
- Add minimal tests where appropriate (unit or smoke-level for new functionality).
- Consider using `--trace` during development to capture run artifacts.

### Code Style
- Prefer simple, readable code; avoid unnecessary dependencies.
- Python: type hints where helpful; keep functions small and focused.

### Reporting Issues / Security
- For bugs and feature requests, open a GitHub issue with details and reproduction steps.
- For security issues, see `SECURITY.md` and use private advisories.
