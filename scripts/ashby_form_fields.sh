#!/bin/bash
# Enumerate an Ashby application form BEFORE opening a browser tab.
#   ./scripts/ashby_form_fields.sh <org-slug> <job-posting-id>
# Prints every field with REQUIRED/optional, its type, and its selectable options.
#
# Why this exists: a screening gate ("Do you have 5 or more years...") can live ONLY in the
# application form, invisible to any board-API sweep of descriptions. Found 2026-09-03.
#
# API notes learned the hard way:
#   - the section field is `fieldEntries`; `formDefinition`, `fields`, `formFields`, `entries`
#     and `descriptors` all fail
#   - `field` is a JSON scalar (title/type/selectableValues), so it takes NO selection set
#   - GraphQL introspection is disabled on this endpoint
#
# Greenhouse equivalent (no helper needed):
#   curl -s "https://boards-api.greenhouse.io/v1/boards/<token>/jobs/<id>?questions=true"
set -euo pipefail
[ $# -eq 2 ] || { echo "usage: $0 <org-slug> <job-posting-id>" >&2; exit 2; }
curl -s -m 25 'https://jobs.ashbyhq.com/api/non-user-graphql?op=ApiJobPosting' \
  -H 'content-type: application/json' \
  --data "{\"operationName\":\"ApiJobPosting\",\"variables\":{\"organizationHostedJobsPageName\":\"$1\",\"jobPostingId\":\"$2\"},\"query\":\"query ApiJobPosting(\$organizationHostedJobsPageName: String!, \$jobPostingId: String!) { jobPosting(organizationHostedJobsPageName: \$organizationHostedJobsPageName, jobPostingId: \$jobPostingId) { applicationForm { sections { title fieldEntries { field isRequired } } } } }\"}" \
 | python3 -c "
import json,sys
d=json.load(sys.stdin)
try: secs=d['data']['jobPosting']['applicationForm']['sections']
except Exception: print('ERR', json.dumps(d)[:500]); sys.exit(1)
for s in secs:
    print('##', s.get('title') or '(main)')
    for fe in s['fieldEntries']:
        f=fe['field']
        req='REQUIRED' if fe['isRequired'] else 'optional'
        sel=f.get('selectableValues') or []
        opts=' :: '+(' | '.join(x.get('label','') for x in sel)) if sel else ''
        print(f\"   [{req:8}] {str(f.get('type')):16} {f.get('title')}{opts}\")
"
