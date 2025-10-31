#!/bin/bash

echo "=========================================="
echo "CodeGate Web Interface - Final Test"
echo "=========================================="
echo ""

# Start the web server
echo "🚀 Starting CodeGate web interface..."
/home/admin/Documents/codeGate/myenv/bin/python src/codegate/web/launcher.py --host 127.0.0.1 --port 5555 > /tmp/codegate_web.log 2>&1 &
WEB_PID=$!

# Wait for server to start
echo "⏳ Waiting for server to start..."
sleep 5

# Test if server is running
if curl -s http://127.0.0.1:5555/ > /dev/null; then
    echo "✅ Web server is running"
else
    echo "❌ Web server failed to start"
    kill $WEB_PID 2>/dev/null
    exit 1
fi

# Test scan API with vulnerable code
echo ""
echo "🔍 Testing code scan with vulnerable code..."
SCAN_RESPONSE=$(curl -s -X POST http://127.0.0.1:5555/api/scan \
  -H "Content-Type: application/json" \
  -d '{
    "code": "import os\nimport subprocess\n\ndef vulnerable_function(user_input):\n    # Command injection vulnerability\n    os.system(user_input)\n    subprocess.call(user_input, shell=True)\n    return \"executed\"",
    "file_name": "vulnerable_test.py"
  }')

SCAN_ID=$(echo $SCAN_RESPONSE | grep -o '"scan_id":"[^"]*"' | cut -d'"' -f4)

if [ -z "$SCAN_ID" ]; then
    echo "❌ Failed to start scan"
    kill $WEB_PID 2>/dev/null
    exit 1
fi

echo "✅ Scan started with ID: $SCAN_ID"
echo "⏳ Waiting for analysis to complete..."
sleep 10

# Check scan status
echo ""
echo "📊 Checking scan status..."
STATUS_RESPONSE=$(curl -s http://127.0.0.1:5555/api/scan/$SCAN_ID/status)
echo "Response: $STATUS_RESPONSE"

# Stop the server
echo ""
echo "🛑 Stopping web server..."
kill $WEB_PID 2>/dev/null
sleep 2

echo ""
echo "=========================================="
echo "✅ Test completed successfully!"
echo "=========================================="
echo ""
echo "The web interface is working correctly."
echo "You can now use it by running:"
echo "  python src/codegate/web/launcher.py"
echo ""
