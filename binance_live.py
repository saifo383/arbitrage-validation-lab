"""Finite, paper-only Binance triangular-arbitrage validation scan.

Uses Binance's public market-data-only REST/WebSocket endpoints.
No API keys are read. No order endpoint is called. No real order can be sent.
"""
from __future__ import annotations

import asyncio
import json
import os
import time
import urllib.request
from collections import Counter, defaultdict
from dataclasses import dataclass
from decimal import Decimal as D
from pathlib import Path
from typing import Dict

import websockets

from arb_engine import Quote, SymbolRules, PaperArbitrageEngine

REST = "https://data-api.binance.vision"
WSS = "wss://data-stream.binance.vision:443/stream?streams="
START = D(os.getenv("PAPER_START_USDT", "68"))
FEE = D(os.getenv("TAKER_FEE_RATE", "0.001"))
SLIP = D(os.getenv("SLIPPAGE_RATE", "0.0002"))
MIN_NET_EDGE_PCT = D(os.getenv("MIN_NET_EDGE_PCT", "0.05"))
MAX_SYMBOLS = int(os.getenv("MAX_SYMBOLS", "160"))
MAX_QUOTE_AGE_MS = int(os.getenv("MAX_QUOTE_AGE_MS", "1000"))
MAX_SKEW_MS = int(os.getenv("MAX_SNAPSHOT_SKEW_MS", "250"))
RUN_SECONDS = int(os.getenv("RUN_SECONDS", "120"))
MIN_MARKETS = int(os.getenv("MIN_MARKETS", "50"))

@dataclass(frozen=True)
class Meta:
    symbol: str
    base: str
    quote: str
    rules: SymbolRules

def get_json(path: str):
    req = urllib.request.Request(REST + path, headers={"User-Agent": "arbitrage-validation-lab/1.1"})
    with urllib.request.urlopen(req, timeout=20) as response:
        return json.loads(response.read().decode())

def dec(value, default="0"):
    try:
        return D(str(value))
    except Exception:
        return D(default)

def parse_rules(symbol_info: dict) -> SymbolRules:
    step = D("0.00000001")
    min_qty = D("0")
    min_notional = D("0")
    for filt in symbol_info.get("filters", []):
        ftype = filt.get("filterType")
        if ftype == "LOT_SIZE":
            step = dec(filt.get("stepSize"), "0.00000001")
            min_qty = dec(filt.get("minQty"), "0")
        elif ftype in ("MIN_NOTIONAL", "NOTIONAL"):
            value = filt.get("minNotional")
            if value is not None:
                min_notional = dec(value, "0")
    return SymbolRules(symbol_info["symbol"], symbol_info["baseAsset"], symbol_info["quoteAsset"], step, min_qty, min_notional)

def load_universe() -> Dict[str, Meta]:
    info = get_json("/api/v3/exchangeInfo")
    tickers = get_json("/api/v3/ticker/24hr")
    volume = {ticker["symbol"]: dec(ticker.get("quoteVolume"), "0") for ticker in tickers if isinstance(ticker, dict) and "symbol" in ticker}

    all_meta: Dict[str, Meta] = {}
    for symbol_info in info.get("symbols", []):
        if symbol_info.get("status") != "TRADING":
            continue
        if symbol_info.get("isSpotTradingAllowed") is False:
            continue
        meta = Meta(symbol_info["symbol"], symbol_info["baseAsset"], symbol_info["quoteAsset"], parse_rules(symbol_info))
        all_meta[meta.symbol] = meta

    usdt = sorted((meta for meta in all_meta.values() if meta.quote == "USDT"), key=lambda meta: volume.get(meta.symbol, D("0")), reverse=True)
    assets = {"USDT", "BTC", "ETH", "BNB"} | {meta.base for meta in usdt[:55]}
    selected = [meta for meta in all_meta.values() if meta.base in assets and meta.quote in assets]
    selected = sorted(selected, key=lambda meta: volume.get(meta.symbol, D("0")), reverse=True)[:MAX_SYMBOLS]
    return {meta.symbol: meta for meta in selected}

def build_pair_index(meta: Dict[str, Meta]):
    pair = {}
    for item in meta.values():
        pair[frozenset((item.base, item.quote))] = item.symbol
    return pair

