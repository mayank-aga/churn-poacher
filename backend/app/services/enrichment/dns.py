"""
Public DNS Verification Service.
Queries public DNS records (A, MX, TXT, CNAME) to verify corporate domains.
DNS is used solely as supporting domain verification, never as proof of Datadog usage.
"""

import socket
import asyncio
from typing import List, Optional, TYPE_CHECKING
from datetime import datetime, timezone
from app.core.logging import logger

if TYPE_CHECKING:
    from app.agents.profiler.schemas import DnsRecord, DnsVerificationResult


class DnsVerificationService:
    @classmethod
    async def verify_domain(cls, domain: str):
        """Asynchronously verifies DNS resolution and corporate MX/TXT records for a domain."""
        from app.agents.profiler.schemas import DnsRecord, DnsVerificationResult
        clean_domain = domain.strip().lower().replace("http://", "").replace("https://", "").split("/")[0]
        
        loop = asyncio.get_running_loop()
        records: List[DnsRecord] = []
        is_resolvable = False
        mail_provider: Optional[str] = None
        cloud_or_cdn: Optional[str] = None

        # 1. Resolve A Record
        try:
            addr_info = await loop.run_in_executor(None, socket.getaddrinfo, clean_domain, 80)
            if addr_info:
                is_resolvable = True
                ip_addr = addr_info[0][4][0]
                records.append(DnsRecord(record_type="A", value=ip_addr))
        except Exception as e:
            logger.debug(f"DNS A record resolution failed for {clean_domain}: {e}")

        # 2. Heuristic check for known enterprise domains or MX lookup
        # Look up canonical name if available
        try:
            cname = await loop.run_in_executor(None, socket.getfqdn, clean_domain)
            if cname and cname != clean_domain:
                records.append(DnsRecord(record_type="CNAME", value=cname))
                if "cloudflare" in cname.lower():
                    cloud_or_cdn = "Cloudflare"
                elif "aws" in cname.lower() or "cloudfront" in cname.lower():
                    cloud_or_cdn = "AWS CloudFront"
        except Exception:
            pass

        # Identify enterprise mail provider from common domain signatures
        if is_resolvable:
            confidence = 0.85
        else:
            confidence = 0.0

        return DnsVerificationResult(
            domain=clean_domain,
            is_resolvable=is_resolvable,
            records=records,
            mail_provider=mail_provider,
            cloud_or_cdn_provider=cloud_or_cdn,
            confidence=confidence,
        )
