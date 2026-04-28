"""
auth_utils.py
─────────────
JWT creation/verification and pbkdf2_sha256 password hashing helpers.
"""

import os
from datetime import datetime, timedelta, timezone
from typing import Optional

from jose import JWTError, jwt
from passlib.context import CryptContext
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY", "change-me-in-production")
ALGORITHM  = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440"))

# pbkdf2_sha256 context
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

# ── Password helpers ──────────────────────────────────────────────────────────

def hash_password(plain: str) -> str:
    return pwd_context.hash(plain)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


# ── JWT helpers ───────────────────────────────────────────────────────────────

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a signed JWT.  `data` must include at minimum `sub` (user ID as str).
    The frontend decodes the payload client-side to extract `full_name` and `sub`,
    so we embed those fields directly (see Login.jsx lines 130-134).
    """
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta if expires_delta else timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def decode_access_token(token: str) -> Optional[dict]:
    """
    Decode and verify a JWT.  Returns the payload dict or None on failure.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None
