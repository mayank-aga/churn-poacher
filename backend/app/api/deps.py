"""
Authentication and Role-Based Access Control (RBAC) Dependencies.
"""

from typing import Optional, List, Callable
from fastapi import Depends, HTTPException, status, Header
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.session import get_db
from app.core.config import settings
from app.core.security import decode_access_token
from app.models.user import User


class AuthenticatedUserContext:
    def __init__(self, id: str, email: str, role: str):
        self.id = id
        self.email = email
        self.role = role


async def get_current_user(
    authorization: Optional[str] = Header(None),
    db: AsyncSession = Depends(get_db),
) -> AuthenticatedUserContext:
    """
    Extracts and validates JWT Bearer token from Authorization header.
    In development mode (ENABLE_AUTH=False), allows anonymous access with default ADMINISTRATOR role.
    """
    if authorization and authorization.startswith("Bearer "):
        token = authorization.split(" ")[1].strip()
        try:
            payload = decode_access_token(token)
            user_id = payload.get("sub")
            role = payload.get("role", "ANALYST")
            email = payload.get("email", "")

            # Verify in DB if user is active
            res = await db.execute(select(User).where(User.id == user_id))
            user = res.scalar_one_or_none()
            if user:
                if not user.is_active:
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail="User account is deactivated",
                    )
                return AuthenticatedUserContext(id=user.id, email=user.email, role=user.role)

            return AuthenticatedUserContext(id=user_id, email=email, role=role)
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=str(e),
                headers={"WWW-Authenticate": "Bearer"},
            )

    if settings.ENABLE_AUTH:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication credentials were not provided",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Development fallback user
    return AuthenticatedUserContext(
        id="dev-admin-id",
        email="admin@churnpoacher.local",
        role="ADMINISTRATOR",
    )


def require_roles(allowed_roles: List[str]) -> Callable:
    """Dependency factory checking that the authenticated user possesses one of the required RBAC roles."""
    async def role_checker(
        current_user: AuthenticatedUserContext = Depends(get_current_user),
    ) -> AuthenticatedUserContext:
        normalized_allowed = [r.upper() for r in allowed_roles]
        if current_user.role.upper() not in normalized_allowed:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=(
                    f"Permission denied: role '{current_user.role}' is not authorized. "
                    f"Required roles: {', '.join(allowed_roles)}"
                ),
            )
        return current_user

    return role_checker
