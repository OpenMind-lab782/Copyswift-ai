#!/data/data/com.termux/files/usr/bin/bash

LOGFILE="logs/swift_api.log"

mkdir -p logs

python -m payment_engine.api.app > "$LOGFILE" 2>&1 &
SERVER_PID=$!

echo "Starting server..."
sleep 3

echo ""
echo "==== Registered Endpoints ===="
python - << 'PY'
from payment_engine.api.app import app

for rule in sorted(app.url_map.iter_rules(), key=lambda r: r.rule):
    methods = ",".join(sorted(rule.methods - {"HEAD","OPTIONS"}))
    print(f"{methods:8} {rule.rule}")
PY

echo ""
echo "Stopping server..."
kill "$SERVER_PID" 2>/dev/null
wait "$SERVER_PID" 2>/dev/null
