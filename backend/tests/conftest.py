"""
Pytest configuration and global fixtures for backend test suite.
"""

import pytest
from sqlalchemy import text
from app.db.session import async_engine, init_db


@pytest.fixture(autouse=True)
async def clean_database():
    """Initializes tables and truncates/cleans all records before each test runs."""
    await init_db()
    async with async_engine.begin() as conn:
        # Disable foreign keys temporarily to truncate tables cleanly in SQLite
        if "sqlite" in str(async_engine.url):
            await conn.execute(text("PRAGMA foreign_keys = OFF;"))
            await conn.execute(text("DELETE FROM deposition_dossiers;"))
            await conn.execute(text("DELETE FROM companies;"))
            await conn.execute(text("DELETE FROM signals;"))
            await conn.execute(text("DELETE FROM agent_execution_logs;"))
            await conn.execute(text("PRAGMA foreign_keys = ON;"))
        else:
            await conn.execute(text("TRUNCATE TABLE deposition_dossiers, companies, signals, agent_execution_logs CASCADE;"))
    yield
