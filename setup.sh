#!/usr/bin/env bash
# please-hire-me — one-time setup. Run this once, then use ./run.sh.
set -uo pipefail
cd "$(dirname "$0")"

BOLD=$'\033[1m'; DIM=$'\033[2m'; GREEN=$'\033[32m'; YELLOW=$'\033[33m'; RED=$'\033[31m'; OFF=$'\033[0m'
ok()   { printf '%s✓%s %s\n' "$GREEN" "$OFF" "$1"; }
warn() { printf '%s!%s %s\n' "$YELLOW" "$OFF" "$1"; }
bad()  { printf '%s✗%s %s\n' "$RED" "$OFF" "$1"; }
head1(){ printf '\n%s%s%s\n' "$BOLD" "$1" "$OFF"; }

ask() { # ask VAR "Question" "default"
  local __var="$1" __q="$2" __def="${3:-}" __ans=""
  if [ -n "$__def" ]; then
    printf '  %s %s[%s]%s ' "$__q" "$DIM" "$__def" "$OFF"
  else
    printf '  %s ' "$__q"
  fi
  IFS= read -r __ans || true
  [ -z "$__ans" ] && __ans="$__def"
  printf -v "$__var" '%s' "$__ans"
}

yesno() { # yesno "Question" default(y|n) -> returns 0 for yes
  local q="$1" def="${2:-y}" a=""
  local hint="[Y/n]"; [ "$def" = "n" ] && hint="[y/N]"
  printf '  %s %s%s%s ' "$q" "$DIM" "$hint" "$OFF"
  IFS= read -r a || true
  a="${a:-$def}"
  case "$a" in [Yy]*) return 0;; *) return 1;; esac
}

cat <<'BANNER'

  ┌────────────────────────────────────────────────┐
  │  please-hire-me — setup                        │
  │  An agent that applies to jobs while you sleep │
  └────────────────────────────────────────────────┘

BANNER

# ── 1. Prerequisites ─────────────────────────────────────────────────────────
head1 "1. Checking prerequisites"

if command -v claude >/dev/null 2>&1; then
  ok "Claude Code CLI found ($(claude --version 2>/dev/null | head -1))"
elif [ -x "$HOME/.local/bin/claude" ]; then
  ok "Claude Code CLI found at ~/.local/bin/claude"
else
  bad "Claude Code CLI not found."
  echo "     Install it, then re-run this script:"
  echo "       npm install -g @anthropic-ai/claude-code"
  echo "     Then run 'claude' once and sign in with your Claude subscription."
  exit 1
fi

if [ -f "$HOME/.claude.json" ] || [ -d "$HOME/.claude" ]; then
  ok "Claude Code config found (you appear to be signed in)"
else
  warn "No Claude Code config yet. Run 'claude' once and sign in, then come back."
fi

command -v python3 >/dev/null 2>&1 && ok "python3 found" || { bad "python3 required."; exit 1; }

echo
echo "  ${BOLD}Chrome extension${OFF} — the agent drives your real Chrome, so it needs:"
echo "    1. Google Chrome installed and running."
echo "    2. The Claude in Chrome extension installed and signed in to the SAME"
echo "       Claude account as your Claude Code CLI."
echo "    3. Permission granted for job-board sites (greenhouse.io, ashbyhq.com,"
echo "       lever.co, and company career pages)."
echo "  ${DIM}Without it every run stops immediately and logs 'extension not connected'.${OFF}"
echo

# ── 2. Config files ──────────────────────────────────────────────────────────
head1 "2. Config files"

copy_template() { # copy_template example target
  if [ -f "$2" ]; then
    ok "$2 already exists (leaving it alone)"
  else
    cp "$1" "$2"; ok "created $2 from template"
  fi
}
copy_template config/settings.example.json config/settings.json
copy_template config/answers.example.md   config/answers.md
copy_template data/queue.example.md       data/queue.md
mkdir -p applications logs screenshots state data
[ -f logs/applications-log.md ] || printf '# Application log\n\n' > logs/applications-log.md
[ -f state/status.md ] || printf '# Run status history\n\nNo runs yet.\n' > state/status.md

