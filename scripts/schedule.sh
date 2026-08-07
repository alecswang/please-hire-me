#!/usr/bin/env bash
# please-hire-me — install / remove the recurring run.
# Usage: ./scripts/schedule.sh [install|uninstall|status]
# Frequency comes from config/settings.json -> schedule.frequency.
set -uo pipefail
cd "$(dirname "$0")/.."

REPO="$(pwd -P)"
LABEL="com.pleasehireme.run"
PLIST="$HOME/Library/LaunchAgents/$LABEL.plist"
CRON_TAG="# please-hire-me"
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

  mkdir -p "$HOME/Library/LaunchAgents" logs
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

uninstall_all() {
  local removed=0
  if [ -f "$PLIST" ]; then
    launchctl unload "$PLIST" 2>/dev/null
    rm -f "$PLIST"; echo "Removed launchd job '$LABEL'."; removed=1
  fi
  if crontab -l 2>/dev/null | grep -q "$CRON_TAG"; then
    crontab -l 2>/dev/null | grep -v "$CRON_TAG" | crontab -
    echo "Removed cron entry."; removed=1
  fi
  [ "$removed" = "0" ] && echo "Nothing scheduled."
}

show_status() {
  echo "Repo:      $REPO"
  echo "Frequency: $(freq)  (config/settings.json -> schedule.frequency)"
  if [ -f "$PLIST" ]; then
    echo "launchd:   installed ($PLIST)"
    launchctl list 2>/dev/null | grep "$LABEL" | sed 's/^/           /'
  else
    echo "launchd:   not installed"
  fi
  if crontab -l 2>/dev/null | grep -q "$CRON_TAG"; then
    echo "cron:      $(crontab -l 2>/dev/null | grep "$CRON_TAG")"
  else
    echo "cron:      not installed"
  fi
}

case "$ACTION" in
  install)
    F="$(freq)"
    [ "$F" = "manual" ] && { echo "schedule.frequency is 'manual'. Set it in config/settings.json first."; exit 0; }
    uninstall_all >/dev/null 2>&1
    if [ "$(uname -s)" = "Darwin" ]; then install_launchd "$F"; else install_cron "$F"; fi
    ;;
  uninstall) uninstall_all ;;
  status)    show_status ;;
  *) echo "Usage: $0 [install|uninstall|status]"; exit 1 ;;
esac
