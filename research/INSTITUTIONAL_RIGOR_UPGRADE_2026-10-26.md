# Institutional Rigor Upgrade — 2026-10-26

## Scope
Paper-only research. No private exchange credentials. No real orders.

## Research standard
Candidates are evaluated with next-bar execution, NDAX flat 0.20% per trade, observed live Level-1 spread proxies, training cost stress at 1.5x, untouched 2026 holdout, 2x cost stress, parameter-neighborhood checks, and minimum trade-count / drawdown gates.

## Five-asset institutional screen
Assets: BTC, ETH, SOL, XRP, DOGE (CAD pairs, NDAX 4h historical data from 2024-01-01 through 2026-10-26/27).

### BTC breakout candidate
Initial selected candidate from training-only screen: Donchian 100/40.
- 2024 @ 1.5x cost: +80.11%, 7 trades, max DD 26.02%
- 2025 @ 1.5x cost: +8.65%, 6 trades, max DD 14.64%
- 2026 holdout: +12.29%, 6 trades, max DD 14.44%
- 2026 @ 1.5x cost: +9.52%
- 2026 @ 2x cost: +6.82%
Initial coarse neighborhood was weak, so a dense grid was required.

### Dense BTC Donchian grid
71 parameter combinations tested around the candidate. Strict gate:
- 2024 and 2025 both positive at 1.5x modeled costs
- >=8 combined training trades
- training max DD <=30%
- 2026 positive at 1.5x and 2x costs
- >=5 2026 holdout trades

Result: 11/71 strict survivors, clustered around entry windows 90–130 4h bars and exit windows 40–50 4h bars. This argues against a single-parameter island.
Examples:
- Donchian 90/45: 2026 +17.24%; 1.5x +14.83%; 2x +12.46%
- Donchian 100/45: same 2026 profile; 2025 training +6.46%
- Donchian 100/40: 2026 +12.29%; 1.5x +9.52%; 2x +6.82%

### Timeframe robustness
Equivalent-duration breakout grids were tested on 2h and 6h data.
- 2h: 0/25 strict survivors — FAILED timeframe robustness on 2h.
- 6h: 7/18 strict survivors — PASSED on 6h.

The 6h survivors cluster around approximately 15–20 day entry lookbacks and 6–9 day exit lookbacks, consistent with the successful duration region seen on 4h.
Training-selected robust representative: Donchian 70/30 on 6h bars (about 17.5-day entry, 7.5-day exit).
- 2024 @1.5x: +66.38%, 8 trades, max DD 31.4%
- 2025 @1.5x: +6.35%, 6 trades, max DD 14.5%
- 2026 holdout: +18.17%, 5 trades, max DD 15.6%
- 2026 @1.5x: +15.74%
- 2026 @2x: +13.35%

Status: PARTIALLY VERIFIED. Strong historical/OOS/cost/parameter evidence, but 2h failure and small trade count mean forward-paper validation remains mandatory.

### XRP mean-reversion candidate
Coarse screen found RSI-trend 35 promising, but dense robustness test evaluated 135 nearby parameter combinations and produced 0 strict survivors once >=5 holdout trades and 2x-cost profitability were required.
Status: REJECTED under strict gate.

### ETH / SOL / DOGE
No candidate passed the institutional training gate in the current 4h multi-family screen under the new strict rule.
Status: no new survivor from this pass.

## Live paper state
BTC/CAD Donchian 70/30 6h is currently CASH.
- Last event: EXIT on 2026-10-08 06:00 UTC
- Latest checked close: 111,719.93 CAD
- Entry level: 120,046.82 CAD
- Distance to entry: ~7.45%
- Exit level: 110,900.32 CAD
- NDAX Level-1 spread at check: ~0.432%
- Real orders: false

## Current ranking
1. Existing BTC/ETH 4h EMA50/150 portfolio — benchmark, forward paper pending.
2. BTC/CAD Donchian duration breakout (~15–20 day entry / ~6–9 day exit), with 6h Donchian 70/30 as the current forward-paper representative — PARTIALLY VERIFIED.
3. XRP RSI-trend candidate — REJECTED after dense grid.

## Non-negotiable next gates
- Forward-paper signal execution on completed bars only.
- Monitor live spread/depth at every signal.
- Track realized paper fills, opportunity count, trade duration, MAE/MFE, net expectancy, and drawdown.
- Cross-validate the breakout concept on another accessible market data venue where practical.
- Keep real trading disabled until forward evidence is sufficient.
