#!/usr/bin/env bash
# Pull the current Hacker News "Who is hiring?" thread as plain text, one posting per block.
#
#   ./scripts/fetch_hn_hiring.sh              # current month's thread
#   ./scripts/fetch_hn_hiring.sh | grep -i "new grad"
#   ./scripts/fetch_hn_hiring.sh 48747976     # a specific thread id
#
# HN's monthly thread is the best source of startups that never post to a job board.
# Roles here almost always link straight to the company's own ATS, which is the only
# channel this project applies through.
set -uo pipefail

ID="${1:-}"
if [ -z "$ID" ]; then
  ID="$(curl -s -m 20 "https://hn.algolia.com/api/v1/search_by_date?tags=story,author_whoishiring&hitsPerPage=1&query=hiring" \
        | python3 -c "import json,sys; h=json.load(sys.stdin)['hits']; print(h[0]['objectID'] if h else '')")"
fi
if [ -z "$ID" ] || ! [ "$ID" -ge 0 ] 2>/dev/null; then
  echo "Could not resolve a thread id." >&2
  exit 1
fi

curl -s -m 30 "https://hn.algolia.com/api/v1/items/$ID" | python3 -c '
import json, sys, re, html

d = json.load(sys.stdin)
title = d.get("title") or "HN Who is hiring"
kids = d.get("children", [])
print("# %s  (thread %s)" % (title, d["id"]))
print("# %d postings\n" % len(kids))


def clean(t):
    t = re.sub(r"<p>", "\n", t or "")
    t = re.sub(r"<[^>]+>", "", t)
    return html.unescape(t).strip()


for c in kids:
    body = clean(c.get("text"))
    if not body:
        continue
    print("-" * 72)
    print(body)
    print("[https://news.ycombinator.com/item?id=%s]" % c["id"])
'
