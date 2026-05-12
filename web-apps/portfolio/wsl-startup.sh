#!/bin/bash
# Add to Windows Task Scheduler or .bashrc

# Kill existing servers
pkill -f "http.server 889" 2>/dev/null

# Start all servers
bash /home/nxelleai/.openclaw/workspace/portfolio/start-server.sh

echo "Portfolio servers ready! 🔥"
