#!/bin/bash
# Duplicate check for ONE company. Run this BEFORE opening a tab. Exit 1 = read the hits, do not
# apply until you have counted them.
#   ./scripts/dupe_check.sh "Acme Capital" [req-id-or-job-id]
#
# WHY THIS EXISTS: one run sent THREE duplicate applications because the check grepped only `### `
# header lines in logs/applications-log.md plus applications/ filenames. All three prior applications
# were recorded somewhere else: a `- [x]` checklist line in data/queue.md (older than the `### ` format)
# and run-SUMMARY bullets in the log.
# RULE: search EVERY record. The log's `### ` headers are NOT the record.
# Exit 3 = the company is in the user's interview tracker: HARD SKIP, stop.
set -uo pipefail
[ $# -ge 1 ] || { echo "usage: $0 \"<Company Name>\" [req-or-job-id]" >&2; exit 2; }
NAME="$1"; REQ="${2:-}"
hit=0
sec () { printf '\n=== %s ===\n' "$1"; }

# ★ INTERVIEW TRACKER FIRST. A hit here is a HARD SKIP, not something to count. Added after a run filled a
# second req at a company where an interview was already on the calendar. Match on the first word of the
# name too: the tracker may say "Acme Tech" while the log says "Acme Technologies".
TRACKER=$(python3 -c 'import json;print(json.load(open("config/settings.json"))["run"].get("interview_tracker_path",""))' 2>/dev/null)
if [ -n "$TRACKER" ] && [ -f "$TRACKER" ]; then
  FIRST="${NAME%% *}"
  PAT="$NAME"; [ ${#FIRST} -ge 4 ] && PAT="$FIRST"
  sec "INTERVIEW TRACKER ($TRACKER) — grep \"$PAT\""
  if grep -in -- "$PAT" "$TRACKER"; then
    echo
    echo "★★★ \"$NAME\" is in your interview tracker. HARD SKIP. Do not open a tab, do not count, do not ask."
    exit 3
  fi
  echo "(not in tracker)"
elif [ -n "$TRACKER" ]; then
  echo "WARNING: run.interview_tracker_path is set but the file is missing: $TRACKER" >&2
fi

sec "logs/applications-log.md — EVERY line, not just ### headers"
grep -in -- "$NAME" logs/applications-log.md && hit=1

sec "data/queue.md — the checklist; holds the oldest applications"
grep -in -- "$NAME" data/queue.md && hit=1

sec "state/status.md"
grep -in -- "$NAME" state/status.md && hit=1

sec "data/boards.md — records 'AT THE CAP' verdicts"
grep -in -- "$NAME" data/boards.md && hit=1

sec "data/ats-field-notes.md — per-company limits and reset dates"
grep -in -- "$NAME" data/ats-field-notes.md && hit=1

sec "applications/ filenames"
ls applications 2>/dev/null | grep -i -- "$(echo "$NAME" | tr ' ' '-')" && hit=1
ls applications 2>/dev/null | grep -i -- "$(echo "$NAME" | tr -d ' ')" && hit=1

sec "screenshots/ filenames — an independent record; a submit can exist ONLY here"
ls screenshots 2>/dev/null | grep -i -- "$(echo "$NAME" | tr ' ' '-')" && hit=1
ls screenshots 2>/dev/null | grep -i -- "$(echo "$NAME" | tr -d ' ')" && hit=1

if [ -n "$REQ" ]; then
  sec "req/job id \"$REQ\" across the whole repo"
  grep -rin -- "$REQ" logs/ data/ state/ applications/ 2>/dev/null && hit=1
fi

printf '\n'
if [ "$hit" -eq 1 ]; then
  echo "★ HITS FOUND for \"$NAME\". READ THEM. Count prior applications, match the role TITLE and the"
  echo "  req id, and look for any 'AT THE CAP' / 'spent' / 'one role only' verdict before applying."
  exit 1
fi
echo "No record of \"$NAME\" anywhere. Clean."
