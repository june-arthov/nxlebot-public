# Nxlebot MCP Hub 👑

**Unified MCP Gateway** buat manage semua AI tools, bug bounty, video generation, dan code documentation.

## 📁 Structure

```
nxlebot-mcp-hub/
├── api_server.py            # FastAPI HTTP Server (Port 8080)
├── nxlebot_mcp_gateway.py   # MCP Protocol Server
├── code_explainer.py        # AI Code Documentation Generator
├── requirements.txt         # Python dependencies
├── generated_courses/       # Output HTML Courses
├── BUG_BOUNTY_MCP_SERVERS.md# Directory MCP servers
└── README.md                # This file
```

## 🚀 Quick Start

### 1. Activate venv
```bash
source /home/nxelleai/.openclaw/workspace/venv_bounty/bin/activate
```

### 2. Run API Server (HTTP)
```bash
cd nxlebot-mcp-hub
uvicorn api_server:app --host 0.0.0.0 --port 8080 --reload
```

### 3. Available API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/security/scan` | POST | Scan security headers (CSP, XSS, etc) |
| `/security/subdomains` | POST | Find subdomains via Certificate Transparency |
| `/video/prompt` | POST | Generate optimized AI video prompts |
| `/docs/generate` | POST | **NEW!** Generate interactive HTML course from codebase |
| `/status` | GET | Check API status |

### 4. Usage Examples

**Scan Security:**
```bash
curl -X POST http://localhost:8080/security/scan -d '{"domain":"google.com"}'
```

**Generate Course:**
```bash
curl -X POST http://localhost:8080/docs/generate \
  -d '{"target_path":"hackingtool/sqlmap-dev", "output_name":"sqlmap.html"}'
```

## 🛠️ Features

1. **Security Scanner** - Automated header & subdomain scanning
2. **Video Prompt Generator** - Optimize prompts for Runway/Pika/SVD
3. **Code Explainer** - Turn any codebase into interactive HTML course (Plain English + Metaphors)
4. **MCP Gateway** - Extensible architecture for more tools

## 💰 Monetization Ideas

1. **Security Audit SaaS** - Charge $50-200 per domain scan
2. **AI Video Service** - Sell prompt engineering & generation
3. **Code Documentation Service** - Charge for legacy code explanation
4. **Bug Bounty Automation** - 24/7 scanning pipeline

---

*Raja Hacker + MCP = UNSTOPPABLE* 👑🐍🐍
