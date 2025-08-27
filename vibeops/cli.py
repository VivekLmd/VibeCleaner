import argparse
import os
from pathlib import Path
from . import __version__
from .utils import load_state, save_state, ensure_state_dir, print_detected_tools, get_default_state_dir
from .prompt_builder import build_prompt
from . import providers
from . import telemetry
from . import report as report_mod
from .otel_export import export_run_to_otel

BASE = Path(__file__).resolve().parent
STATE_DIR = get_default_state_dir()

def cmd_init(args):
    ensure_state_dir(STATE_DIR)
    state = load_state(STATE_DIR)
    state["version"] = __version__
    state["default_mode"] = state.get("default_mode", "mvp")
    save_state(STATE_DIR, state)
    print(f"VibeOps {__version__} initialized. State at {STATE_DIR}")
    print("Tool detection:")
    print_detected_tools()

def _read_ticket(path: Path) -> str:
    if not path.exists():
        raise FileNotFoundError(f"Ticket not found: {path}")
    return path.read_text(encoding="utf-8")

def _choose_provider(mode: str, router_path: Path) -> str:
    try:
        import yaml  # if available
        cfg = yaml.safe_load(router_path.read_text(encoding="utf-8"))
        return cfg.get("defaults", {}).get(mode, "codex")
    except Exception:
        return "claude" if mode in ("design", "production") else "codex"

def cmd_plan(args):
    telemetry.start_run({
        "cmd": "plan",
        "mode": args.mode,
        "provider": args.provider,
        "model": args.model,
    })
    ticket = _read_ticket(Path(args.ticket))
    prompt = build_prompt(BASE, args.mode, ticket, {"phase": "plan"})
    provider_name = args.provider or _choose_provider(args.mode, BASE / "config" / "router.yaml")
    out = getattr(providers, provider_name)(prompt, model=args.model)
    print(out)
    telemetry.end_run(status="ok")

def cmd_gen(args):
    telemetry.start_run({
        "cmd": "gen",
        "mode": args.mode,
        "provider": args.provider,
        "model": args.model,
    })
    ticket = _read_ticket(Path(args.ticket))
    prompt = build_prompt(BASE, args.mode, ticket, {"phase": "gen", "out_dir": args.out})
    provider_name = args.provider or _choose_provider(args.mode, BASE / "config" / "router.yaml")
    out = getattr(providers, provider_name)(prompt, model=args.model)
    Path(args.out).mkdir(parents=True, exist_ok=True)
    (Path(args.out) / "GENERATED.md").write_text(out, encoding="utf-8")
    print(f"Generated output saved to {args.out}/GENERATED.md")
    telemetry.log_event("artifact_saved", path=f"{args.out}/GENERATED.md")
    telemetry.end_run(status="ok")

def cmd_review(args):
    telemetry.start_run({
        "cmd": "review",
        "mode": args.mode,
        "provider": args.provider,
        "model": args.model,
    })
    folder = Path(args.in_path)
    files = [str(p) for p in folder.rglob("*") if p.is_file()]
    ticket = f"Review files: {len(files)} items under {folder}"
    prompt = build_prompt(BASE, args.mode, ticket, {"phase": "review", "files": files[:50]})
    provider_name = args.provider or _choose_provider(args.mode, BASE / "config" / "router.yaml")
    out = getattr(providers, provider_name)(prompt, model=args.model)
    print(out)
    telemetry.end_run(status="ok")

def cmd_swachh(args):
    import runpy
    runpy.run_path((BASE / "swachh.py").as_posix())

from .gh_issues import ensure_labels, create_issue

def cmd_labels(args):
    try:
        import yaml
    except ImportError:
        raise SystemExit("PyYAML is required for this command. Install with: pip install PyYAML")
    cfg = yaml.safe_load(Path(args.backlog).read_text(encoding="utf-8"))
    repo = cfg.get("repo","").strip()
    if not repo:
        raise SystemExit("Set 'repo:' in backlog.yaml (e.g., owner/repo)")
    # collect labels
    all_labels = set(cfg.get("labels_default", []))
    for epic in cfg.get("epics", []):
        for l in epic.get("labels",[]): all_labels.add(l)
        for issue in epic.get("issues", []):
            for l in issue.get("labels",[]): all_labels.add(l)
            mode = issue.get("mode")
            if mode: all_labels.add(f"mode:{mode}")
    ensure_labels(repo, sorted(all_labels))
    print("[labels] done.")

def _issue_body_from(epic, issue):
    header = f"**Epic:** {epic.get('title')}\n\n"
    mode = issue.get('mode')
    if mode:
        header += f"**Mode:** {mode}\n\n"
    return header + (issue.get("body","") or "")

def cmd_issues(args):
    try:
        import yaml
    except ImportError:
        raise SystemExit("PyYAML is required for this command. Install with: pip install PyYAML")
    cfg = yaml.safe_load(Path(args.backlog).read_text(encoding="utf-8"))
    # Minimal schema validation
    if not isinstance(cfg, dict):
        raise SystemExit("backlog.yaml: expected a mapping at top-level")
    repo = cfg.get("repo","").strip()
    if not repo:
        raise SystemExit("Set 'repo:' in backlog.yaml (e.g., owner/repo)")
    if cfg.get("epics") is not None and not isinstance(cfg.get("epics"), list):
        raise SystemExit("backlog.yaml: 'epics' must be a list if present")
    defaults = cfg.get("labels_default", [])
    for epic in cfg.get("epics", []):
        epic_labels = epic.get("labels", [])
        for issue in epic.get("issues", []):
            title = issue["title"]
            labels = defaults + epic_labels + issue.get("labels", [])
            mode = issue.get("mode")
            if mode: labels.append(f"mode:{mode}")
            body = _issue_body_from(epic, issue)
            if args.dryrun:
                print(f"[dryrun] {title} -> labels={labels}")
            else:
                create_issue(repo, title, body, labels=labels, assignees=issue.get("assignees", []))
    print("[issues] complete.")


