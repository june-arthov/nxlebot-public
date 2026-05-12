# 💰 Token Usage Budget & Tracking

_Last updated: 2026-04-07 04:16 GMT+8_

---

## 🎯 Purpose

Track API token usage to manage costs and avoid unexpected bills.

---

## 📊 Current Usage (2026-04-07 04:16)

| Session | Model | Used / Limit | % Used |
|---------|-------|--------------|--------|
| `agent:main:telegram:direct:8621…` | qwen3.5-plus | 71k / 1000k | 7% |
| `agent:main:main` | qwen3-max-2026-01-23 | 22k / 262k | 8% |
| `agent:main:telegram:slash:8621…` | qwen-turbo | unknown / 200k | ?% |

**Total Estimated:** ~93k tokens (conservative)

---

## 💵 Budget Settings

### Monthly Budget
- **Hard Limit:** $50/month (adjust as needed)
- **Soft Limit:** $30/month (warning threshold)
- **Daily Average:** ~$1.67/day

### Token Cost Reference (approximate)
| Model | Cost per 1M tokens |
|-------|-------------------|
| qwen-turbo | ~$0.20 |
| qwen3.5-plus | ~$0.50 |
| qwen3-max | ~$2.00 |
| gpt-4 | ~$30.00 |
| gpt-4-turbo | ~$10.00 |

---

## ⚠️ Alert Thresholds

| Threshold | Action |
|-----------|--------|
| 50% budget ($15) | 🟡 Warning - monitor usage |
| 75% budget ($22.50) | 🟠 Caution - reduce heavy tasks |
| 90% budget ($27) | 🔴 Critical - pause non-essential |
| 100% budget ($30) | 🛑 STOP - wait for next month |

---

## 📝 Usage Notes

- **Heavy tasks:** Long research, code generation, large file analysis
- **Medium tasks:** Normal chat, web search, small file edits
- **Light tasks:** Quick questions, status checks, heartbeats

### Cost-Saving Tips
1. Use cheaper models (qwen-turbo) for simple tasks
2. Batch similar requests together
3. Avoid redundant searches/queries
4. Use local tools when possible (SQLMap, etc.)
5. Cache repeated information

---

## 🔄 Tracking Schedule

- **Daily:** Quick check (heartbeat)
- **Weekly:** Review usage pattern
- **Monthly:** Reset counter, adjust budget

---

## 📈 Log

| Date | Session | Model | Tokens | Est. Cost | Notes |
|------|---------|-------|--------|-----------|-------|
| 2026-04-07 | main | qwen3.5-plus | 71k | ~$0.04 | Setup session |
| 2026-04-07 | main | qwen3-max | 22k | ~$0.04 | Identity setup |

**Total Today:** ~93k tokens | **Est. Cost:** ~$0.08

---

## 🎯 Monthly Target

Keep usage under **$30/month** = ~15M tokens (mixed models)

At current rate: ✅ **ON TRACK**
