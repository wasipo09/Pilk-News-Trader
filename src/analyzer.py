"""News analysis module - LLM-powered sentiment and impact analysis.

This module provides a framework for analyzing news items.
The actual analysis is done by AI model (me) when analyzer is called.
"""

from typing import List, Dict
from pydantic import BaseModel
from datetime import datetime
from enum import Enum

from .aggregator import NewsItem


class Sentiment(str, Enum):
    """Sentiment types."""
    BULLISH = "bullish"
    BEARISH = "bearish"
    NEUTRAL = "neutral"


class Impact(str, Enum):
    """Impact levels."""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class NewsAnalysis(BaseModel):
    """Analysis of a single news item."""

    title: str
    url: str
    source: str
    sentiment: Sentiment
    impact: Impact
    assets: List[str]
    confidence: int  # 0-100
    actionable: bool
    key_takeaways: List[str]
    reasoning: str


class NewsAnalyzer:
    """Analyzes news items using AI.

    The analysis is done by the main AI model during CLI execution.
    This class provides structure and validation.
    """

    def __init__(self):
        """Initialize analyzer."""
        pass

    def analyze_batch(
        self, items: List[NewsItem]
    ) -> List[NewsAnalysis]:
        """Analyze a batch of news items.

        This method is called with news items. The actual analysis
        should be done by AI model interpreting the content.

        Returns a list of analyses (filled in by AI).
        """
        # This is a placeholder - the actual analysis happens
        # when CLI is run and the AI processes the news
        return []

    def create_analysis(
        self,
        item: NewsItem,
        sentiment: Sentiment,
        impact: Impact,
        assets: List[str],
        confidence: int,
        actionable: bool,
        key_takeaways: List[str],
        reasoning: str,
    ) -> NewsAnalysis:
        """Create a news analysis object."""
        return NewsAnalysis(
            title=item.title,
            url=item.url,
            source=item.source,
            sentiment=sentiment,
            impact=impact,
            assets=assets,
            confidence=confidence,
            actionable=actionable,
            key_takeaways=key_takeaways,
            reasoning=reasoning,
        )


# Helper function for AI to use during analysis
def extract_crypto_assets(text: str) -> List[str]:
    """Extract crypto asset mentions from text.

    Common assets: BTC, ETH, SOL, XRP, ADA, DOGE, DOT, etc.
    """
    assets = []
    text_upper = text.upper()

    # Major assets
    known_assets = [
        "BTC", "ETH", "SOL", "XRP", "ADA", "DOGE", "DOT", "MATIC", "LINK",
        "AVAX", "UNI", "ATOM", "LTC", "BCH", "ETC", "ALGO", "VET", "FIL",
        "XLM", "HBAR", "NEAR", "APE", "SAND", "MANA", "AXS", "GALA",
    ]

    for asset in known_assets:
        if asset in text_upper:
            assets.append(asset)

    # Also check for full names
    if "BITCOIN" in text_upper and "BTC" not in assets:
        assets.append("BTC")
    if "ETHEREUM" in text_upper and "ETH" not in assets:
        assets.append("ETH")

    return list(set(assets))  # Deduplicate
