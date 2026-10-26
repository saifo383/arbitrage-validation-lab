# Arbitrage Validation Lab

Evidence-oriented, **paper-only** triangular arbitrage validator.

## Safety boundary
- No API keys.
- No authenticated Binance endpoints.
- No order placement.
- No withdrawals.
- Starting balance is virtual: **68 USDT** by default.
- Zero trades and negative results are valid outcomes.

## What is tested
The engine uses executable top-of-book direction:
- base → quote: SELL at bid
- quote → base: BUY at ask

It models:
- taker fee on each of 3 legs
- configurable slippage on each leg
- LOT_SIZE / min quantity / min notional
- available top-of-book quantity
- stale quotes
- cross-symbol snapshot skew

The live scan uses Binance's public market-data-only endpoints (`data-api.binance.vision` and `data-stream.binance.vision`). It requires at least 50 markets participating in actual triangular cycles before it will label the run as a 50+ market test.

## Outputs
- `paper_journal.jsonl`: append-only scan/execution journal
- `paper_summary.json`: finite-run summary

The GitHub Actions workflow first runs deterministic unit/property validation, then performs a finite live **paper** scan and uploads the evidence files as an artifact.

A successful workflow proves that the code executed and received market data. It does **not** prove durable profitability or live-fill performance.
