"""Tests for news analyzer."""

import pytest

from src.analyzer import NewsAnalyzer, extract_crypto_assets, NewsAnalysis, Sentiment, Impact


class TestNewsAnalyzer:
    """Test news analyzer functionality."""

    @pytest.fixture
    def analyzer(self):
        """Create analyzer instance."""
        return NewsAnalyzer()

    def test_extract_crypto_assets_btc(self):
        """Test BTC asset extraction."""
        text = "Bitcoin surges to new all-time high as BTC breaks $100k"
        assets = extract_crypto_assets(text)

        assert "BTC" in assets

    def test_extract_crypto_assets_eth(self):
        """Test ETH asset extraction."""
        text = "Ethereum 2.0 upgrade complete, ETH gas fees drop"
        assets = extract_crypto_assets(text)

        assert "ETH" in assets

    def test_extract_crypto_assets_multiple(self):
        """Test multiple asset extraction."""
        text = "BTC, ETH, and SOL all rally after positive market news"
        assets = extract_crypto_assets(text)

        assert "BTC" in assets
        assert "ETH" in assets
        assert "SOL" in assets

    def test_extract_crypto_assets_full_names(self):
        """Test full name extraction."""
        text = "Bitcoin and Ethereum prices surge"
        assets = extract_crypto_assets(text)

        assert "BTC" in assets
        assert "ETH" in assets

    def test_extract_crypto_assets_none(self):
        """Test no assets found."""
        text = "Stock market rallies as tech stocks surge"
        assets = extract_crypto_assets(text)

        assert len(assets) == 0

    def test_extract_crypto_assets_deduplicate(self):
        """Test deduplication works."""
        text = "BTC BTC Bitcoin BTC Bitcoin"  # Repeated mentions
        assets = extract_crypto_assets(text)

        assert len(assets) == 1
        assert "BTC" in assets

    def test_create_analysis(self, analyzer):
        """Test creating news analysis."""
        from src.aggregator import NewsItem

        item = NewsItem(
            title="Bitcoin surges 10%",
            url="https://example.com",
            source="Test",
            published_at=datetime.now(),
        )

        analysis = analyzer.create_analysis(
            item=item,
            sentiment=Sentiment.BULLISH,
            impact=Impact.HIGH,
            assets=["BTC"],
            confidence=85,
            actionable=True,
            key_takeaways=["Strong upward momentum"],
            reasoning="Bitcoin broke key resistance",
        )

        assert analysis.sentiment == Sentiment.BULLISH
        assert analysis.impact == Impact.HIGH
        assert "BTC" in analysis.assets
        assert analysis.confidence == 85
        assert analysis.actionable is True

    def test_create_analysis_bearish(self, analyzer):
        """Test creating bearish analysis."""
        from src.aggregator import NewsItem

        item = NewsItem(
            title="Bitcoin crashes 20%",
            url="https://example.com",
            source="Test",
            published_at=datetime.now(),
        )

        analysis = analyzer.create_analysis(
            item=item,
            sentiment=Sentiment.BEARISH,
            impact=Impact.HIGH,
            assets=["BTC"],
            confidence=90,
            actionable=True,
            key_takeaways=["Massive sell-off"],
            reasoning="Market panic selling",
        )

        assert analysis.sentiment == Sentiment.BEARISH
        assert analysis.confidence == 90


class TestSentimentEnum:
    """Test sentiment enum."""

    def test_sentiment_values(self):
        """Test sentiment enum has correct values."""
        assert Sentiment.BULLISH.value == "bullish"
        assert Sentiment.BEARISH.value == "bearish"
        assert Sentiment.NEUTRAL.value == "neutral"


class TestImpactEnum:
    """Test impact enum."""

    def test_impact_values(self):
        """Test impact enum has correct values."""
        assert Impact.HIGH.value == "high"
        assert Impact.MEDIUM.value == "medium"
        assert Impact.LOW.value == "low"


# Fix import for datetime
from datetime import datetime
