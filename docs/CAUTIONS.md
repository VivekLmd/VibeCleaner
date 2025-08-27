## Cautions and Safe Use

Agentic tooling can be powerful but risky. Keep these cautions in mind:

- Destructive actions: commands that create/modify resources (e.g., creating GH issues/labels) can have lasting effects.
- Hallucination/rubbish: model outputs can be incorrect, overly confident, or propose breaking changes.
- Dependency drift: models may suggest upgrades not aligned with your constraints.
- Secrets exposure: avoid pasting secrets into tickets; never hardcode keys in generated code.
- Context leakage: tracing stores prompts and responses locally; treat artifacts as sensitive.

### Built-in Mitigations
- Dry-run by default: commands only print intended actions unless `--apply` is set.
- Safe mode: add `--safe` (or `VIBEOPS_SAFE=1`) to enforce guardrails:
  - Forces dry-run for `issues` and skips `labels` changes.
  - Blocks writing generated output into non-empty directories unless `--force` is passed.
- Dry-run defaults: `issues` defaults to `--dryrun`; use `--apply` to execute.
- Constraints + stack: prompts include project stack and pinned versions; prefer these over the model’s guesses.
- Swachh checks: scan for merge markers, debug prints, very long files, and potential secrets patterns.
- Tracing: enable `--trace` to get a visibility trail of actions for review.

### Recommended Practices
- Start with design/discovery modes before MVP/production changes.
- Review diffs carefully; keep PRs small and reversible.
- Run locally and in CI before merging; expand tests as you go.
- Gate external actions (labels/issues) behind team approval in CI if needed.
- CI policy: this repo’s workflow blocks PRs that introduce `--apply` usage unless the PR has the `allow-apply` label. Use that label after review to permit apply mode in CI contexts.
- Rotate credentials if any accidental exposure is suspected.
