"""
Tests for Entity Resolver.
"""

from app.agents.profiler.entity_resolver import EntityResolver


def test_explicit_company_identification():
    title = "Datadog pricing spike"
    content = "Our team at Acme Cloud Infrastructure is paying $40k/month on Datadog custom metrics."
    candidate, evidence = EntityResolver.resolve(
        title=title,
        content=content,
        author="u/lead_devops",
        source_url="https://acmecloud.io/blog/scaling",
    )
    assert candidate is not None
    assert "Acme" in candidate.company_name
    assert candidate.domain == "acmecloud.io"
    assert candidate.identity_confidence >= 0.70
    assert any(e.classification in ["VERIFIED", "INFERRED"] for e in evidence)


def test_anonymous_signal_remains_unresolved_no_fabrication():
    title = "Datadog bills are ridiculous"
    content = "I really hate how Datadog charges for custom metrics. Every month is a surprise."
    candidate, evidence = EntityResolver.resolve(
        title=title,
        content=content,
        author="u/throwaway99182",
        source_url="https://reddit.com/r/devops/comments/xyz123",
    )
    # Must remain unresolved, zero hallucination
    assert candidate is None
    assert any(e.classification == "UNKNOWN" for e in evidence)


def test_student_or_hobbyist_disqualification():
    title = "Datadog in my university project"
    content = "I am a student setting up an intern project with Datadog and hit a free tier limit."
    candidate, evidence = EntityResolver.resolve(
        title=title,
        content=content,
        author="u/student_cs",
        source_url="https://reddit.com/r/devops/comments/student_post",
    )
    assert candidate is None
    assert any("student" in e.claim.lower() for e in evidence)


def test_ambiguous_vendor_mention_not_treated_as_employer():
    title = "Netflix blog post on Datadog"
    content = "Did you see Netflix's recent blog post on how they manage telemetry with Datadog?"
    candidate, evidence = EntityResolver.resolve(
        title=title,
        content=content,
        author="u/random_dev",
        source_url="https://news.ycombinator.com/item?id=888",
    )
    # Must NOT assign Netflix as the author's employer
    assert candidate is None
