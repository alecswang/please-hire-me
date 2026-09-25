#!/usr/bin/env python3
"""Print the company names in the user's interview tracker, one per line.

Reads run.interview_tracker_path from config/settings.json (or a path given as argv[1]).
A company is any Obsidian wikilink target, with alias and heading parts dropped:
    [[Akuna Capital]]            -> Akuna Capital
    [[Candid Labs|Candid labs]]  -> Candid Labs      (alias after | ignored)
    Space [[xAI|xai]]            -> xAI              (text outside the brackets ignored)
    [[Acme Tech#Notes]]         -> Acme Tech        (heading after # ignored)
Text that is not wikilinked is NOT a company. Wikilink every company in the tracker.
Exit 1 if the tracker is set but unreadable, so callers fail closed.
"""
import json, re, sys

LINK = re.compile(r"\[\[([^\]|#]+)(?:[|#][^\]]*)?\]\]")

def names(text):
    seen, out = set(), []
    for m in LINK.finditer(text):
        n = m.group(1).strip()
        if n and n.lower() not in seen:
            seen.add(n.lower()); out.append(n)
    return out

def main():
    if len(sys.argv) > 1:
        path = sys.argv[1]
    else:
        path = json.load(open("config/settings.json")).get("run", {}).get("interview_tracker_path", "")
    if not path:
        return 0
    try:
        text = open(path, encoding="utf-8").read()
    except OSError as e:
        print(f"ERROR: interview tracker unreadable: {path} ({e})", file=sys.stderr)
        return 1
    for n in names(text):
        print(n)
    return 0

if __name__ == "__main__":
    sys.exit(main())