# ── 3. Profile ───────────────────────────────────────────────────────────────
head1 "3. Who you are"

WRITE_PROFILE=1
if [ -f config/profile.json ]; then
  warn "config/profile.json already exists."
  yesno "Overwrite it with fresh answers?" n || WRITE_PROFILE=0
fi

if [ "$WRITE_PROFILE" = "1" ]; then
  cp config/profile.example.json config/profile.json
  echo "  ${DIM}Press Enter to accept a default. You can edit config/profile.json any time.${OFF}"
  echo
  ask FULLNAME   "Full legal name:"            ""
  FIRST_DEFAULT="${FULLNAME%% *}"; LAST_DEFAULT="${FULLNAME##* }"
  ask FIRSTNAME  "First name as it goes on forms:" "$FIRST_DEFAULT"
  ask LASTNAME   "Last name:"                  "$LAST_DEFAULT"
  ask EMAIL      "Email:"                      ""
  ask PHONE      "Phone (digits only):"        ""
  ask CITY       "City, ST you live in:"       ""
  ask LINKEDIN   "LinkedIn URL:"               ""
  ask GITHUB     "GitHub URL:"                 ""
  ask WEBSITE    "Personal site (optional):"   ""
  echo
  ask SCHOOL     "School:"                     ""
  ask SCHOOLFULL "School's full name as ATS pickers spell it:" "$SCHOOL"
  ask MAJOR      "Major:"                      "Computer Science"
  ask DEGREETYPE "Degree type:"                "Undergraduate / Bachelor's"
  ask GRAD       "Graduation (e.g. May 2027):" ""
  ask GPA        "GPA (only used when a form requires it):" ""
  ask SCHOOLMAIL "School email:"               ""
  echo
  if yesno "Do you need visa sponsorship to work in the US?" n; then
    NEEDSPON="Yes, need sponsorship"; SPON_BOOL=true
    ask VISASTATUS "Current visa status (e.g. F1 visa):" "F1 visa"
    ask VISATYPE   "Visa type to pick in a dropdown (OPT/H1B/TN/None/Other):" "OPT"
    ask CITIZEN    "Country of citizenship:" ""
    AUTHUS="Yes, authorized to work in the US"
  else
    NEEDSPON="No, I do not need sponsorship"; SPON_BOOL=false
    VISASTATUS="US citizen or permanent resident"; VISATYPE="None"; CITIZEN="United States"
    AUTHUS="Yes, authorized to work in the US"
  fi
  echo
  ask RESUMESRC  "Path to your resume PDF:"    ""
  RESUMESRC="${RESUMESRC/#\~/$HOME}"
  RESUME_REL="data/resume.pdf"
  if [ -n "$RESUMESRC" ] && [ -f "$RESUMESRC" ]; then
    cp "$RESUMESRC" data/resume.pdf && ok "copied resume to data/resume.pdf"
  else
    warn "No resume copied. Put your PDF at data/resume.pdf before your first run."
  fi
  ask TRANSCRIPTSRC "Path to your transcript PDF (optional, Enter to skip):" ""
  TRANSCRIPTSRC="${TRANSCRIPTSRC/#\~/$HOME}"
  TRANSCRIPT_REL=""
  if [ -n "$TRANSCRIPTSRC" ] && [ -f "$TRANSCRIPTSRC" ]; then
    cp "$TRANSCRIPTSRC" data/transcript.pdf && TRANSCRIPT_REL="data/transcript.pdf" && ok "copied transcript to data/transcript.pdf"
  fi

  FULLNAME="$FULLNAME" FIRSTNAME="$FIRSTNAME" LASTNAME="$LASTNAME" EMAIL="$EMAIL" PHONE="$PHONE" \
  CITY="$CITY" LINKEDIN="$LINKEDIN" GITHUB="$GITHUB" WEBSITE="$WEBSITE" SCHOOL="$SCHOOL" \
  SCHOOLFULL="$SCHOOLFULL" MAJOR="$MAJOR" DEGREETYPE="$DEGREETYPE" GRAD="$GRAD" GPA="$GPA" \
  SCHOOLMAIL="$SCHOOLMAIL" NEEDSPON="$NEEDSPON" VISASTATUS="$VISASTATUS" VISATYPE="$VISATYPE" \
  CITIZEN="$CITIZEN" AUTHUS="$AUTHUS" RESUME_REL="$RESUME_REL" TRANSCRIPT_REL="$TRANSCRIPT_REL" \
  python3 - <<'PY'
