"""Research report datasource — fetch from 东方财富 reportapi.

Free, no-auth API. Rate-limited by IP.

Endpoints:
  - https://reportapi.eastmoney.com/report/list  — list reports
  - https://data.eastmoney.com/report/zw_industry.jshtml?infocode=XXX — detail page with summary

Report list fields:
  title, stockName, stockCode, orgName, orgSName, publishDate, infoCode,
  industryName, indvInduName, emRatingName, emRatingValue, ratingChange,
  predictThisYearEps, predictThisYearPe, predictNextYearEps, predictNextYearPe,
  encodeUrl, author, researcher
"""

import json
import re
import time
import logging
import urllib.parse
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

import requests

logger = logging.getLogger(__name__)

_DATA_ROOT = Path(__file__).resolve().parents[3] / "data" / "research"
_REPORT_API = "https://reportapi.eastmoney.com/report/list"
_PAGE_SIZE = 50
_MAX_PAGES = 10

_session = requests.Session()
_session.headers.update({
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Referer": "https://data.eastmoney.com/report/",
})


def fetch_reports(
    begin_time: Optional[str] = None,
    end_time: Optional[str] = None,
    industry_code: str = "",
    q_type: str = "0",
    max_pages: int = _MAX_PAGES,
) -> list[dict]:
    """Fetch research reports from 东方财富 reportapi.

    Args:
        begin_time: "YYYY-MM-DD". Default: 7 days ago.
        end_time: "YYYY-MM-DD". Default: today.
        industry_code: SW industry code filter, empty = all.
        q_type: 0=all, 1=industry.
        max_pages: Max pages (50/page).

    Returns:
        List of raw report dicts from API.
    """
    if end_time is None:
        end_time = datetime.now().strftime("%Y-%m-%d")
    if begin_time is None:
        begin_time = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")

    all_reports = []

    for page in range(1, max_pages + 1):
        params = {
            "industryCode": industry_code,
            "pageSize": str(_PAGE_SIZE),
            "industry": "",
            "rating": "",
            "ratingChange": "",
            "beginTime": begin_time,
            "endTime": end_time,
            "pageNo": str(page),
            "fields": "",
            "qType": q_type,
            "orgCode": "",
            "code": "",
            "rcode": "",
            "p": str(page),
            "pageNum": str(page),
            "pageNumber": str(page),
            "_": str(int(time.time() * 1000)),
        }

        try:
            resp = _session.get(_REPORT_API, params=params, timeout=15)
            resp.raise_for_status()
            data = resp.json()

            records = data.get("data", [])
            if not records:
                break

            all_reports.extend(records)

            total_page = data.get("TotalPage", 0)
            if page >= total_page:
                break

            if page < max_pages:
                time.sleep(1)

        except Exception as e:
            logger.error(f"Page {page} failed: {e}")
            break

    logger.info(f"Fetched {len(all_reports)} reports ({begin_time} ~ {end_time})")
    return all_reports


def fetch_report_summary(info_code: str) -> str:
    """Fetch summary text from a single report's detail page.

    Returns empty string if not found.
    """
    url = f"https://data.eastmoney.com/report/zw_industry.jshtml?infocode={info_code}"
    try:
        resp = _session.get(url, timeout=10)
        resp.raise_for_status()
        text = resp.text

        # Extract summary from meta content (the "content: 　　中国人寿..." pattern)
        matches = re.findall(r'content\s*=\s*["\'](.+?)["\']', text)
        for m in matches:
            # The summary line typically starts with Chinese full-width space (　)
            if "　　" in m and len(m) > 50:
                # Clean up the summary
                summary = m.replace("\\n", "\n").strip()
                return summary

        return ""
    except Exception as e:
        logger.warning(f"Failed to fetch summary for {info_code}: {e}")
        return ""


