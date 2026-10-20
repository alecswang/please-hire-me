# please-hire-me: entry point for Grok Bot

The playbook is `CLAUDE.md`. Read it in full and follow it, in its reading order. Every rule there
applies to you: never inventing a fact, never creating an account or typing a password, the
duplicate, lifetime-cap and interview-tracker skips, the target quality gate, logging before
submit, and one screenshot per submit. `config/spec.md` and `config/documents.md` apply unchanged.

`CLAUDE.md` is written for Claude Code driving the user's Chrome through the Claude in Chrome
extension, launched by `run.sh` on a launchd/cron schedule. You have none of those. You have your
own persistent Linux computer with a shell, your own signed-in browser that you drive yourself,
chat with the user (including option cards), and routines. This file maps each mechanism. Where
this file and `CLAUDE.md` disagree on a **mechanism**, this file wins. Where they disagree on a
**rule**, `CLAUDE.md` wins. `AGENTS.md` (the Codex mapping) does not apply to you.

## 0. Get the repo

```bash
cd /workspace
git clone https://github.com/alecswang/please-hire-me.git   # skip if /workspace/please-hire-me exists
cd please-hire-me
```

Work only in `/workspace/please-hire-me`. If it already exists, `git pull` instead of recloning, and
never delete `config/`, `applications/`, `logs/`, `screenshots/`, `state/` or `data/queue.md`: that
is the user's history and the duplicate checks depend on it.

Tell the user, in place of `CLAUDE.md`'s "their data never leaves the machine" line: their config
and application records are gitignored and live on **your** computer (the Grok Bot box), not in
the repo and not on their laptop.

## 1. First run: setup conversation

**Only when config is missing.** If `config/profile.json`, `config/answers.md` and
`config/settings.json` all exist, this is NOT a first run: skip this section and section 2, do not ask
the setup questions, and go straight to the run (section 4, or the run the user asked for in chat).
Still do section 1b's box checks.

Follow `CLAUDE.md` "FIRST RUN" step by step. Do not offer a menu; start at step 1 in your first
reply. Do not open the browser or apply during steps 1-6. Differences only:

| `CLAUDE.md` step | Do this as Grok Bot |
|---|---|
| 1. Copy templates | Same, in the shell. |
| 2. Ask for the resume, read it | Ask them to attach the PDF in chat. Read it, then save it to the path in `profile.json.resume` (default `data/resume.pdf`). Check for `tectonic` and `pdftotext` on your computer. |
| 3. Confirm every extracted value | Same. Show every value; empty stays empty and becomes a question. |
| 4. ONE numbered question list | Same rules exactly: walk `config/profile.example.json` and `config/answers.example.md` key by key, say the count up front, mark optional ones, state defaults, one message back. Ask it as one chat message. Option cards are fine for a single yes/no or pick-one (for example step 7's "now or not yet"), never to split the list into rounds. Replace the `brew install tectonic poppler` question with whether you may install them on your own computer (Linux package manager, or tectonic's release binary; default yes). |
| 5, 5b. Draft `answers.md`, `settings.json`, resume base | Same, including checking every number and title against the resume and the concrete confirmation question. |
| 6. Offer to install the schedule | Do **not** run `./scripts/schedule.sh`. Offer a Grok Bot routine instead (section 4 below). Ask for the frequency from `schedule.frequency`'s values; on yes, write it to `settings.json` and create the routine. |
| 6b. Optional add-ons | One short list, do not push. Mapping in section 5. |
| 7. Supervised first application | Section 2 below. |

Never invent a fact during setup. Confirm before writing each file and say what you wrote.

## 1b. Box checks (every run, including a config copied from the user's laptop)

Config written on the user's Mac carries Mac paths. Fix them on your computer before applying:

- **Every path in `profile.json` must exist on your computer.** `resume`, `transcript`,
  `resume_tailor_base`, and any path inside `resume_build_cmd`. Repo-relative paths (`data/...`) work
  everywhere; `/Users/...` paths do not. Ask the user for the file (or a copy of their LaTeX source and
  build script), save it under `data/`, and update the key. `scripts/app_docs.py` errors out when
  `resume_tailor_base` is set but missing, instead of silently skipping tailoring.
- **Interview tracker.** If `run.interview_tracker_path` points off your computer, ask the user to paste
  or attach the note, save it as `state/interview-tracker.md` (gitignored), and set
  `run.interview_tracker_path` to that path. Until then `tracker_companies.py` exits 1 and
  `dupe_check.sh` exits 4: apply to nothing.
