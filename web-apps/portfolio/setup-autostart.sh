#!/bin/bash
# Setup auto-start for portfolio servers

echo "🔧 Setting up auto-start..."

# Copy service file
sudo cp /home/nxelleai/.openclaw/workspace/portfolio/portfolio-servers.service /etc/systemd/system/

# Reload systemd
sudo systemctl daemon-reload

# Enable service
sudo systemctl enable portfolio-servers.service

# Start service
sudo systemctl start portfolio-servers.service

echo "✅ Auto-start configured!"
echo ""
echo "Commands:"
echo "  sudo systemctl status portfolio-servers  # Check status"
echo "  sudo systemctl stop portfolio-servers    # Stop"
echo "  sudo systemctl start portfolio-servers   # Start"
echo ""
echo "Servers will auto-start on boot! 🚀"
