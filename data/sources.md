# Sourcing List — where to find internship / new-grad / program openings

Research date: 2026-07-22. Written for a new-grad SWE / AI / infra search. Adjust the filters below to
your own cycle, visa status, and target list in `config/settings.json`.

## How to use this file

A **source** finds openings. It is never where you apply. Mine a source, then apply on the company's
own ATS (Greenhouse / Lever / Ashby) per `config/spec.md`. Never apply through Handshake, LinkedIn
Easy Apply, or Simplify.

**Cycle:** mine the list that matches your graduation, and the one on either side of it. A December
graduate fits both the current cycle and the next one, and the lists are named by start year, not by
graduation year.

**Sponsorship filter:** if `settings.json` says you need sponsorship, any employer or program that
requires existing US work authorization is a dead end. Where a program's visa policy is known, it is
stated below.

---

## Tier 1 — Live job lists (mine these first, highest yield)

Every repo below was re-verified against the GitHub API on **2026-08-07**: it exists, is not
archived, and the `last push` column is real. Stars are a proxy for how many people are watching the
same list, which is also a proxy for how fast the good roles go.

| Repo | Stars | Last push | What it is |
|---|---:|---|---|
| [SimplifyJobs/Summer2027-Internships](https://github.com/SimplifyJobs/Summer2027-Internships) | 46.0k | 2026-08-07 | The canonical internship list. Simplify + Pitt CSC scrape career pages hourly. |
| [SimplifyJobs/New-Grad-Positions](https://github.com/SimplifyJobs/New-Grad-Positions) | 17.6k | 2026-08-07 | The canonical new-grad list. SWE, quant, PM. |
| [speedyapply/2027-SWE-College-Jobs](https://github.com/speedyapply/2027-SWE-College-Jobs) | 8.7k | 2026-08-06 | Daily, prioritizes postings from the last 120 days. See `NEW_GRAD_USA.md`. |
| [vanshb03/Summer2027-Internships](https://github.com/vanshb03/Summer2027-Internships) | 8.7k | 2026-08-06 | WeCracked + Resumes.fyi. |
| [ReaVNaiL/New-Grad-2024](https://github.com/ReaVNaiL/New-Grad-2024) | 6.2k | 2024-11-26 | **Stale, do not mine.** Listed so nobody re-adds it. |
| [speedyapply/2027-AI-College-Jobs](https://github.com/speedyapply/2027-AI-College-Jobs) | 6.0k | 2026-08-06 | AI/ML variant. Highest signal for lab and AI-startup roles. |
| [vanshb03/New-Grad-2027](https://github.com/vanshb03/New-Grad-2027) | 2.5k | 2026-08-05 | US, Canada, remote. |
| [northwesternfintech/2027QuantInternships](https://github.com/northwesternfintech/2027QuantInternships) | 2.4k | 2026-07-30 | The best quant list. Software and trading roles both. |
| [sndsh404/summer-2027-internships](https://github.com/sndsh404/summer-2027-internships) | 879 | 2026-08-03 | Includes off-season internships, which the big lists miss. |
| [zapplyjobs/Internships-2027](https://github.com/zapplyjobs/Internships-2027) | 173 | 2026-08-07 | Small but pushes several times a day. |
| [zapplyjobs/New-Grad-Jobs-2027](https://github.com/zapplyjobs/New-Grad-Jobs-2027) | 172 | 2026-08-07 | Broader than SWE: ops, business. |
| [zapplyjobs/New-Grad-Software-Engineering-Jobs-2027](https://github.com/zapplyjobs/New-Grad-Software-Engineering-Jobs-2027) | 53 | 2026-08-07 | SWE-only cut of the above. |

**Finding next year's lists when these age out:** the naming is predictable
(`<owner>/New-Grad-<year>`, `Summer<year>-Internships`), and
[github.com/topics/jobs-2027](https://github.com/topics/jobs-2027) collects them. Check the topic
page each August, verify with the API before trusting a repo, and add what survives.

```bash
# verify a list repo before mining it: exists, not archived, pushed recently
curl -s https://api.github.com/repos/<owner>/<repo> \
  | python3 -c "import json,sys; d=json.load(sys.stdin); print(d['full_name'], d['stargazers_count'], d['pushed_at'], 'ARCHIVED' if d['archived'] else 'active')"
```

---

## Tier 1b — Machine-readable feeds (query these from the shell, no browser)

These return JSON. They are the cheapest way to find a role, because you filter on location,
seniority, and compensation before a browser is ever involved. All verified working 2026-08-07.

**Hacker News "Who is hiring", via the Algolia API.** Posted the 1st of every month, and the best
source of startups that never touch a job board. Fully machine readable, no account.

```bash
# find the current thread
curl -s "https://hn.algolia.com/api/v1/search_by_date?tags=story,author_whoishiring&hitsPerPage=1&query=hiring"
# then pull every posting in it (the August 2026 thread had 195)
curl -s "https://hn.algolia.com/api/v1/items/<objectID>"

# or just run the wrapper, which does both and prints readable blocks
./scripts/fetch_hn_hiring.sh | grep -i "new grad"
```

**Per-company ATS APIs.** The org slug is the only unknown; `data/boards.md` has 235 verified ones.

| ATS | Endpoint | Verified example |
|---|---|---|
| Ashby | `https://api.ashbyhq.com/posting-api/job-board/<org>?includeCompensation=true` | `openai` → 745 postings |
| Greenhouse | `https://boards-api.greenhouse.io/v1/boards/<org>/jobs` | `databricks` → 815 postings |
| Lever | `https://api.lever.co/v0/postings/<org>?mode=json` | `palantir` → 301 postings |
| SmartRecruiters | `https://api.smartrecruiters.com/v1/companies/<org>/postings` | `Visa` → live (case-sensitive org) |
| Workable | `https://apply.workable.com/api/v1/widget/accounts/<org>?details=true` | endpoint live, org names differ from brand |

Greenhouse also serves a form that dodges cross-origin embeds:
`https://boards.greenhouse.io/embed/job_app?for=<org>&token=<job_id>`.

---


## Tier 2 — AI labs and research programs

The strongest category for an AI-leaning resume. Sponsorship varies sharply, so it is listed per program.

### Programs with known visa terms

Terms verified 2026-07-22. Record your own decision per program so the agent does not re-litigate it:

| Program | Terms | Visa | Decision |
|---|---|---|---|
| Anthropic **Claude Corps** | $85K/year, 12 months | US authorization only | Requires existing US work authorization, so a dead end if you need sponsorship. |
| **Anthropic Fellows** | $3,850/week, ~4 months | OPT/EAD eligible | Requires 3 references. Dead end unless you have people lined up. |
| **OpenAI Residency** | $18,333/month | Sponsors visas | Requires letters of recommendation. Same test as above. |
| **MATS** | $5K/month + $8K compute, 10–12 weeks, Berkeley & London | J-1 support | Open. Also needs references. https://www.matsprogram.org |
| **OpenAI Safety Fellowship** | Stipend + compute, 6 months | Global | Open — confirm reference requirement first. |

**Pattern to check before queuing any research program: does it require references or letters of
recommendation?** If you have none lined up, it is a dead end and the agent should skip it, not queue
it. Prefer programs and jobs that need only a resume plus application answers.

### Lab career pages to check directly

Anthropic, OpenAI, Google DeepMind, xAI, Meta AI (FAIR), Mistral, Cohere, Safe Superintelligence,
Thinking Machines, Perplexity, Scale AI, Sierra, Harvey, Figure, Physical Intelligence, Reflection,
Decagon, Cognition. Most run Greenhouse or Ashby, so they are directly submittable.

**AI-impact job board:** 80,000 Hours — https://jobs.80000hours.org — aggregates AI safety and
research roles across labs and nonprofits.

---

## Tier 3 — Quant firms (the money priority)

**Timing is the critical fact here.** Quant full-time and internship roles post **early fall**, and
Jane Street's applications open **July–August on a rolling basis** with Summer 2027 interview slots
often fully booked by **late October**. That window is open right now.

Target the **software / developer** roles at these firms, not trader or researcher roles, if your
resume is software. Firms like Five Rings and Aquatic post a dedicated SWE req alongside the trading
ones; it is easy to miss.

| Firm | Careers | Notes |
|---|---|---|
| Jane Street | https://www.janestreet.com/join-jane-street/ | Custom portal, not a standard ATS. Rolling. |
| Hudson River Trading | https://www.hudsonrivertrading.com/student-opportunities/ | Student page lists the campus reqs. |
| Five Rings | https://fiverings.com/careers/ | Campus SWE req requires a transcript upload. |
| Aquatic Capital | https://job-boards.greenhouse.io/aquaticcapitalmanagement | Form asks for math-competition history. |
| Citadel / Citadel Securities | https://www.citadel.com/careers/ | Custom portal. Separate campus track. |
| Optiver | https://optiver.com/working-at-optiver/career-opportunities/ | Greenhouse. Sponsors, states it in the posting. |
| IMC Trading | https://careers.imc.com | Highest pay of the three Dutch firms (IMC, Optiver, Flow Traders) |
| Flow Traders | https://www.flowtraders.com/careers | US engineering skews senior. |
| SIG | https://careers.sig.com | Custom portal. |
| Akuna Capital | https://akunacapital.com/careers | Accepts F-1 OPT/STEM OPT. One application per season, see ats-field-notes. |
| DRW | https://drw.com/careers | Check the graduation window before applying; it is narrow. |
| Jump Trading | https://www.jumptrading.com/careers/ | Greenhouse `jumptrading`. Campus track sponsors and accepts CPT/OPT. |
| Chicago Trading Company | https://www.chicagotrading.com/campus | Campus page. Form requires a street address. |
| Tower Research | https://www.tower-research.com/open-positions/ | Campus and experienced tracks are separate. |
| Old Mission | https://www.oldmissioncapital.com/careers/ | Routes assessments to the school email. |
| Two Sigma | https://careers.twosigma.com | Custom portal. |
| XTX Markets, Squarepoint, Radix, Headlands | company sites | No public Greenhouse/Ashby board; junior roles often London or Montreal. |

**Quant-specific boards:** https://openquant.co and https://www.tradermath.org/jobs

---

## Tier 4 — Fellowships and grants

Money and prestige, and several fund building a company directly. Worth queuing if starting your own
company is on the table.

| Program | What it gives | URL |
|---|---|---|
| **Thiel Fellowship** (the fellowship itself) | $250,000 over 2 years. **Do not auto-apply — the essays are personal, not a job application. Write them yourself.** | https://thielfellowship.org |
| **Thiel Fellowship jobs board** | Roles at Thiel-backed / past-fellow startups. **THIS is the agent-applyable part** — treat each listing as a normal company application. | https://thielfellowship.org/jobs |
| **Neo Scholars** | Mentorship network for exceptional CS undergrads, run by Ali Partovi. Not an accelerator — a talent network. | https://neo.com/scholars |
| **Kleiner Perkins Fellows** | 3-month paid placement at a top startup, plus $100K seed funding for fellows. 600+ alumni since 2012. | https://fellows.kleinerperkins.com |
| **Contrary** | Venture Partner program: ~20 accepted from ~1,500 applicants. Also a paid Research Fellowship for writing. | https://contrary.com · https://research.contrary.com/fellowship |
| **Interact Fellowship** | 50–100 technologists per year, funding plus community. | https://joininteract.com |
| **YC Summer Fellows** | $20K + ~$90K compute, no equity, for students building. | https://www.ycombinator.com |
| **South Park Commons** | Founder Fellowship, pre-idea funding. | https://www.southparkcommons.com |
| **On Deck** | Founder Fellowship (ODF). | https://www.beondeck.com |
| Emergent Ventures | Fast small grants for ambitious projects. | https://www.mercatus.org/emergent-ventures |

Record any program you have decided against in `settings.json` under `targets.skip_companies` so the
agent stops surfacing it.

---

## Tier 5 — VC portfolio job boards

Breadth across funded startups. Each links out to the company's own ATS, so they satisfy the
apply-on-company-ATS rule.

- **a16z** — https://portfoliojobs.a16z.com/jobs
- **Y Combinator, Work at a Startup** — https://www.workatastartup.com
- **Sequoia** — https://www.sequoiacap.com/jobs/
- **Greylock, Accel, Index, General Catalyst, Khosla, Lightspeed, Kleiner Perkins** — each hosts a
  portfolio board on its own site
- **Top Startups** — https://topstartups.io/jobs (filters by investor: Sequoia / YC / a16z)
- **Wellfound** — https://wellfound.com (startup roles; apply on company ATS where offered)

---

## Tier 6 — Company university hubs

Large companies gate new-grad roles behind a university page separate from the main board.

- **Stripe** — https://stripe.com/jobs/university — checked 2026-07-22: no US new-grad SWE role open;
  the only new-grad SWE was Toronto, which needs Canadian authorization. Revisit in fall.
- Also check the university/campus pages for: Databricks, Snowflake, Ramp, Plaid, Figma, Notion,
  Airbnb, Datadog, Rippling, Brex, Coinbase, Robinhood, Palantir, Nvidia, Netflix.

---

## Timing calendar

| When | What opens |
|---|---|
| **July–August (now)** | Jane Street rolling applications; quant firms begin posting 2027 roles |
| **Early fall (Sep–Oct)** | Peak new-grad and quant season; most 2027 full-time roles post |
| **Late October** | Jane Street Summer 2027 interview slots typically full — apply before this |
| **Fall** | Stripe and other big-company university roles typically post |
| **Rolling** | Anthropic Fellows, OpenAI Residency, MATS cohorts, Thiel, Neo |

---

## Standing rules (from `config/spec.md`)

1. Apply only on the company's own ATS. Sources above are for finding roles, never for applying.
2. Never Handshake, LinkedIn Easy Apply, or Simplify as an application channel.
3. Honor `settings.json` → `targets.skip_companies`.
4. Deprioritize employers that do not sponsor if `settings.json` says you need sponsorship.
5. Verify a posting is live immediately before applying; postings go stale within days.

## Sources

Verified during research on 2026-07-22:
[speedyapply/2027-SWE-College-Jobs](https://github.com/speedyapply/2027-SWE-College-Jobs) ·
[vanshb03/New-Grad-2027](https://github.com/vanshb03/New-Grad-2027) ·
[SimplifyJobs/New-Grad-Positions](https://github.com/SimplifyJobs/New-Grad-Positions) ·
[zapplyjobs/New-Grad-Jobs-2027](https://github.com/zapplyjobs/New-Grad-Jobs-2027) ·
[northwesternfintech/2027QuantInternships](https://github.com/northwesternfintech/2027QuantInternships) ·
[Anthropic Fellows](https://alignment.anthropic.com/2025/anthropic-fellows-program-2026/) ·
[OpenAI Residency](https://openai.com/residency/) ·
[MATS Autumn 2026](https://www.matsprogram.org/program/autumn-2026) ·
[Thiel Fellowship](https://thielfellowship.org/) ·
[Kleiner Perkins Fellows](https://fellows.kleinerperkins.com/) ·
[Contrary Research Fellowship](https://research.contrary.com/fellowship) ·
[Interact](https://joininteract.com/) ·
[a16z Portfolio Jobs](https://portfoliojobs.a16z.com/jobs) ·
[Top Startups](https://topstartups.io/jobs/) ·
[HRT Student Opportunities](https://www.hudsonrivertrading.com/student-opportunities/) ·
[Five Rings Careers](https://fiverings.com/careers/) ·
[OpenQuant](https://openquant.co/)
