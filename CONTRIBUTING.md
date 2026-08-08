# Contributing to please-hire-me

Thanks for being here. This project works because a lot of small, specific knowledge about
application forms is written down in one place. Adding one more piece of that knowledge is a real
contribution, and it is usually a ten-line PR.

## The one rule

**Never make the agent better at lying.**

Rejected on sight, regardless of quality:
- Anything that fabricates an answer, a number, a date, or a credential.
- CAPTCHA solving, CAPTCHA services, or challenge bypasses.
- Fake human behavior signals: synthetic mouse jitter, randomized "human" typing delays, spoofed
  fingerprints, `navigator.webdriver` patching.
- Account creation, credential entry, or anything that logs in as the user.
- Volume features that exist to spam: unlimited caps, retry-until-accepted, one-click apply to every
  posting on a board.

The agent fills a form the way the user would, with facts the user supplied. Everything else is a
NEEDS HUMAN. That constraint is the product, not a limitation to engineer around.

## Good first contributions

**Widget recipes** (`CLAUDE.md`, "Tricky widget recipes"). You hit an ATS control that ate your
input. You worked out why. Write down the symptom, the cause, and the fix in three lines. These are
the highest-value contributions in the repo because every user hits the same widget.

Example of the shape we want:

> **Ashby wipes text typed before hydration finishes.** Treat the first fill pass as a throwaway:
> fill, screenshot, refill anything that came back blank, then submit.

**Sourcing lanes** (`data/sources.md`). A job list, a lab careers page, a fellowship, a quant board
that is actually worth mining. Include the URL and one line on what is different about it. Do not
add aggregators that require an account to see the posting.

**ATS support.** Workable, SmartRecruiters, and Rippling forms are only lightly covered. A recipe
for a platform that is not yet handled is very welcome.

**Setup ergonomics.** `setup.sh` should work on a machine that has never seen this repo. If it
failed on yours, that is a bug worth a PR: better detection, clearer errors, Linux and Windows
(WSL) paths.

**Docs.** If a step confused you, it confuses everyone. Fix the sentence.

## What not to send

- Personal data. Yours or anyone's. See the check below.
- A rewrite of `CLAUDE.md` into a different structure. It is the agent's working memory and it is
  tuned; add to it rather than reorganizing it.
- New runtime dependencies. The project is bash plus python3 standard library, on purpose. It has to
  run on a fresh laptop with nothing installed.
- Scraped job data or company-specific credentials.

## Setting up to develop

```bash
git clone https://github.com/alecswang/please-hire-me.git
cd please-hire-me
./setup.sh
```

Then add `"dry_run": true` to the `run` block in `config/settings.json`. It is not in the default
config, and users are never offered it: their first application is supervised, stopping for approval
before it submits. `dry_run` exists for you. The agent fills every field, verifies it, screenshots
it, writes the log, and never submits, so you can iterate against real forms all day without sending
anything to a real company.

Please do not test against a company you would not actually apply to. Use dry run, and if you need a
form to poke at, use a posting you are genuinely a candidate for.

## Before you open a PR

```bash
# 1. Nothing personal is staged. This must show only code and templates.
git status --porcelain
git diff --cached --stat

# 2. Shell still parses.
bash -n setup.sh run.sh scripts/*.sh

# 3. Config templates still parse.
python3 -m json.tool config/settings.example.json > /dev/null
python3 -m json.tool config/profile.example.json  > /dev/null

# 4. The launcher builds its prompt from your settings without erroring.
#    (This prints the prompt instead of starting a run.)
sed 's|^"$CLAUDE_BIN" -p.*|printf "%s\\n" "$PROMPT"|' run.sh > /tmp/run-render.sh
bash /tmp/run-render.sh 1 | head -20
```

If you touched `run.sh` or `config/settings.example.json`, do one dry run end to end and paste the
result in the PR.

## Personal data, seriously

Everything about a specific job seeker is gitignored: `config/profile.json`, `config/answers.md`,
`config/settings.json`, `data/queue.md`, `data/*.pdf`, `applications/`, `logs/`, `screenshots/`,
`state/`. Only the `.example` versions are tracked.

Before your first push:

```bash
git ls-files | grep -Ev '\.example\.' | grep -E 'profile|answers|queue|applications/|logs/|screenshots/|state/'
```

That should print nothing. If it prints a file, remove it from the index with
`git rm --cached <file>` before committing.

Same rule for issues: when reporting a form bug, include the ATS, the company, the field, and the
symptom. Never paste your filled-in answers, your resume, or a screenshot with your contact details.

## Style

- Shell: `set -euo pipefail`, quote your variables, no dependencies beyond coreutils and python3.
- Python: standard library only, 3.9 compatible.
- Prose in `CLAUDE.md`, `config/spec.md`, and the docs: concise, specific, no em dashes, no
  marketing words. Write the symptom and the fix, not the story.
- Commits: one change per commit, present tense, say what changed and why in the body if it is not
  obvious from the subject.

## Reporting a form that broke

Open an issue with:
1. ATS platform and company.
2. What the agent did and what the form did.
3. The exact error text if the form produced one.
4. Whether a retry fixed it.

A failure you can describe precisely usually becomes a widget recipe, which means nobody else hits
it again.