def build_cycles(meta: Dict[str, Meta]):
    pair = build_pair_index(meta)
    assets = sorted({item.base for item in meta.values()} | {item.quote for item in meta.values()})
    cycles = []
    for asset_a in assets:
        if asset_a == "USDT":
            continue
        first = pair.get(frozenset(("USDT", asset_a)))
        if not first:
            continue
        for asset_b in assets:
            if asset_b in ("USDT", asset_a):
                continue
            second = pair.get(frozenset((asset_a, asset_b)))
            third = pair.get(frozenset((asset_b, "USDT")))
            if second and third:
                cycles.append((("USDT", asset_a, asset_b, "USDT"), (first, second, third)))

    seen = set()
    unique = []
    for cycle in cycles:
        if cycle not in seen:
            seen.add(cycle)
            unique.append(cycle)
    return unique

def append_journal(obj: dict):
    with Path("paper_journal.jsonl").open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(obj, separators=(",", ":")) + "\n")

def write_summary(obj: dict):
    Path("paper_summary.json").write_text(json.dumps(obj, indent=2, sort_keys=True), encoding="utf-8")

async def run_scan():
    if START <= 0:
        raise SystemExit("PAPER_START_USDT must be positive")
    if RUN_SECONDS < 10:
        raise SystemExit("RUN_SECONDS must be at least 10")

    meta = load_universe()
    cycles = build_cycles(meta)
    if not cycles:
        raise SystemExit("No triangular cycles found in selected market universe")

    symbols = sorted({symbol for _, route_symbols in cycles for symbol in route_symbols})[:MAX_SYMBOLS]
    allowed = set(symbols)
    cycles = [cycle for cycle in cycles if all(symbol in allowed for symbol in cycle[1])]
    symbols = sorted({symbol for _, route_symbols in cycles for symbol in route_symbols})

    if len(symbols) < MIN_MARKETS:
        raise SystemExit(f"Only {len(symbols)} markets are in executable cycles; refusing to claim a {MIN_MARKETS}+ market test")

    stream_path = "/".join(symbol.lower() + "@bookTicker" for symbol in symbols)
    uri = WSS + stream_path

    quotes: Dict[str, Quote] = {}
    engine = PaperArbitrageEngine(FEE, SLIP, MAX_QUOTE_AGE_MS, MAX_SKEW_MS)
    cycle_indexes_by_symbol = defaultdict(list)
    for index, (_, route_symbols) in enumerate(cycles):
        for symbol in route_symbols:
            cycle_indexes_by_symbol[symbol].append(index)

    armed = {}
    equity = START
    peak_equity = START
    max_drawdown_pct = D("0")
    paper_executions = 0
    executable_evaluations = 0
    positive_after_cost_candidates = 0
    threshold_candidates = 0
    quote_messages = 0
    evaluation_count = 0
    reject_reasons = Counter()
    max_net_edge_pct = None
    started_wall = time.time()
    started_ms = int(started_wall * 1000)

    start_event = {
        "ts_ms": started_ms,
        "type": "SCAN_START",
        "markets": len(symbols),
        "cycles": len(cycles),
        "paper_start_usdt": str(START),
        "fee_rate_per_leg": str(FEE),
        "slippage_rate_per_leg": str(SLIP),
        "min_execution_edge_pct": str(MIN_NET_EDGE_PCT),
        "run_seconds": RUN_SECONDS,
        "rest_endpoint": REST,
        "websocket_endpoint": "data-stream.binance.vision",
        "real_orders": False,
        "api_keys_used": False,
    }
    append_journal(start_event)
    print(json.dumps(start_event), flush=True)

    async with websockets.connect(uri, ping_interval=20, ping_timeout=20, close_timeout=10, max_size=2**22) as websocket:
        while True:
            elapsed = time.time() - started_wall
            remaining = RUN_SECONDS - elapsed
            if remaining <= 0:
                break
            try:
                raw = await asyncio.wait_for(websocket.recv(), timeout=min(10, remaining))
            except asyncio.TimeoutError:
                continue

            recv_ms = int(time.time() * 1000)
            message = json.loads(raw)
            data = message.get("data", message)
            symbol = data.get("s")
            if symbol not in meta or not all(key in data for key in ("b", "B", "a", "A")):
                continue

            item = meta[symbol]
            quotes[symbol] = Quote(symbol, item.base, item.quote, dec(data["b"]), dec(data["B"]), dec(data["a"]), dec(data["A"]), recv_ms)
            quote_messages += 1

            for cycle_index in cycle_indexes_by_symbol[symbol]:
                assets, route_symbols = cycles[cycle_index]
                if not all(route_symbol in quotes for route_symbol in route_symbols):
                    continue

                route_quotes = tuple(quotes[route_symbol] for route_symbol in route_symbols)
                route_rules = tuple(meta[route_symbol].rules for route_symbol in route_symbols)
                result = engine.evaluate_cycle(equity, assets, route_quotes, route_rules, recv_ms)
                evaluation_count += 1
                key = ">".join(assets)

                if not result.executable:
                    reject_reasons[result.reject_reason or "unknown"] += 1
                    armed[key] = True
                    continue

                executable_evaluations += 1
                if max_net_edge_pct is None or result.net_return_pct > max_net_edge_pct:
                    max_net_edge_pct = result.net_return_pct
                if result.net_return_pct > 0:
                    positive_after_cost_candidates += 1

                profitable = result.net_return_pct >= MIN_NET_EDGE_PCT
                if profitable:
                    threshold_candidates += 1

                if profitable and armed.get(key, True):
                    paper_executions += 1
                    before = equity
                    equity = result.end_amount
                    peak_equity = max(peak_equity, equity)
                    if peak_equity > 0:
                        drawdown = (peak_equity - equity) / peak_equity * D("100")
                        max_drawdown_pct = max(max_drawdown_pct, drawdown)
                    armed[key] = False
                    event = {
                        "ts_ms": recv_ms,
                        "type": "PAPER_EXECUTION",
                        "path": assets,
                        "symbols": route_symbols,
                        "start_equity": str(before),
                        "end_equity": str(equity),
                        "net_pnl": str(result.net_pnl),
                        "net_return_pct": str(result.net_return_pct),
                        "gross_return_pct": str(result.gross_return_pct),
                        "fee_rate_per_leg": str(FEE),
                        "slippage_rate_per_leg": str(SLIP),
                        "trade_no": paper_executions,
                        "real_order": False,
                    }
                    append_journal(event)
                    print(json.dumps(event), flush=True)
                elif not profitable:
                    armed[key] = True

    ended_ms = int(time.time() * 1000)
    net_pnl = equity - START
    summary = {
        "status": "COMPLETED_PAPER_SCAN",
        "started_ms": started_ms,
        "ended_ms": ended_ms,
        "observed_seconds": round((ended_ms - started_ms) / 1000, 3),
        "markets": len(symbols),
        "cycles": len(cycles),
        "quote_messages": quote_messages,
        "cycle_evaluations": evaluation_count,
        "executable_evaluations": executable_evaluations,
        "positive_after_cost_candidates": positive_after_cost_candidates,
        "threshold_candidates": threshold_candidates,
        "paper_executions": paper_executions,
        "start_equity_usdt": str(START),
        "end_equity_usdt": str(equity),
        "net_pnl_usdt": str(net_pnl),
        "net_return_pct": str((equity / START - D("1")) * D("100")),
        "max_observed_net_edge_pct": str(max_net_edge_pct) if max_net_edge_pct is not None else None,
        "max_drawdown_pct": str(max_drawdown_pct),
        "reject_reasons": dict(reject_reasons),
        "fee_rate_per_leg": str(FEE),
        "slippage_rate_per_leg": str(SLIP),
        "execution_threshold_net_pct": str(MIN_NET_EDGE_PCT),
        "max_quote_age_ms": MAX_QUOTE_AGE_MS,
        "max_snapshot_skew_ms": MAX_SKEW_MS,
        "real_orders": False,
        "api_keys_used": False,
    }
    append_journal({"type": "SCAN_SUMMARY", **summary})
    write_summary(summary)
    print(json.dumps(summary), flush=True)

if __name__ == "__main__":
    asyncio.run(run_scan())
