#!/usr/bin/env python3
"""Turn a directory of probed ATS payloads into data/boards.md.

Called by scripts/probe_boards.sh, which sets WORK to a directory holding
ash/<slug>.json and gh/<slug>.json. Standard library only.
"""
import json, os, glob, re, datetime

WORK = os.environ.get("WORK")
if not WORK or not os.path.isdir(WORK):
    raise SystemExit("WORK must point at a directory containing ash/ and gh/ payloads")

US_RE = re.compile(
    r'\b(US|USA|United States|CA|NY|CO|WA|TX|IL|MA|Remote)\b|San Francisco|New York|Seattle|'
    r'Austin|Chicago|Boston|Palo Alto|Mountain View|Menlo Park|Redwood|San Jose|Los Angeles|'
    r'Denver|Bay Area', re.I)


def read(path, ats):
    """-> (job_count, us_count, publishes_band). (0, 0, False) if dead or unparseable."""
    try:
        jobs = json.load(open(path)).get("jobs", [])
    except Exception:
        return 0, 0, False
    us = 0
    band = False
    for j in jobs:
        loc = j.get("location") or "" if ats == "ashby" else (j.get("location") or {}).get("name") or ""
        if US_RE.search(loc):
            us += 1
        if ats == "ashby":
            comp = j.get("compensation") or {}
            if comp.get("compensationTierSummary"):
                band = True
    return len(jobs), us, band


def collect(subdir, ats):
    rows = []
    for f in glob.glob(os.path.join(WORK, subdir, "*.json")):
        slug = os.path.basename(f)[:-5]
        n, us, band = read(f, ats)
        if n:
            rows.append((slug, n, us, band))
    rows.sort(key=lambda r: -r[1])
    return rows


ashby = collect("ash", "ashby")
gh = collect("gh", "greenhouse")
today = datetime.date.today().isoformat()
bt = chr(96)

L = [
    "# Live ATS boards",
    "",
    f"Every org slug this project has ever touched, re-probed against the ATS APIs on **{today}**.",
    "A board appears here only if it returned at least one posting that day. This exists to save",
    "you the slug-guessing game described in `data/ats-field-notes.md`, and to give a new install",
    "somewhere concrete to start sourcing.",
    "",
    "Regenerate with `./scripts/probe_boards.sh`. Boards die and come back, so re-probe rather than",
    "trusting this file forever. Requests are paced on purpose: live orgs return unparseable bodies",
    "under rate limiting and read as dead.",
    "",
    "```bash",
    'curl -s "https://api.ashbyhq.com/posting-api/job-board/<slug>?includeCompensation=true"',
    'curl -s "https://boards-api.greenhouse.io/v1/boards/<slug>/jobs"',
    'curl -s "https://api.lever.co/v0/postings/<slug>?mode=json"',
    "```",
    "",
    "`jobs` is every posting on the board. `US` counts postings whose location string looks United",
    "States based. `band` means at least one posting publishes a compensation range in the API,",
    "which tells you whether a comp filter will work without reading body text.",
    "",
    f"## Ashby ({len(ashby)} live boards)",
    "",
    "| slug | jobs | US | band |",
    "|---|---:|---:|:--:|",
]
L += [f"| {bt}{s}{bt} | {n} | {u} | {'yes' if b else ''} |" for s, n, u, b in ashby]
L += [
    "",
    f"## Greenhouse ({len(gh)} live boards)",
    "",
    "| slug | jobs | US |",
    "|---|---:|---:|",
]
L += [f"| {bt}{s}{bt} | {n} | {u} |" for s, n, u, _ in gh]
L += [
    "",
    "## Not listed",
    "",
    "A slug missing from this file was dead, renamed, or never on that ATS on the probe date.",
    "Before writing one off, try the variants in `data/ats-field-notes.md`: `fal` against",
    "`fal-ai`, `sierra` against `sierraai`, Greenhouse against Ashby for the same company.",
]

with open("data/boards.md", "w") as f:
    f.write("\n".join(L) + "\n")
print(f"data/boards.md: {len(ashby)} Ashby + {len(gh)} Greenhouse boards")
