"""Paper-only NDAX trend signal checker.

No authenticated API calls. No order placement. No withdrawals.
Candidate weights: BTC/CAD 45%, ETH/CAD 5%, Cash 50%.
Signal: EMA(50) vs EMA(150) on completed 4h candles.
"""
from __future__ import annotations

import json
import urllib.request
from dataclasses import dataclass
from datetime import datetime, timezone

BASE = "https://api.ndax.io/AP"
OMS_ID = 1
INTERVAL_SECONDS = 14_400
WEIGHTS = {"BTC": 0.45, "ETH": 0.05, "CASH": 0.50}
INSTRUMENTS = {"BTC": 1, "ETH": 3}
MIN_QTY = {"BTC": 0.00001, "ETH": 0.0001}
REAL_TRADING = False


def post(path: str, payload: dict):
    req = urllib.request.Request(
        f"{BASE}/{path}",
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=15) as response:
        return json.load(response)


def ema(values: list[float], period: int) -> list[float | None]:
    out: list[float | None] = [None] * len(values)
    if len(values) < period:
        return out
    seed = sum(values[:period]) / period
    out[period - 1] = seed
    k = 2 / (period + 1)
    prev = seed
    for i in range(period, len(values)):
        prev = values[i] * k + prev * (1 - k)
        out[i] = prev
    return out


@dataclass
class AssetSignal:
    asset: str
    signal: str
    ema50: float
    ema150: float
    distance_pct: float
    bid: float
    ask: float
    spread_pct: float
    bid_depth_quote: float
    ask_depth_quote: float
    latest_candle: str


def get_signal(asset: str, instrument_id: int) -> AssetSignal:
    candles = post(
        "GetTickerHistory",
        {
            "InstrumentId": instrument_id,
            "Interval": INTERVAL_SECONDS,
            "FromDate": "2026-01-01",
            "ToDate": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
            "OMSId": OMS_ID,
        },
    )
    rows = sorted(
        [r for r in candles if float(r[3]) > 0 and float(r[4]) > 0],
        key=lambda r: int(r[0]),
    )
    closes = [float(r[4]) for r in rows]
    e50, e150 = ema(closes, 50), ema(closes, 150)
    i = len(rows) - 1
    if i < 149 or e50[i] is None or e150[i] is None:
        raise RuntimeError(f"Insufficient completed candles for {asset}")

    level = post("GetLevel1", {"OMSId": OMS_ID, "InstrumentId": instrument_id})
    bid, ask = float(level["BestBid"]), float(level["BestOffer"])
    bid_qty, ask_qty = float(level["BidQty"]), float(level["AskQty"])
    mid = (bid + ask) / 2
    return AssetSignal(
        asset=asset,
        signal="LONG" if e50[i] > e150[i] else "CASH",
        ema50=float(e50[i]),
        ema150=float(e150[i]),
        distance_pct=(float(e50[i]) / float(e150[i]) - 1) * 100,
        bid=bid,
        ask=ask,
        spread_pct=(ask - bid) / mid * 100,
        bid_depth_quote=bid * bid_qty,
        ask_depth_quote=ask * ask_qty,
        latest_candle=datetime.fromtimestamp(int(rows[i][0]) / 1000, tz=timezone.utc).isoformat(),
    )


def main() -> None:
    signals = {asset: get_signal(asset, iid) for asset, iid in INSTRUMENTS.items()}
    result = {
        "mode": "PAPER_ONLY",
        "real_trading": REAL_TRADING,
        "weights": WEIGHTS,
        "signals": {k: vars(v) for k, v in signals.items()},
        "paper_instruction": {
            asset: (f"TARGET_WEIGHT_{WEIGHTS[asset]:.0%}" if s.signal == "LONG" else "TARGET_WEIGHT_0%")
            for asset, s in signals.items()
        },
    }
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
