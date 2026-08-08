#!/usr/bin/env bash
# please-hire-me — install / remove the recurring run.
# Usage: ./scripts/schedule.sh [install|uninstall|uninstall-all|status]
# Frequency comes from config/settings.json -> schedule.frequency.
#
# Each checkout gets its OWN launchd label and cron tag, derived from its path,
# so two clones can be scheduled at the same time and neither can silently
# overwrite the other. `status` lists every please-hire-me job on the machine.
set -uo pipefail
cd "$(dirname "$0")/.."

REPO="$(pwd -P)"

# Label is per-checkout: a readable folder name plus a hash of the full path, so
# two folders with the same basename still get different labels.
SLUG_BASE="$(basename "$REPO" | tr -c 'A-Za-z0-9' '-' | sed 's/-*$//')"
SLUG_HASH="$(printf '%s' "$REPO" | shasum 2>/dev/null | cut -c1-8)"
[ -z "$SLUG_HASH" ] && SLUG_HASH="$(printf '%s' "$REPO" | cksum | cut -d' ' -f1)"
LABEL="com.pleasehireme.${SLUG_BASE}.${SLUG_HASH}"
PLIST="$HOME/Library/LaunchAgents/$LABEL.plist"
CRON_TAG="# please-hire-me:${SLUG_HASH}"

# Pre-0.2 installs all shared one label and one cron tag. Recognised so an
# existing install migrates cleanly instead of being orphaned.
LEGACY_LABEL="com.pleasehireme.run"
LEGACY_PLIST="$HOME/Library/LaunchAgents/$LEGACY_LABEL.plist"
LEGACY_CRON_TAG="# please-hire-me"

AGENT_DIR="$HOME/Library/LaunchAgents"
ACTION="${1:-status}"

freq() {
  python3 -c "import json;print(json.load(open('config/settings.json')).get('schedule',{}).get('frequency','manual'))" 2>/dev/null
}

seconds_for() {
  case "$1" in
    hourly)         echo 3600 ;;
    every-2-hours)  echo 7200 ;;
    every-3-hours)  echo 10800 ;;
    every-6-hours)  echo 21600 ;;
    daily)          echo 86400 ;;
    *)              echo "" ;;
  esac
}

cron_for() {
  case "$1" in
    hourly)         echo "0 * * * *" ;;
    every-2-hours)  echo "0 */2 * * *" ;;
    every-3-hours)  echo "0 */3 * * *" ;;
    every-6-hours)  echo "0 */6 * * *" ;;
    daily)          echo "0 9 * * *" ;;
    weekdays)       echo "0 9 * * 1-5" ;;
    *)              echo "" ;;
  esac
}

plist_owner() {  # path -> the checkout that plist runs
  sed -n 's:.*<key>WorkingDirectory</key><string>\(.*\)</string>.*:\1:p' "$1" 2>/dev/null | head -1
}

# A plist is ours only if it is BOTH named com.pleasehireme.* AND actually runs
# this project's scheduled_run.sh. The name alone is not proof; nothing here may
# ever unload or delete a LaunchAgent belonging to something else.
is_ours() {
  [ -f "$1" ] || return 1
  grep -q 'scripts/scheduled_run\.sh' "$1" 2>/dev/null
}

each_plist() {  # every please-hire-me plist on this machine, legacy included
  local p
  for p in $(ls "$AGENT_DIR"/com.pleasehireme.*.plist "$LEGACY_PLIST" 2>/dev/null | sort -u); do
    is_ours "$p" && echo "$p"
  done
}

# An old install owned by THIS checkout becomes this checkout's new per-path job.
# One owned by a different checkout is left alone; it is not ours to remove.
migrate_legacy() {
  [ -f "$LEGACY_PLIST" ] || return 0
  local owner; owner="$(plist_owner "$LEGACY_PLIST")"
  if [ "$owner" = "$REPO" ]; then
    launchctl unload "$LEGACY_PLIST" 2>/dev/null
    rm -f "$LEGACY_PLIST"
    echo "Migrated this checkout off the old shared label '$LEGACY_LABEL'."
  fi
}

# Two checkouts applying to jobs under one name is worth saying out loud, but it
# is the user's call, so this informs and never blocks.
warn_other_schedules() {
  local p owner shown=0
  for p in $(each_plist); do
    [ "$p" = "$PLIST" ] && continue
    owner="$(plist_owner "$p")"
    [ -n "$owner" ] && [ "$owner" = "$REPO" ] && continue
    if [ "$shown" = "0" ]; then
      echo
      echo "  NOTE: another please-hire-me checkout is also scheduled on this Mac:"
      shown=1
    fi
    echo "    ${owner:-unknown}  ($(basename "$p"))"
  done
  if [ "$shown" = "1" ]; then
    echo "  Both will run and both apply under your name. Each keeps its own queue,"
    echo "  logs, and history. Turn one off with:  cd <that folder> && ./scripts/schedule.sh uninstall"
  fi
}

