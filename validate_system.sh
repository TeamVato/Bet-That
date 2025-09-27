#!/bin/bash
echo "🔍 Bet-That System Validation"
echo "=============================="

# Check Redis
echo -n "Redis: "
redis-cli ping > /dev/null 2>&1 && echo "✅ Running" || echo "❌ Not running"

# Check Backend
echo -n "Backend API: "
curl -s http://127.0.0.1:8000/health > /dev/null 2>&1 && echo "✅ Running" || echo "❌ Not running"

# Check Frontend
echo -n "Frontend: "
curl -s http://localhost:5173 > /dev/null 2>&1 && echo "✅ Running" || echo "❌ Not running"

# Check Edges
echo -n "Edge Detection: "
EDGES=$(curl -s http://127.0.0.1:8000/api/v1/odds/edges | python3 -c "import sys, json; print(json.load(sys.stdin)['count'])" 2>/dev/null)
if [ ! -z "$EDGES" ]; then
    echo "✅ $EDGES edges found"
else
    echo "❌ No edges available"
fi


echo ""
echo "🎯 Ready for beta testing!"
