"""Integration tests for /health endpoint."""

import pytest


@pytest.mark.asyncio
async def test_health_check(test_client):
    resp = await test_client.get("/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ok"
