#!/usr/bin/env python3
"""PreToolUse guard for the Chrome tools: block any text about to go into a form that speaks as the
tool instead of the candidate ("wrote with AI", "Here's a", a word count, markdown), or that carries
a canary word a posting planted for AI readers (state/canary-words.txt, written by
`app_docs.py scan-posting`). Policy runs here so it holds even when a run forgets the rules."""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
from app_docs import LEAK_RES, CANARY_FILE  # noqa: E402

# Markdown patterns would misfire on JavaScript source, so code only gets the prose checks.
PROSE_RES = [r for r in LEAK_RES if "\\*\\*" not in r]


def typed_strings(node, key=None, code=False):
    """Values the tool will put on the page: `text` of type actions, `value` of form_input,
    recursing into browser_batch action lists."""
    if isinstance(node, dict):
        if node.get("action") == "key":
            return
        for k, v in node.items():
            yield from typed_strings(v, k, code)
    elif isinstance(node, list):
        for v in node:
            yield from typed_strings(v, key, code)
    elif isinstance(node, str) and key in ("code", "script", "function"):
        yield "code", node
    elif isinstance(node, str) and key in ("text", "value"):
        yield ("code" if code else "text"), node


def main():
    data = json.load(sys.stdin)
    canaries = []
    if CANARY_FILE.is_file():
        canaries = [w for w in CANARY_FILE.read_text().split("\n") if w.strip()]
    hits = []
    is_js = re.search(r"javascript|evaluate_script", data.get("tool_name", ""))
    for kind, s in typed_strings(data.get("tool_input", {}), code=bool(is_js)):
        for r in (LEAK_RES if kind == "text" else PROSE_RES):
            hits += [m.group(0).strip() for m in re.finditer(r, s, re.I | re.M)]
        hits += [w for w in canaries if re.search(r"\b" + re.escape(w) + r"\b", s, re.I)]
    if hits:
        print("Blocked by .claude/hooks/block-ai-leaks.py: this text speaks as the tool or carries a "
              "posting's AI canary: " + ", ".join(f'"{h}"' for h in hits[:5]) + ". Rewrite it as the "
              "candidate, or leave the field for the user (NEEDS HUMAN).", file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()
