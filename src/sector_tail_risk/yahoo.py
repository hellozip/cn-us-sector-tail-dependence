from __future__ import annotations

import json
import time
import urllib.parse
import urllib.request
from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
from typing import Iterable

import pandas as pd


@dataclass(frozen=True)
class YahooResult:
    prices: pd.Series
    meta: dict


def _parse_date(value: str | date) -> date:
    if isinstance(value, date):
        return value
    return datetime.strptime(value, "%Y-%m-%d").date()


def _to_unix_utc(value: date) -> int:
    return int(datetime(value.year, value.month, value.day, tzinfo=timezone.utc).timestamp())


def _chart_url(symbol: str, start: date, end: date) -> str:
    # Yahoo period boundaries can be sensitive to exchange time zones. Fetch a buffered
    # window, then filter by exchange-local dates after timestamp conversion.
    period1 = _to_unix_utc(start - timedelta(days=3))
    period2 = _to_unix_utc(end + timedelta(days=3))
    encoded = urllib.parse.quote(symbol)
    return (
        f"https://query1.finance.yahoo.com/v8/finance/chart/{encoded}"
        f"?period1={period1}&period2={period2}&interval=1d"
        "&events=history&includeAdjustedClose=true"
    )


def fetch_symbol(symbol: str, start: str | date, end: str | date, timeout: int = 20) -> YahooResult:
    start_date = _parse_date(start)
    end_date = _parse_date(end)
    url = _chart_url(symbol, start_date, end_date)
    headers = {"User-Agent": "Mozilla/5.0"}
    last_error: Exception | None = None

    for attempt in range(3):
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=timeout) as response:
                payload = json.load(response)
            chart = payload.get("chart", {})
            if chart.get("error"):
                raise RuntimeError(f"Yahoo error for {symbol}: {chart['error']}")
            result = (chart.get("result") or [None])[0]
            if not result:
                raise RuntimeError(f"No Yahoo chart result for {symbol}")

            timestamps = result.get("timestamp") or []
            meta = result.get("meta", {})
            quote = (result.get("indicators", {}).get("quote") or [{}])[0]
            close = quote.get("close") or []
            adj = ((result.get("indicators", {}).get("adjclose") or [{}])[0]).get("adjclose")
            values = adj if adj else close
            if not timestamps or not values:
                raise RuntimeError(f"No price observations for {symbol}")

            timezone_name = meta.get("exchangeTimezoneName") or meta.get("timezone") or "UTC"
            dates = pd.to_datetime(timestamps, unit="s", utc=True)
            try:
                dates = dates.tz_convert(timezone_name)
            except Exception:
                dates = dates.tz_convert("UTC")
            df = pd.DataFrame(
                {
                    "date": dates.tz_localize(None).normalize(),
                    "close": values,
                }
            ).dropna()
            df = df.drop_duplicates("date", keep="last").set_index("date").sort_index()
            df = df.loc[(df.index.date >= start_date) & (df.index.date <= end_date)]
            return YahooResult(prices=df["close"].astype(float).rename(symbol), meta=meta)
        except Exception as exc:  # pragma: no cover - retries cover transient network failures.
            last_error = exc
            time.sleep(1.5 * (attempt + 1))

    raise RuntimeError(f"Failed to fetch {symbol}") from last_error


def fetch_prices(assets: pd.DataFrame, start: str | date, end: str | date) -> tuple[pd.DataFrame, pd.DataFrame]:
    series: list[pd.Series] = []
    meta_rows: list[dict] = []
    for row in assets.itertuples(index=False):
        result = fetch_symbol(row.ticker, start, end)
        prices = result.prices.rename(row.id)
        series.append(prices)
        meta = result.meta
        meta_rows.append(
            {
                "id": row.id,
                "ticker": row.ticker,
                "yahoo_symbol": meta.get("symbol"),
                "exchange": meta.get("exchangeName"),
                "currency": meta.get("currency"),
                "long_name": meta.get("longName"),
                "first_price_date": prices.index.min().date().isoformat(),
                "last_price_date": prices.index.max().date().isoformat(),
                "price_observations": int(prices.notna().sum()),
            }
        )
    prices_df = pd.concat(series, axis=1).sort_index()
    return prices_df, pd.DataFrame(meta_rows)


def missing_tickers(assets: pd.DataFrame, prices: pd.DataFrame) -> list[str]:
    return [ticker for ticker in assets["id"].tolist() if ticker not in prices.columns]
