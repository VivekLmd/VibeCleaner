import json
import os
import time
import uuid
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any

from .utils import get_default_state_dir


def _now_iso() -> str:
    return datetime.utcnow().isoformat() + "Z"


def runs_base_dir() -> Path:
    return get_default_state_dir() / "runs"


def _ensure_run_dir(run_id: str) -> Path:
    rd = runs_base_dir() / run_id
    rd.mkdir(parents=True, exist_ok=True)
    return rd


def start_run(context: Dict[str, Any]) -> Dict[str, Any]:
    run_id = context.get("run_id") or uuid.uuid4().hex[:12]
    run_dir = _ensure_run_dir(run_id)
    env_trace = os.environ.get("VIBEOPS_TRACE", "0")
    context_out = {
        **context,
        "run_id": run_id,
        "trace": env_trace in ("1", "true", "TRUE"),
        "started_at": _now_iso(),
    }
    (run_dir / "run.json").write_text(json.dumps(context_out, indent=2), encoding="utf-8")
    os.environ.setdefault("VIBEOPS_RUN_ID", run_id)
    os.environ.setdefault("VIBEOPS_RUN_DIR", str(run_dir))
    _append_event(run_dir, {
        "ts": _now_iso(),
        "event": "run_start",
        "context": {k: v for k, v in context_out.items() if k != "prompt"},
    })
    return {"run_id": run_id, "run_dir": str(run_dir)}


def _append_event(run_dir: Path, payload: Dict[str, Any]):
    try:
        with (run_dir / "events.jsonl").open("a", encoding="utf-8") as f:
            f.write(json.dumps(payload, ensure_ascii=False) + "\n")
    except Exception:
        pass


def log_event(event: str, **fields):
    run_dir = Path(os.environ.get("VIBEOPS_RUN_DIR", runs_base_dir()))
    _append_event(run_dir, {"ts": _now_iso(), "event": event, **fields})


def record_artifact(name: str, content: str, subdir: Optional[str] = None):
    # Only record artifacts if tracing is enabled
    trace_on = os.environ.get("VIBEOPS_TRACE", "0") in ("1", "true", "TRUE")
    if not trace_on:
        return
    run_dir = Path(os.environ.get("VIBEOPS_RUN_DIR", runs_base_dir()))
    if subdir:
        run_dir = run_dir / subdir
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / name).write_text(content, encoding="utf-8")


def end_run(status: str = "ok", **fields):
    run_dir = Path(os.environ.get("VIBEOPS_RUN_DIR", runs_base_dir()))
    _append_event(run_dir, {"ts": _now_iso(), "event": "run_end", "status": status, **fields})