import json, os
p = 'config/profile.json'
d = json.load(open(p))
e = os.environ.get
d.update({
  "name_combined": e("FULLNAME",""), "name_legal": e("FULLNAME",""),
  "name_preferred": e("FIRSTNAME",""), "first_name": e("FIRSTNAME",""),
  "legal_first_name": e("FULLNAME","").split(" ")[0], "preferred_first_name": e("FIRSTNAME",""),
  "last_name": e("LASTNAME",""),
  "email": e("EMAIL",""), "school_email": e("SCHOOLMAIL",""), "phone": e("PHONE",""),
  "location": e("CITY",""),
  "linkedin": e("LINKEDIN",""), "github": e("GITHUB",""), "website": e("WEBSITE",""),
  "resume": e("RESUME_REL","data/resume.pdf"), "transcript": e("TRANSCRIPT_REL",""),
  "work_authorized_us": e("AUTHUS",""), "visa_needs_sponsorship": e("NEEDSPON",""),
  "visa_status": e("VISASTATUS",""), "citizenship": e("CITIZEN",""),
  "sponsorship_visa_type_answer": e("VISATYPE",""),
  "school": e("SCHOOL",""), "school_full_name": e("SCHOOLFULL",""), "major": e("MAJOR",""),
  "degree_type_answer": e("DEGREETYPE",""), "graduation": e("GRAD",""),
  "college_end_date": e("GRAD","") + " (graduation)",
  "degree": f'{e("DEGREETYPE","")}, {e("MAJOR","")}, {e("SCHOOL","")}',
  "highest_education_completed_answer": f'{e("DEGREETYPE","")} in {e("MAJOR","")}, {e("SCHOOL","")}',
  "us_person_export_control_answer": ("I am a US citizen or permanent resident"
      if e("NEEDSPON","").startswith("No") else
      f'Not a US person. Citizen of {e("CITIZEN","")}, currently on {e("VISASTATUS","")}.'),
  "gpa": e("GPA",""),
})
for k in ("mailing_address_street","mailing_address_city","mailing_address_state",
          "mailing_address_zip","mailing_address_full","high_school_name","high_school_grad_year",
          "current_employer"):
    d[k] = ""
json.dump(d, open(p,'w'), indent=2, ensure_ascii=False)
open(p,'a').write('\n')
PY
  ok "wrote config/profile.json"
fi

# ── 4. Run settings ──────────────────────────────────────────────────────────
head1 "4. How the agent should run"

ask MAXAPPS "Max applications per run:" "3"
echo "  Frequency: manual · hourly · every-2-hours · every-3-hours · every-6-hours · daily · weekdays"
ask FREQ    "How often should it run?" "daily"
echo "  What are you looking for?  1) internships  2) new-grad full-time  3) both"
ask SENIORITY "Pick 1, 2, or 3:" "3"
ask MINCOMP "Minimum annual comp for FULL-TIME roles, USD (0 for no floor):" "0"
if [ "$SENIORITY" != "2" ]; then
  echo "  ${DIM}Internships post hourly pay, so the annual floor above is ignored for them.${OFF}"
  ask INTERNHOURLY "Minimum hourly rate for internships, USD (0 for no floor):" "0"
