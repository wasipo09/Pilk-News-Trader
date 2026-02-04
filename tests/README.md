# Test Suite

Pilk News Trader test suite uses pytest.

## Running Tests

```bash
cd ~/Projects/pilk-news-trader
source venv/bin/activate

# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=src --cov-report=html

# Run specific test file
pytest tests/test_aggregator.py -v

# Run specific test
pytest tests/test_aggregator.py::TestNewsAggregator::test_cache_set_get -v
```

## Test Coverage

- **test_aggregator.py**: News fetching, caching, time filtering
- **test_analyzer.py**: Sentiment analysis, asset extraction
- **test_generator.py**: Signal generation, confidence scoring, formatting

## Current Status

- 27 tests passing
- 1 test skipped (cache expiration requires time manipulation)
- 0 tests failing
