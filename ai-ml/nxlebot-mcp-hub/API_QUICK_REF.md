# Nxlebot MCP API - Quick Reference

**Base URL:** `http://localhost:8080`

---

## 🔒 Security Endpoints

### 1. Scan Security Headers
```bash
curl -X POST http://localhost:8080/security/scan \
  -H "Content-Type: application/json" \
  -d '{"domain":"example.com"}'
```

**Response:**
```json
{
  "domain": "example.com",
  "status_code": 200,
  "security_headers": {
    "CSP": "MISSING",
    "X-XSS-Protection": "MISSING",
    "X-Content-Type-Options": "MISSING",
    "Referrer-Policy": "MISSING",
    "Strict-Transport-Security": "MISSING"
  },
  "missing_headers": ["CSP", "X-XSS-Protection", ...]
}
```

### 2. Find Subdomains
```bash
curl -X POST http://localhost:8080/security/subdomains \
  -H "Content-Type: application/json" \
  -d '{"domain":"example.com"}'
```

**Response:**
```json
{
  "domain": "example.com",
  "subdomains_found": 221,
  "subdomains": ["*.api.example.com", "*.docs.example.com", ...]
}
```

---

## 🎥 Video Generation

### 3. Generate Video Prompt
```bash
curl -X POST http://localhost:8080/video/prompt \
  -H "Content-Type: application/json" \
  -d '{"description":"drone shot over mountain","style":"cinematic"}'
```

**Available Styles:**
- `cinematic` - Dramatic, 4k, cinematic lighting
- `anime` - Vibrant, Studio Ghibli style
- `realistic` - Photorealistic, 8k, natural lighting
- `cyberpunk` - Neon lights, futuristic
- `fantasy` - Magical, ethereal

**Response:**
```json
{
  "prompt": "drone shot over mountain, cinematic lighting, 4k...",
  "style": "cinematic",
  "recommended_models": ["Stable Video Diffusion", "Runway Gen-2", ...],
  "aspect_ratios": ["16:9", "9:16", "1:1", "21:9"]
}
```

---

## 📊 System

### 4. Check Status
```bash
curl http://localhost:8080/status
```

---

## 🚀 Usage Examples

### Bug Bounty Workflow
```bash
# 1. Find subdomains
curl -s -X POST http://localhost:8080/security/subdomains \
  -d '{"domain":"target.com"}' | jq '.subdomains[]'

# 2. Scan each subdomain
for sub in $(cat subdomains.txt); do
  curl -s -X POST http://localhost:8080/security/scan \
    -d "{\"domain\":\"$sub\"}" | jq '.missing_headers'
done
```

### AI Video Workflow
```bash
# Generate optimized prompt
curl -s -X POST http://localhost:8080/video/prompt \
  -d '{"description":"cyberpunk city at night","style":"cyberpunk"}' | \
  jq '.prompt'

# Use prompt with Stable Video Diffusion / Runway / Pika
```

---

## 💡 Monetization Ideas

1. **Security Audit Service**
   - Charge $50-200 per domain scan
   - Generate PDF reports
   - Offer remediation advice

2. **Bug Bounty Automation**
   - Scan multiple targets automatically
   - Track vulnerabilities over time
   - Sell as SaaS

3. **AI Video Service**
   - Generate video prompts for clients
   - Offer full video creation service
   - Charge $10-50 per video

4. **API as Service**
   - Expose API to developers
   - Charge per request
   - Tiered pricing

---

*Managed by Nxlebot MCP Hub* 👑
