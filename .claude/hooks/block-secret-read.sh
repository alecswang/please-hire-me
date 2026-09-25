#!/bin/bash
# PreToolUse guard for Bash: keep the agent's shell away from the secrets scripts/code_broker.py handles.
# The broker reads the Gmail app password from the Keychain and puts codes on the clipboard; the agent must
# only ever invoke the broker, never read either store itself. This is policy, not a sandbox: it blocks the
# obvious reads so a secret cannot land in a transcript by accident.
input=$(cat)
if printf '%s' "$input" | grep -Eqi 'find-(generic|internet)-password|dump-keychain|export-keychain|pbpaste|generalPasteboard|NSPasteboard|stringForType|get the clipboard|clipboard info|BW_SESSION|\bbw (get|export|unlock|list)\b|\bop (read|item get)\b'; then
  echo "Blocked by .claude/hooks/block-secret-read.sh: the agent never reads the Keychain, clipboard or vault directly. Use scripts/code_broker.py." >&2
  exit 2
fi
exit 0
