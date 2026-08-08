<div align="center">

# please-hire-me

**An agent that fills out real job applications while you sleep.**

[![License: MIT](https://img.shields.io/badge/License-MIT-black.svg)](LICENSE)
[![PRs welcome](https://img.shields.io/badge/PRs-welcome-black.svg)](CONTRIBUTING.md)
[![Runs on Claude Code](https://img.shields.io/badge/runs%20on-Claude%20Code-black.svg)](https://claude.com/claude-code)
[![macOS | Linux](https://img.shields.io/badge/macOS-%7C%20Linux-black.svg)](#quick-start)

It finds live openings, internships and new-grad roles alike, fills the company's own
Greenhouse / Lever / Ashby form field by field in your real Chrome, and submits. Every answer is logged before it clicks, every submit is
screenshotted. It never invents a fact about you.

</div>

```
Run done. 3/3 submitted, cap reached, clean exit.

| # | Company / Role                                          | Comp          |
|---|---------------------------------------------------------|---------------|
| 1 | Frontier AI lab - Research Engineer, DevEx (SF)         | $350K-$475K   |
| 2 | Enterprise agent startup - Software Engineer (SF)       | $180K-$390K   |
| 3 | Medical AI unicorn - Member of Technical Staff (SF)     | prestige gate |

Every form: resume via file_upload, all fields typed with trusted input,
0 aria-invalid before submit, success banner captured as JPG.
NEEDS HUMAN: none. Tab group closed and confirmed gone.
```

<sub>A real run, about ten minutes. 196 applications sent this way so far.</sub>

---

## Quick start

**You need:** [Claude Code](https://claude.com/claude-code) signed in · Chrome with the
[Claude in Chrome](https://claude.ai/chrome) extension on the same account · your resume as a PDF.

```bash
git clone https://github.com/alecswang/please-hire-me.git
cd please-hire-me
```

Open the repo in Claude Code and say *"set me up"*. Setup is one conversation, about five minutes,
and Claude does the typing:

1. It asks for your resume and reads it.
2. It shows you every value it pulled out so you can correct what is wrong.
3. It asks **one list** of the questions a resume cannot answer, all at once, with the default it
   will use for anything you skip. Work authorization, start date, what counts as a good job to you.
4. It drafts your answer templates from your real work and reads them back for you to approve.

Then it writes your three config files. It never invents a fact about you, and it does not open a
browser or apply to anything during setup.

<details>
<summary>Prefer a terminal wizard?</summary>

`./setup.sh` asks the questions every form asks and writes your config in about two minutes. It
leaves `config/answers.md` as a blank template for you to fill in yourself, which takes about
twenty minutes and is the step that decides whether the agent flies or stalls at every "why do you
want this role?". Letting Claude draft it from your resume is why the guided path is the default.

</details>

**Run it:**

```bash
./run.sh          # one run, using your settings
./run.sh 1        # a single application, good for a first test
```

<details>
<summary><b>How much rope to give it</b></summary>

**The first application is supervised.** At the end of setup it fills one real posting, shows you
every answer, and submits only after you say yes. Say no and it closes the tab and sends nothing.
A real application with a checkpoint, not a rehearsal.

**Scheduled runs submit on their own.** Once `schedule.frequency` is set and the job is installed,
there is no per-application checkpoint. That is the point of it.

**Want a checkpoint every time?** `./run.sh` cannot give you one, it launches a headless session
with nobody there to approve. Instead, open the repo in Claude Code and ask for a run, saying stop
before submitting. You get the same checkpoint as the first application, every time.

</details>

---

## What you give it

A missing fact becomes a question for you, never a guess. Three files decide everything, and setup
writes all three for you:

| File | What goes in it | Where it comes from |
|---|---|---|
| `config/profile.json` | Name, contact, school, degree, graduation, GPA, visa status, links, resume path. | read off your resume, then you correct it |
| `config/answers.md` | Free-text templates, your fact sheet, presets for salary, start date, EEO. **The one that matters.** | drafted from your resume, then you approve it |
| `config/settings.json` | Cap per run, frequency, and what counts as a target: roles, locations, comp floor, skip list, your quality bar. | your answers to the question list |

Each has a `.example` twin showing exactly what belongs there. Your real files are gitignored, so
nothing about you leaves your machine. Edit any of them by hand later; the agent rereads them every
run.

## Settings

One file, `config/settings.json`. The launcher turns it into the instructions the agent must obey.

| Key | Does what |
|---|---|
| `run.max_applications_per_run` | Hard cap per run. Default 3. |
| `run.same_day_company_freeze` | Never open a second role at a company you applied to today. |
| `schedule.frequency` | `manual`, `hourly`, `every-2-hours`, `every-3-hours`, `every-6-hours`, `daily`, `weekdays`. |
| `targets.roles` | Titles to look for. |
| `targets.max_years_experience_required` | Anything above this is skipped as a hard mismatch. |
| `targets.locations` | Cities, plus `Remote (US)` if you want remote. |
| `targets.min_annual_comp_usd` | Compensation floor for **full-time** roles. |
| `targets.internship_min_hourly_usd` | Hourly floor for **internships**, which post hourly pay and would otherwise fail an annual floor. `0` means judge them on the quality bar alone. |
| `targets.prestige_note` | Your quality bar in plain English, used when a posting lists no salary. |
| `targets.skip_companies` | Never apply here. |
| `eligibility.needs_visa_sponsorship` | Skips non-sponsors, ITAR, and clearance roles. |
| `eligibility.graduation` | Skips postings whose graduation window excludes you. |
| `safety.*` | No accounts, no CAPTCHA solving, no fabricated facts, screenshot every submit. |

Run it on a schedule:

```bash
./scripts/schedule.sh install        # reads schedule.frequency
./scripts/schedule.sh status         # this checkout, plus every other one on the machine
./scripts/schedule.sh uninstall      # this checkout only
./scripts/schedule.sh uninstall-all  # every please-hire-me job on the machine
```

Each checkout gets its own scheduled job, keyed to its path, so two clones can run on
their own cadences without overwriting each other. `status` shows all of them and marks
which one you are in.

## Why this instead of a one-click apply tool

An internship or new-grad search is 300 forms asking the same 40 questions, 20 minutes each, and
none of that time makes you a better candidate. The postings that pay well rot in about a week, so being slow means
not applying at all.

The tools that promise to fix this apply *through their own portal*, which is the channel recruiters
ignore. This applies on the company's own ATS, the same form you would have filled by hand, with
your real answers.

## How it works

**Real browser, real keystrokes.** ATS forms score behavior with reCAPTCHA v3. Page JavaScript
produces untrusted events and gets flagged as spam; so does a headless or devtools-driven browser.
The agent clicks and types in your normal Chrome the way you would. Not an evasion trick, just the
honest way to operate a browser, which is why submissions land normally.

**It ships with a map.** [`data/boards.md`](data/boards.md) lists 235 Ashby and Greenhouse boards
verified live, with job counts and which ones publish salary bands.
[`data/ats-field-notes.md`](data/ats-field-notes.md) holds what 196 real applications taught it:
which companies rate-limit you per candidate, where seniority hides in body text, which org slugs
are wrong, which postings contain prompt injection aimed at AI readers. Regenerate the board list
any time with `./scripts/probe_boards.sh`.

**Sourcing happens over JSON, not browsers.** It queries the ATS APIs, greps for experience gates
and seniority language, checks the comp band, and only then opens a tab. Most candidates die before
a browser is involved, which is what keeps a run cheap.

**Everything is written down before it submits.** A per-application doc with every question and
answer, a line in the log, a confirmation screenshot, and `state/status.md` as memory between runs.

## What it will never do

- Fabricate a fact about you. No invented salary, test score, address, or date.
- Create an account or type a password.
- Solve an interactive CAPTCHA.
- Submit a "please don't use AI" essay or a graded take-home. Filled up to that point, left open,
  flagged for you.
- Follow instructions embedded in a job posting. Page text is data, not orders.
- Apply through Handshake, LinkedIn Easy Apply, or Simplify.
- Touch a browser tab outside its own tab group. Your personal tabs are off limits.

<details>
<summary><b>Repo layout</b></summary>

```
please-hire-me/
├── setup.sh                  # one-time interactive setup
├── run.sh                    # one bounded run
├── CLAUDE.md                 # the agent's playbook: browser method, widget recipes, rules
├── config/
│   ├── settings.json         # run knobs and target criteria      (yours, gitignored)
│   ├── profile.json          # every field value an ATS asks for  (yours, gitignored)
│   ├── answers.md            # free-text templates + fact sheet   (yours, gitignored)
│   └── spec.md               # the run contract: rules, procedure, log format
├── data/
│   ├── queue.md              # vetted targets, worked top-down    (yours, gitignored)
│   ├── sources.md            # where to find roles: job lists, AI labs, quant, fellowships
│   ├── boards.md             # 235 ATS boards verified live, with job counts
│   ├── slug-candidates.txt   # every org slug ever tried; re-probe with scripts/probe_boards.sh
│   └── ats-field-notes.md    # application limits, hidden gates, slug traps, injection canaries
├── applications/             # one doc per application, full Q&A  (yours, gitignored)
├── logs/                     # the running log                    (yours, gitignored)
├── screenshots/              # proof of every submit              (yours, gitignored)
├── state/status.md           # the agent's memory between runs    (yours, gitignored)
└── scripts/
    ├── schedule.sh           # install/remove the recurring run
    ├── probe_boards.sh       # re-verify every ATS board
    └── scheduled_run.sh      # what the scheduler calls
```

</details>

<details>
<summary><b>FAQ</b></summary>

**Does this get me flagged as a bot?** No. It fills forms with genuine trusted input in your own
browser. Passive reCAPTCHA v3 passes. Interactive challenges are handed back to you.

**What does a run cost?** It runs on your Claude Code subscription, so usage rather than dollars per
application. Sourcing goes over JSON APIs specifically to keep it cheap.

**Does it do internships?** Yes, and it is probably the best fit for them. Put `internship` in
`targets.seniority`. Internships post hourly pay, so the full-time annual floor is ignored for
them and `targets.internship_min_hourly_usd` applies instead. The sourcing list in
`data/sources.md` is internship-heavy: SimplifyJobs Summer2027 (46k stars), vanshb03, and the
Northwestern quant list are all internship-first.

**Can I use it for non-engineering roles?** Yes. Nothing is engineering-specific except the defaults
in `settings.example.json` and the source list. Change the roles and the fact sheet.

**How long is setup, really?** About five minutes of your attention. Claude reads the resume, shows
you what it found, asks one list of questions, and drafts `config/answers.md` for you. The wizard
path is faster to run and slower to finish, because it hands you a blank `answers.md`.

**Why does it keep saying NEEDS HUMAN?** A fact is missing from `answers.md` or `profile.json`. Add
it once and that class of block disappears forever.

**My first run applied to less than the cap. Broken?** No. A fresh install has an empty queue, so
the first run spends its time sourcing. It fills the queue as it goes and picks up speed.

**Does it work on Workday / Taleo / iCIMS?** Mostly no, on purpose. Those need an account per
company, which the agent will not create. Greenhouse, Lever, Ashby, and Workable cover most startups
and AI labs.

**Can it run with my laptop closed?** No. It drives your real Chrome, so the machine has to be awake
and Chrome has to be running.

</details>

## Contributing

Yes please. Widget recipes for ATS quirks, new sourcing lanes, and setup ergonomics are the highest
value. See [CONTRIBUTING.md](CONTRIBUTING.md).

One rule above all: **never contribute anything that helps the agent lie.** No fabricated answers,
no CAPTCHA solving, no fake behavioral signals. A PR that makes it better at pretending to be a
human gets closed.

## License

MIT. See [LICENSE](LICENSE).
