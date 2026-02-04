"""Signal generator module.

Aggregates analyzed news and generates tradeable signals.
"""

from typing import List, Dict, Literal
from collections import defaultdict
from pydantic import BaseModel
from datetime import datetime, timedelta

from .analyzer import NewsAnalysis, Sentiment


class Direction(str, Literal["LONG", "SHORT", "NEUTRAL"]):
    """Trade direction."""


class Signal(BaseModel):
    """Tradeable signal."""

    asset: str
    direction: Direction
    confidence: int  # 0-100
    key_drivers: List[str]
    risk_notes: List[str]
    news_count: int
    last_updated: datetime


class SignalGenerator:
    """Generates signals from analyzed news."""

    SOURCE_AUTHORITY = {
        "CoinDesk": 1.0,
        "Cointelegraph": 0.9,
        "Bitcoin Magazine": 0.85,
        "Decrypt": 0.85,
        "The Block": 0.9,
    }

    def __init__(self):
        """Initialize signal generator."""
        pass

    def _score_sentiment(self, sentiment: Sentiment) -> int:
        """Convert sentiment to score."""
        scores = {"bullish": 1, "bearish": -1, "neutral": 0}
        return scores.get(sentiment, 0)

    def _score_impact(self, impact: str) -> int:
        """Convert impact to score."""
        scores = {"high": 3, "medium": 2, "low": 1}
        return scores.get(impact, 1)

    def _score_recency(self, published_at: datetime) -> float:
        """Newer news = higher score."""
        hours_old = (datetime.now() - published_at).total_seconds() / 3600
        # Decay: 1.0 for 0-6h, 0.7 for 6-12h, 0.4 for 12-24h
        if hours_old <= 6:
            return 1.0
        elif hours_old <= 12:
            return 0.7
        else:
            return 0.4

    def generate_signals(
        self,
        analyses: List[NewsAnalysis],
        min_confidence: int = 0,
    ) -> List[Signal]:
        """Generate signals from analyzed news."""
        # Group by asset
        asset_news: Dict[str, List[NewsAnalysis]] = defaultdict(list)
        for analysis in analyses:
            for asset in analysis.assets:
                if analysis.actionable:
                    asset_news[asset].append(analysis)

        signals = []

        for asset, news_list in asset_news.items():
            # Calculate weighted score
            total_score = 0.0
            total_weight = 0.0
            key_drivers = []
            risk_notes = []
            bullish_count = 0
            bearish_count = 0

            for news in news_list:
                # Weight = sentiment * impact * recency * source_authority * confidence
                sentiment_score = self._score_sentiment(news.sentiment)
                impact_score = self._score_impact(news.impact)
                recency_score = self._score_recency(datetime.now())  # Simplified
                source_score = self.SOURCE_AUTHORITY.get(news.source, 0.7)
                confidence_score = news.confidence / 100.0

                weight = (
                    abs(sentiment_score)
                    * impact_score
                    * recency_score
                    * source_score
                    * confidence_score
                )

                total_score += sentiment_score * weight
                total_weight += weight

                # Track sentiment counts
                if news.sentiment == "bullish":
                    bullish_count += 1
                elif news.sentiment == "bearish":
                    bearish_count += 1

                # Collect key drivers
                if news.impact in ["high", "medium"]:
                    key_drivers.append(f"• {news.title[:80]}... ({news.source})")

                # Collect risk notes from reasoning
                if "risk" in news.reasoning.lower():
                    risk_notes.append(news.reasoning[:100])

            # Skip if not enough data
            if total_weight < 1.0:
                continue

            # Calculate direction
            net_sentiment = total_score / total_weight

            if net_sentiment > 0.2:
                direction = Direction.LONG
            elif net_sentiment < -0.2:
                direction = Direction.SHORT
            else:
                direction = Direction.NEUTRAL

            # Calculate confidence
            sentiment_confidence = min(bullish_count, bearish_count) / max(bullish_count, bearish_count, 1)
            weight_confidence = min(total_weight / 3.0, 1.0)
            confidence = int((sentiment_confidence * 0.4 + weight_confidence * 0.6) * 100)

            # Skip if below threshold
            if confidence < min_confidence:
                continue

            # Limit key drivers and risk notes
            key_drivers = key_drivers[:5]
            risk_notes = risk_notes[:3]

            # Add risk note if mixed signals
            if bullish_count > 0 and bearish_count > 0:
                risk_notes.append(f"Mixed signals: {bullish_count} bullish, {bearish_count} bearish")

            # Create signal
            signal = Signal(
                asset=asset,
                direction=direction,
                confidence=confidence,
                key_drivers=key_drivers,
                risk_notes=risk_notes,
                news_count=len(news_list),
                last_updated=datetime.now(),
            )

            signals.append(signal)

        # Sort by confidence
        signals.sort(key=lambda x: x.confidence, reverse=True)

        return signals


def format_signal(signal: Signal) -> str:
    """Format signal for CLI output."""
    direction_emoji = {"LONG": "🟢", "SHORT": "🔴", "NEUTRAL": "⚪"}

    output = [f"{direction_emoji[signal.direction]} {signal.asset} | {signal.direction} | {signal.confidence}% confidence"]
    output.append("=" * 60)

    if signal.key_drivers:
        output.append("\nKey Drivers:")
        output.extend(signal.key_drivers)

    if signal.risk_notes:
        output.append("\nRisk Notes:")
        output.extend([f"• {note}" for note in signal.risk_notes])

    output.append(f"\nNews analyzed: {signal.news_count}")

    return "\n".join(output)
