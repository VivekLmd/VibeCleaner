import json, shutil, os, sys
from pathlib import Path

STATE_FILE = "state.json"

def ensure_state_dir(state_dir: Path):
    state_dir.mkdir(parents=True, exist_ok=True)

def save_state(state_dir: Path, data: dict):
    ensure_state_dir(state_dir)
    (state_dir / STATE_FILE).write_text(json.dumps(data, indent=2), encoding="utf-8")

def load_state(state_dir: Path) -> dict:
    p = state_dir / STATE_FILE
    if p.exists():
        return json.loads(p.read_text(encoding="utf-8"))
    return {}

def detect_cli(cmd: str) -> bool:
    return shutil.which(cmd) is not None

def print_detected_tools():
    tools = ["claude", "codex", "git", "gh", "node", "python"]
    detected = {t: (shutil.which(t) or "") for t in tools}
    for k, v in detected.items():
        print(f"{k:8} -> {v or 'NOT FOUND'}")

def _user_config_base() -> Path:
    try:
        # Prefer platformdirs if available
        from platformdirs import user_config_path
        return Path(user_config_path("vibecleaner"))
    except Exception:
        # Cross-platform fallback
        if os.name == "nt":
            base = os.environ.get("APPDATA") or os.path.expanduser("~\\AppData\\Roaming")
            return Path(base) / "vibecleaner"
        # POSIX
        base = os.environ.get("XDG_CONFIG_HOME", str(Path.home() / ".config"))
        return Path(base) / "vibeops"

def get_default_state_dir() -> Path:
    """Return a writable per-user state/config directory for VibeCleaner."""
    return _user_config_base()