- **Tools.** `pdftotext`/`pdfinfo` come from `poppler-utils` (`sudo apt-get install -y poppler-utils`).
  tectonic is not packaged on Debian: `curl -fsSL https://drop-sh.fullyjustified.net | sh`, then move
  the `tectonic` binary into `~/.local/bin` and make sure that directory is on PATH in every shell
  (`export PATH="$HOME/.local/bin:$PATH"`). A `resume_build_cmd` build script that fixes ligatures needs
  `qpdf` and `fix-qdf` (`sudo apt-get install -y qpdf`). Where `CLAUDE.md` or a script says
  `brew install`, use these.
- **`documents.*` defaults.** A `settings.json` without a `documents` block means cover letters and
  tailoring are both ON, one page, 150-250 word letters (`config/documents.md`). That is not an error.
- **Ashby API.** `api.ashbyhq.com` answers 403 to a request without a browser `User-Agent`. The sweeps
  send `User-Agent: Mozilla/5.0`; do the same in any ad-hoc `curl -A 'Mozilla/5.0'` or `urllib` query.

## 1c. Dry runs ("do everything except submit")

When the user asks for a test or dry run, nothing it does may count as an application or move the
history that the next real run depends on:

- Run the sweeps with `--no-advance` (alias of `--dry`; `delta_sweep.py`, `portal_sweep.py`,
  `list_sweep.py`, `linkedin_sweep.py`), so `state/last_*sweep.txt` cutoffs and
  `data/slug-candidates.txt` stay put. `state/sweep/*.json` outputs are still rewritten; that is fine.
- Name the per-application doc `applications/<company>-<role>.DRYRUN.md` and say DRY RUN at its top.
  `dupe_check.sh` lists `.DRYRUN.` files separately and does not count them. Files still go in
  `applications/files/<company>-<role>/`.
- Write nothing to `logs/applications-log.md`, `state/status.md` or `data/queue.md`. Put the run notes
  in `state/dryrun/<date>-<what>.md` instead.
- Never open the form's Submit, never create an account, never send email.

## 2. The supervised first application

Run it in the setup conversation, from `config/settings.json`, without `./run.sh`. Ask one
question: now (recommended) or not yet.

- **Now.** Source one real posting with the sweeps, run every duplicate and tracker check, fill
  every field, verify, screenshot, write the log entry and the `applications/` doc, then **stop and
  show the user everything before Submit**: the posting URL, every question and answer, the
  uploaded resume and cover letter if any, and the screenshot. Submit only on an explicit yes in
  chat. Anything else, including silence, means close the tab and send nothing. Then name the
  posting and point at the `applications/` doc and screenshot.
