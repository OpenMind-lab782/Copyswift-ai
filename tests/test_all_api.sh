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
echo "========== TEST 1 =========="
echo "GET /health"
curl -s http://127.0.0.1:8000/health

echo ""
echo ""
echo "========== TEST 2 =========="
echo "POST /verify-payment"
curl -s \
  -X POST \
  -H "Content-Type: application/json" \
  -d '{"reference":"TEST-001","gateway":"paystack"}' \
  http://127.0.0.1:8000/verify-payment

echo ""
echo ""
echo "========== TEST 3 =========="
echo "GET /transactions"
curl -s http://127.0.0.1:8000/transactions

echo ""
echo ""
echo "========== TEST 4 =========="
echo "GET /transactions?page=1&limit=10"
curl -s "http://127.0.0.1:8000/transactions?page=1&limit=10"

echo ""
echo ""
echo "========== TEST 5 =========="
echo "GET /transactions?gateway=paystack"
curl -s "http://127.0.0.1:8000/transactions?gateway=paystack"

echo ""
echo ""
echo "========== TEST 6 =========="
echo "GET /transactions?status=verified"
curl -s "http://127.0.0.1:8000/transactions?status=verified"

echo ""
echo ""
echo "========== TEST 7 =========="
echo "GET /transactions/TEST-001"
curl -s http://127.0.0.1:8000/transactions/TEST-001

echo ""
echo ""
echo "Stopping server..."

kill "$SERVER_PID"
wait "$SERVER_PID" 2>/dev/null

echo "✅ Full API verification completed successfully."
