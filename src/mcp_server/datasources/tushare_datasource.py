"""Tushare data source - comprehensive China stock data via Tushare API."""

import os
import time
from functools import lru_cache
from typing import Optional, Literal

import requests
import pandas as pd

from mcp.server.fastmcp import FastMCP

tushare_tools = FastMCP("tushare-tools")

_TUSHARE_TOKEN = os.environ.get("TUSHARE_TOKEN", "")
_TUSHARE_BASE_URL = "http://api.tushare.pro"
_CACHE_TTL = 300  # 5 minutes

# --- Simple in-memory cache ---
_cache: dict = {}


def _get_cache(key: str) -> Optional[dict]:
    """Get cached value if not expired."""
    if key in _cache:
        entry = _cache[key]
        if time.time() - entry["ts"] < _CACHE_TTL:
            return entry["data"]
        del _cache[key]
    return None


def _set_cache(key: str, data: dict):
    """Set cache entry with timestamp."""
    _cache[key] = {"data": data, "ts": time.time()}


def _call_tushare(api_name: str, params: dict, fields: list) -> dict:
    """Call Tushare API with token."""
    if not _TUSHARE_TOKEN:
        return {"error": "TUSHARE_TOKEN not set in environment variables"}

    payload = {
        "api_name": api_name,
        "token": _TUSHARE_TOKEN,
        "params": params,
        "fields": ",".join(fields) if fields else "",
    }

    try:
        resp = requests.post(_TUSHARE_BASE_URL, json=payload, timeout=30)
        result = resp.json()

        if result.get("code") != 0:
            return {"error": result.get("msg", "Unknown error"), "code": result.get("code")}

        data = result.get("data", {})
        if not data:
            return {"error": "No data returned", "code": -1}

        columns = data.get("fields", [])
        items = data.get("items", [])

        if not items:
            return {"error": "Empty result", "data": None}

        df = pd.DataFrame(items, columns=columns)
        return {"data": df, "code": 0}

    except requests.exceptions.Timeout:
        return {"error": "Request timeout", "code": -1}
    except Exception as e:
        return {"error": str(e), "code": -1}


# =====================
# Market Data APIs
# =====================

@tushare_tools.tool()
def get_daily_price(ts_code: str, start_date: str = "", end_date: str = "") -> dict:
    """
    Get daily price data for a stock (Tushare API: daily).

    Args:
        ts_code: Tushare stock code (e.g., "600519.SH" for 贵州茅台)
                 Format: {code}.{exchange} (SH=Shanghai, SZ=Shenzhen)
        start_date: Start date in YYYYMMDD format (default: 30 days ago)
        end_date: End date in YYYYMMDD format (default: today)

    Returns:
        dict: OHLCV data with date, open, high, low, close, volume, amount
    """
    cache_key = f"daily_{ts_code}_{start_date}_{end_date}"
    cached = _get_cache(cache_key)
    if cached:
        return cached

    if not start_date:
        start_date = pd.Timestamp.now().strftime("%Y%m%d")
        start_date = pd.Timestamp.now() - pd.Timedelta(days=30)
        start_date = start_date.strftime("%Y%m%d")
    if not end_date:
        end_date = pd.Timestamp.now().strftime("%Y%m%d")

    result = _call_tushare(
        "daily",
        params={"ts_code": ts_code, "start_date": start_date, "end_date": end_date},
        fields="ts_code,trade_date,open,high,low,close,vol,amount",
    )

    if "error" in result:
        return result

    df = result["data"]
    records = df.to_dict("records")

    data = {
        "ts_code": ts_code,
        "start_date": start_date,
        "end_date": end_date,
        "data": records,
        "count": len(records),
        "timestamp": time.time(),
    }
    _set_cache(cache_key, data)
    return data


@tushare_tools.tool()
def get_weekly_price(ts_code: str, start_date: str = "", end_date: str = "") -> dict:
    """
    Get weekly price data for a stock (Tushare API: weekly).

    Args:
        ts_code: Tushare stock code (e.g., "600519.SH")
        start_date: Start date in YYYYMMDD format
        end_date: End date in YYYYMMDD format

    Returns:
        dict: Weekly OHLCV data
    """
    cache_key = f"weekly_{ts_code}_{start_date}_{end_date}"
    cached = _get_cache(cache_key)
    if cached:
        return cached

    if not start_date:
        start_date = (pd.Timestamp.now() - pd.Timedelta(days=365)).strftime("%Y%m%d")
    if not end_date:
        end_date = pd.Timestamp.now().strftime("%Y%m%d")

    result = _call_tushare(
        "weekly",
        params={"ts_code": ts_code, "start_date": start_date, "end_date": end_date},
        fields="ts_code,trade_date,open,high,low,close,vol",
    )

    if "error" in result:
        return result

    df = result["data"]
    records = df.to_dict("records")

    data = {
        "ts_code": ts_code,
        "period": "weekly",
        "data": records,
        "count": len(records),
        "timestamp": time.time(),
    }
    _set_cache(cache_key, data)
    return data


