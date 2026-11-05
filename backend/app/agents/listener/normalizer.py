"""
Signal Normalizer.
Standardizes raw signals from Datadog Status, Hacker News, Reddit, and Synthetic generators
into a uniform NormalizedSignal schema.
"""

from datetime import datetime, timezone
from typing import Dict, Any, Optional
from app.agents.listener.schemas import NormalizedSignal


def _parse_iso_datetime(dt_str: Optional[str]) -> datetime:
    """Parses an ISO datetime string into UTC timezone-aware datetime."""
    if not dt_str:
        return datetime.now(timezone.utc)
    try:
        # Handles 'Z' or standard offsets
        dt = datetime.fromisoformat(dt_str.replace("Z", "+00:00"))
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(timezone.utc)
    except Exception:
        return datetime.now(timezone.utc)


def _parse_unix_timestamp(ts: Optional[float]) -> datetime:
    """Parses a unix epoch timestamp into UTC timezone-aware datetime."""
    if not ts:
        return datetime.now(timezone.utc)
    try:
        return datetime.fromtimestamp(float(ts), tz=timezone.utc)
    except Exception:
        return datetime.now(timezone.utc)


class SignalNormalizer:
    @staticmethod
    def normalize_datadog_incident(raw: Dict[str, Any]) -> NormalizedSignal:
        """Normalizes an incident from Datadog Statuspage API."""
        incident_id = raw.get("id", "unknown-incident")
        name = raw.get("name", "Datadog Service Incident")
        status = raw.get("status", "investigating")
        impact = raw.get("impact", "minor")
        created_at = _parse_iso_datetime(raw.get("created_at"))
        shortlink = raw.get("shortlink") or f"https://status.datadoghq.com/incidents/{incident_id}"
        
        # Incident updates
        updates = raw.get("incident_updates", [])
        latest_body = updates[0].get("body", "") if updates else ""
        content = f"Incident: {name}\nStatus: {status}\nImpact: {impact}\nLatest Update: {latest_body}"
        
        return NormalizedSignal(
            source="DATADOG_STATUS",
            source_id=f"dd-status-{incident_id}",
            source_url=shortlink,
            vendor="Datadog",
            title=name,
            content=content.strip(),
            author="Datadog StatusPage",
            published_at=created_at,
            detected_at=datetime.now(timezone.utc),
            signal_type="VENDOR_INCIDENT",
            complaint_category="VENDOR_INCIDENT",
            sentiment="NEUTRAL",
            urgency_score=0.90 if impact in ["critical", "major"] else 0.65,
            confidence_score=1.0,
            relevance_score=0.95,
            extracted_evidence={
                "incident_id": incident_id,
                "impact": impact,
                "status": status,
                "components_affected": [c.get("name") for c in raw.get("components", []) if isinstance(c, dict)],
            },
            is_synthetic=False,
        )

    @staticmethod
    def normalize_hackernews_item(raw: Dict[str, Any]) -> NormalizedSignal:
        """Normalizes a story or comment from Hacker News Algolia Search API."""
        object_id = str(raw.get("objectID", ""))
        title = raw.get("title") or raw.get("story_title") or "Hacker News Discussion"
        story_text = raw.get("story_text") or raw.get("comment_text") or ""
        url = raw.get("url") or f"https://news.ycombinator.com/item?id={object_id}"
        author = raw.get("author", "unknown_user")
        created_at_str = raw.get("created_at")
        published_at = _parse_iso_datetime(created_at_str)
        
        content = f"{title}\n\n{story_text}".strip()
        points = raw.get("points", 0)
        num_comments = raw.get("num_comments", 0)
        
        return NormalizedSignal(
            source="HACKER_NEWS",
            source_id=f"hn-{object_id}",
            source_url=url,
            vendor="Datadog",
            title=title,
            content=content,
            author=author,
            published_at=published_at,
            detected_at=datetime.now(timezone.utc),
            signal_type="DISCUSSION",
            complaint_category="GENERAL_DISCUSSION",
            sentiment="NEUTRAL",
            urgency_score=0.5,
            confidence_score=0.85,
            relevance_score=0.75,
            extracted_evidence={
                "points": points,
                "num_comments": num_comments,
                "hn_id": object_id,
            },
            is_synthetic=False,
        )

    @staticmethod
    def normalize_reddit_post(raw: Dict[str, Any]) -> NormalizedSignal:
        """Normalizes a post from Reddit API."""
        post_id = raw.get("id", "")
        title = raw.get("title", "")
        selftext = raw.get("selftext", "")
        url = raw.get("url") or f"https://reddit.com{raw.get('permalink', '')}"
        author = raw.get("author", "reddit_user")
        created_utc = raw.get("created_utc")
        published_at = _parse_unix_timestamp(created_utc)
        
        content = f"{title}\n\n{selftext}".strip()
        subreddit = raw.get("subreddit", "devops")
        score = raw.get("score", 0)
        num_comments = raw.get("num_comments", 0)
        
        return NormalizedSignal(
            source="REDDIT",
            source_id=f"reddit-{post_id}",
            source_url=url,
            vendor="Datadog",
            title=title,
            content=content,
            author=f"u/{author}",
            published_at=published_at,
            detected_at=datetime.now(timezone.utc),
            signal_type="COMPLAINT",
            complaint_category="GENERAL_DISCUSSION",
            sentiment="NEUTRAL",
            urgency_score=0.5,
            confidence_score=0.85,
            relevance_score=0.80,
            extracted_evidence={
                "subreddit": subreddit,
                "score": score,
                "num_comments": num_comments,
            },
            is_synthetic=False,
        )

    @staticmethod
    def normalize_synthetic(raw: Dict[str, Any]) -> NormalizedSignal:
        """Normalizes a pre-generated synthetic signal."""
        published_at = raw.get("published_at")
        if isinstance(published_at, str):
            published_at = _parse_iso_datetime(published_at)
        elif not isinstance(published_at, datetime):
            published_at = datetime.now(timezone.utc)
            
        return NormalizedSignal(
            source="SYNTHETIC",
            source_id=raw.get("source_id", f"synth-{int(datetime.now().timestamp())}"),
            source_url=raw.get("source_url", "https://demo.churnpoacher.io/signals/synthetic"),
            vendor=raw.get("vendor", "Datadog"),
            title=raw.get("title", "Datadog Dissatisfaction Signal"),
            content=raw.get("content", ""),
            author=raw.get("author", "verified_devops_lead"),
            published_at=published_at,
            detected_at=datetime.now(timezone.utc),
            signal_type=raw.get("signal_type", "COMPLAINT"),
            complaint_category=raw.get("complaint_category", "PRICING_SHOCK"),
            sentiment=raw.get("sentiment", "NEGATIVE"),
            urgency_score=float(raw.get("urgency_score", 0.85)),
            confidence_score=float(raw.get("confidence_score", 0.95)),
            relevance_score=float(raw.get("relevance_score", 0.90)),
            extracted_evidence=raw.get("extracted_evidence", {}),
            is_synthetic=True,
        )
