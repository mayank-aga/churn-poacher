"""
Deterministic Mock Provider for Crustdata Intelligence.
Used when CRUSTDATA_API_KEY is not set or when running in test/demo mode.
Always tags records with is_mock=True to prevent confusing synthetic fixtures with real data.
"""

import uuid
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional

from app.services.crustdata.schemas import (
    EntityType,
    EnrichmentLevel,
    VerificationClassification,
    EntityCandidate,
    CrustdataCreditsInfo,
    CompanyIntelligenceProfile,
    PersonIntelligenceProfile,
    TechnographicItem,
    FundingRoundItem,
    JobListingItem,
    WorkHistoryItem,
    IntelligenceEvidenceItem,
)


class CrustdataMockProvider:
    """Provides structured, high-fidelity mock data for entities requested in testing."""

    MOCK_CREDITS = CrustdataCreditsInfo(
        total_credits=1000.0,
        remaining_credits=842.5,
        used_credits=157.5,
        renewal_date="2026-12-01T00:00:00Z",
        enabled_endpoints=[
            "/screener/company/search",
            "/screener/company/enrich",
            "/screener/person/search",
            "/screener/person/enrich",
            "/screener/job/search",
            "/web/search/live",
            "/account/credits",
        ],
        is_mock=True,
    )

    # Known high-fidelity company mock profiles
    MOCK_COMPANIES: Dict[str, Dict[str, Any]] = {
        "spacex": {
            "name": "SpaceX",
            "primary_domain": "spacex.com",
            "website": "https://www.spacex.com",
            "linkedin_url": "https://www.linkedin.com/company/spacex",
            "description": "Space exploration technologies and orbital aerospace manufacturer.",
            "industry": "Aerospace & Defense",
            "headcount": "10,000+ employees",
            "annual_revenue_range": "$5B - $10B",
            "headquarters": "Hawthorne, California, USA",
            "founding_year": 2002,
            "technographics": [
                {"name": "Kubernetes", "category": "Containers", "classification": "VERIFIED"},
                {"name": "Prometheus", "category": "Observability", "classification": "VERIFIED"},
                {"name": "Grafana", "category": "Observability", "classification": "VERIFIED"},
                {"name": "Datadog", "category": "Observability", "classification": "INFERRED", "source_url": "https://spacex.com/careers/observability-engineer"},
                {"name": "Python", "category": "Languages", "classification": "VERIFIED"},
                {"name": "C++", "category": "Languages", "classification": "VERIFIED"},
            ],
            "funding_rounds": [
                {"round_name": "Private Equity", "amount_usd": 750000000.0, "round_date": "2023-01-02", "investors": ["Andreessen Horowitz", "Founders Fund"]},
            ],
            "total_funding_usd": 9800000000.0,
            "leadership": [
                {"name": "Elon Musk", "title": "CEO & Chief Engineer", "linkedin": "https://linkedin.com/in/elonmusk"},
                {"name": "Gwynne Shotwell", "title": "President & COO", "linkedin": "https://linkedin.com/in/gwynneshotwell"},
            ],
            "active_jobs": [
                {"title": "Senior Telemetry & Observability Engineer", "department": "Avionics Software", "location": "Hawthorne, CA", "required_technologies": ["OpenTelemetry", "Grafana", "Datadog", "C++"]},
            ],
        },
        "openai": {
            "name": "OpenAI",
            "primary_domain": "openai.com",
            "website": "https://openai.com",
            "linkedin_url": "https://www.linkedin.com/company/openai",
            "description": "AI research and deployment company behind ChatGPT and foundation models.",
            "industry": "Artificial Intelligence / Software",
            "headcount": "1,000 - 5,000 employees",
            "annual_revenue_range": "$1B - $5B",
            "headquarters": "San Francisco, California, USA",
            "founding_year": 2015,
            "technographics": [
                {"name": "Kubernetes", "category": "Containers", "classification": "VERIFIED"},
                {"name": "Microsoft Azure", "category": "Cloud Provider", "classification": "VERIFIED"},
                {"name": "Datadog", "category": "Observability", "classification": "VERIFIED", "source_url": "https://openai.com/careers/infrastructure-eng"},
                {"name": "PyTorch", "category": "AI Framework", "classification": "VERIFIED"},
                {"name": "Ray", "category": "Distributed Compute", "classification": "VERIFIED"},
            ],
            "funding_rounds": [
                {"round_name": "Corporate Venture", "amount_usd": 10000000000.0, "round_date": "2023-01-23", "investors": ["Microsoft"]},
            ],
            "total_funding_usd": 14000000000.0,
            "leadership": [
                {"name": "Sam Altman", "title": "CEO", "linkedin": "https://linkedin.com/in/samaltman"},
                {"name": "Greg Brockman", "title": "President", "linkedin": "https://linkedin.com/in/gregbrockman"},
            ],
            "active_jobs": [
                {"title": "Systems Reliability Engineer (SRE)", "department": "Platform", "location": "San Francisco, CA", "required_technologies": ["Datadog", "Kubernetes", "Azure", "Terraform"]},
            ],
        },
        "nvidia": {
            "name": "NVIDIA",
            "primary_domain": "nvidia.com",
            "website": "https://www.nvidia.com",
            "linkedin_url": "https://www.linkedin.com/company/nvidia",
            "description": "Pioneer of GPU-accelerated computing, AI platforms, and enterprise data centers.",
            "industry": "Semiconductors & AI Hardware",
            "headcount": "25,000+ employees",
            "annual_revenue_range": "$50B+",
            "headquarters": "Santa Clara, California, USA",
            "founding_year": 1993,
            "technographics": [
                {"name": "CUDA", "category": "Parallel Computing", "classification": "VERIFIED"},
                {"name": "Kubernetes", "category": "Containers", "classification": "VERIFIED"},
                {"name": "Prometheus", "category": "Observability", "classification": "VERIFIED"},
                {"name": "Datadog", "category": "Observability", "classification": "INFERRED"},
                {"name": "AWS", "category": "Cloud Provider", "classification": "VERIFIED"},
            ],
            "funding_rounds": [],
            "total_funding_usd": 0.0,
            "leadership": [
                {"name": "Jensen Huang", "title": "Founder & CEO", "linkedin": "https://linkedin.com/in/jensenhuang"},
            ],
            "active_jobs": [
                {"title": "Principal Infrastructure Architect", "department": "AI Enterprise", "location": "Santa Clara, CA", "required_technologies": ["Kubernetes", "Datadog", "Prometheus", "OpenTelemetry"]},
            ],
        },
        "datadog": {
            "name": "Datadog",
            "primary_domain": "datadoghq.com",
            "website": "https://www.datadoghq.com",
            "linkedin_url": "https://www.linkedin.com/company/datadog",
            "description": "Cloud monitoring and observability service for enterprise cloud applications.",
            "industry": "Developer Tools & Observability",
            "headcount": "5,000 - 10,000 employees",
            "annual_revenue_range": "$2B - $3B",
            "headquarters": "New York, NY, USA",
            "founding_year": 2010,
            "technographics": [
                {"name": "AWS", "category": "Cloud Provider", "classification": "VERIFIED"},
                {"name": "Kubernetes", "category": "Containers", "classification": "VERIFIED"},
                {"name": "Go", "category": "Languages", "classification": "VERIFIED"},
                {"name": "Kafka", "category": "Streaming", "classification": "VERIFIED"},
            ],
            "funding_rounds": [],
            "total_funding_usd": 147000000.0,
            "leadership": [
                {"name": "Olivier Pomel", "title": "CEO", "linkedin": "https://linkedin.com/in/olivierpomel"},
                {"name": "Alexis Lê-Quôc", "title": "CTO", "linkedin": "https://linkedin.com/in/alexislequoc"},
            ],
            "active_jobs": [],
        },
    }

    # Known high-fidelity person mock profiles
    MOCK_PEOPLE: Dict[str, Dict[str, Any]] = {
        "elon musk": {
            "full_name": "Elon Musk",
            "current_title": "CEO & Chief Engineer",
            "current_company": "SpaceX",
            "headline": "CEO of SpaceX, Tesla, xAI, CTO of X",
            "location": "Austin, Texas, USA",
            "linkedin_url": "https://www.linkedin.com/in/elonmusk",
            "twitter_url": "https://twitter.com/elonmusk",
            "verified_work_email": "elon@spacex.com",
            "summary_bio": "Founder and technology leader focusing on sustainable transport, reusable spaceflight, and AI.",
            "is_decision_maker": True,
            "decision_maker_score": 0.99,
            "work_history": [
                {"company_name": "SpaceX", "title": "CEO & Chief Engineer", "start_date": "2002-05", "is_current": True},
                {"company_name": "Tesla", "title": "CEO & Product Architect", "start_date": "2004-02", "is_current": True},
                {"company_name": "xAI", "title": "Founder", "start_date": "2023-03", "is_current": True},
            ],
            "skills": ["Systems Architecture", "Aerospace Engineering", "Distributed Systems", "Venture Capital"],
        },
        "sam altman": {
            "full_name": "Sam Altman",
            "current_title": "CEO",
            "current_company": "OpenAI",
            "headline": "CEO at OpenAI, former President of Y Combinator",
            "location": "San Francisco, California, USA",
            "linkedin_url": "https://www.linkedin.com/in/samaltman",
            "twitter_url": "https://twitter.com/sama",
            "verified_work_email": "sam@openai.com",
            "summary_bio": "Entrepreneur and investor, leading research in safe artificial general intelligence.",
            "is_decision_maker": True,
            "decision_maker_score": 0.98,
            "work_history": [
                {"company_name": "OpenAI", "title": "CEO", "start_date": "2019-03", "is_current": True},
                {"company_name": "Y Combinator", "title": "President", "start_date": "2014-02", "end_date": "2019-03", "is_current": False},
            ],
            "skills": ["Artificial Intelligence", "Corporate Strategy", "Venture Capital", "Product Management"],
        },
    }

    @classmethod
    def get_credits(cls) -> CrustdataCreditsInfo:
        return cls.MOCK_CREDITS

    @classmethod
    def search_candidates(cls, query: str, entity_type: Optional[EntityType] = None, limit: int = 5) -> List[EntityCandidate]:
        q_clean = query.lower().strip()
        candidates: List[EntityCandidate] = []

        # Check companies
        if entity_type in (EntityType.COMPANY, None):
            for key, c in cls.MOCK_COMPANIES.items():
                if key in q_clean or q_clean in c["name"].lower() or c["primary_domain"] in q_clean:
                    candidates.append(
                        EntityCandidate(
                            candidate_id=f"comp_{key}",
                            entity_type=EntityType.COMPANY,
                            name=c["name"],
                            primary_domain=c["primary_domain"],
                            headline=c["description"][:80],
                            location=c["headquarters"],
                            confidence_score=0.95,
                            is_mock=True,
                        )
                    )

        # Check people
        if entity_type in (EntityType.PERSON, None):
            for key, p in cls.MOCK_PEOPLE.items():
                if key in q_clean or q_clean in p["full_name"].lower():
                    candidates.append(
                        EntityCandidate(
                            candidate_id=f"person_{key.replace(' ', '_')}",
                            entity_type=EntityType.PERSON,
                            name=p["full_name"],
                            current_title=p["current_title"],
                            company_name=p["current_company"],
                            headline=p["headline"],
                            profile_url=p["linkedin_url"],
                            location=p["location"],
                            confidence_score=0.95,
                            is_mock=True,
                        )
                    )

        # Generic fallback candidate generator if not in pre-defined set
        if not candidates:
            is_likely_person = " " in query.strip() and not any(ext in q_clean for ext in [".com", ".io", ".org", ".ai", "corp", "inc", "ltd"])
            cand_type = EntityType.PERSON if is_likely_person else EntityType.COMPANY
            
            clean_name = query.title().strip()
            clean_dom = f"{q_clean.replace(' ', '')}.io" if cand_type == EntityType.COMPANY else None
            
            candidates.append(
                EntityCandidate(
                    candidate_id=f"gen_{uuid.uuid4().hex[:8]}",
                    entity_type=cand_type,
                    name=clean_name,
                    primary_domain=clean_dom,
                    headline=f"Synthetic profile for {clean_name}",
                    location="Global / Remote",
                    confidence_score=0.75,
                    is_mock=True,
                )
            )

        return candidates[:limit]

    @classmethod
    def enrich_company(
        cls,
        identifier: str,
        level: EnrichmentLevel = EnrichmentLevel.LEVEL_2_STANDARD,
    ) -> CompanyIntelligenceProfile:
        q_clean = identifier.lower().strip().replace("https://", "").replace("http://", "").replace("www.", "").split("/")[0]
        
        # Match from known
        matched_key = None
        for key, c in cls.MOCK_COMPANIES.items():
            if key in q_clean or c["primary_domain"] in q_clean:
                matched_key = key
                break

        if matched_key:
            data = cls.MOCK_COMPANIES[matched_key]
        else:
            # Generic synthetic enterprise profile
            company_name = q_clean.split(".")[0].capitalize()
            data = {
                "name": company_name,
                "primary_domain": f"{q_clean.split('.')[0]}.io",
                "website": f"https://{q_clean.split('.')[0]}.io",
                "linkedin_url": f"https://www.linkedin.com/company/{q_clean.split('.')[0]}",
                "description": f"{company_name} enterprise cloud infrastructure operations.",
                "industry": "B2B Technology / SaaS",
                "headcount": "250 - 1,000 employees",
                "annual_revenue_range": "$20M - $50M",
                "headquarters": "Austin, Texas, USA",
                "founding_year": 2018,
                "technographics": [],
                "funding_rounds": [
                    {"round_name": "Series B", "amount_usd": 35000000.0, "round_date": "2023-06-15", "investors": ["Benchmark", "Sequoia Capital"]},
                ],
                "total_funding_usd": 48000000.0,
                "leadership": [
                    {"name": f"Alex Morgan", "title": "VP of Infrastructure & DevOps", "linkedin": f"https://linkedin.com/in/alex-morgan-{q_clean.split('.')[0]}"},
                ],
                "active_jobs": [
                    {"title": "Senior Cloud SRE", "department": "Platform Operations", "location": "Remote, US", "required_technologies": ["Datadog", "Kubernetes", "AWS"]},
                ],
            }

        techs = [TechnographicItem(**t) for t in data.get("technographics", [])]
        fundings = [FundingRoundItem(**f) for f in data.get("funding_rounds", [])]
        jobs = [JobListingItem(**j) for j in data.get("active_jobs", [])]

        evidence_list = [
            IntelligenceEvidenceItem(
                data_category="FIRMOGRAPHICS",
                claim=f"Operating domain verified as {data['primary_domain']}",
                source_url=data.get("website"),
                confidence=0.95,
                verification_classification=VerificationClassification.VERIFIED,
                metadata={"headcount": data.get("headcount"), "industry": data.get("industry")},
            )
        ]
        for t in techs:
            evidence_list.append(
                IntelligenceEvidenceItem(
                    data_category="TECHNOGRAPHICS",
                    claim=f"Installed software: {t.name} ({t.category})",
                    source_url=t.source_url or data.get("website"),
                    confidence=0.90 if t.classification == VerificationClassification.VERIFIED else 0.70,
                    verification_classification=t.classification,
                )
            )

        credits = 1.0 if level == EnrichmentLevel.LEVEL_2_STANDARD else 15.0

        return CompanyIntelligenceProfile(
            entity_id=f"comp_{uuid.uuid4().hex[:8]}",
            name=data["name"],
            primary_domain=data["primary_domain"],
            website=data.get("website"),
            linkedin_url=data.get("linkedin_url"),
            description=data.get("description"),
            industry=data.get("industry"),
            headcount=data.get("headcount"),
            annual_revenue_range=data.get("annual_revenue_range"),
            headquarters=data.get("headquarters"),
            founding_year=data.get("founding_year"),
            technographics=techs,
            funding_rounds=fundings,
            total_funding_usd=data.get("total_funding_usd"),
            leadership=data.get("leadership", []),
            active_jobs=jobs,
            evidence=evidence_list,
            enrichment_level=level,
            credits_consumed=credits,
            data_freshness="REALTIME_CRAWL" if level == EnrichmentLevel.LEVEL_3_DEEP else "CACHED",
            is_mock=True,
        )

    @classmethod
    def enrich_person(
        cls,
        identifier: str,
        level: EnrichmentLevel = EnrichmentLevel.LEVEL_2_STANDARD,
    ) -> PersonIntelligenceProfile:
        q_clean = identifier.lower().strip()
        matched_key = None
        for key, p in cls.MOCK_PEOPLE.items():
            if key in q_clean or p["full_name"].lower() in q_clean:
                matched_key = key
                break

        if matched_key:
            data = cls.MOCK_PEOPLE[matched_key]
        else:
            name = identifier.title().strip()
            data = {
                "full_name": name,
                "current_title": "VP of Engineering & Infrastructure",
                "current_company": "Apex Dynamics",
                "headline": f"Engineering Leader & Cloud Architect at Apex Dynamics",
                "location": "San Francisco Bay Area, CA",
                "linkedin_url": f"https://www.linkedin.com/in/{name.lower().replace(' ', '')}",
                "verified_work_email": f"{name.lower().split()[0]}@apexdynamics.io" if " " in name else f"{name.lower()}@apexdynamics.io",
                "summary_bio": f"Engineering leader specializing in multi-cloud infrastructure and DevOps.",
                "is_decision_maker": True,
                "decision_maker_score": 0.88,
                "work_history": [
                    {"company_name": "Apex Dynamics", "title": "VP of Engineering", "start_date": "2021-04", "is_current": True},
                    {"company_name": "CloudScale Systems", "title": "Director of SRE", "start_date": "2018-01", "end_date": "2021-03", "is_current": False},
                ],
                "skills": ["Kubernetes", "Datadog", "Observability", "Cloud Cost Optimization", "Site Reliability Engineering"],
            }

        history = [WorkHistoryItem(**h) for h in data.get("work_history", [])]
        evidence = [
            IntelligenceEvidenceItem(
                data_category="PROFESSIONAL_IDENTITY",
                claim=f"{data['full_name']} verified as {data.get('current_title')} at {data.get('current_company')}",
                source_url=data.get("linkedin_url"),
                confidence=0.92,
                verification_classification=VerificationClassification.VERIFIED,
            )
        ]

        credits = 1.5 if level == EnrichmentLevel.LEVEL_2_STANDARD else 12.0

        return PersonIntelligenceProfile(
            entity_id=f"person_{uuid.uuid4().hex[:8]}",
            full_name=data["full_name"],
            current_title=data.get("current_title"),
            current_company=data.get("current_company"),
            headline=data.get("headline"),
            location=data.get("location"),
            linkedin_url=data.get("linkedin_url"),
            twitter_url=data.get("twitter_url"),
            verified_work_email=data.get("verified_work_email"),
            summary_bio=data.get("summary_bio"),
            is_decision_maker=data.get("is_decision_maker", False),
            decision_maker_score=data.get("decision_maker_score", 0.5),
            work_history=history,
            skills=data.get("skills", []),
            evidence=evidence,
            enrichment_level=level,
            credits_consumed=credits,
            data_freshness="REALTIME_CRAWL" if level == EnrichmentLevel.LEVEL_3_DEEP else "CACHED",
            is_mock=True,
        )
