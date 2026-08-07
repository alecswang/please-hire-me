# Run Spec

The contract for one run. `CLAUDE.md` is the how (browser method, widget recipes);
this file is the what (rules, per-application procedure, log format). Every value comes from
`config/settings.json`, `config/profile.json`, and `config/answers.md`. Never guess.

## Run config
Read from `config/settings.json`:
- `run.max_applications_per_run` — hard cap. The launcher passes it in the prompt; an argument to
  `./run.sh` overrides it.
- `run.dry_run` — when true, fill and verify and screenshot every form, then close the tab WITHOUT
  submitting. Log the application as DRY RUN.
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
   account, so expect to skip most Workday.
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

## Per-application procedure
1. Find the posting. Confirm the role matches `targets`, is not on the skip list, and is not
   already in `applications/` / `data/queue.md` / `logs/applications-log.md`. Verify the URL is
   LIVE — postings rot within days, and a req id from a previous run can be dead.
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
