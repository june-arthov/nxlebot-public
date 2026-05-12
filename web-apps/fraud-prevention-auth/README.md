# 🔐 Fraud Prevention Authentication System

Advanced authentication system with multi-layered fraud prevention for The Golden City platform.

## 🛡️ Features

### Authentication Methods
- **Password Authentication** - PBKDF2 with SHA-256 (100k iterations)
- **SMS OTP** - 6-digit codes, 5-minute expiry
- **TOTP** - Time-based OTP for authenticator apps (Google Authenticator, Authy)
- **Silent Authentication** - Background verification (prepared for implementation)
- **Hardware Keys** - YubiKey support (prepared for implementation)

### Fraud Prevention
- **Device Fingerprinting** - Track devices by multiple attributes
- **Risk-Based Authentication** - Adaptive MFA based on risk score
- **Rate Limiting** - Block IPs after failed attempts
- **Account Lockout** - Auto-lock after 5 failed attempts
- **Velocity Checks** - Detect unusual login patterns

### Risk Factors
| Factor | Weight | Description |
|--------|--------|-------------|
| New Device | +25 | Unknown device fingerprint |
| Unknown IP | +20 | IP not in user's history |
| Failed Attempts | +5/attempt | Recent failed logins |
| Unusual Time | +15 | Login outside normal hours |
| Velocity | +10 | Too many attempts too fast |

### Risk Levels
- **LOW** (0-24): Standard login
- **MEDIUM** (25-49): Require MFA
- **HIGH** (50-69): Require MFA + email verification
- **CRITICAL** (70+): Block login, manual review

## 🚀 Usage

### Basic Setup
```python
from auth_system import FraudPreventionAuth, DeviceFingerprint

# Initialize
auth = FraudPreventionAuth()

# Register user
user = auth.register_user(
    username="nyxelle",
    email="nyx@goldencity.com",
    phone="+628123456789",
    password="SecurePass123!"
)

# Setup MFA
mfa_setup = auth.setup_mfa(user.user_id, AuthMethod.TOTP)
print(f"Secret: {mfa_setup['secret']}")
```

### Login Flow
```python
# Step 1: Password + Risk Assessment
device = DeviceFingerprint(
    user_agent="Mozilla/5.0...",
    ip_address="192.168.1.100",
    screen_resolution="1920x1080",
    timezone="Asia/Singapore",
    language="en-US",
    platform="Win32"
)

success, user_id, risk = auth.authenticate_step1(
    username="nyxelle",
    password="SecurePass123!",
    device_fp=device
)

# Step 2: MFA (if required)
if risk != RiskLevel.LOW:
    totp = input("Enter TOTP: ")
    mfa_success = auth.authenticate_step2(
        user_id, totp, AuthMethod.TOTP
    )
```

## 📊 Security Metrics

### Password Security
- Salted hashing (PBKDF2)
- 100,000 iterations
- Unique salt per user
- Timing attack resistant (hmac.compare_digest)

### OTP Security
- Cryptographically secure random
- Time-bound expiry (5 minutes)
- Single-use only
- TOTP: 30-second windows

### Rate Limiting
- 5 attempts per 5 minutes
- 1-hour block after limit
- Per-IP tracking
- Automatic cleanup

## 🔧 Integration with Golden City

### For Academy Platform
```python
# Student login with course access control
if auth_success and risk_level == RiskLevel.LOW:
    grant_course_access(user_id, course_id)
elif auth_success and risk_level == RiskLevel.MEDIUM:
    grant_readonly_access(user_id, course_id)
    require_email_verification()
```

### For Career Platform
```python
# Employer verification
if user.mfa_enabled and risk_level in [RiskLevel.LOW, RiskLevel.MEDIUM]:
    allow_job_posting(employer_id)
else:
    require_identity_verification(employer_id)
```

## 📝 Research Sources

Based on best practices from:
- 1Password Authentication Methods Guide
- CIAM Best Practices (Frontegg, Ping Identity)
- Vonage Silent Authentication
- 8x8 Fraud Prevention Blog
- Adaptive MFA Research (LoginRadius)

## 🎯 Next Steps

1. **Database Integration** - Connect to PostgreSQL/MongoDB
2. **SMS Gateway** - Integrate Twilio/8x8 for OTP
3. **Email Service** - SendGrid/AWS SES for notifications
4. **Monitoring** - Log all auth attempts for audit
5. **Machine Learning** - Train fraud detection model

## 👑 The King Hacker's Note

> "Real security isn't about blocking everyone. It's about letting the right people in while keeping the bad actors out. This system balances security with user experience - the hallmark of professional fraud prevention."

---

Built for The Golden City - Where Good People Build Tomorrow 🏛️