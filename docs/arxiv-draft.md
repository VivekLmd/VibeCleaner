# Vibe Coding at the Edge of Practicality: A Case Study of Agentic Folder Cleaning at Scale

Authors: Anonymous, VibeCleaner Contributors

Abstract

We report on an applied study of “vibe coding” — using general-purpose language model agents to both author and operate software — in the concrete context of organizing real-world Downloads folders. We built VibeCleaner, an AI-assisted folder organizer, and evaluated agentic workflows across two test environments. While small-scale tasks succeeded, large-scale operations failed catastrophically when archive extraction expanded file counts from ~2,800 to ~15,323, collapsing semantic relationships and overwhelming agent context windows. We document failure modes (archive semantics loss, instruction drift, overconfident NLP renaming), contrast provider behaviors, and extract design principles that make such systems usable: provenance-first design, reversible-by-construction operations, contractual safety invariants, chunked planning, and deterministic fallbacks. We argue that for safety-critical, stateful tasks on user data, the agent role must be bounded and instrumented by deterministic control planes.

1. Introduction

Language model (LM) agents promise to translate natural language intent directly into action. This work examines the limits of that promise in a mundane yet consequential domain: cleaning and organizing Downloads folders. We ask whether general-purpose agents can reliably (1) write the code to perform the task and (2) execute the task itself on real, messy data. Our findings show a stark scale sensitivity. Success on tens to hundreds of files gives way to systemic failure at tens of thousands, especially after archive extraction. We contribute an empirical account, a taxonomy of failures, and system design guidance derived from building and testing VibeCleaner.

Contributions:

- A grounded case study of agentic workflows on filesystem operations with real data.
- Empirical observations across two environments, including the “archive explosion” failure.
- A failure taxonomy and root-cause analysis for agentic file management.
- A practical architecture that bounds agent behavior with deterministic safeguards.

2. Background and Related Work

Agents have demonstrated strong performance in code generation and small-scope automation, but their reliability degrades on long-horizon, stateful tasks with large, evolving contexts. File organization adds domain-specific challenges: provenance, reversibility, naming stability, and safety. Prior art in data engineering and operations emphasizes transaction logs, idempotency, and rollback — patterns that are notably absent from naive agentic approaches.

3. System Overview: VibeCleaner

VibeCleaner is an experimental tool that organizes Downloads folders through a hybrid of deterministic rules and optional AI assistance.

- Modules: `cli.py` (interface), `cleaner.py` (deterministic operations), `ai_assistant.py` (LLM adapter, interactive mode), `scheduler.py` (automation), `config.py` (policy).
- Core capabilities: extension-based categorization, date bucketization, duplicate detection, dry-run previews, and undo for recent operations.
- Agent role: interpret natural language requests, propose actions, and assist in ambiguous cases; deterministic engine executes committed steps.

4. Experimental Setup

We evaluated two environments that reflect realistic usage patterns:

Environment A (OneDrive Workspace)
- ~579 files; 12 pre-existing subdirectories; 13 unprocessed ZIPs; ~50+ extensions. Result: Successful organization with preserved usability.

Environment B (Main Downloads)
- ~2,800 files initially. A user request to “unzip downloads” triggered extraction, expanding the set to ~15,323 files. Result: Severe degradation: context loss, archive semantics collapse, and renaming instability.

Procedure
- Iterative agent prompting with dry-run previews where available.
- Alternating between two providers (e.g., Codex-inspired vs. Claude-inspired behavior) to cross-pollinate strategies.
- Manual validation for correctness, safety incidents, and usability.

5. Results

Small-scale success: batches of 20–30 files, clear extensions (images), date-based archiving, and hash-based duplicate handling performed reliably. Large-scale failure: archive extraction multiplied file counts (≈5.4×), destroying semantic groupings and exceeding agent context capacity, which led to inconsistent categorization and instruction drift.

The most damaging behavior was “smart” OCR/NLP renaming: content guesses produced high-entropy filenames, conflicted with existing versions, and erased meaningful provenance. Confidence remained high while accuracy and reversibility plummeted.

Final State Snapshot (ORGANIZED_FINAL/.ai)
- Total files: 14,643 (~30.5 GB); Duplicates relocated: 10,355 (~6.7 GB).
- Renamed: 595 files, with a `rename_map.csv` capturing normalization of duplicate suffixes and noisy titles.
- Moves by destination (from logs): 01_Tax_Financial (1,328), 10_Reports_Analytics (530), 13_Company_B (272), 05_Presentations_Proposals (168), 02_Legal_Corporate (145).
- Anchored/guarded areas (projects, dev roots) were respected, reducing collateral damage.

6. Failure Analysis

- Context Collapse: Beyond ~100–500 files, plans and constraints were not maintained across steps.
- Archive Semantics Loss: No notion that files extracted from the same archive belong together; folder structure inside archives was ignored.
- Instruction Drift: Safety constraints (dry-run, whitelists) were inconsistently obeyed in longer sessions.
- Overconfident Renaming: Aggressive content-based renaming introduced information loss and collisions.
- Provider Divergence: One agent favored complex learning systems; another emphasized pragmatic, rule-based workflows. Cross-pollination rarely converged.

7. Design Principles

We distilled operational principles for agentic systems acting on user files:

- Provenance-First: Track origin (archive, path) and preserve group relationships; treat provenance as immutable metadata.
- Reversible by Construction: Encode every change as a diff with a precise inverse; default to reversible transforms.
- Contractual Invariants: Machine-enforced safety constraints (e.g., backup-before-delete, reversible rename maps).
- Chunked Planning: Split work along provenance/type boundaries; commit per chunk with idempotent retries and journals.
- Bounded Agency: Use deterministic executors; escalate only ambiguous cases to the agent via bounded choice prompts.

Operationalization Notes
- Adopt a persistent learning store (hash→destination decisions) akin to `organizer_learning.json` for stability across runs.
- Emit canonical reports (summary, top-level distribution, moves by destination, rename map) for auditability and human-in-the-loop review.

8. Discussion

The central lesson is architectural: agents excel as advisors and bounded classifiers within a control plane that ensures safety, reproducibility, and reversibility. Unbounded agency over mutable, large state leads to compounding errors. The delta between “working once” and “operationally reliable” is bridged by proven data engineering patterns, not by more prompts alone.

9. Threats to Validity

- Dataset idiosyncrasies: Personal Downloads may not represent broader distributions.
- Evaluation bias: Quantitative counts (moved/deleted) can overshadow experiential utility (findability).
- Observer effect: Renaming reshapes the future ground truth.

10. Recommendations

- Never bulk-unzip without archive-aware staging and grouping.
- Treat renames as proposals with previews and reversible commits.
- Gate OCR and semantic reading behind strict caps and representative sampling.
- Prefer narrow, high-precision classifiers over open-ended NLP for categorization.
- Keep an always-on dry-run and one-command rollback.

11. Conclusion

Vibe coding can bootstrap useful tools, but deploying agents on large, stateful user data requires architectural guardrails. Our case study shows a reliable path: deterministic cores, provenance-aware chunking, reversible operations, and bounded agent roles. Future work should standardize these patterns into libraries and benchmarks so that agentic systems can be both helpful and safe at scale.

Appendix A: Practical Metrics

- Categorization Precision/Recall on labeled samples.
- Rename Stability across reruns.
- Duplicate Handling accuracy on synthetic dups.
- Safety Incidents prevented by invariants.
- Rollback Success from journals.
- Latency and throughput per 100 files.
