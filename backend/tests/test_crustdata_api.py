"""
Tests for Phase 4: Crustdata REST API Endpoints.
"""

import pytest
from httpx import AsyncClient, ASGITransport

from app.main import app
from app.db.session import init_db


@pytest.fixture(autouse=True)
async def setup_test_db():
    await init_db()


@pytest.mark.asyncio
async def test_api_credits_endpoint():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        res = await client.get("/api/v1/crustdata/credits")
        assert res.status_code == 200
        data = res.json()
        assert "remaining_credits" in data
        assert "enabled_endpoints" in data
        assert data["is_mock"] is True


@pytest.mark.asyncio
async def test_api_search_endpoint():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        payload = {"query": "NVIDIA", "entity_type": "COMPANY", "limit": 5}
        res = await client.post("/api/v1/crustdata/search", json=payload)
        assert res.status_code == 200
        data = res.json()
        assert data["query"] == "NVIDIA"
        assert len(data["candidates"]) >= 1
        assert "NVIDIA" in data["candidates"][0]["name"]


@pytest.mark.asyncio
async def test_api_enrich_and_export_endpoints():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # 1. Standard Enrichment (Level 2)
        enrich_payload = {
            "identifier": "nvidia.com",
            "entity_type": "COMPANY",
            "level": "LEVEL_2_STANDARD",
            "force_refresh": True,
        }
        res = await client.post("/api/v1/crustdata/enrich", json=enrich_payload)
        assert res.status_code == 200
        profile = res.json()
        assert profile["name"] == "NVIDIA"
        assert profile["primary_domain"] == "nvidia.com"
        entity_id = profile["entity_id"]

        # 2. Level 3 Deep Enrichment without confirmation -> returns estimate
        deep_unconfirmed = {
            "identifier": "nvidia.com",
            "entity_type": "COMPANY",
            "level": "LEVEL_3_DEEP",
            "confirmation_confirmed": False,
        }
        res_deep = await client.post("/api/v1/crustdata/enrich", json=deep_unconfirmed)
        assert res_deep.status_code == 200
        est = res_deep.json()
        assert "estimated_credits" in est
        assert est["estimated_credits"] == 15.0

        # 3. Retrieve Entity Profile by ID
        res_ent = await client.get(f"/api/v1/crustdata/entities/{entity_id}")
        assert res_ent.status_code == 200
        ent_data = res_ent.json()
        assert ent_data["primary_name"] == "NVIDIA"
        assert len(ent_data["evidence"]) >= 1

        # 4. Search History
        res_hist = await client.get("/api/v1/crustdata/searches/history")
        assert res_hist.status_code == 200
        assert isinstance(res_hist.json(), list)

        # 5. Export Markdown
        res_md = await client.post(
            "/api/v1/crustdata/export",
            json={"entity_id": entity_id, "export_format": "markdown"},
        )
        assert res_md.status_code == 200
        md_data = res_md.json()
        assert md_data["format"] == "markdown"
        assert "# Crustdata Intelligence Report: NVIDIA" in md_data["content"]
        assert "## Technographics" in md_data["content"]

        # 6. Export JSON
        res_json = await client.post(
            "/api/v1/crustdata/export",
            json={"entity_id": entity_id, "export_format": "json"},
        )
        assert res_json.status_code == 200
        j_data = res_json.json()
        assert j_data["primary_name"] == "NVIDIA"
        assert "profile" in j_data
