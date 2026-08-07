# Vetted Application Queue (template)

Copy to `data/queue.md`. This is the agent's working checklist: it reads it top-down, verifies each
posting is still live, applies, and marks it. Anything not in this file, the agent finds itself from
`data/sources.md`, then appends here.

Rule that never bends: **the queue only ever contains links to a company's own ATS**
(Greenhouse, Lever, Ashby, Workable, or the company's career portal). Never an aggregator.

Status legend: `[ ]` pending · `[x]` submitted · `[~]` needs human · `[-]` skipped.

## Next up
One line per target. Include everything the agent needs so it does not have to re-research:

- [ ] Company | Role title (Location) | **$comp band if posted.** ATS org slug + req id.
  One sentence on why it clears your gate, plus any gotcha (years requirement, sponsorship policy,
  form quirk). Link to the posting.

Worked example of the shape:

- [ ] Example Labs | Software Engineer, Product (San Francisco) | **$180K-$300K plus equity.**
  Ashby `examplelabs`, req `e2d3e1f5-03cb-4e18-9f3d-a32f0bb6ff91`. No years gate, sponsors visas,
  posting says all qualifications are preferred. https://jobs.ashbyhq.com/examplelabs/e2d3e1f5

## Already applied
The agent maintains this section itself and checks it before every application, alongside
`applications/` and `logs/applications-log.md`. Three-way duplicate check, every time.

- [x] Example Labs | Software Engineer, Product | 2027-01-15 | SUBMITTED

## Skipped, with the reason
Keeping the reason stops the agent from re-researching the same dead end next run.

- [-] Another Co | Backend Engineer | requires 5+ years, hard mismatch
- [-] Some Startup | Founding Engineer | US citizens only

## Blocked, needs you
- [~] Third Co | Deployed Engineer | form requires a graded take-home; tab left open
