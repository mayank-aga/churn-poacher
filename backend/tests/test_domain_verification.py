"""
Tests for Domain Verifier.
"""

import pytest
from unittest.mock import patch
from app.agents.profiler.domain_verifier import DomainVerifier


@pytest.mark.asyncio
async def test_resolvable_domain_verification():
    with patch("socket.getaddrinfo") as mock_dns:
        mock_dns.return_value = [(2, 1, 0, "", ("93.184.216.34", 80))]
        result, evidence = await DomainVerifier.verify("example.com")
        
        assert result.is_resolvable is True
        assert result.confidence >= 0.80
        assert len(result.records) >= 1
        assert any(e.classification == "VERIFIED" for e in evidence)


@pytest.mark.asyncio
async def test_unresolvable_domain_verification():
    with patch("socket.getaddrinfo", side_effect=Exception("Name or service not known")):
        result, evidence = await DomainVerifier.verify("invalid-nonexistent-domain-xyz999.io")
        
        assert result.is_resolvable is False
        assert result.confidence == 0.0
        assert any(e.classification == "UNKNOWN" for e in evidence)
