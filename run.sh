#!/usr/bin/env bash
# please-hire-me — launch one bounded application run in a fresh Claude Code session.
# Usage: ./run.sh [max_applications]     (arg overrides config/settings.json)
set -euo pipefail

cd "$(dirname "$0")"
LOCK_DIR=".hourly-run.lock"

if [ $# -ge 1 ] && ! [ "$1" -ge 0 ] 2>/dev/null; then
  echo "Usage: ./run.sh [max_applications]   (a non-negative integer; omit to use config/settings.json)" >&2
  exit 2
fi

for f in config/settings.json config/profile.json config/answers.md; do
  [ -f "$f" ] || { echo "ERROR: $f is missing. Run ./setup.sh first." >&2; exit 1; }
done

# launchd runs with a minimal PATH that lacks the user's shell setup, so resolve
# the agent binary explicitly. Prefer the stable ~/.local/bin symlink, then PATH.
find_bin() {
  if [ -x "$HOME/.local/bin/$1" ]; then echo "$HOME/.local/bin/$1"
  elif command -v "$1" >/dev/null 2>&1; then command -v "$1"
  fi
}

# AGENT=claude|codex picks the driver. Default prefers claude, which is the only
# one whose browser path is verified against reCAPTCHA v3 scoring. See AGENTS.md.
AGENT="${AGENT:-auto}"
CLAUDE_BIN="$(find_bin claude)"
CODEX_BIN="$(find_bin codex)"

case "$AGENT" in
  auto)
    if [ -n "$CLAUDE_BIN" ]; then AGENT=claude
    elif [ -n "$CODEX_BIN" ]; then AGENT=codex
    else
      echo "ERROR: neither 'claude' nor 'codex' found (checked ~/.local/bin and PATH)." >&2
      exit 127
    fi
    ;;
  claude) [ -n "$CLAUDE_BIN" ] || { echo "ERROR: AGENT=claude but claude binary not found." >&2; exit 127; } ;;
  codex)  [ -n "$CODEX_BIN"  ] || { echo "ERROR: AGENT=codex but codex binary not found." >&2;  exit 127; } ;;
  *) echo "ERROR: AGENT must be claude, codex, or auto. Got '$AGENT'." >&2; exit 2 ;;
esac

# Turn config/settings.json into the sentences the agent has to obey this run.
SETTINGS_PROMPT="$(MAX_OVERRIDE="${1:-}" python3 - <<'PY'
import json, os
s = json.load(open('config/settings.json'))
run, t, el = s.get('run', {}), s.get('targets', {}), s.get('eligibility', {})
ch, sf = s.get('channels', {}), s.get('safety', {})
out = []
mx = os.environ.get('MAX_OVERRIDE') or run.get('max_applications_per_run', 3)
out.append(f"Submit at most {mx} new applications this run, then exit.")
if run.get('dry_run'):
    out.append("DRY RUN IS ON: fill every field, verify it, screenshot it, write the log entry and "
               "the per-application doc marked DRY RUN, then close the tab WITHOUT clicking submit. "
               "Do not submit anything this run under any circumstance.")
if run.get('one_application_per_company_per_run', True):
    out.append("One application per company per run.")
if run.get('same_day_company_freeze', True):
    out.append("Never open a second req at a company that already received an application today; "
               "check the Date applied line in the matching applications/*.md file.")
if t.get('roles'):
    out.append("Target roles: " + ", ".join(t['roles']) + ".")
if t.get('seniority'):
    out.append("Seniority in scope: " + ", ".join(t['seniority']) + ".")
if t.get('max_years_experience_required') is not None:
    out.append(f"Skip any posting requiring more than {t['max_years_experience_required']} "
               "year(s) of professional experience; that is a hard eligibility mismatch, not a "
               "needs-human block.")
if t.get('locations'):
    out.append("Locations in scope: " + ", ".join(t['locations']) + ".")
if t.get('min_annual_comp_usd'):
    line = f"For FULL-TIME roles, apply only when credible annual compensation is at least ${t['min_annual_comp_usd']:,}"
    if t.get('prioritize_above_usd'):
        line += f", prioritizing roles above ${t['prioritize_above_usd']:,}"
    out.append(line + ".")
if 'internship' in [x.lower() for x in t.get('seniority', [])]:
    hourly = t.get('internship_min_hourly_usd') or 0
    if hourly:
        out.append(f"INTERNSHIPS are in scope and are judged separately: require at least ${hourly}/hour "
                   "(annualize a monthly or weekly stipend to compare). NEVER skip an internship for "
                   "failing the full-time annual floor; that floor does not apply to internships.")
    else:
        out.append("INTERNSHIPS are in scope and the full-time annual compensation floor does NOT apply "
                   "to them. Internships post hourly or monthly pay; judge them on the quality bar "
                   "below, not on an annual number, and never skip one for lacking an annual band.")
if t.get('count_equity_toward_comp') is False:
    out.append("Do not count equity with a vesting cliff toward the compensation floor.")
if t.get('prestige_note'):
    out.append("Quality bar, in the user's own words: " + t['prestige_note'])
if t.get('priority_companies'):
    out.append("Prioritize these companies when they have an eligible opening: "
               + ", ".join(t['priority_companies']) + ".")
if t.get('skip_companies'):
    out.append("NEVER apply to: " + ", ".join(t['skip_companies']) + ".")
for n in t.get('skip_notes', []):
    out.append(n)
if el.get('needs_visa_sponsorship'):
    out.append("The user needs visa sponsorship. Skip employers that state they do not sponsor, and "
               "skip US-citizen, US-person, security-clearance, and ITAR roles.")
if el.get('us_person_only_roles_ok') is False and not el.get('needs_visa_sponsorship'):
    out.append("Skip US-person-only, clearance, and ITAR roles.")
