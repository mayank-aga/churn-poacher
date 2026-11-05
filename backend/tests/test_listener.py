"""
Integration Tests for Listener Agent and Listener API endpoints.
"""

import pytest
from unittest.mock import patch, AsyncMock
from httpx import AsyncClient, ASGITransport

from app.main import app
from app.db.session import init_db, AsyncSessionLocal
from app.agents.listener.agent import ListenerAgent
from app.services.sources.synthetic_generator import SyntheticSignalGenerator


@pytest.fixture(autouse=True)
async def setup_test_db():
    await init_db()


@pytest.mark.asyncio
async def test_listener_agent_run_cycle_with_synthetic():
    async with AsyncSessionLocal() as session:
        agent = ListenerAgent()
        
        # Mock network sources to isolate synthetic testing
        agent.datadog_status.fetch_signals = AsyncMock(return_value=[])
        agent.hackernews.fetch_signals = AsyncMock(return_value=[])
        
        # 1. Run first ingestion cycle
        summary1 = await agent.run_ingestion_cycle(db=session, include_synthetic=True)
        assert summary1.total_fetched >= 4
        assert summary1.new_signals_saved >= 4
        assert summary1.duplicates_skipped == 0
        assert summary1.execution_time_ms > 0

        # 2. Run second ingestion cycle with the same signals (Verify Deduplication)
        summary2 = await agent.run_ingestion_cycle(db=session, include_synthetic=True)
        assert summary2.new_signals_saved == 0
        assert summary2.duplicates_skipped >= 4


@pytest.mark.asyncio
async def test_listener_api_endpoints():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Mock external network adapters to return empty lists for fast, reliable testing
        with patch("app.services.sources.datadog_status.DatadogStatusAdapter.fetch_signals", new_callable=AsyncMock) as mock_dd, \
             patch("app.services.sources.hackernews.HackerNewsAdapter.fetch_signals", new_callable=AsyncMock) as mock_hn:
            mock_dd.return_value = []
            mock_hn.return_value = []

            # 1. POST /api/v1/listener/run
            run_res = await client.post("/api/v1/listener/run", json={"include_synthetic": True, "max_items_per_source": 5})
            assert run_res.status_code == 200
            data = run_res.json()
            assert "total_fetched" in data
            assert "new_signals_saved" in data
            assert "duplicates_skipped" in data

            # 2. GET /api/v1/listener/status
            status_res = await client.get("/api/v1/listener/status")
            assert status_res.status_code == 200
            status_data = status_res.json()
            assert "adapters" in status_data
            adapter_names = [a["name"] for a in status_data["adapters"]]
            assert "DATADOG_STATUS" in adapter_names
            assert "HACKER_NEWS" in adapter_names
            assert "REDDIT" in adapter_names
            assert "SYNTHETIC_GENERATOR" in adapter_names

            # 3. GET /api/v1/listener/metrics
            metrics_res = await client.get("/api/v1/listener/metrics")
            assert metrics_res.status_code == 200
            metrics_data = metrics_res.json()
            assert metrics_data["total_signals_collected"] >= 4
            assert metrics_data["synthetic_signals_count"] >= 4
            assert "signals_by_source" in metrics_data
            assert "signals_by_category" in metrics_data
