# 🚀 Nxlebot Pro v3 - Production Deployment Guide

---

## 📋 **Quick Start**

### **One-Command Deployment:**
```bash
cd /home/nxelleai/.openclaw/workspace/chat-pro
./production.sh
```

---

## 🔧 **Manual Setup**

### **1. Install Dependencies**
```bash
# No external dependencies needed!
# Uses Python 3 standard library only
python3 --version  # Should be 3.8+
```

### **2. Configure Environment**
```bash
# Edit .env file
nano .env

# Set Telegram bot token (optional)
TELEGRAM_BOT_TOKEN="your_token_here"
```

### **3. Start Server**
```bash
# Development
python3 server-v3.py

# Production (via systemd)
sudo systemctl start nxlebot-chat
sudo systemctl enable nxlebot-chat
```

---

## 🌐 **Access Points**

| Service | URL | Port |
|---------|-----|------|
| **Chat Web UI** | http://localhost:8087 | 8087 |
| **API** | http://localhost:8087/api/chat | 8087 |
| **Telegram Webhook** | POST /api/telegram/message | 8087 |

---

## 🔌 **Telegram Integration**

### **Option 1: Run Telegram Bridge**
```bash
# Set bot token
export TELEGRAM_BOT_TOKEN="your_bot_token_from_botfather"

# Run bridge
python3 openclaw-telegram-bridge.py
```

### **Option 2: Configure OpenClaw Webhook**
```yaml
# In OpenClaw config
webhooks:
  telegram_sync:
    url: http://localhost:8087/api/telegram/message
    events:
      - message.received
```

### **Option 3: Manual API Call**
```bash
curl -X POST http://localhost:8087/api/telegram/message \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "8621864972",
    "message": "Hello from Telegram",
    "message_id": 123
  }'
```

---

## 📊 **Monitoring**

### **Check Status**
```bash
# Service status
sudo systemctl status nxlebot-chat

# Quick monitor
./monitor.sh

# View logs
journalctl -u nxlebot-chat -f

# Last 50 lines
journalctl -u nxlebot-chat -n 50
```

### **API Health Check**
```bash
# Check if server is responding
curl http://localhost:8087/api/stats

# Expected response:
# {"success": true, "total": 10, "web": 5, "tg": 3, "bot": 5}
```

---

## 💾 **Backup**

### **Manual Backup**
```bash
./backup.sh
```

### **Auto Backup**
- Runs daily at 2:00 AM
- Keeps last 30 days
- Location: `/home/nxelleai/.openclaw/backups/chat/`

### **Restore Backup**
```bash
cp /home/nxelleai/.openclaw/backups/chat/chat_history_YYYYMMDD.json chat_history_v3.json
sudo systemctl restart nxlebot-chat
```

---

## 🔒 **Security**

### **Firewall Rules**
```bash
# Allow only localhost (recommended)
sudo ufw allow from 127.0.0.1 to any port 8087

# Or allow specific IP
sudo ufw allow from 192.168.1.100 to any port 8087

# Or allow all (NOT recommended for production)
sudo ufw allow 8087
```

### **HTTPS Setup (Optional)**
```bash
# Using Nginx reverse proxy
sudo apt install nginx
sudo nano /etc/nginx/sites-available/nxlebot

# Nginx config:
server {
    listen 443 ssl;
    server_name chat.yourdomain.com;
    
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    
    location / {
        proxy_pass http://localhost:8087;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}

sudo ln -s /etc/nginx/sites-available/nxlebot /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

---

## 🛠️ **Troubleshooting**

### **Service Won't Start**
```bash
# Check logs
journalctl -u nxlebot-chat -n 100

# Check port conflict
netstat -tlnp | grep 8087

# Kill conflicting process
sudo kill -9 <PID>

# Restart service
sudo systemctl restart nxlebot-chat
```

### **Port Already in Use**
```bash
# Find process using port 8087
lsof -i :8087

# Kill it
sudo kill -9 <PID>

# Or change port in .env
PORT=8088
```

### **Chat Not Saving**
```bash
# Check file permissions
ls -la chat_history_v3.json

# Fix permissions
chmod 644 chat_history_v3.json
chown nxelleai:nxelleai chat_history_v3.json
```

---

## 📈 **Performance Tuning**

### **Increase Max Connections**
Edit `server-v3.py`:
```python
# Change this line:
with socketserver.TCPServer(("", PORT), Handler) as httpd:

# To:
socketserver.TCPServer.allow_reuse_address = True
with socketserver.TCPServer(("", PORT), Handler) as httpd:
    httpd.max_children = 100  # Add this
```

### **Enable Caching**
Add to `.env`:
```bash
CACHE_ENABLED=true
CACHE_TTL=300  # 5 minutes
```

---

## 🔄 **Updates**

### **Update from Git**
```bash
cd /home/nxelleai/.openclaw/workspace/chat-pro
git pull origin master
sudo systemctl restart nxlebot-chat
```

### **Manual Update**
```bash
# Stop service
sudo systemctl stop nxlebot-chat

# Backup
./backup.sh

# Replace files
# ... copy new files ...

# Start service
sudo systemctl start nxlebot-chat
```

---

## 📱 **Mobile Access**

### **Local Network**
```bash
# Find your IP
hostname -I

# Access from mobile
http://<YOUR_IP>:8087
```

### **Remote Access (Tailscale)**
```bash
# If using Tailscale
tailscale ip

# Access from anywhere
http://<TAILSCALE_IP>:8087
```

---

## 🎯 **Feature Checklist**

| Feature | Status | Notes |
|---------|--------|-------|
| ✅ Web Chat UI | Production | Port 8087 |
| ✅ Telegram Sync | Ready | Need bot token |
| ✅ Emoji Picker | Production | 30+ emojis |
| ✅ Smart Responses | Production | Context-aware |
| ✅ Auto Backup | Production | Daily 2 AM |
| ✅ Monitoring | Production | ./monitor.sh |
| ✅ Log Rotation | Production | 14 days |
| ✅ Systemd Service | Production | Auto-start |
| ⏳ HTTPS | Optional | Need cert |
| ⏳ Database | Future | SQLite → PostgreSQL |

---

## 📞 **Support**

### **Logs Location**
```bash
# Systemd logs
journalctl -u nxlebot-chat -f

# Application logs
tail -f /home/nxelleai/.openclaw/workspace/chat-pro/chat-server.log
```

### **Common Commands**
```bash
# Start
sudo systemctl start nxlebot-chat

# Stop
sudo systemctl stop nxlebot-chat

# Restart
sudo systemctl restart nxlebot-chat

# Status
sudo systemctl status nxlebot-chat

# Logs
journalctl -u nxlebot-chat -f

# Monitor
./monitor.sh

# Backup
./backup.sh
```

---

## 🎉 **You're Ready!**

**Access your production chat:**
```
http://localhost:8087
```

**Or from network:**
```
http://<YOUR_IP>:8087
```

---

*Deployed with ❤️ by Nxlebot*