if el.get('graduation'):
    out.append(f"Graduation is {el['graduation']}. Never misstate it to fit a posting's window; if a "
               "posting hard-requires a window that excludes it, skip the posting.")
if el.get('earliest_start') or el.get('latest_start'):
    out.append(f"Start window: {el.get('earliest_start','')} to {el.get('latest_start','')}.")
if ch.get('allowed_ats'):
    out.append("Apply only on: " + ", ".join(ch['allowed_ats']) + ".")
if ch.get('blocked_aggregators'):
    out.append("Never apply through: " + ", ".join(ch['blocked_aggregators']) + ".")
if sf.get('never_create_accounts', True):
    out.append("Never create accounts or enter passwords.")
if sf.get('never_solve_interactive_captcha', True):
    out.append("Never solve interactive CAPTCHA challenges; log NEEDS HUMAN instead. Passive "
               "reCAPTCHA v3 with no challenge is fine to submit through with trusted input.")
if sf.get('never_fabricate_a_fact', True):
    out.append("Never fabricate a fact. A required answer with no preset in config/answers.md or "
               "config/profile.json is NEEDS HUMAN, not a guess.")
if sf.get('screenshot_every_submit', True):
    out.append("Save a confirmation screenshot as JPG directly under screenshots/ after each submit. "
               "Never record or export GIFs and never touch ~/Downloads.")
if sf.get('require_log_before_submit', True):
    out.append("Before clicking submit, append the full question-and-answer log to "
               "logs/applications-log.md and write applications/<company>-<role>.md with every "
               "question, every answer, the URL, and today's date.")
print(" ".join(out))
PY
)"

if ! mkdir "$LOCK_DIR" 2>/dev/null; then
  # Lock exists. If the process that created it is dead (hard kill / power loss
  # left a stale lock), reclaim it. Otherwise a real run is active; skip.
  stale_pid="$(cat "$LOCK_DIR/pid" 2>/dev/null || true)"
  if [ -n "$stale_pid" ] && kill -0 "$stale_pid" 2>/dev/null; then
    printf 'Another run (pid %s) is active. Skipping this trigger.\n' "$stale_pid"
    exit 0
  fi
  printf 'Removing stale lock (pid %s no longer running).\n' "${stale_pid:-unknown}"
  rm -rf "$LOCK_DIR"
  mkdir "$LOCK_DIR" || { printf 'Could not acquire lock. Skipping.\n'; exit 0; }
fi
echo "$$" > "$LOCK_DIR/pid"
trap 'rm -rf "$LOCK_DIR" 2>/dev/null || true' EXIT

# The browser half of the method is the only agent-specific part of the prompt.
# Everything else (sourcing, vetting, logging, scope) is identical.
if [ "$AGENT" = "claude" ]; then
  ENTRY_DOC="CLAUDE.md"
  METHOD_PROMPT="use the connected real Chrome through the Claude-in-Chrome extension and fill every field with trusted computer-tool input. Use file_upload for the resume and transcript. At the start, call tabs_context_mcp and close ONLY leftover job-application tabs inside your own MCP tab group from prior crashed runs; NEVER close, read, or navigate any tab that is not listed in your group, those are the user's personal tabs. Do the whole run in one reused tab, navigating it from posting to posting so no half-filled form is left behind. If the tab group drops mid-fill, reconnect via tabs_context_mcp, abandon the half-filled form rather than resuming it, and restart that company from a clean tab. Before exiting, close EVERY tab in your group with tabs_close_mcp and confirm tabs_context_mcp answers that no tab group exists."
else
  ENTRY_DOC="AGENTS.md"
  METHOD_PROMPT="drive the user's own already-running Chrome over the Chrome DevTools MCP server, attached to it by remote debugging port so the real profile, cookies, and IP are used. Read AGENTS.md before touching the browser; it states which parts of the Claude method do and do not carry over. Fill fields with the MCP input tools rather than page JavaScript: page-dispatched events are untrusted and read as spam. Attach the resume and transcript with the file-upload tool against the file input, never by clicking Attach, which opens an OS dialog. Work in ONE tab that you opened yourself, navigate it from posting to posting, and never read, navigate, or close a tab you did not open. Close that tab at the end of the run."
fi

PROMPT="Continue the job application run in $(pwd). This is a fresh session: derive all durable state from repository files, not from chat history.

Read and follow, in order: ${ENTRY_DOC}, config/settings.json, config/profile.json, config/answers.md, config/spec.md, data/queue.md, state/status.md, and logs/applications-log.md.

RUN CONFIG (from config/settings.json, obey exactly): ${SETTINGS_PROMPT}

METHOD: ${METHOD_PROMPT}

SCOPE: verify every posting is live and check applications/, data/queue.md, and logs/applications-log.md for duplicates before opening a tab. A hard eligibility mismatch is a SKIP with a one-line log entry, not a NEEDS HUMAN. NEEDS HUMAN is only for a role the user is eligible for that is missing a fact they could supply. Never submit a weak target just to reach the cap; zero strong submissions beats one bad one.

END OF RUN: update the per-application docs, data/queue.md, logs/applications-log.md, and add a new status block at the top of state/status.md. If Chrome is disconnected or required facts are missing, log it and exit. Keep token use low by working the queue top-down and avoiding repeated research."

if [ "$AGENT" = "claude" ]; then
  "$CLAUDE_BIN" -p --chrome --no-session-persistence --dangerously-skip-permissions "$PROMPT"
else
  # Codex needs write access to the repo and network access for the ATS APIs.
  # It reads AGENTS.md automatically as its project instruction file.
  "$CODEX_BIN" exec -C "$(pwd)" -s danger-full-access "$PROMPT"
fi
