import subprocess, json
from pathlib import Path

class GHError(RuntimeError): pass

def _run_args(args: list[str], input_text: str | None = None):
    proc = subprocess.Popen(args,
                            stdin=subprocess.PIPE if input_text else None,
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    out, err = proc.communicate(input_text)
    if proc.returncode != 0:
        raise GHError(err.strip())
    return out

def ensure_labels(repo: str, labels: list[str]):
    # Fetch all labels (paginate) in a cross-platform-safe way
    out = _run_args(["gh", "api", f"repos/{repo}/labels", "--paginate", "-q", ".[].name"])
    existing = {line.strip() for line in out.splitlines() if line.strip()}
    for name in labels:
        if name in existing: 
            continue
        try:
            _run_args(["gh", "api", f"repos/{repo}/labels", "-X", "POST",
                      "-f", f"name={name}", "-f", "color=ededed"])
            print(f"[labels] created '{name}'")
        except GHError as e:
            print(f"[labels] warn: {name}: {e}")

def create_issue(repo: str, title: str, body: str, labels: list[str] | None = None, assignees: list[str] | None = None):
    args = ["gh","issue","create","--repo",repo,"--title",title,"--body",body]
    if labels:
        for l in labels: args += ["--label", l]
    if assignees:
        for a in assignees: args += ["--assignee", a]
    proc = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    out, err = proc.communicate()
    if proc.returncode != 0:
        raise GHError(err.strip())
    print(out.strip())  # prints issue URL
