#!/usr/bin/env python3
"""Pilk News Trader - CLI-based news-to-signal tool."""

import sys
from pathlib import Path
from typing import Optional, List

import click
import pandas as pd
from rich.console import Console
from rich.table import Table

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.aggregator import NewsAggregator, NewsItem
from src.analyzer import NewsAnalyzer, NewsAnalysis, Sentiment, Impact, extract_crypto_assets
from src.generator import SignalGenerator, format_signal


console = Console()


@click.command()
@click.option("--asset", help="Filter by asset (e.g., BTC, ETH)")
@click.option("--sentiment", help="Filter by sentiment (bullish, bearish, neutral)")
@click.option("--min-confidence", type=int, default=0, help="Minimum confidence threshold (0-100)")
@click.option("--hours", type=int, default=24, help="Lookback period in hours")
@click.option("--json", "json_output", is_flag=True, help="Output as JSON")
@click.option("--csv", "csv_output", is_flag=True, help="Output as CSV")
@click.option("--verbose", is_flag=True, help="Show individual news analysis")
def main(
    asset: Optional[str],
    sentiment: Optional[str],
    min_confidence: int,
    hours: int,
    json_output: bool,
    csv_output: bool,
    verbose: bool,
):
    """Fetch news, analyze, and generate signals."""

    console.print(f"📰 PILK NEWS-TRADER - {get_current_time()}\n")

    # Step 1: Fetch news
    with console.status("[bold green]Fetching news...", spinner="dots"):
        aggregator = NewsAggregator()
        news_items = aggregator.fetch(hours=hours)

    if not news_items:
        console.print("[yellow]No news found within time window.[/yellow]")
        return

    console.print(f"Analyzing {len(news_items)} articles...\n")

    # Step 2: Analyze news (this is where AI analyzes each item)
    # NOTE: The AI model should analyze each news item here
    # This is a placeholder - in actual use, I will analyze each item naturally
    analyses: List[NewsAnalysis] = []

    # Placeholder: Simple rule-based analysis as fallback
    # In production, AI would analyze each item for proper sentiment/impact
    for item in news_items[:20]:  # Limit to 20 for demo
        title_lower = item.title.lower()

        # Simple heuristic sentiment
        if any(word in title_lower for word in ["surge", "rally", "soar", "jump", "gain", "bull", "positive"]):
            sentiment_val = Sentiment.bullish
        elif any(word in title_lower for word in ["plunge", "crash", "dump", "fall", "bear", "negative", "fear"]):
            sentiment_val = Sentiment.bearish
        else:
            sentiment_val = Sentiment.neutral

        # Simple heuristic impact
        if any(word in title_lower for word in ["break", "record", "major", "significant", "alert", "urgent"]):
            impact_val = Impact.high
        elif any(word in title_lower for word in ["update", "report", "data", "news"]):
            impact_val = Impact.medium
        else:
            impact_val = Impact.low

        # Extract assets
        assets = extract_crypto_assets(item.title + " " + (item.summary or ""))

        # Simple confidence based on source
        confidence = 50
        if item.source in ["CoinDesk", "The Block"]:
            confidence = 70

        analysis = NewsAnalysis(
            title=item.title,
            url=item.url,
            source=item.source,
            sentiment=sentiment_val,
            impact=impact_val,
            assets=assets,
            confidence=confidence,
            actionable=len(assets) > 0,
            key_takeaways=[item.title[:80]] if assets else [],
            reasoning=f"Based on keywords in title: {sentiment_val} sentiment",
        )

        analyses.append(analysis)

    # Step 3: Generate signals
    with console.status("[bold green]Generating signals...", spinner="dots"):
        generator = SignalGenerator()
        signals = generator.generate_signals(analyses, min_confidence=min_confidence)

    # Filter by asset
    if asset:
        asset = asset.upper()
        signals = [s for s in signals if s.asset == asset]

    # Filter by sentiment
    if sentiment:
        sentiment = sentiment.lower()
        signals = [s for s in signals if s.direction.lower() == sentiment]

    # Output
    if json_output:
        import json
        output = [s.model_dump() for s in signals]
        console.print(json.dumps(output, indent=2, default=str))
    elif csv_output:
        df = pd.DataFrame([s.model_dump() for s in signals])
        console.print(df.to_csv(index=False))
    else:
        # Pretty CLI output
        if signals:
            for signal in signals:
                console.print(format_signal(signal))
                console.print()
        else:
            console.print("[yellow]No signals matching criteria.[/yellow]")

        # Summary
        bullish = sum(1 for s in signals if s.direction == "LONG")
        bearish = sum(1 for s in signals if s.direction == "SHORT")
        neutral = sum(1 for s in signals if s.direction == "NEUTRAL")

        console.print("=" * 60)
        console.print(f"Summary: {len(signals)} signals | 🟢 {bullish} bullish | 🔴 {bearish} bearish | ⚪ {neutral} neutral")
        console.print("=" * 60)

    # Verbose mode - show individual news analysis
    if verbose and analyses:
        console.print("\n[bold]Individual News Analysis:[/bold]\n")
        for i, analysis in enumerate(analyses[:10], 1):
            console.print(f"{i}. {analysis.title}")
            console.print(f"   Sentiment: {analysis.sentiment} | Impact: {analysis.impact} | Assets: {', '.join(analysis.assets)}")
            console.print(f"   Reasoning: {analysis.reasoning}")
            console.print()


def get_current_time() -> str:
    """Get current time formatted."""
    from datetime import datetime
    return datetime.now().strftime("%Y-%m-%d %H:%M ICT")


if __name__ == "__main__":
    main()
