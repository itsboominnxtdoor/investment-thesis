"""Market sentiment service — fetches news & analyst context from Alpha Vantage."""

import logging

logger = logging.getLogger(__name__)

# Higher absolute value = more opinionated (bull or bear)
_SENTIMENT_RANK = {
    "Bullish": 2,
    "Somewhat-Bullish": 1,
    "Neutral": 0,
    "Somewhat-Bearish": -1,
    "Bearish": -2,
}


class MarketSentimentService:
    """Pulls recent news sentiment and analyst overview data from Alpha Vantage.

    Used to ground LLM thesis generation in real analyst commentary.
    All methods fall back gracefully — never raise.
    """

    def __init__(self):
        # Lazy import to avoid circular dependency
        from app.services.financial_data_service import FinancialDataService
        self._fds = FinancialDataService()

    async def get_market_context(self, ticker: str) -> dict:
        """Fetch analyst overview + recent news for a ticker.

        Returns:
            {
                "analyst_target_price": "185.00" | None,
                "52_week_range": "$124.17 – $198.23" | None,
                "pe_ratio": "28.5" | None,
                "forward_pe": "25.1" | None,
                "recent_news": [
                    {
                        "title": "...",
                        "source": "Seeking Alpha",
                        "summary": "...",
                        "sentiment": "Bullish",
                        "time_published": "20250115",
                    },
                    ...
                ],
            }
        """
        import asyncio

        overview, news = await asyncio.gather(
            self._get_overview(ticker),
            self._get_news(ticker),
            return_exceptions=True,
        )

        if isinstance(overview, Exception):
            logger.warning("AV OVERVIEW failed for %s: %s", ticker, overview)
            overview = {}
        if isinstance(news, Exception):
            logger.warning("AV NEWS_SENTIMENT failed for %s: %s", ticker, news)
            news = []

        return {
            "analyst_target_price": overview.get("analyst_target_price"),
            "52_week_range": overview.get("52_week_range"),
            "pe_ratio": overview.get("pe_ratio"),
            "forward_pe": overview.get("forward_pe"),
            "recent_news": news,
        }

    def format_for_prompt(self, ctx: dict) -> str:
        """Render market context as a prompt-friendly string."""
        if not ctx:
            return "No market context available."

        lines: list[str] = []

        # Analyst metrics line
        metrics = []
        if ctx.get("analyst_target_price"):
            metrics.append(f"Analyst Consensus Target: ${ctx['analyst_target_price']}")
        if ctx.get("52_week_range"):
            metrics.append(f"52-Week Range: {ctx['52_week_range']}")
        if ctx.get("pe_ratio") and ctx["pe_ratio"] not in ("None", "-"):
            metrics.append(f"P/E: {ctx['pe_ratio']}")
        if ctx.get("forward_pe") and ctx["forward_pe"] not in ("None", "-"):
            metrics.append(f"Fwd P/E: {ctx['forward_pe']}")
        if metrics:
            lines.append("  ".join(metrics))

        news = ctx.get("recent_news") or []
        if news:
            lines.append("")
            lines.append("Recent Analyst & News Commentary:")
            for art in news:
                sentiment_tag = f"[{art['sentiment']}]" if art.get("sentiment") else ""
                source_tag = f"({art['source']}, {art['time_published']})" if art.get("source") else ""
                lines.append(f"  {sentiment_tag} \"{art['title']}\" {source_tag}")
                if art.get("summary"):
                    lines.append(f"    {art['summary']}")
        else:
            lines.append("No recent analyst news available.")

        return "\n".join(lines)

    # ------------------------------------------------------------------ #
    # Private helpers
    # ------------------------------------------------------------------ #

    async def _get_overview(self, ticker: str) -> dict:
        data = await self._fds._get("OVERVIEW", {"symbol": ticker})
        if not data or "Symbol" not in data:
            return {}
        high = data.get("52WeekHigh") or ""
        low = data.get("52WeekLow") or ""
        week_range = f"${low} – ${high}" if high and low and high != "None" and low != "None" else None
        return {
            "analyst_target_price": _clean(data.get("AnalystTargetPrice")),
            "52_week_range": week_range,
            "pe_ratio": _clean(data.get("PERatio")),
            "forward_pe": _clean(data.get("ForwardPE")),
        }

    async def _get_news(self, ticker: str) -> list[dict]:
        data = await self._fds._get(
            "NEWS_SENTIMENT",
            {"tickers": ticker, "limit": "20", "sort": "RELEVANCE"},
        )
        feed = data.get("feed") or []
        if not feed:
            return []

        results = []
        for art in feed:
            # Filter to articles where this ticker is a primary subject
            ticker_sentiment = next(
                (t for t in art.get("ticker_sentiment", []) if t.get("ticker", "").upper() == ticker.upper()),
                None,
            )
            if ticker_sentiment:
                try:
                    relevance = float(ticker_sentiment.get("relevance_score", 0))
                except (ValueError, TypeError):
                    relevance = 0.0
                if relevance < 0.25:
                    continue
            elif not ticker_sentiment:
                # Article mentions the ticker but no per-ticker sentiment block — include anyway
                pass

            results.append({
                "title": art.get("title", ""),
                "source": art.get("source", ""),
                "summary": (art.get("summary") or "")[:500],
                "sentiment": art.get("overall_sentiment_label", "Neutral"),
                "time_published": (art.get("time_published") or "")[:8],
            })

        # Sort: most opinionated articles first (bull/bear > neutral), keeping variety
        results.sort(
            key=lambda a: abs(_SENTIMENT_RANK.get(a["sentiment"], 0)),
            reverse=True,
        )
        return results[:8]


def _clean(val: str | None) -> str | None:
    """Return None for missing / placeholder AV values."""
    if not val or val in ("None", "-", "0", "0.0", "N/A"):
        return None
    return val
