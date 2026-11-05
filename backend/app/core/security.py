"""
Security and Cryptography Module.
Provides secure password hashing (PBKDF2-HMAC-SHA256) and JWT token generation/validation.
"""

import hashlib
import secrets
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any
import jwt

from app.core.config import settings
from app.core.logging import logger

PBKDF2_ITERATIONS = 100_000


def hash_password(password: str) -> str:
    """Hashes a plaintext password using salted PBKDF2-HMAC-SHA256."""
    salt = secrets.token_hex(16)
    key = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        PBKDF2_ITERATIONS,
    )
    return f"{salt}${key.hex()}"


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifies a plaintext password against a stored salted hash in constant time."""
    try:
        parts = hashed_password.split("$")
        if len(parts) != 2:
            return False
        salt, expected_hash = parts[0], parts[1]
        test_key = hashlib.pbkdf2_hmac(
            "sha256",
            plain_password.encode("utf-8"),
            salt.encode("utf-8"),
            PBKDF2_ITERATIONS,
        )
        return secrets.compare_digest(test_key.hex(), expected_hash)
    except Exception as e:
        logger.error(f"Password verification error: {e}")
        return False


def create_access_token(
    subject: str,
    role: str,
    email: str,
    expires_delta: Optional[timedelta] = None,
) -> str:
    """Encodes a JWT bearer token containing user identity and RBAC role."""
    now = datetime.now(timezone.utc)
    if expires_delta:
        expire = now + expires_delta
    else:
        expire = now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    payload: Dict[str, Any] = {
        "sub": subject,
        "email": email,
        "role": role,
        "iat": int(now.timestamp()),
        "exp": int(expire.timestamp()),
        "iss": "churn-poacher",
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_access_token(token: str) -> Dict[str, Any]:
    """Decodes and validates an incoming JWT token."""
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
            issuer="churn-poacher",
        )
        return payload
    except jwt.ExpiredSignatureError:
        raise ValueError("Authentication token has expired")
    except jwt.InvalidTokenError as e:
        raise ValueError(f"Invalid authentication token: {e}")