- **Not yet.** Say they can ask you for one application any time ("apply to one job, stop before
  submitting"). There is no `./run.sh 1` for them to run.

Say plainly what happens next, as `CLAUDE.md` requires: **routine runs submit on their own, with
no per-application checkpoint.** Anyone who wants a checkpoint every time should ask you for a run
in chat and say "stop before submitting", instead of a routine.

## 3. Browser: your own browser replaces the Chrome extension

- Use your own browser. Skip every Claude in Chrome check in `CLAUDE.md`: `list_connected_browsers`,
  the ABSENT signature, the claude.ai/chrome install steps, per-site extension permissions,
  "Couldn't determine which page this action targets", and the one-domain-per-`browser_batch`
  rule. None apply.
- **Trusted input only**, as `CLAUDE.md` section 1 says: real clicks and real keystrokes. Never
  fill a form by setting values or dispatching events from page JavaScript. JavaScript is for
  read-only checks (`aria-invalid` count, `value.length >= maxLength`, Ashby `input.checked`).
  Never fake human behavior (jitter, randomized delays).
- **Resume and transcript upload**: use your browser's file-upload ability on the form's file
  input with the absolute path from `profile.json` (the file is on your computer). Never click an
  Attach button that opens a native OS dialog you cannot operate. The cross-origin-iframe limit and
  the Greenhouse `/embed/job_app` workaround in `CLAUDE.md` section 2 still apply. If upload fails
  after one page reload, NEEDS HUMAN. `scripts/resume_server.py` is legacy; don't use it.
- **Shortcuts**: you are on Linux. Where `CLAUDE.md` says `cmd+a` / `cmd+v`, use `ctrl+a` / `ctrl+v`.
- **Native `<select>`**: prefer real interaction (click then keyboard). `CLAUDE.md`'s one-off JS
  value-set is only allowed on a form the user submits by hand.
- **Every widget recipe in `CLAUDE.md`** (Ashby Yes/No binding, Ashby hydration wipe, upload reflow
  wiping values, 255-char truncation, never pressing Return in a Greenhouse dropdown, D. E. Shaw,
  Google Careers, Workday) is about the ATS, so it applies unchanged.
- **Tabs**: the browser is yours, so there are no user tabs to protect, but keep the discipline:
  one tab reused posting to posting, never resume a half-filled form after a crash (restart that
  company clean), and at end of run close every tab you opened for applications. The one exception
  stays: a tab left open for the user (email-code gate, no-AI essay, interactive CAPTCHA, sign-in),
  named in the NEEDS HUMAN log line.

## 4. Scheduled runs: a Grok Bot routine replaces run.sh and cron

Do not use `run.sh`, `scripts/schedule.sh` or `scripts/scheduled_run.sh`. Create one routine at
the frequency the user chose (`schedule.frequency`: `hourly`, `every-2-hours`, `every-3-hours`,
`every-6-hours`, `daily`, `weekdays`; `manual` means no routine). Store the chosen value in
`settings.json` so the files stay the source of truth. Suggested routine prompt:

> please-hire-me scheduled run. `cd /workspace/please-hire-me && git pull --ff-only`. Read
> GROKBOT.md, then CLAUDE.md and the files in its reading order, and do one run obeying
> `config/settings.json` exactly (`run.max_applications_per_run` is a hard cap). No checkpoint:
> submit applications that pass every check. If config is missing, do not apply; tell me setup is
> needed. When done, reply with the run summary.

Each routine run must:
1. Run `python3 scripts/tracker_companies.py` first if `run.interview_tracker_path` is set.
2. Run `delta_sweep.py`, `portal_sweep.py`, `list_sweep.py`, `linkedin_sweep.py` in the
   **foreground** and wait for them to exit. Never background them. The delta and LinkedIn sweeps
   take up to 7-8 minutes each; give the shell call a long enough timeout. (Dry runs: `--no-advance`.)
3. Apply every skip: tracker, `skip_companies`, duplicate grep of `applications/` and
   `logs/applications-log.md`, same-day freeze, `max_applications_per_company_lifetime`,
   `pause_company_while_interviewing`, posted per-company limits, the quality gate, hard
   eligibility mismatches. Never submit a weak target to reach the cap.
4. Log before submit, screenshot after, write the run summary at the top of
   `logs/applications-log.md` and a new block at the top of `state/status.md`.
5. End with a short chat message: submitted (company, role, link to doc), skipped counts, and every
   NEEDS HUMAN with its URL, plus the "FOR YOU, BY HAND" rows from `portal_sweep.py`.

Only one please-hire-me routine per checkout. Changing frequency means updating that routine, not
adding another. A routine runs on your computer, so the user's laptop can be closed.

## 5. Things only the user can do: hand them the screen

Never create an account, type a password, read an emailed login code, or solve an interactive
CAPTCHA. Those rules from `CLAUDE.md` and `safety.*` are unchanged.

- **Interactive CAPTCHA, login, 2FA, "verify your email"**: in a live conversation, hand the
  screen to the user to do that step, then continue once they say done and you have confirmed the
  page state. In a routine run nobody is watching: log NEEDS HUMAN with the URL, leave that one tab
  open, and move on.
- **Signed-in portals** (`channels.signed_in_portals`): the user signs in once in **your** browser
  through the screen hand-off; then add the host. Before touching any form, confirm the header shows
  them signed in. Signed out mid-run is NEEDS HUMAN. Workday sessions expire within hours, so
  Workday is best done in a live conversation right after they sign in.
- **Emailed post-submit codes** (add-on 2): the repo's rule is that the agent never sees the code,
  and it says not to use a Gmail connector for codes because that puts the code and email in your
  context. Follow that: use `scripts/code_broker.py` with the user storing their app password
  themselves (never pasted into chat), and the paste-without-reading sequence in `CLAUDE.md`. The
  broker reads the password from the macOS Keychain, which your Linux computer doesn't have. Until
  it has a Linux secret store the user fills in without you seeing the value, treat these
  applications as NEEDS HUMAN. Do not swap in the Gmail connector to read codes unless the
  maintainer changes this rule.
- **Interview tracker** (add-on 3): the note has to be on your computer. Ask the user to paste or
  attach it, save it under `state/` (gitignored), set `run.interview_tracker_path` to it, and remind
  them it only stays current if they send updates.

## 6. Where things go

All paths are relative to `/workspace/please-hire-me` on your computer:

- Per-application docs: `applications/<company>-<role>.md`, files in `applications/files/<company>-<role>/`.
- Log and run summary: `logs/applications-log.md`. Memory between runs: `state/status.md`.
- Submit screenshots: `screenshots/` (JPG only, never GIF).

When the user asks to see results, send them the screenshot and doc from those paths. Don't commit
or push any of them; they are gitignored on purpose.