@tushare_tools.tool()
def get_realtime_quote(ts_code: str) -> dict:
    """
    Get realtime quote for a stock (Tushare API:实时行情).

    Args:
        ts_code: Tushare stock code (e.g., "600519.SH")

    Returns:
        dict: Current price, change %, volume, etc.
    """
    cache_key = f"realtime_{ts_code}"
    cached = _get_cache(cache_key)
    if cached:
        return cached

    result = _call_tushare(
        "quotes",
        params={"ts_code": ts_code},
        fields="ts_code,name,open,high,low,close,pre_close,change,pct_chg,vol,amount",
    )

    if "error" in result:
        return result

    df = result["data"]
    if df.empty:
        return {"error": f"No data for {ts_code}", "ts_code": ts_code}

    record = df.iloc[0].to_dict()

    data = {
        "ts_code": ts_code,
        "name": record.get("name"),
        "open": record.get("open"),
        "high": record.get("high"),
        "low": record.get("low"),
        "close": record.get("close"),
        "pre_close": record.get("pre_close"),
        "change": record.get("change"),
        "pct_chg": record.get("pct_chg"),
        "vol": record.get("vol"),
        "amount": record.get("amount"),
        "timestamp": time.time(),
    }
    _set_cache(cache_key, data)
    return data


@tushare_tools.tool()
def get_index_daily(index_code: str, start_date: str = "", end_date: str = "") -> dict:
    """
    Get index daily K-line data (Tushare API: index_daily).

    Args:
        index_code: Index code (e.g., "000300.SH" for CSI 300, "000001.SH" for Shanghai)
        start_date: Start date in YYYYMMDD format
        end_date: End date in YYYYMMDD format

    Returns:
        dict: Index OHLCV data
    """
    cache_key = f"index_{index_code}_{start_date}_{end_date}"
    cached = _get_cache(cache_key)
    if cached:
        return cached

    # Convert common index codes to Tushare format
    if index_code in ["000300", "399300"]:
        index_code = "000300.SH"
    elif index_code in ["000001", "sh000001"]:
        index_code = "000001.SH"
    elif index_code in ["399001", "sz399001"]:
        index_code = "399001.SZ"

    if not start_date:
        start_date = (pd.Timestamp.now() - pd.Timedelta(days=365)).strftime("%Y%m%d")
    if not end_date:
        end_date = pd.Timestamp.now().strftime("%Y%m%d")

    result = _call_tushare(
        "index_daily",
        params={"ts_code": index_code, "start_date": start_date, "end_date": end_date},
        fields="ts_code,trade_date,open,high,low,close,vol,amount",
    )

    if "error" in result:
        return result

    df = result["data"]
    records = df.to_dict("records")

    data = {
        "index_code": index_code,
        "data": records,
        "count": len(records),
        "timestamp": time.time(),
    }
    _set_cache(cache_key, data)
    return data


# =====================
# Fundamental Data APIs
# =====================

@tushare_tools.tool()
def get_financial_indicator(ts_code: str) -> dict:
    """
    Get financial indicators for a stock (Tushare API: fina_indicator).

    Includes: PE, PB, ROE, gross margin, etc.

    Args:
        ts_code: Tushare stock code (e.g., "600519.SH")

    Returns:
        dict: Financial indicators
    """
    cache_key = f"financial_{ts_code}"
    cached = _get_cache(cache_key)
    if cached:
        return cached

    result = _call_tushare(
        "fina_indicator",
        params={"ts_code": ts_code, "period_type": "Q"},
        fields="ts_code,trade_date,pe,pb,roe,gross_profit_margin,net_profit_margin,debt_to_assets",
    )

    if "error" in result:
        return result

    df = result["data"]
    records = df.head(16).to_dict("records")  # Last 16 quarters

    data = {
        "ts_code": ts_code,
        "data": records,
        "count": len(records),
        "timestamp": time.time(),
    }
    _set_cache(cache_key, data)
    return data


