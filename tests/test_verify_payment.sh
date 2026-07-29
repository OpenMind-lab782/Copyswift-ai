#!/data/data/com.termux/files/usr/bin/bash

LOGFILE="logs/swift_api.log"

mkdir -p logs

python -m payment_engine.api.app > "$LOGFILE" 2>&1 &
SERVER_PID=$!

echo "Starting Swift Payment Engine API..."

READY=0
for i in $(seq 1 15); do
    if curl -s http://127.0.0.1:8000/health >/dev/null 2>&1; then
        READY=1
        break
    fi
    sleep 1
done

if [ "$READY" -ne 1 ]; then
    echo ""
    echo "❌ Server did not become ready."
    echo ""
    cat "$LOGFILE"
    kill "$SERVER_PID" 2>/dev/null
    wait "$SERVER_PID" 2>/dev/null
    exit 1
fi

echo ""
echo "Testing POST /verify-payment..."
echo ""

curl -s \
  -X POST \
  -H "Content-Type: application/json" \
  -d '{"reference":"TEST-001","gateway":"paystack"}' \
  http://127.0.0.1:8000/verify-payment

echo ""
echo ""
echo "Stopping server..."

kill "$SERVER_PID"
wait "$SERVER_PID" 2>/dev/null

echo "✅ Verify-payment API test completed successfully."
