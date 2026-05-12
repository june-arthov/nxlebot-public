#!/bin/bash
# ==========================================
# Nxlebot Pro v3 - Production Deployment
# ==========================================

set -e

echo "============================================"
echo "🚀 Nxlebot Pro v3 - Production Setup"
echo "============================================"

# Configuration
APP_NAME="nxlebot-chat"
APP_DIR="/home/nxelleai/.openclaw/workspace/chat-pro"
PORT=8087
USER="nxelleai"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}✅ Starting production deployment...${NC}"

# Step 1: Create systemd service
echo -e "${YELLOW}📝 Creating systemd service...${NC}"

sudo cat > /etc/systemd/system/${APP_NAME}.service << EOF
[Unit]
Description=Nxlebot Pro v3 Chat Server
After=network.target

[Service]
Type=simple
User=${USER}
WorkingDirectory=${APP_DIR}
ExecStart=/usr/bin/python3 ${APP_DIR}/server-v3.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal
SyslogIdentifier=${APP_NAME}

# Environment
Environment="PYTHONUNBUFFERED=1"
Environment="PORT=${PORT}"

# Security
NoNewPrivileges=true
PrivateTmp=true

[Install]
WantedBy=multi-user.target
EOF

echo -e "${GREEN}✅ Systemd service created${NC}"

# Step 2: Create environment file
echo -e "${YELLOW}📝 Creating environment file...${NC}"

cat > ${APP_DIR}/.env << EOF
# Nxlebot Pro v3 - Environment Configuration
# Production Settings

# Server
PORT=8087
HOST=0.0.0.0
DEBUG=false

# Telegram Bot (Optional)
# Get token from @BotFather
TELEGRAM_BOT_TOKEN=

# OpenClaw Gateway
OPENCLAW_API=http://localhost:18789

# Chat Server
CHAT_SERVER_URL=http://localhost:8087

# Logging
LOG_LEVEL=INFO
LOG_FILE=${APP_DIR}/chat-server.log

# Security
# Change these in production!
API_KEY=
SECRET_KEY=
EOF

chmod 600 ${APP_DIR}/.env

echo -e "${GREEN}✅ Environment file created${NC}"

# Step 3: Create log rotation
echo -e "${YELLOW}📝 Setting up log rotation...${NC}"

sudo cat > /etc/logrotate.d/${APP_NAME} << EOF
${APP_DIR}/*.log {
    daily
    missingok
    rotate 14
    compress
    delaycompress
    notifempty
    create 0640 ${USER} ${USER}
    postrotate
        systemctl reload ${APP_NAME} > /dev/null 2>&1 || true
    endscript
}
EOF

echo -e "${GREEN}✅ Log rotation configured${NC}"

# Step 4: Create backup script
echo -e "${YELLOW}📝 Creating backup script...${NC}"

cat > ${APP_DIR}/backup.sh << 'BACKUP_EOF'
#!/bin/bash
# Automated backup script

BACKUP_DIR="/home/nxelleai/.openclaw/backups/chat"
DATE=$(date +%Y%m%d_%H%M%S)
mkdir -p ${BACKUP_DIR}

# Backup chat history
if [ -f "chat_history_v3.json" ]; then
    cp chat_history_v3.json ${BACKUP_DIR}/chat_history_${DATE}.json
    echo "✅ Chat history backed up"
fi

# Keep only last 30 days
find ${BACKUP_DIR} -name "*.json" -mtime +30 -delete

echo "✅ Backup complete: ${BACKUP_DIR}/chat_history_${DATE}.json"
BACKUP_EOF

chmod +x ${APP_DIR}/backup.sh

echo -e "${GREEN}✅ Backup script created${NC}"

# Step 5: Setup auto-backup cron job
echo -e "${YELLOW}📝 Setting up auto-backup...${NC}"

(crontab -l 2>/dev/null; echo "0 2 * * * cd ${APP_DIR} && ./backup.sh") | crontab -

echo -e "${GREEN}✅ Auto-backup scheduled (daily at 2 AM)${NC}"

# Step 6: Create monitoring script
echo -e "${YELLOW}📝 Creating monitoring script...${NC}"

cat > ${APP_DIR}/monitor.sh << 'MONITOR_EOF'
#!/bin/bash
# Simple monitoring script

SERVICE="nxlebot-chat"
PORT=8087

# Check if service is running
if systemctl is-active --quiet ${SERVICE}; then
    echo "✅ Service is running"
else
    echo "❌ Service is NOT running"
    echo "🔄 Attempting to restart..."
    sudo systemctl restart ${SERVICE}
fi

# Check if port is listening
if netstat -tlnp 2>/dev/null | grep -q ":${PORT}"; then
    echo "✅ Port ${PORT} is listening"
else
    echo "❌ Port ${PORT} is NOT listening"
fi

# Show recent logs
echo ""
echo "📋 Recent logs:"
journalctl -u ${SERVICE} -n 10 --no-pager
MONITOR_EOF

chmod +x ${APP_DIR}/monitor.sh

echo -e "${GREEN}✅ Monitoring script created${NC}"

# Step 7: Enable and start service
echo -e "${YELLOW}🔄 Enabling and starting service...${NC}"

sudo systemctl daemon-reload
sudo systemctl enable ${APP_NAME}
sudo systemctl start ${APP_NAME}

# Wait for service to start
sleep 3

# Check status
if systemctl is-active --quiet ${APP_NAME}; then
    echo -e "${GREEN}✅ Service started successfully${NC}"
else
    echo -e "${RED}❌ Service failed to start${NC}"
    echo "Check logs: journalctl -u ${APP_NAME} -n 50"
    exit 1
fi

# Step 8: Final checks
echo ""
echo -e "${YELLOW}🔍 Running final checks...${NC}"

# Check port
if netstat -tlnp 2>/dev/null | grep -q ":${PORT}"; then
    echo -e "${GREEN}✅ Port ${PORT} is open${NC}"
else
    echo -e "${YELLOW}⚠️  Port ${PORT} is not responding yet${NC}"
fi

# Show status
echo ""
echo -e "${GREEN}============================================${NC}"
echo -e "${GREEN}✅ PRODUCTION DEPLOYMENT COMPLETE!${NC}"
echo -e "${GREEN}============================================${NC}"
echo ""
echo "📊 Service Status:"
sudo systemctl status ${APP_NAME} --no-pager -l
echo ""
echo "🌐 Access URL: http://localhost:${PORT}"
echo "📋 Logs: journalctl -u ${APP_NAME} -f"
echo "🔄 Restart: sudo systemctl restart ${APP_NAME}"
echo "🛑 Stop: sudo systemctl stop ${APP_NAME}"
echo "📊 Monitor: ${APP_DIR}/monitor.sh"
echo "💾 Backup: ${APP_DIR}/backup.sh"
echo ""
echo -e "${GREEN}============================================${NC}"
