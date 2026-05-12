#!/bin/bash
# OC+ Runner — dipanggil cronjob Hermes
# Usage: ./nxlebot-runner.sh <script.ocp>
# Output: hasil eksekusi (ke stdout → dikirim Hermes ke Telegram)

SCRIPT="${1:-health-check.ocp}"
SCRIPT_DIR="$(cd "$(dirname "$0")/../examples" && pwd)"
API="http://localhost:8000/execute"

SCRIPT_CONTENT=$(cat "$SCRIPT_DIR/$SCRIPT" 2>/dev/null)
if [ -z "$SCRIPT_CONTENT" ]; then
  echo "❌ Script '$SCRIPT' gak ditemukan di $SCRIPT_DIR"
  exit 1
fi

RESULT=$(curl -s -X POST "$API" \
  -H "Content-Type: application/json" \
  -d "$(jq -n --arg script "$SCRIPT_CONTENT" '{script: $script}')" 2>/dev/null)

STATUS=$(echo "$RESULT" | jq -r '.status // "error"')
OUTPUT=$(echo "$RESULT" | jq -r '.output // "no output"')
EXIT_CODE=$(echo "$RESULT" | jq -r '.exit_code // -1')

echo "📋 *OC+ $SCRIPT*"
echo "Status: $STATUS (exit: $EXIT_CODE)"
echo "\`\`\`"
echo "$OUTPUT"
echo "\`\`\`"
