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
    echo "❌ Server failed to start."
    echo ""
    cat "$LOGFILE"
    kill "$SERVER_PID" 2>/dev/null
    wait "$SERVER_PID" 2>/dev/null
    exit 1
fi

echo ""
echo "==============================="
echo "TEST 1: GET /transactions"
echo "==============================="
curl -s http://127.0.0.1:8000/transactions

echo ""
echo ""
echo "==============================="
echo "TEST 2: GET /transactions/TEST-001"
echo "==============================="
curl -s http://127.0.0.1:8000/transactions/TEST-001

echo ""
echo ""
echo "==============================="
echo "TEST 3: GET /transactions/UNKNOWN-001"
echo "==============================="
curl -s http://127.0.0.1:8000/transactions/UNKNOWN-001

echo ""
echo ""
echo "Stopping server..."

kill "$SERVER_PID"
wait "$SERVER_PID" 2>/dev/null

echo "✅ Transactions API tests completed successfully."
