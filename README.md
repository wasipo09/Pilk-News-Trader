# Pilk News Trader

CLI-based news-to-signal tool for crypto trading.

Fetches news from top crypto sources, analyzes sentiment and impact, generates tradeable signals.

## Concept

News → LLM Analysis → Signal Generator → CLI Output

No auto-trade. Smart signals you can act on.

## Installation

```bash
cd ~/Projects/pilk-news-trader
pip install -r requirements.txt
```

## Usage

```bash
# Full report
python3 news_trader.py

# Specific asset
python3 news_trader.py --asset BTC

# Filter by sentiment
python3 news_trader.py --sentiment bullish

# Min confidence
python3 news_trader.py --min-confidence 75

# Lookback period (default 24h)
python3 news_trader.py --hours 12

# Export
python3 news_trader.py --json > signals.json
python3 news_trader.py --csv > signals.csv

# Verbose mode (show individual news analysis)
python3 news_trader.py --verbose
```

## News Sources

- CoinDesk
- Cointelegraph
- Bitcoin Magazine
- Decrypt
- The Block

## Output

```
📰 PILK NEWS-TRADER - 2026-02-04 11:33 ICT

============================================================
BTC/USDT | BEARISH | 72% confidence
============================================================
Key Drivers:
• BTC fell from $80k to ~$74k over weekend - capitulation (CoinDesk)
• $469M in long liquidations - extreme fear (Hokanews)
• Net GEX negative at $80k resistance (Option data)

Risk Notes:
• High IV (91%) makes options expensive
• Need to test $75-76k support

Recommendation: Wait for stabilization
============================================================
```

## Tech Stack

- Python 3.10+
- requests, beautifulsoup4, feedparser
- rich, click (CLI)
- pandas (data processing)
- pydantic (validation)
- SQLite (cache)
