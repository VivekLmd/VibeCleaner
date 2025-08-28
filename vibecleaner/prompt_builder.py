import json
from pathlib import Path
from typing import Dict

MODES = {"discovery", "design", "mvp", "production"}

def build_prompt(base_dir: Path, mode: str, ticket_text: str, extra_context: Dict) -> str:
    if mode not in MODES:
        raise ValueError(f"Unknown mode: {mode}")

    prompts_dir = base_dir / "templates" / "prompts"
    mode_file = {
        "discovery": "discovery.md",
        "design": "design.md",
        "mvp": "mvp.md",
        "production": "production.md",
    }[mode]

    system_rules = (base_dir / "config" / "agents.yaml").read_text(encoding="utf-8")
    constraints_py = (base_dir / "config" / "constraints-python.txt").read_text(encoding="utf-8")
    constraints_node = (base_dir / "config" / "constraints-node.txt").read_text(encoding="utf-8")
    stack = (base_dir / "config" / "stack.md").read_text(encoding="utf-8")
    rules = (base_dir / "config" / "rules.md").read_text(encoding="utf-8")
    mode_prompt = (prompts_dir / mode_file).read_text(encoding="utf-8")

    header = f"""### VIBECLEANER CONTEXT (Do not ignore)
- MODE: {mode.upper()}
- RULES (agents.yaml):
{system_rules}

- STACK (current project reality; prefer this over your own training cutoff):
{stack}

- CONSTRAINTS (hard pins; **never** upgrade or invent versions):
Python:
{constraints_py}

Node.js:
{constraints_node}

- HOUSE RULES:
{rules}

### TICKET / TASK
{ticket_text}

### MODE PROMPT
{mode_prompt}

### OUTPUT REQUIREMENTS
- Respect MODE. If production: no breaking changes; add/extend tests; propose ADR for any risky migration.
- Use the stack/constraints above. Do not cite or depend on your own (model) cutoff knowledge for versions.
- Be explicit about files to create/modify with clear diffs or code blocks.
- Keep code simple and maintainable.
"""
    if extra_context:
        header += "\n### EXTRA CONTEXT\n" + json.dumps(extra_context, indent=2)

    return header
