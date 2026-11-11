#!/bin/sh
set -e

# Doc token tu tuy chon cua add-on (/data/options.json) neu nguoi dung co dat.
if [ -f /data/options.json ]; then
  TOKEN=$(python3 -c "import json; print(json.load(open('/data/options.json')).get('token', '') or '')" 2>/dev/null || echo "")
  if [ -n "$TOKEN" ]; then
    export PRINT_BOT_TOKEN="$TOKEN"
  fi
fi

exec python3 /app/print-learn-server.py
