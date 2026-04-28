"""
routes/auth.py
──────────────
POST /auth/register  — Create tenant + super_admin user
POST /auth/login     — Authenticate, return JWT
GET  /auth/me        — Return current user's profile + tenant
PATCH /auth/me/profile  — Update display name
PATCH /auth/me/password — Change password
"""

import re
import uuid
import secrets
import os
from datetime import datetime, timezone, timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from db.database import get_db
from db.models import Tenant, UserProfile, RoleEnum
from schemas import (
    RegisterRequest, LoginRequest, AuthResponse, MeResponse,
    UserProfileOut, TenantOut, UserProfileUpdate, PasswordUpdate,
    MessageResponse,
)
from auth_utils import hash_password, verify_password, create_access_token
from dependencies import get_current_user


router = APIRouter(prefix="/auth", tags=["auth"])


# ── Helpers ───────────────────────────────────────────────────────────────────

def _slugify(text: str) -> str:
    """Convert arbitrary text to a URL-safe slug."""
    slug = text.lower().strip()
    slug = re.sub(r"[^\w\s-]", "", slug)
    slug = re.sub(r"[\s_-]+", "-", slug)
    slug = slug.strip("-")
    return slug or "org"


def _unique_slug(base: str, db: Session) -> str:
    """Ensure the slug is unique in the tenants table."""
    slug = _slugify(base)
    candidate = slug
    counter = 1
    while db.query(Tenant).filter(Tenant.slug == candidate).first():
        candidate = f"{slug}-{counter}"
        counter += 1
    return candidate


def _build_auth_response(user: UserProfile, db: Session) -> dict:
    """Build the dict used by AuthResponse."""
    tenant = db.query(Tenant).filter(Tenant.id == user.tenant_id).first() if user.tenant_id else None
    profile_out = UserProfileOut.model_validate(user)
    tenant_out  = TenantOut.model_validate(tenant) if tenant else None
    token = create_access_token({
        "sub": str(user.id),
        "email": user.email,
        "full_name": user.full_name,
        "role": user.role.value if user.role else "viewer",
        "tenant_id": str(user.tenant_id) if user.tenant_id else None,
    })
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": profile_out,
        "profile": profile_out,
        "tenant": tenant_out,
    }


# ── Routes ────────────────────────────────────────────────────────────────────

@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
def register(body: RegisterRequest, db: Session = Depends(get_db)):
    """
    Register a new organisation.
    Creates:
      1. A Tenant row
      2. A UserProfile with role=super_admin
    Returns a JWT so the user is immediately logged in (matches Register.jsx behaviour).
    """
    # Duplicate email check
    if db.query(UserProfile).filter(UserProfile.email == body.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")

    # Create tenant
    slug = _unique_slug(body.tenant_slug or body.tenant_name, db)
    tenant = Tenant(
        id=uuid.uuid4(),
        name=body.tenant_name,
        slug=slug,
    )
    db.add(tenant)
    db.flush()  # get tenant.id before committing

    # Create super_admin user
    user = UserProfile(
        id=uuid.uuid4(),
        email=body.email,
        full_name=body.full_name,
        password_hash=hash_password(body.password),
        role=RoleEnum.super_admin,
        tenant_id=tenant.id,
        is_active=True,
        account_status="active",
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    return _build_auth_response(user, db)


@router.post("/login", response_model=AuthResponse)
def login(body: LoginRequest, db: Session = Depends(get_db)):
    """
    Authenticate with email + password.
    Returns JWT and user/profile/tenant data.
    Matches the shape consumed by Login.jsx → useAuth.js.
    """
    user = db.query(UserProfile).filter(UserProfile.email == body.email).first()
    if not user or not user.password_hash:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    if not verify_password(body.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    if not user.is_active:
        raise HTTPException(status_code=403, detail="Account is deactivated")

    return _build_auth_response(user, db)


@router.get("/me", response_model=MeResponse)
def me(current_user: UserProfile = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Return the authenticated user's profile and tenant.
    Called by useAuth.js on every app load to hydrate the Zustand store.
    """
    tenant = (
        db.query(Tenant).filter(Tenant.id == current_user.tenant_id).first()
        if current_user.tenant_id else None
    )
    profile_out = UserProfileOut.model_validate(current_user)
    return {
        "user": profile_out,
        "profile": profile_out,
        "tenant": TenantOut.model_validate(tenant) if tenant else None,
    }


@router.patch("/me/profile", response_model=UserProfileOut)
def update_profile(
    body: UserProfileUpdate,
    current_user: UserProfile = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update full_name (Settings.jsx profile section)."""
    if body.full_name is not None:
        current_user.full_name = body.full_name
    db.commit()
    db.refresh(current_user)
    return UserProfileOut.model_validate(current_user)


@router.patch("/me/password", response_model=MessageResponse)
def change_password(
    body: PasswordUpdate,
    current_user: UserProfile = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Change password (Settings.jsx + AcceptInvite.jsx)."""
    current_user.password_hash = hash_password(body.new_password)
    db.commit()
    return {"message": "Password updated successfully"}