def cmd_report(args):
    # Determine run id
    run_id = args.run
    if not run_id:
        if getattr(args, "latest", False):
            run_id = report_mod.latest_run_id()
        if not run_id:
            raise SystemExit("No run id provided and no runs found.")
    # Determine out path
    if args.out:
        out_path = Path(args.out)
    else:
        out_path = (telemetry.runs_base_dir() / run_id / "report.html")
    out = report_mod.generate_html_report(run_id, out_path)
    print(f"Report written: {out}")


def cmd_otel_export(args):
    run_id = args.run
    if not run_id:
        if getattr(args, "latest", False):
            run_id = report_mod.latest_run_id()
        if not run_id:
            raise SystemExit("No run id provided and no runs found.")
    msg = export_run_to_otel(run_id)
    print(msg)


def cmd_reports_bundle(args):
    # Choose run ids
    run_ids = []
    if args.runs:
        run_ids = [r.strip() for r in args.runs.split(",") if r.strip()]
    else:
        # Default: latest N runs by directory name
        base = telemetry.runs_base_dir()
        if base.exists():
            all_runs = sorted([p.name for p in base.iterdir() if p.is_dir()])
            run_ids = all_runs[-args.latest_count:]
    if not run_ids:
        raise SystemExit("No runs found to bundle.")
    out_dir = Path(args.out or "reports")
    out = report_mod.bundle_reports(run_ids, out_dir)
    print(f"Reports bundled in: {out}")


def main(argv=None):
    p = argparse.ArgumentParser("vibeops", description="Vibe coding orchestrator for Claude + Codex")
    p.add_argument("--trace", action="store_true", help="Enable visibility trail for this run")
    sub = p.add_subparsers(dest="cmd")

    sp = sub.add_parser("init", help="Initialize state and detect tools")
    sp.set_defaults(func=cmd_init)

    sp = sub.add_parser("plan", help="Ask for plan/design before coding")
    sp.add_argument("--ticket", required=True, help="Path to a ticket markdown/text")
    sp.add_argument("--mode", choices=["discovery", "design", "mvp", "production"], default="design")
    sp.add_argument("--provider", choices=["claude", "codex"])
    sp.add_argument("--model", help="Optional provider model name")
    sp.set_defaults(func=cmd_plan)

    sp = sub.add_parser("gen", help="Generate code/artifacts")
    sp.add_argument("--ticket", required=True)
    sp.add_argument("--mode", choices=["discovery", "design", "mvp", "production"], default="mvp")
    sp.add_argument("--out", default="generated")
    sp.add_argument("--provider", choices=["claude", "codex"])
    sp.add_argument("--model", help="Optional provider model name")
    sp.set_defaults(func=cmd_gen)

    sp = sub.add_parser("review", help="Run model-based review over generated files")
    sp.add_argument("--in", dest="in_path", required=True)
    sp.add_argument("--mode", choices=["discovery", "design", "mvp", "production"], default="production")
    sp.add_argument("--provider", choices=["claude", "codex"])
    sp.add_argument("--model", help="Optional provider model name")
    sp.set_defaults(func=cmd_review)

    sp = sub.add_parser("swachh", help="Static hygiene checks for garbage code")
    sp.set_defaults(func=cmd_swachh)

    sp = sub.add_parser("labels", help="Create missing GitHub labels from backlog.yaml")
    sp.add_argument("--backlog", default="backlog.yaml")
    sp.set_defaults(func=cmd_labels)

    sp = sub.add_parser("issues", help="Create GitHub issues from backlog.yaml")
    sp.add_argument("--backlog", default="backlog.yaml")
    sp.add_argument("--dryrun", action="store_true", default=True, help="Dry run (default): show actions only")
    sp.add_argument("--apply", action="store_false", dest="dryrun", help="Actually create issues in GitHub")
    sp.set_defaults(func=cmd_issues)

    sp = sub.add_parser("report", help="Generate an HTML report for a run")
    sp.add_argument("--run", help="Run id to report on")
    sp.add_argument("--latest", action="store_true", help="Use latest run if --run omitted")
    sp.add_argument("--out", help="Output path for HTML report")
    sp.set_defaults(func=cmd_report)

    sp = sub.add_parser("otel-export", help="Export a run as OpenTelemetry trace")
    sp.add_argument("--run", help="Run id to export")
    sp.add_argument("--latest", action="store_true", help="Use latest run if --run omitted")
    sp.set_defaults(func=cmd_otel_export)

    sp = sub.add_parser("reports-bundle", help="Bundle HTML reports for multiple runs into ./reports/")
    sp.add_argument("--runs", help="Comma-separated run ids to include")
    sp.add_argument("--latest-count", type=int, default=5, help="If --runs omitted, take N latest (default 5)")
    sp.add_argument("--out", help="Output directory (default ./reports)")
    sp.set_defaults(func=cmd_reports_bundle)

    args = p.parse_args(argv)
    if getattr(args, "trace", False):
        os.environ["VIBEOPS_TRACE"] = "1"
    if not hasattr(args, "func"):
        p.print_help()
        return 2
    return args.func(args)

if __name__ == "__main__":
    main()
