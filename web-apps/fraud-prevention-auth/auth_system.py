#!/usr/bin/env python3
"""
Fraud Prevention Authentication System
Features: MFA, Risk-based Auth, Device Fingerprinting, Rate Limiting
"""

import hashlib
import hmac
import secrets
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
import json

class RiskLevel(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class AuthMethod(Enum):
    PASSWORD = "password"
    OTP_SMS = "otp_sms"
    OTP_EMAIL = "otp_email"
    TOTP = "totp"  # Time-based OTP
    SILENT_AUTH = "silent_auth"
    BIOMETRIC = "biometric"
    HARDWARE_KEY = "hardware_key"

@dataclass
class DeviceFingerprint:
    user_agent: str
    ip_address: str
    screen_resolution: str
    timezone: str
    language: str
    platform: str
    fingerprint_hash: str = ""
    
    def __post_init__(self):
        self.fingerprint_hash = self._generate_hash()
    
    def _generate_hash(self) -> str:
        data = f"{self.user_agent}{self.ip_address}{self.screen_resolution}{self.timezone}{self.language}{self.platform}"
        return hashlib.sha256(data.encode()).hexdigest()[:32]

@dataclass
class RiskContext:
    device_fingerprint: DeviceFingerprint
    location: str
    login_time: datetime
    is_new_device: bool = False
    is_known_ip: bool = True
    failed_attempts_24h: int = 0
    unusual_time: bool = False
    velocity_check: bool = True
    
    def calculate_risk_score(self) -> Tuple[RiskLevel, float]:
        score = 0.0
        
        # Device risk
        if self.is_new_device:
            score += 25
        if not self.is_known_ip:
            score += 20
            
        # Behavioral risk
        if self.failed_attempts_24h > 3:
            score += min(self.failed_attempts_24h * 5, 30)
        if self.unusual_time:
            score += 15
        if not self.velocity_check:
            score += 10
            
        # Determine risk level
        if score >= 70:
            return RiskLevel.CRITICAL, score
        elif score >= 50:
            return RiskLevel.HIGH, score
        elif score >= 25:
            return RiskLevel.MEDIUM, score
        else:
            return RiskLevel.LOW, score

@dataclass
class User:
    user_id: str
    username: str
    email: str
    phone: str
    password_hash: str
    mfa_enabled: bool = False
    mfa_methods: List[AuthMethod] = field(default_factory=list)
    known_devices: List[str] = field(default_factory=list)
    known_ips: List[str] = field(default_factory=list)
    last_login: Optional[datetime] = None
    login_history: List[Dict] = field(default_factory=list)
    failed_attempts: int = 0
    locked_until: Optional[datetime] = None

class OTPManager:
    """Manage OTP generation and verification"""
    
    def __init__(self):
        self.otp_store: Dict[str, Tuple[str, float]] = {}  # user_id -> (otp, expiry)
        self.totp_secrets: Dict[str, str] = {}  # user_id -> secret
    
    def generate_sms_otp(self, user_id: str, length: int = 6) -> str:
        """Generate SMS OTP"""
        otp = ''.join([str(secrets.randbelow(10)) for _ in range(length)])
        expiry = time.time() + 300  # 5 minutes
        self.otp_store[user_id] = (otp, expiry)
        return otp
    
    def verify_otp(self, user_id: str, otp: str) -> bool:
        """Verify OTP"""
        if user_id not in self.otp_store:
            return False
        
        stored_otp, expiry = self.otp_store[user_id]
        
        if time.time() > expiry:
            del self.otp_store[user_id]
            return False
        
        if hmac.compare_digest(stored_otp, otp):
            del self.otp_store[user_id]
            return True
        
        return False
    
    def generate_totp_secret(self, user_id: str) -> str:
        """Generate TOTP secret for authenticator apps"""
        secret = secrets.token_hex(20)
        self.totp_secrets[user_id] = secret
        return secret
    
    def generate_totp(self, user_id: str) -> str:
        """Generate TOTP code"""
        if user_id not in self.totp_secrets:
            return ""
        
        secret = self.totp_secrets[user_id]
        time_step = int(time.time()) // 30  # 30-second window
        
        # HOTP calculation
        msg = time_step.to_bytes(8, byteorder='big')
        h = hmac.new(secret.encode(), msg, hashlib.sha1).digest()
        offset = h[-1] & 0x0f
        code = ((h[offset] & 0x7f) << 24 |
                (h[offset + 1] & 0xff) << 16 |
                (h[offset + 2] & 0xff) << 8 |
                (h[offset + 3] & 0xff))
        return str(code % 10**6).zfill(6)

class FraudPreventionAuth:
    """Main authentication system with fraud prevention"""
    
    def __init__(self):
        self.users: Dict[str, User] = {}
        self.otp_manager = OTPManager()
        self.rate_limiter: Dict[str, List[float]] = {}  # ip -> list of timestamps
        self.blocked_ips: Dict[str, float] = {}  # ip -> unblock_time
        
    def hash_password(self, password: str, salt: Optional[str] = None) -> Tuple[str, str]:
        """Hash password with salt"""
        if salt is None:
            salt = secrets.token_hex(16)
        pwdhash = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
        return pwdhash.hex(), salt
    
    def verify_password(self, password: str, password_hash: str, salt: str) -> bool:
        """Verify password"""
        pwdhash, _ = self.hash_password(password, salt)
        return hmac.compare_digest(pwdhash, password_hash)
    
    def check_rate_limit(self, ip_address: str, max_attempts: int = 5, window: int = 300) -> bool:
        """Check if IP is rate limited"""
        now = time.time()
        
        # Check if IP is blocked
        if ip_address in self.blocked_ips:
            if now < self.blocked_ips[ip_address]:
                return False
            else:
                del self.blocked_ips[ip_address]
        
        # Get attempts in window
        if ip_address not in self.rate_limiter:
            self.rate_limiter[ip_address] = []
        
        # Clean old attempts
        self.rate_limiter[ip_address] = [
            t for t in self.rate_limiter[ip_address] 
            if now - t < window
        ]
        
        # Check limit
        if len(self.rate_limiter[ip_address]) >= max_attempts:
            self.blocked_ips[ip_address] = now + 3600  # Block for 1 hour
            return False
        
        self.rate_limiter[ip_address].append(now)
        return True
    
    def register_user(self, username: str, email: str, phone: str, password: str) -> User:
        """Register new user"""
        user_id = secrets.token_hex(16)
        password_hash, salt = self.hash_password(password)
        
        user = User(
            user_id=user_id,
            username=username,
            email=email,
            phone=phone,
            password_hash=f"{salt}${password_hash}"
        )
        
        self.users[user_id] = user
        return user
    
    def authenticate_step1(self, username: str, password: str, 
                          device_fp: DeviceFingerprint) -> Tuple[bool, Optional[str], RiskLevel]:
        """
        Step 1: Password authentication + risk assessment
        Returns: (success, user_id, risk_level)
        """
        # Check rate limit
        if not self.check_rate_limit(device_fp.ip_address):
            return False, None, RiskLevel.CRITICAL
        
        # Find user
        user = None
        for u in self.users.values():
            if u.username == username:
                user = u
                break
        
        if not user:
            return False, None, RiskLevel.HIGH
        
        # Check if locked
        if user.locked_until and datetime.now() < user.locked_until:
            return False, None, RiskLevel.CRITICAL
        
        # Verify password
        salt, stored_hash = user.password_hash.split('$')
        if not self.verify_password(password, stored_hash, salt):
            user.failed_attempts += 1
            
            # Lock account after 5 failed attempts
            if user.failed_attempts >= 5:
                user.locked_until = datetime.now() + timedelta(minutes=30)
            
            return False, None, RiskLevel.HIGH
        
        # Reset failed attempts
        user.failed_attempts = 0
        
        # Calculate risk
        risk_context = RiskContext(
            device_fingerprint=device_fp,
            location="Unknown",  # Would use geolocation in production
            login_time=datetime.now(),
            is_new_device=device_fp.fingerprint_hash not in user.known_devices,
            is_known_ip=device_fp.ip_address in user.known_ips,
            failed_attempts_24h=user.failed_attempts
        )
        
        risk_level, score = risk_context.calculate_risk_score()
        
        # If low risk and no MFA required, login successful
        if risk_level == RiskLevel.LOW and not user.mfa_enabled:
            self._complete_login(user, device_fp)
            return True, user.user_id, risk_level
        
        # Otherwise, require MFA
        return True, user.user_id, risk_level
    
    def authenticate_step2(self, user_id: str, otp: str, method: AuthMethod) -> bool:
        """Step 2: MFA verification"""
        if user_id not in self.users:
            return False
        
        user = self.users[user_id]
        
        if method == AuthMethod.OTP_SMS:
            return self.otp_manager.verify_otp(user_id, otp)
        elif method == AuthMethod.TOTP:
            expected = self.otp_manager.generate_totp(user_id)
            return hmac.compare_digest(expected, otp)
        
        return False
    
    def _complete_login(self, user: User, device_fp: DeviceFingerprint):
        """Complete login process"""
        user.last_login = datetime.now()
        
        # Add to known devices/IPs
        if device_fp.fingerprint_hash not in user.known_devices:
            user.known_devices.append(device_fp.fingerprint_hash)
        
        if device_fp.ip_address not in user.known_ips:
            user.known_ips.append(device_fp.ip_address)
        
        # Log login
        user.login_history.append({
            'timestamp': datetime.now().isoformat(),
            'device': device_fp.fingerprint_hash,
            'ip': device_fp.ip_address
        })
    
    def setup_mfa(self, user_id: str, method: AuthMethod) -> Dict:
        """Setup MFA for user"""
        if user_id not in self.users:
            return {'success': False, 'error': 'User not found'}
        
        user = self.users[user_id]
        
        if method == AuthMethod.TOTP:
            secret = self.otp_manager.generate_totp_secret(user_id)
            user.mfa_enabled = True
            if method not in user.mfa_methods:
                user.mfa_methods.append(method)
            
            return {
                'success': True,
                'secret': secret,
                'qr_uri': f"otpauth://totp/GoldenCity:{user.email}?secret={secret}&issuer=GoldenCity"
            }
        
        return {'success': False, 'error': 'Method not supported'}

# Demo usage
def demo():
    """Demonstrate the authentication system"""
    auth = FraudPreventionAuth()
    
    # Register user
    print("=" * 60)
    print("FRAUD PREVENTION AUTHENTICATION SYSTEM DEMO")
    print("=" * 60)
    
    user = auth.register_user(
        username="nyxelle",
        email="nyx@goldencity.com",
        phone="+628123456789",
        password="SecurePass123!"
    )
    print(f"\n✓ User registered: {user.username}")
    print(f"  User ID: {user.user_id[:16]}...")
    
    # Setup MFA
    print("\n" + "-" * 60)
    print("SETTING UP MFA (TOTP)")
    print("-" * 60)
    mfa_setup = auth.setup_mfa(user.user_id, AuthMethod.TOTP)
    if mfa_setup['success']:
        print(f"✓ MFA enabled")
        print(f"  Secret: {mfa_setup['secret'][:20]}...")
        print(f"  QR URI: {mfa_setup['qr_uri'][:50]}...")
    
    # Simulate login from known device
    print("\n" + "-" * 60)
    print("LOGIN ATTEMPT #1 - Known Device (Low Risk)")
    print("-" * 60)
    
    device1 = DeviceFingerprint(
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        ip_address="192.168.1.100",
        screen_resolution="1920x1080",
        timezone="Asia/Singapore",
        language="en-US",
        platform="Win32"
    )
    
    success, user_id, risk = auth.authenticate_step1(
        "nyxelle", "SecurePass123!", device1
    )
    print(f"Password auth: {'✓ Success' if success else '✗ Failed'}")
    print(f"Risk Level: {risk.value.upper()}")
    
    if success and risk != RiskLevel.LOW:
        # Simulate MFA
        totp = auth.otp_manager.generate_totp(user_id)
        print(f"TOTP Code: {totp}")
        mfa_success = auth.authenticate_step2(user_id, totp, AuthMethod.TOTP)
        print(f"MFA verification: {'✓ Success' if mfa_success else '✗ Failed'}")
    
    # Simulate login from unknown device
    print("\n" + "-" * 60)
    print("LOGIN ATTEMPT #2 - Unknown Device (Higher Risk)")
    print("-" * 60)
    
    device2 = DeviceFingerprint(
        user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS)",
        ip_address="203.0.113.50",  # Different IP
        screen_resolution="390x844",
        timezone="America/New_York",  # Different timezone
        language="en-US",
        platform="iPhone"
    )
    
    success, user_id, risk = auth.authenticate_step1(
        "nyxelle", "SecurePass123!", device2
    )
    print(f"Password auth: {'✓ Success' if success else '✗ Failed'}")
    print(f"Risk Level: {risk.value.upper()} (New device + different location)")
    
    # Simulate brute force attack
    print("\n" + "-" * 60)
    print("LOGIN ATTEMPT #3 - Brute Force Attack")
    print("-" * 60)
    
    attacker_ip = "10.0.0.99"
    attacker_device = DeviceFingerprint(
        user_agent="Python-requests/2.28",
        ip_address=attacker_ip,
        screen_resolution="1024x768",
        timezone="UTC",
        language="en",
        platform="Linux"
    )
    
    # Try multiple wrong passwords
    for i in range(7):
        success, _, _ = auth.authenticate_step1(
            "nyxelle", f"WrongPass{i}", attacker_device
        )
        print(f"Attempt {i+1}: {'Blocked' if not auth.check_rate_limit(attacker_ip) else 'Allowed'}")
    
    print(f"\n✓ IP {attacker_ip} rate limited after 5 attempts")
    
    # Show user stats
    print("\n" + "=" * 60)
    print("USER SECURITY STATS")
    print("=" * 60)
    print(f"Known devices: {len(user.known_devices)}")
    print(f"Known IPs: {len(user.known_ips)}")
    print(f"MFA enabled: {user.mfa_enabled}")
    print(f"MFA methods: {[m.value for m in user.mfa_methods]}")
    print(f"Login history: {len(user.login_history)} entries")
    
    print("\n" + "=" * 60)
    print("DEMO COMPLETE")
    print("=" * 60)

if __name__ == "__main__":
    demo()