install_launchd() {
  local f="$1" interval plist_schedule
  interval="$(seconds_for "$f")"
  if [ -n "$interval" ]; then
    plist_schedule="  <key>StartInterval</key><integer>$interval</integer>"
  elif [ "$f" = "weekdays" ]; then
    plist_schedule="  <key>StartCalendarInterval</key>
  <array>"
    for d in 1 2 3 4 5; do
      plist_schedule+="
    <dict><key>Weekday</key><integer>$d</integer><key>Hour</key><integer>9</integer><key>Minute</key><integer>0</integer></dict>"
    done
    plist_schedule+="
  </array>"
  else
    echo "Unknown frequency '$f'." >&2; return 1
  fi

  mkdir -p "$AGENT_DIR" logs
  cat > "$PLIST" <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key><string>$LABEL</string>
  <key>ProgramArguments</key>
  <array>
    <string>/bin/bash</string>
    <string>$REPO/scripts/scheduled_run.sh</string>
  </array>
  <key>WorkingDirectory</key><string>$REPO</string>
$plist_schedule
  <key>RunAtLoad</key><false/>
  <key>StandardOutPath</key><string>$REPO/logs/launchd.out.log</string>
  <key>StandardErrorPath</key><string>$REPO/logs/launchd.err.log</string>
</dict>
</plist>
EOF

  launchctl unload "$PLIST" 2>/dev/null
  if launchctl load "$PLIST" 2>/dev/null; then
    echo "Installed launchd job '$LABEL' ($f)."
    echo "  repo:  $REPO"
    echo "  plist: $PLIST"
    echo "  log:   $REPO/logs/scheduled-run.log"
    case "$REPO" in
      "$HOME/Desktop"/*|"$HOME/Documents"/*|"$HOME/Downloads"/*)
        echo
        echo "  NOTE: macOS privacy blocks background jobs from reading Desktop, Documents,"
        echo "  and Downloads. Either move this repo somewhere else (e.g. ~/please-hire-me), or"
        echo "  grant Full Disk Access to /bin/bash in System Settings > Privacy & Security."
        ;;
    esac
    warn_other_schedules
  else
    echo "launchctl load failed. Falling back to cron." >&2
    install_cron "$f"
  fi
}

install_cron() {
  local f="$1" spec
  spec="$(cron_for "$f")"
  [ -z "$spec" ] && { echo "Unknown frequency '$f'." >&2; return 1; }
  local line="$spec cd $REPO && /bin/bash scripts/scheduled_run.sh $CRON_TAG"
  ( crontab -l 2>/dev/null | grep -v "$CRON_TAG"; echo "$line" ) | crontab -
  echo "Installed cron entry ($f):"
  echo "  $line"
}

# Removes only THIS checkout's job, plus the legacy one when it points here.
uninstall_this() {
  local removed=0
  if [ -f "$PLIST" ]; then
    launchctl unload "$PLIST" 2>/dev/null
    rm -f "$PLIST"; echo "Removed launchd job '$LABEL'."; removed=1
  fi
  if [ -f "$LEGACY_PLIST" ] && [ "$(plist_owner "$LEGACY_PLIST")" = "$REPO" ]; then
    launchctl unload "$LEGACY_PLIST" 2>/dev/null
    rm -f "$LEGACY_PLIST"; echo "Removed legacy launchd job '$LEGACY_LABEL'."; removed=1
  fi
  local tag
  for tag in "$CRON_TAG" "$LEGACY_CRON_TAG"; do
    if crontab -l 2>/dev/null | grep -q "cd $REPO .*$tag"; then
      crontab -l 2>/dev/null | grep -v "cd $REPO .*$tag" | crontab -
      echo "Removed cron entry."; removed=1
    fi
  done
  [ "$removed" = "0" ] && echo "Nothing scheduled for this checkout."
  return 0
}

# Escape hatch: every please-hire-me job on this machine, whoever owns it.
# Scoped by BOTH the com.pleasehireme.* name and the scheduled_run.sh check in
# is_ours, so no other application's LaunchAgent can be caught by it. Cron lines
# are matched on this project's own tag for the same reason.
uninstall_every() {
  local p removed=0
  for p in $(each_plist); do
    launchctl unload "$p" 2>/dev/null
    rm -f "$p"; echo "Removed $(basename "$p" .plist)."; removed=1
  done
  if crontab -l 2>/dev/null | grep -q "scheduled_run.sh.*$LEGACY_CRON_TAG"; then
    crontab -l 2>/dev/null | grep -v "scheduled_run.sh.*$LEGACY_CRON_TAG" | crontab -
    echo "Removed cron entries."; removed=1
  fi
  [ "$removed" = "0" ] && echo "Nothing scheduled anywhere."
  return 0
}

show_status() {
  echo "Repo:      $REPO"
  echo "Label:     $LABEL"
  echo "Frequency: $(freq)  (config/settings.json -> schedule.frequency)"
  if [ -f "$PLIST" ]; then
    echo "launchd:   installed ($PLIST)"
    launchctl list 2>/dev/null | grep "$LABEL" | sed 's/^/           /'
  else
    echo "launchd:   not installed for this checkout"
  fi
  if crontab -l 2>/dev/null | grep -q "cd $REPO "; then
    echo "cron:      $(crontab -l 2>/dev/null | grep "cd $REPO " | head -1)"
  else
    echo "cron:      not installed for this checkout"
  fi

  local p owner any=0
  for p in $(each_plist); do
    [ "$any" = "0" ] && { echo; echo "All please-hire-me schedules on this Mac:"; any=1; }
    owner="$(plist_owner "$p")"
    if [ "$owner" = "$REPO" ]; then
      echo "  * ${owner:-unknown}   <- this checkout"
    else
      echo "    ${owner:-unknown}"
    fi
  done
}

case "$ACTION" in
  install)
    F="$(freq)"
    [ "$F" = "manual" ] && { echo "schedule.frequency is 'manual'. Set it in config/settings.json first."; exit 0; }
    migrate_legacy
    if [ "$(uname -s)" = "Darwin" ]; then install_launchd "$F"; else install_cron "$F"; fi
    ;;
  uninstall)     uninstall_this ;;
  uninstall-all) uninstall_every ;;
  status)        show_status ;;
  *) echo "Usage: $0 [install|uninstall|uninstall-all|status]"; exit 1 ;;
esac
