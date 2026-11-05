"""
Signal Classifier.
Performs rule-based and contextual sentiment, urgency, and category classification on signals.
"""

import re
from typing import Tuple, Dict, Any
from app.agents.listener.schemas import NormalizedSignal


class SignalClassifier:
    """Classifies competitor distress signals into structured categories with sentiment and urgency."""

    PRICING_KEYWORDS = [
        r"\bpricing\b", r"\bbill\b", r"\bbilling\b", r"\bexpensive\b", r"\bcost\b",
        r"\bcosts\b", r"\boverage\b", r"\bcustom metrics?\b", r"\bsurprise bill\b",
        r"\bprice hike\b", r"\bprice increase\b", r"\binvoice\b", r"\$\d+", r"\bcontract renewal\b",
        r"\bjumped\b", r"\bspik(e|ed|ing)\b", r"\bdoubled\b"
    ]
    
    OUTAGE_KEYWORDS = [
        r"\boutage\b", r"\bdown\b", r"\bunavailable\b", r"\b504\b", r"\b502\b",
        r"\bincident\b", r"\bdegraded\b", r"\bstatus page\b", r"\bblackout\b",
        r"\bcan't access\b", r"\bdown detector\b", r"\btimeouts?\b"
    ]
    
    MIGRATION_KEYWORDS = [
        r"\bmigrat(e|ing|ion)\b", r"\bswitch(ing)? (from|away from)\b", r"\balternatives? to datadog\b",
        r"\balternatives?\b", r"\bmoving to signoz\b", r"\bmoving to grafana\b", r"\bopentelemetry\b",
        r"\botel\b", r"\breplac(e|ing) datadog\b", r"\bleaving datadog\b", r"\bditching datadog\b"
    ]
    
    RELIABILITY_KEYWORDS = [
        r"\blatency\b", r"\bdropped (spans|logs|metrics)\b", r"\bdelayed alerts?\b",
        r"\bflaky\b", r"\bunreliable\b", r"\blag\b", r"\bmissing data\b"
    ]
    
    DEPRECATION_KEYWORDS = [
        r"\bdeprecat(ed|ion)\b", r"\bsunset(ting)?\b", r"\bbreaking change\b",
        r"\bremoved support\b", r"\bend of life\b", r"\beol\b"
    ]

    POSITIVE_KEYWORDS = [
        r"\blove datadog\b", r"\bgreat tool\b", r"\bawesome\b", r"\bhelpful\b",
        r"\bworked well\b", r"\bseamless\b", r"\bamazing\b", r"\bfavorite\b"
    ]

    @classmethod
    def classify(cls, signal: NormalizedSignal) -> NormalizedSignal:
        """Applies classification heuristics and updates category, sentiment, and urgency."""
        if signal.signal_type == "VENDOR_INCIDENT":
            signal.complaint_category = "VENDOR_INCIDENT"
            signal.sentiment = "NEUTRAL"
            signal.urgency_score = max(signal.urgency_score, 0.85)
            return signal

        text = f"{signal.title} {signal.content}".lower()

        # 1. Determine Sentiment
        sentiment, sentiment_intensity = cls._detect_sentiment(text)
        signal.sentiment = sentiment

        # 2. Determine Category
        if sentiment == "POSITIVE":
            category = "GENERAL_DISCUSSION"
            confidence = 0.90
        else:
            category, confidence = cls._detect_category(text)
            
        signal.complaint_category = category
        signal.confidence_score = confidence

        # 3. Calculate Urgency & Relevance Scores
        if sentiment == "POSITIVE":
            urgency = 0.20
            relevance = 0.20
        else:
            urgency, relevance = cls._calculate_scores(text, category, sentiment_intensity)
            
        signal.urgency_score = urgency
        signal.relevance_score = relevance

        # 4. Extract Key Evidence Indicators
        cls._extract_evidence(signal, text)

        return signal

    @classmethod
    def _detect_sentiment(cls, text: str) -> Tuple[str, float]:
        """Calculates sentiment polarity and intensity without falsely flagging positive mentions."""
        pos_hits = sum(1 for p in cls.POSITIVE_KEYWORDS if re.search(p, text))
        
        strong_neg = ["insane", "ridiculous", "robbery", "scam", "nightmare", "furious", "unacceptable", "dumpster fire"]
        strong_neg_hits = sum(1 for w in strong_neg if w in text)
        
        mild_neg = [
            "hate", "sucks", "broken", "annoying", "pain", "expensive", "struggling",
            "down", "issue", "bug", "overage", "overages", "jumped", "spike", "doubled",
            "unexpected"
        ]
        mild_neg_hits = sum(1 for w in mild_neg if w in text)

        # If positive mentions dominate, classify as positive
        if pos_hits > 0 and strong_neg_hits == 0 and pos_hits >= mild_neg_hits:
            return "POSITIVE", 0.10
        
        if strong_neg_hits >= 1 or mild_neg_hits >= 3:
            return "EXTREMELY_NEGATIVE", 0.95
        elif mild_neg_hits >= 1:
            return "NEGATIVE", 0.70
        else:
            return "NEUTRAL", 0.30

    @classmethod
    def _detect_category(cls, text: str) -> Tuple[str, float]:
        """Detects the primary distress category using regex frequency analysis."""
        scores = {
            "PRICING_SHOCK": sum(1 for p in cls.PRICING_KEYWORDS if re.search(p, text)),
            "MIGRATION_INTENT": sum(1 for p in cls.MIGRATION_KEYWORDS if re.search(p, text)) * 1.5,
            "OUTAGE": sum(1 for p in cls.OUTAGE_KEYWORDS if re.search(p, text)),
            "RELIABILITY": sum(1 for p in cls.RELIABILITY_KEYWORDS if re.search(p, text)),
            "DEPRECATION": sum(1 for p in cls.DEPRECATION_KEYWORDS if re.search(p, text)),
        }

        best_category = max(scores, key=scores.get)
        best_score = scores[best_category]

        if best_score == 0:
            return "GENERAL_DISCUSSION", 0.50

        # Confidence scaled by keyword density
        confidence = min(0.60 + (best_score * 0.10), 0.98)
        return best_category, round(confidence, 2)

    @classmethod
    def _calculate_scores(cls, text: str, category: str, sentiment_intensity: float) -> Tuple[float, float]:
        """Computes urgency and competitive takeout relevance."""
        floor_urgency = {
            "OUTAGE": 0.85,
            "PRICING_SHOCK": 0.78,
            "MIGRATION_INTENT": 0.80,
            "RELIABILITY": 0.65,
            "DEPRECATION": 0.60,
            "GENERAL_DISCUSSION": 0.35,
            "VENDOR_INCIDENT": 0.85,
        }.get(category, 0.40)

        # Urgency adjustment based on sentiment intensity
        urgency = min(floor_urgency + (0.15 * sentiment_intensity), 1.0)

        # Relevance to competitive takeout
        base_relevance = {
            "MIGRATION_INTENT": 0.95,
            "PRICING_SHOCK": 0.90,
            "OUTAGE": 0.85,
            "RELIABILITY": 0.75,
            "DEPRECATION": 0.70,
            "GENERAL_DISCUSSION": 0.40,
            "VENDOR_INCIDENT": 0.60,
        }.get(category, 0.50)

        return round(urgency, 2), round(base_relevance, 2)

    @classmethod
    def _extract_evidence(cls, signal: NormalizedSignal, text: str) -> None:
        """Extracts specific dollar numbers, percentage hikes, or service mentions."""
        evidence = signal.extracted_evidence or {}
        
        dollar_matches = re.findall(r"\$\d+(?:,\d{3})*(?:\.\d+)?(?:k|m)?\b", text)
        if dollar_matches:
            evidence["financial_figures"] = dollar_matches

        pct_matches = re.findall(r"\b\d+%", text)
        if pct_matches:
            evidence["percentage_increases"] = pct_matches

        products_found = []
        for prod in ["apm", "logs", "custom metrics", "synthetics", "rum", "cloud cost management", "database monitoring"]:
            if prod in text:
                products_found.append(prod)
        if products_found:
            evidence["products_mentioned"] = products_found

        signal.extracted_evidence = evidence
