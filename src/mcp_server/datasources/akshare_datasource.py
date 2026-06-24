"""Stock data source - uses Sina Finance API (no external dependency required)."""

import time
from functools import lru_cache
from typing import Optional

import requests

from mcp.server.fastmcp import FastMCP

akshare_tools = FastMCP("akshare-tools")

_SINA_BASE = "https://hq.sinajs.cn/list={}"
_HEADERS = {"Referer": "https://finance.sina.com.cn", "User-Agent": "Mozilla/5.0"}


def _check_akshare():
    """Always available - we use requests directly."""
    pass


def _get_cacheTTL():
    """Get cache TTL in seconds (5 minutes)."""
    return 300


def _ticker_to_sina(ticker: str) -> str:
    """Convert A-share ticker to Sina format."""
    ticker = ticker.strip().upper()
    if ticker.startswith("SH") or ticker.startswith("SZ"):
        return ticker.lower()
    # Pure number: guess exchange
    if len(ticker) == 6 and ticker.isdigit():
        # 6-digit A-share:000xxx -> sh, 600xxx -> sh, others -> sz
        if ticker.startswith("6") or ticker.startswith("000") or ticker.startswith("001"):
            return f"sh{ticker}"
        else:
            return f"sz{ticker}"
    return ticker


@akshare_tools.tool()
def get_stock_quote(ticker: str) -> dict:
    """
    Get real-time quote for a stock ticker.

    Args:
        ticker: Stock ticker symbol (e.g., "600519", "sh600519", "贵州茅台")

    Returns:
        dict: Current price, change %, volume
    """
    cache_key = f"quote_{ticker}"
    cached = _get_cached(cache_key)
    if cached:
        return cached

    try:
        sina_code = _ticker_to_sina(ticker)
        url = f"https://hq.sinajs.cn/list={sina_code}"
        resp = requests.get(url, headers=_HEADERS, timeout=10)
        resp.encoding = "gbk"
        text = resp.text.strip()

        if '=","' in text or text.count('"') < 2:
            return {"error": f"Ticker {ticker} not found", "ticker": ticker}

        # Parse: var hq_str_sh600519="贵州茅台,1278.000,..."
        data_part = text.split('"')[1]
        fields = data_part.split(",")

        name = fields[0]
        prev_close = float(fields[2])
        open_price = float(fields[1])
        current_price = float(fields[3])
        high = float(fields[4])
        low = float(fields[5])
        volume = int(fields[8]) if len(fields) > 8 else 0
        amount = float(fields[9]) if len(fields) > 9 else 0
        change_pct = (current_price - prev_close) / prev_close * 100 if prev_close else 0

        data = {
            "ticker": ticker,
            "name": name,
            "price": current_price,
            "prev_close": prev_close,
            "open": open_price,
            "high": high,
            "low": low,
            "change_pct": round(change_pct, 2),
            "volume": volume,
            "amount": amount,
            "timestamp": time.time(),
        }
        _set_cached(cache_key, data)
        return data
    except Exception as e:
        return {"error": str(e), "ticker": ticker}


@akshare_tools.tool()
def get_stock_history(ticker: str, period: str = "daily") -> dict:
    """
    Get historical K-line data for a stock.

    Args:
        ticker: Stock ticker symbol (e.g., "600519")
        period: K-line period - "daily", "weekly", "monthly" (default: "daily")

    Returns:
        dict: OHLCV data with date, open, high, low, close, volume
    """
    cache_key = f"history_{ticker}_{period}"
    cached = _get_cached(cache_key)
    if cached:
        return cached

    try:
        sina_code = _ticker_to_sina(ticker)
        # Sina k-line API: 1=daily, 2=weekly, 3=monthly
        period_map = {"daily": "1", "weekly": "2", "monthly": "3"}
        p = period_map.get(period, "1")

        url = f"https://money.finance.sina.com.com/quotes_service/api/json_v2.php/CN_MarketDataService.getKLineData"
        params = {"symbol": sina_code, "scale": p, "datalen": "100"}
        resp = requests.get(url, params=params, headers=_HEADERS, timeout=10)
        resp.encoding = "utf-8"
        data = resp.json()

        records = [
            {
                "date": d["day"],
                "open": float(d["open"]),
                "close": float(d["close"]),
                "high": float(d["high"]),
                "low": float(d["low"]),
                "volume": int(d["volume"]) if d.get("volume") else 0,
            }
            for d in data
        ]

        return {
            "ticker": ticker,
            "period": period,
            "data": records,
            "count": len(records),
            "timestamp": time.time(),
        }
    except Exception as e:
        return {"error": str(e), "ticker": ticker}


