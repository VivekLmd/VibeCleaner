import subprocess, shlex, os, time
from . import telemetry

class ProviderError(RuntimeError):
    pass

def _run(cmd: str, input_text: str, timeout: float | None = None):
    """Run a shell command with stdin text and capture output."""
    try:
        proc = subprocess.Popen(
            shlex.split(cmd),
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        out, err = proc.communicate(input_text, timeout=timeout)
        return proc.returncode, out, err
    except FileNotFoundError as e:
        raise ProviderError(f"Command not found: {cmd}") from e

def claude(prompt: str, model: str | None = None) -> str:
    """Generic wrapper for a Claude CLI (assumed `claude`)."""
    cmd = os.environ.get("VIBEOPS_CLAUDE_CMD", "claude")
    if model:
        cmd = f"{cmd} --model {shlex.quote(model)}"
    timeout = float(os.environ.get("VIBEOPS_PROVIDER_TIMEOUT", "0") or 0) or None
    start = time.time()
    telemetry.log_event("provider_call_start", provider="claude", model=model or "")
    telemetry.record_artifact("prompt.txt", prompt, subdir="claude")
    code, out, err = _run(cmd, prompt, timeout=timeout)
    elapsed_ms = int((time.time() - start) * 1000)
    telemetry.record_artifact("response.txt", out or "", subdir="claude")
    if err:
        telemetry.record_artifact("stderr.txt", err, subdir="claude")
    telemetry.log_event("provider_call_end", provider="claude", rc=code, duration_ms=elapsed_ms)
    if code != 0:
        hint = "Install the Claude CLI or set VIBEOPS_CLAUDE_CMD to your binary."
        raise ProviderError(f"Claude CLI failed: {err.strip()}\n{hint}")
    return out

def codex(prompt: str, model: str | None = None) -> str:
    """Generic wrapper for a Codex/OpenAI CLI (assumed `codex`)."""
    cmd = os.environ.get("VIBEOPS_CODEX_CMD", "codex")
    if model:
        cmd = f"{cmd} --model {shlex.quote(model)}"
    timeout = float(os.environ.get("VIBEOPS_PROVIDER_TIMEOUT", "0") or 0) or None
    start = time.time()
    telemetry.log_event("provider_call_start", provider="codex", model=model or "")
    telemetry.record_artifact("prompt.txt", prompt, subdir="codex")
    code, out, err = _run(cmd, prompt, timeout=timeout)
    elapsed_ms = int((time.time() - start) * 1000)
    telemetry.record_artifact("response.txt", out or "", subdir="codex")
    if err:
        telemetry.record_artifact("stderr.txt", err, subdir="codex")
    telemetry.log_event("provider_call_end", provider="codex", rc=code, duration_ms=elapsed_ms)
    if code != 0:
        hint = "Install the Codex CLI or set VIBEOPS_CODEX_CMD to your binary."
        raise ProviderError(f"Codex CLI failed: {err.strip()}\n{hint}")
    return out

def mock(prompt: str, model: str | None = None) -> str:
    """Mock provider for tests/CI: echoes metadata and a truncated prompt digest."""
    size = len(prompt)
    head = prompt[:200]
    return f"[MOCK PROVIDER]\nmodel={model or 'n/a'}\nbytes={size}\nhead=\n{head}"
