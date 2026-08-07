#!/usr/bin/env bash
# Wrapper used by the scheduler (launchd / cron). One bounded run, everything logged.
# Run it by hand any time to see exactly what the scheduler sees.
set -uo pipefail

cd "$(dirname "$0")/.."
mkdir -p logs
LOG_FILE="logs/scheduled-run.log"

{
  printf '\n=== Scheduled run: %s ===\n' "$(date '+%Y-%m-%d %H:%M:%S %Z')"
  ./run.sh
  status=$?
  printf '=== Session exited with status %s ===\n' "$status"

  # Optional local post-run hook. Not shipped: drop your own script at this path and set
  # integrations.post_run_script in config/settings.json to enable it.
  HOOK="$(python3 -c "import json;print(json.load(open('config/settings.json')).get('integrations',{}).get('post_run_script',''))" 2>/dev/null)"
  if [ -n "$HOOK" ] && [ -f "$HOOK" ]; then
    python3 "$HOOK" 2>&1 || printf 'post-run hook failed (non-fatal)\n'
  fi
} >> "$LOG_FILE" 2>&1

exit "$status"
