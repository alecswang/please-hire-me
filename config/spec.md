# Run Spec

The contract for one run. `CLAUDE.md` is the how (browser method, widget recipes);
this file is the what (rules, per-application procedure, log format). Every value comes from
`config/settings.json`, `config/profile.json`, and `config/answers.md`. Never guess.

## Run config
Read from `config/settings.json`:
- `run.max_applications_per_run` — hard cap. The launcher passes it in the prompt; an argument to
  `./run.sh` overrides it.
- `run.dry_run` — **contributor flag, absent from the default config on purpose.** When present and
  true, fill and verify and screenshot every form, then close the tab WITHOUT submitting, and log
  the application as DRY RUN. It exists so contributors can iterate against real forms without
  sending anything. Do not offer it to a user as a way to run: a run that cannot submit burns a
  real posting and teaches them nothing the supervised checkpoint does not.
- `run.daily_application_target` / `run.max_applications_per_day` — the day's goal and hard ceiling,
  counted across every run that day (see "Daily pacing" below). Whichever of the per-run cap and the
  remaining daily allowance is smaller wins.
- `sourcing.*` — whether broad sweeps are allowed and whether methods must rotate (see "Sourcing
  discipline" below).
- `targets.*` — roles, seniority, locations, compensation floors, years-of-experience ceiling,
  the user's own quality bar, priority list, skip list. Note `min_annual_comp_usd` is a
  full-time floor; internships are judged by `internship_min_hourly_usd`.
- `eligibility.*` — sponsorship need, start window, graduation.
- `channels.*` — which ATS platforms are allowed, which aggregators are banned.
- `safety.*` — the hard rules below.

Sources for finding roles: company career pages (Greenhouse / Lever / Ashby / Workable preferred)
and login-free job boards. Applying happens only on the company's own ATS.

## Hard rules
1. **Never fabricate.** Only facts from `config/profile.json` and `config/answers.md`. A required
   field with no preset → log NEEDS HUMAN, leave the form, move on.
2. **Never create accounts, enter passwords, or solve interactive CAPTCHA challenges** (checkbox
   "I'm not a robot" plus image puzzles) → those are NEEDS HUMAN. Passive reCAPTCHA v3 (no
   challenge, just a hidden score) is NOT a challenge: submit through it normally using genuine
   trusted input, which passes. Never fake behavior to beat a detector. Workday usually needs an
   account, so expect to skip most Workday. Login codes count as passwords. The one code the agent may
   enter is a post-Submit email verification code (Greenhouse), pasted through `scripts/code_broker.py`
   without the agent seeing it. Procedure in CLAUDE.md under "Signed-in portals".
3. **EEO, demographic, veteran, and disability questions** come from the presets in
   `config/answers.md`. No preset → decline to self-identify where the form allows it, otherwise
   NEEDS HUMAN.
4. **Legal questions** (visa, work authorization, age, relocation) come only from presets.
5. **One application per company per run** unless the settings say otherwise. Check
   `applications/`, `data/queue.md`, and `logs/applications-log.md` first.
6. **Ambiguous form → skip and log.** An unsent application costs nothing. A wrong one costs the
   company a real review and costs the user their name on it.
7. **HARD ELIGIBILITY MISMATCH → SKIP, not NEEDS HUMAN.** If the posting requires something the
   user structurally cannot meet, it is out of scope: skip it, log one line, move on. This covers
   a graduation window that excludes theirs, a years-of-experience minimum above the settings
   ceiling, a required stack they lack, a US-citizen / US-person / clearance / ITAR rule when they
   are not eligible, and a residency requirement they cannot meet.
   NEEDS HUMAN is ONLY for a role the user IS eligible for that is missing a fact they could
   supply: an address, a notice period, a personal-history answer, a preference. If no additional
   fact could make them eligible, it is a skip.
8. **A graded work sample, a "please don't use AI" essay, or a question testing the candidate's
   knowledge is NEEDS HUMAN.** Fill everything else, leave the tab open, log it clearly.
9. **Never hand over sensitive financial or identity data.** No SSN (full or partial), bank account or
   routing number, credit/debit card, government ID number or ID upload (passport, driver's license,
   state ID), date of birth, or any payment, ever, by the agent. These are not in `profile.json` and
   must never be added there. A legitimate employer asks for them only after an offer (I-9, payroll,
   background-check vendor), and that step is always the user's. See "Scam and data-harvesting screen".

## Daily pacing
- Count today's SUBMITTED entries in `logs/applications-log.md` before the first application of a run.
  At `run.max_applications_per_day` (default 10), submit nothing more today: log one line and end.
- `run.daily_application_target` (default 5) is a goal for STRONG applications, not a quota. **Never
  lower the fit bar, widen locations, stretch the years ceiling, or accept a weak employer to reach it.**
- When strong matches run out, stop for the day, even at zero. Record in `state/status.md` which
  sources were exhausted so the next day starts somewhere else.

## Sourcing discipline
- **Prefer the employer's own career page or a verified ATS board** (Greenhouse, Lever, Ashby,
  Workable, or a portal the company's own site links to). Job boards (LinkedIn, Indeed, list feeds) are
  sources for leads only.
- **Verify remote and location on the employer's own posting.** A LinkedIn or Indeed "Remote" label is
  not evidence: on 2026-10-07 most LinkedIn "remote" results were on-site reqs (PowerSchool Dallas,
  Applied Systems Chicago/Dallas/Toronto, Imprivata St. Petersburg).
- **When `sourcing.broad_sweeps` is false**, do not run `delta_sweep.py`, `portal_sweep.py`, or
  multi-page scans. Work one employer board or one single-page search at a time, stop at the first
  strong match, apply (or skip), then look for the next.
- **When `sourcing.rotate_methods` is true**, do not run the same search method twice in a row. Rotate
  between employer boards, a narrow LinkedIn search, `list_sweep.py`, and Indeed (source only). Write
  the method and the boards checked into the run's status block so the next run picks different ones.

## Scam and data-harvesting screen
Run this before opening a form (posting checks) and again while filling (form checks). A hit means
**do not fill further and do not submit**.

**SKIP and log one line** (out of scope, no question for the user):
- The employer or its domain cannot be verified: the posting is not on the company's own domain or on
  an ATS board whose slug matches the company, and the company's own site does not link to it.
- The employer or end client is hidden ("a leading Fortune 500 client", "confidential company"), or a
  staffing firm does not name the client and the relationship is unclear.
- The job requires buying equipment, depositing or forwarding checks, handling cryptocurrency or gift
  cards, or sending money for any reason, including "training" or "equipment" fees repaid from pay.
- Compensation is implausibly high for the role while the duties are vague (e.g. "$150K entry-level,
  no experience, flexible hours, simple data tasks").
- Commission-only, unpaid, or training-repayment terms (already a settings skip).

**STOP for user review** (log `NEEDS HUMAN — SCAM-CHECK` with the URL and the exact wording, leave
every sensitive field blank, keep the tab open only if the user should see it):
- Any field asks for an SSN, bank or routing number, card number, government ID number or upload, or
  date of birth, or any payment, before a legitimate post-offer stage.
- A recruiter claims to represent a company but writes from a free or unrelated email domain (gmail,
  outlook, yahoo, a lookalike domain), or asks to move to Telegram, WhatsApp, Signal, or text chat.
- The form appears designed mainly to collect personal data: little or no job detail, no real
  employer behind it, but asks for full address, DOB, ID, references' contact details, or similar.

Form check, read-only, before typing anything into a form:
```js
[...document.querySelectorAll('label,legend,[aria-label],input[placeholder]')]
  .map(e => e.innerText || e.getAttribute('aria-label') || e.placeholder || '')
  .filter(t => /social security|\bssn\b|bank|routing|account number|credit card|debit card|card number|cvv|passport|driver'?s licen[cs]e|government[- ]issued|state id|date of birth|\bdob\b|payment|deposit/i.test(t))
```
Any non-empty result is a STOP. A field mentioning a "bank" or "payment" as an employer/industry name
is a false positive the agent may clear only by quoting it to the user.

## Per-application procedure
1. Find the posting. Confirm the role matches `targets`, is not on the skip list, and is not
   already in `applications/` / `data/queue.md` / `logs/applications-log.md`. Verify the URL is
   LIVE — postings rot within days, and a req id from a previous run can be dead. Confirm the
   employer and the location on the employer's own posting, check today's count against
   `run.max_applications_per_day`, and run the posting checks of the "Scam and data-harvesting
   screen". When the form opens, run its form check before typing anything.
2. Upload the resume from the path in `config/profile.json` using `file_upload`. Pick the closest
   template in `config/answers.md` for any free text.
3. Fill EVERY field with the `computer` tool (trusted input) on the real Chrome. Presets only.
4. Verify 0 invalid required fields (`aria-invalid`) and dump the field values with a read-only
   eval. BEFORE submit: append the log line to `logs/applications-log.md` AND write
   `applications/<company>-<role>.md` with every question, every answer, the URL, and the date.
5. Submit with a real trusted click. Save a confirmation screenshot (JPG) directly into
   `screenshots/`. Never record or export GIFs, and never touch `~/Downloads`. Mark the per-app doc
   and the log SUBMITTED with the date.
6. Blocked at any point (login wall, interactive CAPTCHA, missing preset, missing file) → NEEDS
   HUMAN with details in the per-app doc and the log, then move on.
7. **Tab hygiene (safety):** the extension has its OWN isolated MCP tab group. Only ever close or
   navigate tabs that `tabs_context_mcp` lists for that group; never the user's other tabs. At run
   start, close leftover job-application tabs from prior crashed runs and work in ONE reused tab.
   After each company, navigate that tab straight to the next posting so no half-filled form is
   left. If the tab group drops mid-fill, reconnect, abandon the partial form, and restart that
   company from a clean tab.
8. **MANDATORY LAST STEP — close the tab group.** Do not park a tab on `about:blank`; a blank tab
   keeps the group visible in Chrome. Call `tabs_context_mcp`, `tabs_close_mcp` on EVERY tab id it
   lists, then call `tabs_context_mcp` once more and confirm it returns "No tab group exists for
   this session." Run this even when the run submitted nothing. Sole exception: a form intentionally
   left open for the user. Keep that one tab, close the rest, and say so in the log line.

ALWAYS record the date applied. ALWAYS keep a per-application doc in `applications/` with all Q&A.

## Log entry format (append to logs/applications-log.md before each submit)
```
### [timestamp] Company — Role — STATUS
- URL:
- Resume used:
- Questions & answers:
  - Q: ... A: ...
```

## End of run
1. Write a summary at the top of `logs/applications-log.md`: submitted count, NEEDS HUMAN count,
   what to fix next run.
2. Add a new status block at the top of `state/status.md`: what was submitted, what was skipped and
   why, which leads are vetted and ready for the next run, and any new lesson about a form or a
   board. This is what the next run reads instead of re-researching.
3. Close every tab in the group (see step 8 above).