@tushare_tools.tool()
def get_income_statement(ts_code: str, period: str = "") -> dict:
    """
    Get income statement (P&L) for a stock (Tushare API: income).

    Args:
        ts_code: Tushare stock code (e.g., "600519.SH")
        period: Reporting period in YYYYMMDD format (e.g., "20250331" for Q1 2025)

    Returns:
        dict: Income statement data
    """
    cache_key = f"income_{ts_code}_{period}"
    cached = _get_cache(cache_key)
    if cached:
        return cached

    params = {"ts_code": ts_code}
    if period:
        params["period"] = period

    result = _call_tushare(
        "income",
        params=params,
        fields="ts_code,report_date,total_revenue,revenue,cost,gross_profit,operate_profit,net_profit",
    )

    if "error" in result:
        return result

    df = result["data"]
    records = df.head(8).to_dict("records")  # Last 8 periods

    data = {
        "ts_code": ts_code,
        "data": records,
        "count": len(records),
        "timestamp": time.time(),
    }
    _set_cache(cache_key, data)
    return data


@tushare_tools.tool()
def get_balance_sheet(ts_code: str, period: str = "") -> dict:
    """
    Get balance sheet data (Tushare API: balancesheet).

    Args:
        ts_code: Tushare stock code (e.g., "600519.SH")
        period: Reporting period in YYYYMMDD format

    Returns:
        dict: Balance sheet data
    """
    cache_key = f"balance_{ts_code}_{period}"
    cached = _get_cache(cache_key)
    if cached:
        return cached

    params = {"ts_code": ts_code}
    if period:
        params["period"] = period

    result = _call_tushare(
        "balancesheet",
        params=params,
        fields="ts_code,report_date,total_assets,total_liabilities,total_equity,fixed_assets",
    )

    if "error" in result:
        return result

    df = result["data"]
    records = df.head(8).to_dict("records")

    data = {
        "ts_code": ts_code,
        "data": records,
        "count": len(records),
        "timestamp": time.time(),
    }
    _set_cache(cache_key, data)
    return data


@tushare_tools.tool()
def get_cash_flow(ts_code: str, period: str = "") -> dict:
    """
    Get cash flow statement (Tushare API: cashflow).

    Args:
        ts_code: Tushare stock code (e.g., "600519.SH")
        period: Reporting period in YYYYMMDD format

    Returns:
        dict: Cash flow data
    """
    cache_key = f"cashflow_{ts_code}_{period}"
    cached = _get_cache(cache_key)
    if cached:
        return cached

    params = {"ts_code": ts_code}
    if period:
        params["period"] = period

    result = _call_tushare(
        "cashflow",
        params=params,
        fields="ts_code,report_date,net_operate_cashflow,net_invest_cashflow,net_finance_cashflow",
    )

    if "error" in result:
        return result

    df = result["data"]
    records = df.head(8).to_dict("records")

    data = {
        "ts_code": ts_code,
        "data": records,
        "count": len(records),
        "timestamp": time.time(),
    }
    _set_cache(cache_key, data)
    return data


# =====================
# Index & Industry APIs
# =====================

@tushare_tools.tool()
def get_index_components(index_code: str = "000300.SH") -> dict:
    """
    Get constituent stocks of an index (Tushare API: index_weight).

    Args:
        index_code: Index code (e.g., "000300.SH" for CSI 300)

    Returns:
        dict: List of constituent stocks with weight
    """
    cache_key = f"index_components_{index_code}"
    cached = _get_cache(cache_key)
    if cached:
        return cached

    result = _call_tushare(
        "index_weight",
        params={"index_code": index_code},
        fields="index_code,con_code,trade_date,weight",
    )

    if "error" in result:
        return result

    df = result["data"]
    records = df.to_dict("records")

    data = {
        "index_code": index_code,
        "data": records,
        "count": len(records),
        "timestamp": time.time(),
    }
    _set_cache(cache_key, data)
    return data


@tushare_tools.tool()
def get_industry_classification(ts_code: str) -> dict:
    """
    Get industry classification for a stock (Tushare API: stock_basic + industry).

    Args:
        ts_code: Tushare stock code (e.g., "600519.SH")

    Returns:
        dict: Industry info (SW industry, Shenwan classification)
    """
    cache_key = f"industry_{ts_code}"
    cached = _get_cache(cache_key)
    if cached:
        return cached

    # Get stock basic info including industry
    result = _call_tushare(
        "stock_basic",
        params={"ts_code": ts_code, "list_status": "L"},
        fields="ts_code,name,industry,market,list_date",
    )

    if "error" in result:
        return result

    df = result["data"]
    if df.empty:
        return {"error": f"Stock {ts_code} not found", "ts_code": ts_code}

    record = df.iloc[0].to_dict()

    data = {
        "ts_code": ts_code,
        "name": record.get("name"),
        "industry": record.get("industry"),
        "market": record.get("market"),
        "list_date": record.get("list_date"),
        "timestamp": time.time(),
    }
    _set_cache(cache_key, data)
    return data


# =====================
# Valuation & Analysis APIs
# =====================

