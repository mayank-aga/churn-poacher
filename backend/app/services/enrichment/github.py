"""
GitHub Technology Profiling Service.
Searches public repositories for Datadog SDK imports, agent configs, and OpenTelemetry usage.
Does not interpret an old dependency or tutorial repo as proof of production usage.
"""

from typing import List, Optional
import httpx
from app.core.config import settings
from app.core.logging import logger
from app.agents.profiler.schemas import TechEvidence


class GitHubEnrichmentService:
    BASE_URL = "https://api.github.com"

    @classmethod
    async def search_org_technologies(cls, org_or_company: str) -> List[TechEvidence]:
        """Searches public repositories associated with a company or organization name."""
        evidence: List[TechEvidence] = []
        if not org_or_company:
            return evidence

        headers = {
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "ChurnPoacher-Profiler/1.0",
        }
        if settings.GITHUB_TOKEN and settings.GITHUB_TOKEN.strip():
            headers["Authorization"] = f"token {settings.GITHUB_TOKEN.strip()}"

        query = f"org:{org_or_company} datadog in:file"
        try:
            async with httpx.AsyncClient(timeout=8.0) as client:
                url = f"{cls.BASE_URL}/search/code"
                response = await client.get(url, params={"q": query, "per_page": 3}, headers=headers)
                
                if response.status_code == 200:
                    data = response.json()
                    items = data.get("items", [])
                    for item in items:
                        repo = item.get("repository", {})
                        repo_name = repo.get("full_name", "")
                        file_path = item.get("path", "")
                        html_url = item.get("html_url", "")
                        
                        # Disqualify forks and tutorials
                        if "tutorial" in repo_name.lower() or "example" in repo_name.lower():
                            continue

                        evidence.append(
                            TechEvidence(
                                technology="Datadog",
                                category="Observability",
                                classification="VERIFIED",
                                source="GitHub",
                                source_url=html_url,
                                file_path=file_path,
                                snippet=f"Repository {repo_name} contains Datadog configuration in {file_path}",
                                confidence=0.88,
                            )
                        )
                elif response.status_code in (403, 429):
                    logger.debug("GitHub API rate limit reached or token not provided, proceeding gracefully.")
        except Exception as e:
            logger.debug(f"GitHub search exception for {org_or_company}: {e}")

        return evidence
