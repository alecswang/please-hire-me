#!/usr/bin/env bash
# Re-verify every ATS org slug and rewrite data/boards.md.
#
#   ./scripts/probe_boards.sh                 # re-probe every slug in data/slug-candidates.txt
#   ./scripts/probe_boards.sh extra-slugs.txt # probe those too (one slug per line)
#
# Boards die and come back, so run this before a big sourcing session. It takes a few
# minutes: requests are paced because live orgs return unparseable bodies under rate
# limiting and read as dead.
set -uo pipefail
cd "$(dirname "$0")/.."

WORK="$(mktemp -d)"; trap 'rm -rf "$WORK"' EXIT
mkdir -p "$WORK/ash" "$WORK/gh"
SLUGS="$WORK/slugs.txt"

{
  grep -v '^#' data/slug-candidates.txt 2>/dev/null
  grep -o '^| `[a-z0-9-]*`' data/boards.md 2>/dev/null | tr -d '|` '
  [ $# -ge 1 ] && [ -f "$1" ] && cat "$1"
} | sed '/^$/d' | sort -u > "$SLUGS"

TOTAL=$(wc -l < "$SLUGS" | tr -d ' ')
echo "Probing $TOTAL slugs against Ashby and Greenhouse. This takes a few minutes."

probe_one() {
  local s="$1"
  curl -s -m 15 "https://api.ashbyhq.com/posting-api/job-board/$s?includeCompensation=true" -o "$WORK/ash/$s.json"
  curl -s -m 15 "https://boards-api.greenhouse.io/v1/boards/$s/jobs" -o "$WORK/gh/$s.json"
}

i=0
while read -r s; do
  probe_one "$s"
  i=$((i+1))
  [ $((i % 25)) -eq 0 ] && echo "  $i / $TOTAL"
  sleep 0.6
done < "$SLUGS"

echo "Second pass over the misses (catches rate-limit false negatives)..."
while read -r s; do
  python3 -c "import json,sys; json.load(open('$WORK/ash/$s.json')).get('jobs')" 2>/dev/null || {
    sleep 1.5
    curl -s -m 15 "https://api.ashbyhq.com/posting-api/job-board/$s?includeCompensation=true" -o "$WORK/ash/$s.json"
  }
done < "$SLUGS"

WORK="$WORK" python3 scripts/render_boards.py
echo "Rewrote data/boards.md"
