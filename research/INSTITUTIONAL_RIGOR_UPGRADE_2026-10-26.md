# Institutional Rigor Upgrade — 2026-10-26

## SUPERSEDED RESEARCH SNAPSHOT

This file is retained only as a record of an earlier research stage. **Do not use its Donchian ranking or PARTIALLY VERIFIED label as the current strategy status.**

The authoritative current assessment is:

- `research/FINAL_CANDIDATE.md`

## Why this snapshot was superseded

The earlier dense-grid and timeframe tests made BTC Donchian breakout look promising. A later, stricter adaptive rolling walk-forward test materially changed the conclusion:

- 10 out-of-sample folds
- Base chained return: **+5.36%**
- 1.5x-cost chained return: **-5.43%**
- 2x-cost chained return: **-15.11%**
- Positive folds: **4 / 10**

Therefore Donchian is now:

**RESEARCH_ONLY**

It is not an active paper strategy and is not ranked as a validated second edge.

## Current benchmark status

The fixed BTC/ETH EMA50/150 4h portfolio at nominal 45% BTC / 5% ETH / 50% cash remains the strongest benchmark, but only **PARTIALLY VERIFIED**.

Later evidence not present in the original version of this document includes:

- strict NDAX rolling OOS: +69.65% base, +59.12% at 1.5x costs, +49.26% at 2x costs; 9/17 positive folds
- supportive Kraken price-pattern portability
- dual random-timing null tests that **failed to establish timing specificity**: p=0.1394 and p=0.1355
- moving-block bootstrap with 90% terminal-positive simulations but p05 terminal return -16.28%, max-DD p95 45.08%, worst simulated DD 63.59%
- zero closed prospective forward-paper trades at the time of this update

## Other later research changes

- Hyperliquid short-basket: **REJECTED**, 0/144 training survivors at 1.5x costs
- Hyperliquid 95–100% fill-level elite screens: **not confirmed at exact completed trade-cycle level**
- Binance Web3 Gold #2 BSC: **NOT ENOUGH DATA**
- ZzzzzSol: **REJECTED as a copyable edge** because creator-fee / token-launch privileges materially affected the observed economics

## Safety state

- Paper research only
- Real orders: OFF
- No private exchange credentials used

See `research/FINAL_CANDIDATE.md` for the current evidence hierarchy and promotion gates.