@tushare_tools.tool()
def get_valuation_multi(stock_list: list[str], start_date: str = "", end_date: str = "") -> dict:
    """
    Get PE/PB ratios for multiple stocks over time (Tushare API: daily + basic).

    Args:
        stock_list: List of Tushare stock codes (e.g., ["600519.SH", "000858.SZ"])
        start_date: Start date in YYYYMMDD format
        end_date: End date in YYYYMMDD format

    Returns:
        dict: Valuation data for multiple stocks
    """
    cache_key = f"valuation_{','.join(stock_list)}_{start_date}_{end_date}"
    cached = _get_cache(cache_key)
    if cached:
        return cached

    if not start_date:
        start_date = (pd.Timestamp.now() - pd.Timedelta(days=30)).strftime("%Y%m%d")
    if not end_date:
        end_date = pd.Timestamp.now().strftime("%Y%m%d")

    all_records = []
    for ts_code in stock_list:
        result = _call_tushare(
            "daily",
            params={"ts_code": ts_code, "start_date": start_date, "end_date": end_date},
            fields="ts_code,trade_date,close",
        )
        if "error" not in result:
            all_records.extend(result["data"].to_dict("records"))

    data = {
        "stocks": stock_list,
        "data": all_records,
        "count": len(all_records),
        "timestamp": time.time(),
    }
    _set_cache(cache_key, data)
    return data


@tushare_tools.tool()
def get_market_top_movers(trade_date: str = "") -> dict:
    """
    Get top gainers/losers for the day (Tushare API: top_list).

    Args:
        trade_date: Trading date in YYYYMMDD format (default: today)

    Returns:
        dict: Top gainers, losers, and most active stocks
    """
    cache_key = f"top_movers_{trade_date}"
    cached = _get_cache(cache_key)
    if cached:
        return cached

    if not trade_date:
        trade_date = pd.Timestamp.now().strftime("%Y%m%d")

    result = _call_tushare(
        "top_list",
        params={"trade_date": trade_date},
        fields="trade_date,ts_code,name,close,pct_chg,vol,amount,turnover_rate",
    )

    if "error" in result:
        return result

    df = result["data"]
    records = df.to_dict("records")

    data = {
        "trade_date": trade_date,
        "data": records,
        "count": len(records),
        "timestamp": time.time(),
    }
    _set_cache(cache_key, data)
    return data


@tushare_tools.tool()
def get_stock_pledge_status(ts_code: str) -> dict:
    """
    Get stock pledge (股权质押) status (Tushare API: pledge_stat).

    Args:
        ts_code: Tushare stock code (e.g., "600519.SH")

    Returns:
        dict: Pledge ratio and status
    """
    cache_key = f"pledge_{ts_code}"
    cached = _get_cache(cache_key)
    if cached:
        return cached

    result = _call_tushare(
        "pledge_stat",
        params={"ts_code": ts_code},
        fields="ts_code,end_date,pledge_ratio,unpledged_ratio,total_pledge_ratio",
    )

    if "error" in result:
        return result

    df = result["data"]
    records = df.head(4).to_dict("records")

    data = {
        "ts_code": ts_code,
        "data": records,
        "count": len(records),
        "timestamp": time.time(),
    }
    _set_cache(cache_key, data)
    return data


# =====================
# Utility Functions
# =====================

@tushare_tools.tool()
def convert_ticker(ts_code_or_ticker: str) -> str:
    """
    Convert common stock ticker to Tushare format.

    Args:
        ts_code_or_ticker: Either Tushare format (600519.SH) or plain number (600519)

    Returns:
        str: Tushare format code
    """
    ts_code_or_ticker = ts_code_or_ticker.strip()

    # Already in Tushare format
    if "." in ts_code_or_ticker:
        return ts_code_or_ticker.upper()

    # Pure number: 6-digit A-share
    if len(ts_code_or_ticker) == 6 and ts_code_or_ticker.isdigit():
        code = ts_code_or_ticker
        if code.startswith("6") or code.startswith("000") or code.startswith("001"):
            return f"{code}.SH"
        else:
            return f"{code}.SZ"

    return ts_code_or_ticker


@tushare_tools.tool()
def check_token_status() -> dict:
    """
    Check if Tushare token is configured and valid.

    Returns:
        dict: Token status and user info
    """
    if not _TUSHARE_TOKEN:
        return {
            "status": "not_configured",
            "message": "TUSHARE_TOKEN environment variable not set",
        }

    # Try a simple API call to verify token
    result = _call_tushare(
        "trade_cal",
        params={"exchange": "SSE", "start_date": "20250601", "end_date": "20250601"},
        fields="exchange,cal_date,is_open",
    )

    if "error" in result:
        return {"status": "invalid", "message": result["error"], "token_set": True}

    return {"status": "valid", "message": "Token is configured and working", "token_set": True}