#!/usr/bin/env python3
"""Collect Kalshi 15-minute market history (minute candles and trades) for study.

Runs in GitHub Actions (no browser CORS problem there) and writes data/<series>.json,
one entry per settled market: strike, result, minute candles (price, bid, ask, volume,
open interest) and the trade tape (time, price, count, taker side). Re-runs merge, so the
files grow into a dataset.

    python3 fetch-kalshi-history.py [--series KXETH15M,KXXRP15M] [--markets 120] [--trades 60]
"""
import argparse, json, os, sys, time, urllib.request, urllib.parse, pathlib

API = "https://api.elections.kalshi.com/trade-api/v2"
OUT = pathlib.Path(__file__).parent / "data"


def get(path, **params):
    url = API + path + ("?" + urllib.parse.urlencode(params) if params else "")
    for attempt in range(5):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "eth15-tools study"}), timeout=30) as r:
                return json.load(r)
        except Exception as e:  # rate limit or hiccup: back off
            if attempt == 4:
                raise
            time.sleep(1.5 * (attempt + 1))


def iso_to_ts(s):
    from datetime import datetime, timezone
    return int(datetime.strptime(s.replace("Z", "+0000"), "%Y-%m-%dT%H:%M:%S%z").timestamp())


def candles(series, ticker, open_ts, close_ts):
    j = get("/series/%s/markets/%s/candlesticks" % (series, ticker), start_ts=open_ts - 60, end_ts=close_ts + 60, period_interval=1)
    out = []
    for c in j.get("candlesticks", []):
        p, yb, ya = c.get("price", {}), c.get("yes_bid", {}), c.get("yes_ask", {})
        out.append({"t": c.get("end_period_ts"), "o": p.get("open"), "c": p.get("close"), "h": p.get("high"), "l": p.get("low"),
                    "bid": yb.get("close"), "ask": ya.get("close"), "v": c.get("volume"), "oi": c.get("open_interest")})
    return out


def trades(ticker, max_pages=6):
    rows, cursor = [], None
    for _ in range(max_pages):
        params = {"ticker": ticker, "limit": 1000}
        if cursor:
            params["cursor"] = cursor
        j = get("/markets/trades", **params)
        for t in j.get("trades", []):
            rows.append({"t": iso_to_ts(t["created_time"][:19] + "Z") if "created_time" in t else None, "p": t.get("yes_price"),
                         "n": t.get("count"), "s": t.get("taker_side")})
        cursor = j.get("cursor")
        if not cursor:
            break
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--series", default="KXETH15M,KXXRP15M,KXSOL15M,KXBTC15M")
    ap.add_argument("--markets", type=int, default=120, help="settled markets per series to look at")
    ap.add_argument("--trades", type=int, default=48, help="how many of the newest markets also get their trade tape")
    a = ap.parse_args()
    OUT.mkdir(exist_ok=True)
    for series in a.series.split(","):
        path = OUT / (series + ".json")
        have = {}
        if path.exists():
            have = {m["ticker"]: m for m in json.loads(path.read_text())}
        mk, cursor, got = [], None, 0
        while got < a.markets:
            params = {"series_ticker": series, "status": "settled", "limit": min(200, a.markets - got)}
            if cursor:
                params["cursor"] = cursor
            j = get("/markets", **params)
            ms = j.get("markets", [])
            mk += ms; got += len(ms); cursor = j.get("cursor")
            if not ms or not cursor:
                break
        added = 0
        for i, m in enumerate(mk):
            tk = m["ticker"]
            if tk in have and (have[tk].get("trades") is not None or i >= a.trades):
                continue
            open_ts, close_ts = iso_to_ts(m["open_time"][:19] + "Z"), iso_to_ts(m["close_time"][:19] + "Z")
            rec = have.get(tk) or {"ticker": tk, "open": open_ts, "close": close_ts, "strike": m.get("floor_strike"),
                                   "result": m.get("result"), "volume": m.get("volume_fp") or m.get("volume")}
            if "candles" not in rec:
                rec["candles"] = candles(series, tk, open_ts, close_ts); time.sleep(0.25)
            if i < a.trades and rec.get("trades") is None:
                rec["trades"] = trades(tk); time.sleep(0.25)
            have[tk] = rec; added += 1
        rows = sorted(have.values(), key=lambda r: r["open"])
        path.write_text(json.dumps(rows, separators=(",", ":")))
        print(series, "markets", len(rows), "updated", added, file=sys.stderr)


if __name__ == "__main__":
    main()
