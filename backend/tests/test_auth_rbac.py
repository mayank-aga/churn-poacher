"""
Authentication and Role-Based Access Control (RBAC) Tests.
Verifies secure password hashing, JWT creation/decoding, and strict permission enforcement.
"""

import pytest
import uuid
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.main import app
from app.db.session import AsyncSessionLocal
from app.models.user import User
from app.models.signal import Signal
from app.models.company import Company
from app.models.dossier import DepositionDossier
from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    decode_access_token,
)


def test_password_hashing_and_verification():
    password = "SuperSecurePassword123!"
    hashed = hash_password(password)
    assert hashed != password
    assert "$" in hashed
    assert verify_password(password, hashed) is True
    assert verify_password("WrongPassword!", hashed) is False


def test_jwt_token_lifecycle():
    token = create_access_token(
        subject="user-uuid-1234",
        role="SALES_MANAGER",
        email="sales@example.com",
    )
    payload = decode_access_token(token)
    assert payload["sub"] == "user-uuid-1234"
    assert payload["role"] == "SALES_MANAGER"
    assert payload["email"] == "sales@example.com"


@pytest.mark.asyncio
async def test_auth_login_and_me_endpoints():
    async with AsyncSessionLocal() as db:
        test_email = f"analyst_{uuid.uuid4().hex[:6]}@example.com"
        user = User(
            email=test_email,
            hashed_password=hash_password("Analyst123!"),
            full_name="Lead Analyst",
            role="ANALYST",
            is_active=True,
        )
        db.add(user)
        await db.commit()

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Invalid password -> 401
        res_fail = await client.post(
            "/api/v1/auth/login",
            json={"email": test_email, "password": "WrongPassword!"},
        )
        assert res_fail.status_code == 401

        # Valid login -> 200 with token
        res_ok = await client.post(
            "/api/v1/auth/login",
            json={"email": test_email, "password": "Analyst123!"},
        )
        assert res_ok.status_code == 200
        data = res_ok.json()
        assert "access_token" in data
        assert data["role"] == "ANALYST"
        token = data["access_token"]

        # Call /me with bearer token
        me_res = await client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert me_res.status_code == 200
        me_data = me_res.json()
        assert me_data["email"] == test_email
        assert me_data["role"] == "ANALYST"
        assert me_data["permissions"]["can_approve_outreach"] is False
        assert me_data["permissions"]["can_export_dossier"] is False


@pytest.mark.asyncio
async def test_rbac_approval_and_export_role_gating():
    """
    Verifies that ANALYST role is rejected (403 Forbidden) when attempting to approve or export,
    while SALES_MANAGER or ADMINISTRATOR roles succeed.
    """
    async with AsyncSessionLocal() as db:
        sig = Signal(
            signal_id=f"sig-rbac-{uuid.uuid4().hex[:8]}",
            source="SYNTHETIC",
            original_url="https://synthetic.example.com",
            complaint_category="PRICING_SHOCK",
            raw_content="Datadog pricing spike test for RBAC",
            is_synthetic=True,
        )
        db.add(sig)
        await db.commit()

        comp = Company(
            name="RBAC Target Inc",
            signal_id=sig.id,
            icp_score=0.85,
            qualification_status="ACCEPTED",
            is_synthetic=True,
        )
        db.add(comp)
        await db.commit()

        dos = DepositionDossier(
            company_id=comp.id,
            signal_id=sig.id,
            status="DRAFT_PENDING_APPROVAL",
            outreach_drafts={"company_name": "RBAC Target Inc", "executive_emails": []},
            is_synthetic=True,
        )
        db.add(dos)
        await db.commit()
        await db.refresh(dos)
        dossier_id = dos.id

    analyst_token = create_access_token(subject="u1", role="ANALYST", email="analyst@test.com")
    sales_token = create_access_token(subject="u2", role="SALES_MANAGER", email="sales@test.com")

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # 1. Analyst attempts to approve -> 403 Forbidden
        analyst_approve = await client.patch(
            f"/api/v1/copywriter/{dossier_id}/approve",
            headers={"Authorization": f"Bearer {analyst_token}"},
        )
        assert analyst_approve.status_code == 403
        assert "Permission denied" in analyst_approve.json()["detail"]

        # 2. Sales Manager approves -> 200 OK
        sales_approve = await client.patch(
            f"/api/v1/copywriter/{dossier_id}/approve",
            headers={"Authorization": f"Bearer {sales_token}"},
        )
        assert sales_approve.status_code == 200
        assert sales_approve.json()["status"] == "APPROVED"

        # 3. Analyst attempts to export approved dossier -> 403 Forbidden
        analyst_export = await client.post(
            f"/api/v1/copywriter/{dossier_id}/export",
            headers={"Authorization": f"Bearer {analyst_token}"},
        )
        assert analyst_export.status_code == 403

        # 4. Sales Manager exports approved dossier -> 200 OK
        sales_export = await client.post(
            f"/api/v1/copywriter/{dossier_id}/export",
            headers={"Authorization": f"Bearer {sales_token}"},
        )
        assert sales_export.status_code == 200
        assert sales_export.json()["status"] == "EXPORTED"
