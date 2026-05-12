# API Keys Status

_Last updated: 2026-04-07 11:56 GMT+8_

---

## 🔑 GroqCloud API

| Field | Value |
|-------|-------|
| **API Key** | `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` |
| **Status** | ✅ ACTIVE & WORKING |
| **Model** | llama-3.1-8b-instant |
| **Speed** | ~500 tokens/sec |
| **Free Tier** | 30 requests/minute |
| **Test** | ✅ Passed |

---

## 🔑 Google Gemini API

| Field | Value |
|-------|-------|
| **API Key** | `AIzaSyBK06h3bgGgx-0hxNHTBNsBBIGf5AU6UyE` |
| **Project** | 42336769167 |
| **Status** | ⚠️ QUOTA EXHAUSTED |
| **Retry After** | 51 seconds |
| **Free Tier** | 0 requests remaining |

### Issue:
```
Quota exceeded for:
- generativelanguage.googleapis.com/generate_content_free_tier_requests
- Limit: 0
```

### Solutions:
1. Wait 51s for rate limit reset
2. Create new Google Cloud project
3. Use different Google account
4. Switch to Groq/OpenRouter

---

## 🎯 Next Steps

- [ ] Test again after 51s
- [ ] Or create new project for fresh quota
- [ ] Or setup Groq as alternative

---

## 📊 Free Tier Limits (Gemini)

| Limit | Value |
|-------|-------|
| Requests/minute | 15 RPM |
| Requests/day | 1,000 |
| Tokens/month | 1M |