@akshare_tools.tool()
def get_index_components(index_code: str) -> dict:
    """
    Get constituent stocks of an index (CSI300, etc).
    Note: Simplified - returns basic info from Sina.

    Args:
        index_code: Index code (e.g., "000300" for CSI 300, "000001" for Shanghai)

    Returns:
        dict: Index name and current value
    """
    cache_key = f"index_{index_code}"
    cached = _get_cached(cache_key)
    if cached:
        return cached

    try:
        sina_code = _ticker_to_sina(index_code)
        url = f"https://hq.sinajs.cn/list={sina_code}"
        resp = requests.get(url, headers=_HEADERS, timeout=10)
        resp.encoding = "gbk"
        text = resp.text.strip()
        data_part = text.split('"')[1]
        fields = data_part.split(",")

        data = {
            "index_code": index_code,
            "name": fields[0],
            "current": float(fields[1]) if len(fields) > 1 else None,
            "change_pct": float(fields[3]) if len(fields) > 3 else None,
            "timestamp": time.time(),
        }
        _set_cached(cache_key, data)
        return data
    except Exception as e:
        return {"error": str(e), "index_code": index_code}


@akshare_tools.tool()
def get_valuation(ticker: str) -> dict:
    """
    Get valuation data for a stock.
    Note: Sina provides limited fundamental data - returns price-based metrics.

    Args:
        ticker: Stock ticker symbol (e.g., "600519")

    Returns:
        dict: Price-based valuation info
    """
    cache_key = f"valuation_{ticker}"
    cached = _get_cached(cache_key)
    if cached:
        return cached

    quote = get_stock_quote(ticker)
    if "error" in quote:
        return quote

    data = {
        "ticker": ticker,
        "name": quote.get("name"),
        "price": quote.get("price"),
        "prev_close": quote.get("prev_close"),
        "change_pct": quote.get("change_pct"),
        "timestamp": time.time(),
    }
    _set_cached(cache_key, data)
    return data


@akshare_tools.tool()
def get_market_sentiment() -> dict:
    """
    Get overall market sentiment indicators.
    Returns Shanghai Composite as a proxy for market sentiment.

    Returns:
        dict: Index value, change %, sentiment reading
    """
    cache_key = "market_sentiment"
    cached = _get_cached(cache_key)
    if cached:
        return cached

    try:
        # Shanghai composite (上证指数)
        resp = requests.get(
            "https://hq.sinajs.cn/list=sh000001",
            headers=_HEADERS,
            timeout=10
        )
        resp.encoding = "gbk"
        text = resp.text.strip()
        data_part = text.split('"')[1]
        fields = data_part.split(",")

        current = float(fields[1])
        prev = float(fields[2])
        change_pct = (current - prev) / prev * 100 if prev else 0

        # Simple sentiment classification
        if change_pct > 1:
            sentiment = "乐观"
        elif change_pct < -1:
            sentiment = "悲观"
        else:
            sentiment = "中性"

        data = {
            "index": "上证指数",
            "code": "sh000001",
            "current": current,
            "change_pct": round(change_pct, 2),
            "sentiment": sentiment,
            "timestamp": time.time(),
        }
        _set_cached(cache_key, data)
        return data
    except Exception as e:
        return {"error": str(e)}


# --- Simple in-memory cache (5-minute TTL) ---
_cache: dict = {}
_CACHE_TTL = 300  # 5 minutes


def _get_cached(key: str) -> Optional[dict]:
    """Get cached value if not expired."""
    if key in _cache:
        entry = _cache[key]
        if time.time() - entry["ts"] < _CACHE_TTL:
            return entry["data"]
        del _cache[key]
    return None


def _set_cached(key: str, data: dict):
    """Set cache entry with timestamp."""
    _cache[key] = {"data": data, "ts": time.time()}