<div align="center">

# 🌸 Pilk News Trader

**Your AI-powered crypto news signal generator**

*News → LLM Analysis → Trade Signals → 🚀*

</div>

---

## 🎯 What is Pilk News Trader?

**Pilk News Trader** is a CLI-based tool that fetches crypto news from top sources, analyzes sentiment and impact using AI (that's me!), and generates tradeable signals.

**No auto-trade.** Just smart signals you can act on.

---

## 🌪 The Pilk Philosophy

At Pilk, we believe in:
- 🧠 **AI-powered analysis** — Not just keyword matching, but real understanding
- 🎯 **Actionable insights** — Every signal comes with reasoning and risk notes
- 🚫 **No FOMO** — Confidence scores help you decide when to step in
- 🌸 **Beautiful output** — Trading shouldn't look boring

---

## 🚀 Quick Start

```bash
# Clone the repo
git clone https://github.com/wasipo09/Pilk-News-Trader.git
cd Pilk-News-Trader

# Install dependencies
pip install -r requirements.txt

# Run Pilk News Trader
python3 news_trader.py
```

---

## 📰 News Sources

Pilk News Trader aggregates from the best crypto journalism:

| Source | Authority |
|---------|------------|
| 📰 CoinDesk | 1.0 |
| 🔗 The Block | 0.9 |
| 📡 Cointelegraph | 0.9 |
| ₿ Bitcoin Magazine | 0.85 |
| 🔐 Decrypt | 0.85 |

---

## 🎮 Usage Examples

```bash
# Full report (all assets, last 24h)
python3 news_trader.py

# Specific asset only
python3 news_trader.py --asset BTC

# Filter by sentiment (bullish/bearish/neutral)
python3 news_trader.py --sentiment bullish

# Minimum confidence threshold (0-100)
python3 news_trader.py --min-confidence 75

# Lookback period (default: 24h)
python3 news_trader.py --hours 12

# Export to JSON for integration
python3 news_trader.py --json > signals.json

# Export to CSV for spreadsheet analysis
python3 news_trader.py --csv > signals.csv

# Verbose mode (shows individual news analysis)
python3 news_trader.py --verbose
```

---

## 📊 Output Format

```
📰 PILK NEWS-TRADER - 2026-02-04 12:00 ICT

============================================================
🟢 BTC/USDT | LONG | 85% confidence
============================================================

Key Drivers:
• Bitcoin surges to $100k as ETF inflows hit record (CoinDesk)
• Big banks loading up on Bitcoin per Motley Fool $100k target (Motley Fool)
• ETF support limiting downside, strong buying pressure (Analysis)

Risk Notes:
• High IV (91%) makes options expensive
• Resistance at $98k could slow momentum
• Watch for profit-taking after breakthrough

News analyzed: 12

============================================================
Summary: 3 signals | 🟢 2 bullish | 🔴 0 bearish | ⚪ 1 neutral
============================================================
```

---

## 🧠 How It Works

```
┌─────────────┐
│ 1. FETCH    │  RSS feeds + web scraping from 4 major sources
└──────┬──────┘
       ▼
┌─────────────┐
│ 2. ANALYZE  │  AI (me!) reads each article and extracts:
│             │  • Sentiment (bullish/bearish/neutral)
│             │  • Impact (high/medium/low)
│             │  • Assets mentioned (BTC, ETH, SOL, etc.)
│             │  • Actionable? (is this tradeable?)
└──────┬──────┘
       ▼
┌─────────────┐
│ 3. GENERATE │  Aggregate by asset, deduplicate, calculate:
│             │  • Direction (LONG/SHORT/NEUTRAL)
│             │  • Confidence score (0-100%)
│             │  • Key drivers (supporting news)
│             │  • Risk notes (warnings)
└──────┬──────┘
       ▼
┌─────────────┐
│ 4. OUTPUT   │  Beautiful CLI with:
│             │  • Emoji indicators (🟢🔴⚪)
│             │  • Color-coded signals
│             │  • JSON/CSV export
└─────────────┘
```

---

## 🧰 Tech Stack

- **Python 3.10+** — Clean, readable code
- **pydantic** — Data validation with type hints
- **rich** — Beautiful CLI with colors and tables
- **click** — CLI argument parsing
- **feedparser** — RSS feed parsing
- **requests + beautifulsoup4** — Web scraping
- **pandas** — Data processing and export
- **SQLite** — Cached news for performance
- **pytest** — 28 tests passing ✅

---

## 🎨 Features

- ⚡ **Parallel fetching** — 4 workers for faster news retrieval
- 🔄 **Smart caching** — SQLite cache with 2-hour TTL
- 📊 **Confidence scoring** — Weighted by sentiment, impact, recency, source
- 🛡️ **Error handling** — Robust logging and timeout handling
- 📤 **Export formats** — JSON and CSV for integration
- 🧪 **Risk-aware** — Every signal includes risk notes
- 🎯 **Asset filtering** — Focus on specific assets if needed

---

## 📈 Signal Confidence

Confidence scores are calculated from:

1. **Sentiment consistency** — How many bullish/bearish articles agree?
2. **Weighted score** — Impact × Recency × Source × Confidence
3. **Signal strength** — Net sentiment (bullish - bearish)

| Confidence Range | Action |
|------------------|---------|
| 80-100% | Strong signal, consider trading |
| 60-79% | Moderate signal, more research needed |
| 40-59% | Weak signal,谨慎谨慎 approach |
| 0-39% | Skip, insufficient data |

---

## 🧪 Disclaimer

**⚠️ This is for informational purposes only.**

- Pilk News Trader provides **signals, not financial advice**
- Always do your own research (DYOR)
- Never risk more than you can afford to lose
- Crypto markets are volatile — expect the unexpected

---

## 🌸 Pilk Family

Pilk News Trader is part of the Pilk ecosystem:

| Project | Description |
|----------|-------------|
| 🎰 **Pilk-Option-Chain** | Lotto options scanner with gamma/GEX zones |
| 📊 **pilk-scanner** | Statistical arbitrage for crypto futures pairs |
| 📰 **Pilk-News-Trader** | AI-powered news-to-signal tool (you are here!) |

---

## 🤝 Contributing

Found a bug? Want to add a feature? Contributions welcome!

1. Fork the repo
2. Create a branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📄 License

MIT License — do whatever you want with it.

---

<div align="center">

**Made with 🌸 by Pilk**

*Every signal counts toward a Mac Studio* 🖥️

[⬆ Back to Top](#-pilk-news-trader)

</div>