else
  INTERNHOURLY=0
fi
ask LOCS    "Locations, comma separated (add 'Remote (US)' if you want remote):" "Remote (US)"
echo
echo "  ${DIM}One or two sentences on what makes a company worth your time. The agent uses this${OFF}"
echo "  ${DIM}when a posting lists no salary. Example: 'Only frontier AI labs and top quant firms.'${OFF}"
ask PRESTIGE "Your quality bar:" "Any reputable company hiring for this role."
ask SKIPS    "Companies to never apply to, comma separated (optional):" ""

MAXAPPS="$MAXAPPS" FREQ="$FREQ" MINCOMP="$MINCOMP" LOCS="$LOCS" PRESTIGE="$PRESTIGE" \
SENIORITY="$SENIORITY" INTERNHOURLY="$INTERNHOURLY" \
SKIPS="$SKIPS" SPON_BOOL="${SPON_BOOL:-false}" GRAD="${GRAD:-}" python3 - <<'PY'
import json, os
p = 'config/settings.json'
d = json.load(open(p))
e = os.environ.get
split = lambda s: [x.strip() for x in s.split(',') if x.strip()]
d["run"]["max_applications_per_run"] = int(e("MAXAPPS","3") or 3)
d["schedule"]["frequency"] = e("FREQ","manual")
d["targets"]["min_annual_comp_usd"] = int(e("MINCOMP","0") or 0)
d["targets"]["internship_min_hourly_usd"] = int(e("INTERNHOURLY","0") or 0)
d["targets"]["seniority"] = {"1": ["internship"], "2": ["new-grad"]}.get(e("SENIORITY","3"), ["new-grad", "internship"])
d["targets"]["locations"] = split(e("LOCS","")) or ["Remote (US)"]
d["targets"]["prestige_note"] = e("PRESTIGE","")
d["targets"]["skip_companies"] = split(e("SKIPS",""))
d["eligibility"]["needs_visa_sponsorship"] = e("SPON_BOOL","false") == "true"
if e("GRAD"): d["eligibility"]["graduation"] = e("GRAD")
json.dump(d, open(p,'w'), indent=2, ensure_ascii=False)
open(p,'a').write('\n')
PY
ok "wrote config/settings.json"

# ── 5. Schedule ──────────────────────────────────────────────────────────────
head1 "5. Schedule"
if [ "$FREQ" != "manual" ]; then
  if yesno "Install the $FREQ schedule now so it runs by itself?" y; then
    ./scripts/schedule.sh install || warn "Schedule install failed. Run ./scripts/schedule.sh install by hand."
  else
    echo "  ${DIM}Later: ./scripts/schedule.sh install${OFF}"
  fi
else
  echo "  ${DIM}Frequency is 'manual'. Run ./run.sh yourself, or set a frequency in config/settings.json.${OFF}"
fi

# ── 6. What's left ───────────────────────────────────────────────────────────
head1 "Setup done. One thing left, and it is the important one."
cat <<EOF

  ${BOLD}Open config/answers.md and fill it in.${OFF} That file is the only source the agent
  may use for free-text answers, and it is the difference between an agent that
  applies to 50 jobs and one that stops at every "why do you want this role?".

  It needs:
    · 2-4 short paragraphs about things you actually built, with real numbers.
    · A fact sheet: every job, project, and result, one line each.
    · Your preset answers for salary, visa, EEO, and start date.

  Nothing in there means no invented answers. Anything the agent cannot answer
  from that file, it leaves blank and logs as NEEDS HUMAN.

  Then:
    ${BOLD}./run.sh${OFF}          one run now, obeying config/settings.json
    ${BOLD}./run.sh 1${OFF}        a single application, good for a first test
    ${BOLD}tail -f logs/scheduled-run.log${OFF}   watch a scheduled run

  Tip for the first run: set "dry_run": true in config/settings.json. The agent
  fills every form and screenshots it, but never clicks submit.

EOF
