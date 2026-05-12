#!/bin/bash
# Auto-start portfolio servers

echo "🚀 Starting portfolio servers..."

# Golden City
cd /home/nxelleai/.openclaw/workspace/portfolio/golden-city
python3 -m http.server 8892 > /dev/null 2>&1 &
echo "✅ Golden City: http://localhost:8892"

# Clear Cafe
cd /home/nxelleai/.openclaw/workspace/portfolio/clear-cafe-final
python3 -m http.server 8891 > /dev/null 2>&1 &
echo "✅ Clear Cafe: http://localhost:8891"

# Restaurant Sample
cd /home/nxelleai/.openclaw/workspace/portfolio/restaurant-sample
python3 -m http.server 8889 > /dev/null 2>&1 &
echo "✅ Restaurant Sample: http://localhost:8889"

echo ""
echo "All servers running! 🔥"
