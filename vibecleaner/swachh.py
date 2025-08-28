import re
from pathlib import Path

TARGET_EXTS = {".py", ".js", ".ts", ".tsx", ".jsx", ".md", ".json", ".yaml", ".yml"}

def scan_repo(root: Path):
    problems = []
    for p in root.rglob("*"):
        if p.is_dir():
            continue
        if p.suffix.lower() in TARGET_EXTS:
            try:
                text = p.read_text(encoding="utf-8", errors="ignore")
            except Exception:
                continue
            if "<<<<<<< HEAD" in text or ">>>>>>>" in text:
                problems.append((p, "git-merge-conflict-markers"))
            if re.search(r"\bTODO\b|\bFIXME\b|\bHACK\b", text):
                problems.append((p, "todo/fixme/hack markers present"))
            if re.search(r"api_key\s*=\s*['\"][A-Za-z0-9_\-]{12,}['\"]", text):
                problems.append((p, "possible hardcoded secret (api_key=...)"))
            # Flag potential debug prints conservatively to reduce false positives
            if p.suffix in {".js", ".ts", ".tsx", ".jsx"} and "console.log(" in text:
                problems.append((p, "console.log present (debug print?)"))
            if p.suffix == ".py":
                # Only flag print() if it appears to be a debug message
                for line in text.splitlines():
                    if "print(" in line and ("debug" in line.lower() or "todo" in line.lower()):
                        problems.append((p, "print() debug/todo message present"))
                        break
            if text.count("\n") > 2000:
                problems.append((p, f"file very long (~{text.count('\n')} lines)"))
    return problems

def main():
    root = Path(".").resolve()
    problems = scan_repo(root)
    if not problems:
        print("Swachh check: no obvious issues found ✅")
        return 0
    print("Swachh check: potential issues:")
    for p, msg in problems:
        print(f" - {p}: {msg}")
    return 1

if __name__ == "__main__":
    raise SystemExit(main())
