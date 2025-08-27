import html
import json
from pathlib import Path
from typing import Optional, Dict, Any

from .telemetry import runs_base_dir


def _read_json(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _read_jsonl(path: Path):
    if not path.exists():
        return []
    out = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            out.append(json.loads(line))
        except Exception:
            pass
    return out


def latest_run_id() -> Optional[str]:
    base = runs_base_dir()
    if not base.exists():
        return None
    runs = sorted([p.name for p in base.iterdir() if p.is_dir()])
    return runs[-1] if runs else None


def generate_html_report(run_id: str, out_path: Path) -> Path:
    base = runs_base_dir() / run_id
    run_meta = _read_json(base / "run.json")
    events = _read_jsonl(base / "events.jsonl")
    providers = []
    for prov in ("codex", "claude"):
        pdir = base / prov
        if pdir.exists():
            prompt = (pdir / "prompt.txt").read_text(encoding="utf-8") if (pdir / "prompt.txt").exists() else ""
            response = (pdir / "response.txt").read_text(encoding="utf-8") if (pdir / "response.txt").exists() else ""
            stderr = (pdir / "stderr.txt").read_text(encoding="utf-8") if (pdir / "stderr.txt").exists() else ""
            providers.append({
                "name": prov,
                "prompt": prompt,
                "response": response,
                "stderr": stderr,
            })

    def esc(s: str) -> str:
        return html.escape(s)

    def section(title: str, body: str) -> str:
        return f"<section><h2>{esc(title)}</h2>{body}</section>"

    styles = """
    body { font-family: system-ui, -apple-system, Segoe UI, Roboto, sans-serif; margin: 2rem; }
    header { margin-bottom: 1rem; }
    code, pre { background: #f6f8fa; padding: .5rem; border-radius: 6px; overflow: auto; }
    .kv { display: grid; grid-template-columns: max-content 1fr; gap: .25rem .75rem; }
    .event { border-left: 3px solid #e1e4e8; padding-left: .5rem; margin: .25rem 0; }
    h2 { border-bottom: 1px solid #eee; padding-bottom: .3rem; }
    .prov { margin: .75rem 0; }
    .small { color: #666; font-size: 0.9em; }
    """

    meta_items = "".join(
        f"<div><strong>{esc(str(k))}</strong></div><div>{esc(str(v))}</div>" for k, v in run_meta.items()
    ) or "<div class=small>No run metadata</div>"

    events_html = "".join(
        f"<div class=event><strong>{esc(e.get('event',''))}</strong> <span class=small>{esc(e.get('ts',''))}</span>"
        + ("<div class=small>" + esc(json.dumps({k:v for k,v in e.items() if k not in ('event','ts')})) + "</div>" if len(e)>2 else "")
        + "</div>"
        for e in events
    ) or "<div class=small>No events recorded</div>"

    prov_html = "".join(
        f"<div class=prov><h3>{esc(p['name'])}</h3>"
        f"<h4>Prompt</h4><pre>{esc(p['prompt'][:10000])}</pre>"
        f"<h4>Response</h4><pre>{esc(p['response'][:10000])}</pre>"
        + (f"<h4>Stderr</h4><pre>{esc(p['stderr'][:8000])}</pre>" if p['stderr'] else "")
        + "</div>"
        for p in providers
    ) or "<div class=small>No provider artifacts</div>"

    html_doc = f"""
    <!doctype html>
    <html>
    <head>
      <meta charset="utf-8" />
      <title>VibeOps Report - {esc(run_id)}</title>
      <style>{styles}</style>
    </head>
    <body>
      <header>
        <h1>VibeOps Run Report</h1>
        <div class=small>run_id: {esc(run_id)}</div>
      </header>
      {section('Metadata', f'<div class=kv>{meta_items}</div>')}
      {section('Events', events_html)}
      {section('Provider Artifacts', prov_html)}
    </body>
    </html>
    """

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(html_doc, encoding="utf-8")
    return out_path


def bundle_reports(run_ids: list[str], out_dir: Path) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    # Generate per-run reports
    for rid in run_ids:
        generate_html_report(rid, out_dir / f"{rid}.html")
    # Build index
    links = "".join(
        f"<li><a href='{rid}.html'>{rid}</a></li>" for rid in run_ids
    ) or "<li>No runs to show</li>"
    index = f"""
    <!doctype html>
    <html>
    <head><meta charset='utf-8'><title>VibeOps Reports</title>
    <style>body{{font-family:system-ui;margin:2rem}} li{{margin:.25rem 0}}</style></head>
    <body>
      <h1>VibeOps Reports</h1>
      <ul>{links}</ul>
    </body>
    </html>
    """
    (out_dir / "index.html").write_text(index, encoding="utf-8")
    return out_dir