def normalize_report(report: dict, with_summary: bool = False) -> dict:
    """Normalize raw API report to standard schema.

    Args:
        report: Raw API dict.
        with_summary: If True, fetch detail page for full summary.
    """
    title = report.get("title", "")
    org = report.get("orgSName", "") or report.get("orgName", "")
    stock = report.get("stockName", "")
    code = report.get("stockCode", "")
    industry = report.get("indvInduName", "") or report.get("industryName", "")
    rating = report.get("emRatingName", "")
    rating_value = report.get("emRatingValue", "")
    rating_change = report.get("ratingChange", "")
    pub_date = report.get("publishDate", "")
    info_code = report.get("infoCode", "")
    author = report.get("author", "") or report.get("researcher", "")

    # Predictions
    this_eps = report.get("predictThisYearEps", "")
    this_pe = report.get("predictThisYearPe", "")
    next_eps = report.get("predictNextYearEps", "")
    next_pe = report.get("predictNextYearPe", "")

    # Build summary
    summary = ""
    if with_summary and info_code:
        time.sleep(0.5)  # rate limit for detail pages
        summary = fetch_report_summary(info_code)

    # Build searchable text blob for vector embedding
    parts = [f"【{org}】{title}"]
    if stock:
        parts.append(f"标的：{stock}({code})")
    if industry:
        parts.append(f"行业：{industry}")
    if rating:
        change_str = f"({rating_change})" if rating_change else ""
        parts.append(f"评级：{rating}{change_str}")
    if this_eps and this_pe:
        parts.append(f"今年预测EPS:{this_eps} PE:{this_pe}")
    if next_eps and next_pe:
        parts.append(f"明年预测EPS:{next_eps} PE:{next_pe}")
    if summary:
        parts.append(f"摘要：{summary}")
    if author:
        parts.append(f"作者：{author}")
    if pub_date:
        parts.append(f"发布时间：{pub_date[:10]}")

    text = "。".join(parts) + "。"

    return {
        "info_code": info_code,
        "title": title,
        "org_name": org,
        "stock_name": stock,
        "stock_code": code,
        "industry_name": industry,
        "rating": rating,
        "rating_value": rating_value,
        "rating_change": rating_change,
        "publish_date": pub_date,
        "predict_this_year_eps": this_eps,
        "predict_this_year_pe": this_pe,
        "predict_next_year_eps": next_eps,
        "predict_next_year_pe": next_pe,
        "summary": summary,
        "author": author,
        "text": text,
        "url": f"https://data.eastmoney.com/report/zw_industry.jshtml?infocode={info_code}" if info_code else "",
        "_fetched_at": datetime.now().isoformat(),
    }


def save_reports(reports: list[dict], filename: Optional[str] = None) -> Path:
    """Save normalized reports to JSON."""
    _DATA_ROOT.mkdir(parents=True, exist_ok=True)

    if filename is None:
        filename = f"reports_{datetime.now().strftime('%Y%m%d')}.json"

    out_path = _DATA_ROOT / filename
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(reports, f, ensure_ascii=False, indent=2)

    logger.info(f"Saved {len(reports)} reports to {out_path}")
    return out_path


def fetch_and_save(
    begin_time: Optional[str] = None,
    end_time: Optional[str] = None,
    max_pages: int = _MAX_PAGES,
    with_summary: bool = False,
) -> tuple[list[dict], Path]:
    """Fetch, normalize, and save reports."""
    raw = fetch_reports(begin_time=begin_time, end_time=end_time, max_pages=max_pages)
    normalized = [normalize_report(r, with_summary=with_summary) for r in raw]
    path = save_reports(normalized)
    return normalized, path


def list_saved_reports() -> list[Path]:
    """List all saved report JSON files."""
    if not _DATA_ROOT.exists():
        return []
    return sorted(_DATA_ROOT.glob("reports_*.json"))


def load_saved_reports(filename: str) -> list[dict]:
    """Load reports from a saved JSON file."""
    path = _DATA_ROOT / filename
    if not path.exists():
        return []
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def load_all_saved_reports() -> list[dict]:
    """Load all saved report JSONs, deduplicated by info_code."""
    all_reports = []
    seen_codes = set()
    for path in list_saved_reports():
        with open(path, encoding="utf-8") as f:
            batch = json.load(f)
        for r in batch:
            code = r.get("info_code", "")
            if code and code not in seen_codes:
                seen_codes.add(code)
                all_reports.append(r)
            elif not code:
                all_reports.append(r)
    return all_reports


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    reports, path = fetch_and_save(max_pages=1)
    print(f"Fetched {len(reports)} reports -> {path}")
    for r in reports[:3]:
        print(f"  [{r['industry_name']}] {r['title'][:60]} — {r['org_name']} — 评级:{r['rating']}")
