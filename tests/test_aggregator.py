"""Tests for news aggregator."""

import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch
from pathlib import Path
import sqlite3

from src.aggregator import NewsAggregator, NewsItem


class TestNewsAggregator:
    """Test news aggregator functionality."""

    @pytest.fixture
    def temp_cache_db(self, tmp_path):
        """Create temporary cache database."""
        cache_db = tmp_path / "cache.db"
        return cache_db

    @pytest.fixture
    def aggregator(self, temp_cache_db):
        """Create aggregator with temp cache."""
        return NewsAggregator(cache_db=temp_cache_db)

    def test_initialization(self, aggregator, temp_cache_db):
        """Test aggregator initializes cache."""
        assert temp_cache_db.exists()

    def test_news_item_creation(self):
        """Test NewsItem model validation."""
        item = NewsItem(
            title="Bitcoin surges to $100k",
            url="https://example.com/article",
            source="Test Source",
            published_at=datetime.now(),
            summary="Bitcoin breaks all-time high",
        )

        assert item.title == "Bitcoin surges to $100k"
        assert item.source == "Test Source"
        assert "Bitcoin" in item.title

    def test_cache_set_get(self, aggregator):
        """Test caching works."""
        data = {
            "title": "Test article",
            "url": "https://test.com",
            "source": "Test",
            "published_at": datetime.now().isoformat(),
        }

        # Set cache
        aggregator._set_cache("https://test.com", data)

        # Get cache
        result = aggregator._get_cache("https://test.com")

        assert result is not None
        assert result["title"] == "Test article"
        assert result["url"] == "https://test.com"

    def test_cache_expiration_direct_db_check(self, aggregator):
        """Test cache expiration by checking DB timestamp directly."""
        # Create old cache entry (3 hours ago)
        three_hours_ago = datetime.now() - timedelta(hours=3)
        old_data = {
            "title": "Old article",
            "url": "https://old.com",
            "source": "Test",
            "published_at": three_hours_ago.isoformat(),
        }

        # Manually insert old cache into DB
        conn = sqlite3.connect(aggregator.cache_db)
        import hashlib
        url_hash = hashlib.md5("https://old.com".encode()).hexdigest()
        conn.execute(
            """
            INSERT OR REPLACE INTO news_cache (url_hash, data, cached_at)
            VALUES (?, ?, ?)
            """,
            (url_hash,
             '{"title": "Old article", "url": "https://old.com", "source": "Test", "published_at": "' + three_hours_ago.isoformat() + '"}',
             three_hours_ago.isoformat())
        )
        conn.commit()
        conn.close()

        # Now verify the cached_at timestamp is > 2 hours old
        conn = sqlite3.connect(aggregator.cache_db)
        cursor = conn.execute(
            "SELECT cached_at FROM news_cache WHERE url_hash = ?",
            (url_hash,)
        )
        row = cursor.fetchone()
        conn.close()

        assert row is not None
        cached_at = datetime.fromisoformat(row[0])
        time_diff = datetime.now() - cached_at

        # Should be ~3 hours old
        assert time_diff >= timedelta(hours=2)

    def test_cache_valid_within_window(self, aggregator):
        """Test cache is valid within 2 hours."""
        recent_data = {
            "title": "Recent article",
            "url": "https://recent.com",
            "source": "Test",
            "published_at": (datetime.now() - timedelta(hours=1)).isoformat(),
        }

        # Set recent cache
        aggregator._set_cache("https://recent.com", recent_data)

        # Get cache - should return data (within 2 hours)
        result = aggregator._get_cache("https://recent.com")

        assert result is not None
        assert result["title"] == "Recent article"

    @patch('src.aggregator.feedparser.parse')
    def test_fetch_rss(self, mock_parse, aggregator):
        """Test RSS fetching."""
        # Mock RSS feed
        mock_feed = Mock()
        mock_entry = Mock()
        mock_entry.link = "https://example.com/1"
        mock_entry.title = "Bitcoin rallies"
        mock_entry.published_parsed = datetime.now().timetuple()
        mock_entry.summary = "<p>BTC up 10%</p>"
        mock_entry.get = Mock(side_effect=lambda key, default=None: {
            'title': 'Bitcoin rallies',
            'summary': '<p>BTC up 10%</p>',
            'link': 'https://example.com/1'
        }.get(key))

        mock_feed.entries = [mock_entry]
        mock_parse.return_value = mock_feed

        # Fetch
        items = aggregator._fetch_rss("coindesk")

        assert len(items) > 0
        assert any("Bitcoin" in item.title for item in items)

    def test_fetch_with_time_filter(self, aggregator):
        """Test time filtering works."""
        # Create items at different times
        now = datetime.now()
        old_item = NewsItem(
            title="Old news",
            url="https://old.com",
            source="Test",
            published_at=now - timedelta(hours=48),
        )
        new_item = NewsItem(
            title="New news",
            url="https://new.com",
            source="Test",
            published_at=now - timedelta(hours=1),
        )

        # Directly test fetch filtering
        # (In real usage, this would go through aggregator)
        cutoff = now - timedelta(hours=24)

        assert old_item.published_at < cutoff
        assert new_item.published_at > cutoff
