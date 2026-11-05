"""
Authentication and User Management Endpoints.
"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.session import get_db
from app.models.user import User
from app.core.security import hash_password, verify_password, create_access_token
from app.api.deps import get_current_user, require_roles, AuthenticatedUserContext

router = APIRouter(prefix="/auth", tags=["Authentication & RBAC"])


class LoginRequest(BaseModel):
    email: str
    password: str


class RegisterUserRequest(BaseModel):
    email: str
    password: str
    full_name: str = ""
    role: str = "ANALYST"  # ADMINISTRATOR, ANALYST, SALES_MANAGER


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: str
    email: str
    role: str


@router.post("/login", response_model=TokenResponse)
async def login(req: LoginRequest, db: AsyncSession = Depends(get_db)):
    """Authenticates user with email and password and returns a signed JWT token."""
    res = await db.execute(select(User).where(User.email == req.email.lower()))
    user = res.scalar_one_or_none()

    if not user or not verify_password(req.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is disabled",
        )

    token = create_access_token(subject=user.id, role=user.role, email=user.email)
    return TokenResponse(
        access_token=token,
        token_type="bearer",
        user_id=user.id,
        email=user.email,
        role=user.role,
    )


@router.post("/register", response_model=TokenResponse)
async def register(req: RegisterUserRequest, db: AsyncSession = Depends(get_db)):
    """Registers a new user account."""
    existing = await db.execute(select(User).where(User.email == req.email.lower()))
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email is already registered",
        )

    role = req.role.upper()
    if role not in ["ADMINISTRATOR", "ANALYST", "SALES_MANAGER"]:
        role = "ANALYST"

    user = User(
        email=req.email.lower(),
        hashed_password=hash_password(req.password),
        full_name=req.full_name,
        role=role,
        is_active=True,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)

    token = create_access_token(subject=user.id, role=user.role, email=user.email)
    return TokenResponse(
        access_token=token,
        token_type="bearer",
        user_id=user.id,
        email=user.email,
        role=user.role,
    )


@router.get("/me")
async def get_me(current_user: AuthenticatedUserContext = Depends(get_current_user)):
    """Returns profile and role claims of the current authenticated user."""
    return {
        "id": current_user.id,
        "email": current_user.email,
        "role": current_user.role,
        "permissions": {
            "can_approve_outreach": current_user.role in ["ADMINISTRATOR", "SALES_MANAGER"],
            "can_export_dossier": current_user.role in ["ADMINISTRATOR", "SALES_MANAGER"],
            "can_manage_settings": current_user.role == "ADMINISTRATOR",
            "can_trigger_workers": current_user.role in ["ADMINISTRATOR", "ANALYST"],
        },
    }


@router.post("/seed-defaults")
async def seed_default_users(db: AsyncSession = Depends(get_db)):
    """Seeds default test accounts for Administrator, Sales Manager, and Analyst if none exist."""
    seeds = [
        ("admin@churnpoacher.local", "AdminPass123!", "Lead Administrator", "ADMINISTRATOR"),
        ("sales@churnpoacher.local", "SalesPass123!", "Enterprise Sales Director", "SALES_MANAGER"),
        ("analyst@churnpoacher.local", "AnalystPass123!", "Competitive Intelligence Analyst", "ANALYST"),
    ]
    created = []
    for email, pwd, name, role in seeds:
        res = await db.execute(select(User).where(User.email == email))
        if not res.scalar_one_or_none():
            user = User(
                email=email,
                hashed_password=hash_password(pwd),
                full_name=name,
                role=role,
                is_active=True,
            )
            db.add(user)
            created.append(email)

    await db.commit()
    return {"message": "Default seed completed", "created_users": created}
