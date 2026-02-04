"""Tests for signal generator."""

import pytest
from datetime import datetime, timedelta

from src.generator import SignalGenerator, format_signal, Direction
from src.analyzer import NewsAnalysis, Sentiment, Impact


class TestSignalGenerator:
    """Test signal generator functionality."""

    @pytest.fixture
    def generator(self):
        """Create signal generator."""
        return SignalGenerator()

    def test_score_sentiment(self, generator):
        """Test sentiment scoring."""
        assert generator._score_sentiment(Sentiment.BULLISH) == 1
        assert generator._score_sentiment(Sentiment.BEARISH) == -1
        assert generator._score_sentiment(Sentiment.NEUTRAL) == 0

    def test_score_impact(self, generator):
        """Test impact scoring."""
        assert generator._score_impact("high") == 3
        assert generator._score_impact("medium") == 2
        assert generator._score_impact("low") == 1

    def test_score_recency(self, generator):
        """Test recency scoring."""
        now = datetime.now()

        # Fresh news (< 6h) = 1.0
        assert generator._score_recency(now) == 1.0

        # Medium fresh (6-12h) = 0.7
        assert generator._score_recency(now - timedelta(hours=8)) == 0.7

        # Old news (> 12h) = 0.4
        assert generator._score_recency(now - timedelta(hours=18)) == 0.4

    def test_generate_signals_bullish(self, generator):
        """Test generating bullish signal."""
        analyses = [
            NewsAnalysis(
                title="Bitcoin surges to $100k",
                url="https://example.com",
                source="CoinDesk",
                sentiment=Sentiment.BULLISH,
                impact=Impact.HIGH,
                assets=["BTC"],
                confidence=85,
                actionable=True,
                key_takeaways=["Breakout above resistance"],
                reasoning="Strong buy pressure",
            )
        ]

        signals = generator.generate_signals(analyses, min_confidence=0)

        assert len(signals) > 0
        assert signals[0].asset == "BTC"
        assert signals[0].direction == Direction.LONG

    def test_generate_signals_bearish(self, generator):
        """Test generating bearish signal."""
        analyses = [
            NewsAnalysis(
                title="Bitcoin crashes 20% in sell-off",
                url="https://example.com",
                source="CoinDesk",
                sentiment=Sentiment.BEARISH,
                impact=Impact.HIGH,
                assets=["BTC"],
                confidence=85,
                actionable=True,
                key_takeaways=["Market panic"],
                reasoning="Heavy selling pressure",
            )
        ]

        signals = generator.generate_signals(analyses, min_confidence=0)

        assert len(signals) > 0
        assert signals[0].asset == "BTC"
        assert signals[0].direction == Direction.SHORT

    def test_generate_signals_mixed(self, generator):
        """Test mixed bullish/bearish signals."""
        analyses = [
            NewsAnalysis(
                title="Bitcoin surges",
                url="https://example.com/1",
                source="CoinDesk",
                sentiment=Sentiment.BULLISH,
                impact=Impact.HIGH,
                assets=["BTC"],
                confidence=85,
                actionable=True,
                key_takeaways=["Upward momentum"],
                reasoning="Bullish",
            ),
            NewsAnalysis(
                title="Bitcoin falls",
                url="https://example.com/2",
                source="CoinDesk",
                sentiment=Sentiment.BEARISH,
                impact=Impact.HIGH,
                assets=["BTC"],
                confidence=85,
                actionable=True,
                key_takeaways=["Downward pressure"],
                reasoning="Bearish",
            ),
        ]

        signals = generator.generate_signals(analyses, min_confidence=0)

        # Should have mixed sentiment, might result in NEUTRAL or one dominant
        assert len(signals) > 0
        assert signals[0].asset == "BTC"

    def test_min_confidence_filter(self, generator):
        """Test confidence filtering."""
        # Single bullish article with HIGH impact yields ~51% confidence
        analyses = [
            NewsAnalysis(
                title="Test news 1",
                url="https://example.com/1",
                source="CoinDesk",
                sentiment=Sentiment.BULLISH,
                impact=Impact.HIGH,
                assets=["BTC"],
                confidence=85,
                actionable=True,
                key_takeaways=["Test"],
                reasoning="Test",
            ),
            NewsAnalysis(
                title="Test news 2",
                url="https://example.com/2",
                source="CoinDesk",
                sentiment=Sentiment.BULLISH,
                impact=Impact.HIGH,
                assets=["BTC"],
                confidence=85,
                actionable=True,
                key_takeaways=["Test"],
                reasoning="Test",
            ),
        ]

        # With min confidence 80, should return empty (2 bull articles = ~70% confidence)
        signals = generator.generate_signals(analyses, min_confidence=80)
        assert len(signals) == 0

        # With min confidence 40, should return signal
        signals = generator.generate_signals(analyses, min_confidence=40)
        assert len(signals) > 0

    def test_no_actionable_signals(self, generator):
        """Test that non-actionable analyses are filtered."""
        analyses = [
            NewsAnalysis(
                title="Generic tech news",
                url="https://example.com",
                source="Test",
                sentiment=Sentiment.NEUTRAL,
                impact=Impact.LOW,
                assets=[],
                confidence=50,
                actionable=False,
                key_takeaways=[],
                reasoning="No crypto assets",
            )
        ]

        signals = generator.generate_signals(analyses, min_confidence=0)
        assert len(signals) == 0


class TestFormatSignal:
    """Test signal formatting."""

    def test_format_bullish_signal(self):
        """Test formatting bullish signal."""
        signal = type('Signal', (), {
            'direction': Direction.LONG,
            'asset': 'BTC',
            'confidence': 85,
            'key_drivers': ['• Bitcoin breaks $100k (CoinDesk)'],
            'risk_notes': ['• High volatility'],
            'news_count': 3,
        })()

        output = format_signal(signal)

        assert '🟢' in output
        assert 'BTC' in output
        assert 'LONG' in output
        assert '85% confidence' in output

    def test_format_bearish_signal(self):
        """Test formatting bearish signal."""
        signal = type('Signal', (), {
            'direction': Direction.SHORT,
            'asset': 'BTC',
            'confidence': 75,
            'key_drivers': ['• Bitcoin crashes below $80k (CoinDesk)'],
            'risk_notes': ['• Panic selling'],
            'news_count': 2,
        })()

        output = format_signal(signal)

        assert '🔴' in output
        assert 'BTC' in output
        assert 'SHORT' in output

    def test_format_neutral_signal(self):
        """Test formatting neutral signal."""
        signal = type('Signal', (), {
            'direction': Direction.NEUTRAL,
            'asset': 'BTC',
            'confidence': 60,
            'key_drivers': ['• Mixed signals (CoinDesk)'],
            'risk_notes': [],
            'news_count': 1,
        })()

        output = format_signal(signal)

        assert '⚪' in output
        assert 'BTC' in output
        assert 'NEUTRAL' in output
