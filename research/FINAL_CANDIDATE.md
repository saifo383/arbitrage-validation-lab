# Current Paper-Trading Benchmark — 2026-10-26

## Status
**PARTIALLY VERIFIED — not VERIFIED.**

This remains the strongest repeatable candidate in the research program, but future profitability is unknown. Real trading is disabled. No private exchange credentials are required or used.

## Benchmark
- Venue for primary historical/live paper validation: NDAX public market data
- Timeframe: 4-hour completed candles only
- Signal: EMA(50) / EMA(150), long-only
- Entry condition: EMA50 > EMA150 on the last completed 4h candle; execution model uses the next tradable bar / observed paper execution evidence
- Exit condition: EMA50 < EMA150 on the last completed 4h candle
- Nominal weights: BTC/CAD 45%, ETH/CAD 5%, Cash 50%
- Current allocator: `LOCKED_BENCHMARK`
- Real orders: OFF

## Cost model
- NDAX fee: 0.20% per side
- Historical crossing-cost proxy uses observed Level-1 spread assumptions
- BTC baseline spread proxy: ~0.4307%
- ETH baseline spread proxy: ~0.5882%
- Robustness checks include 1x, 1.5x and 2x modeled costs

## Strongest robustness evidence
### Strict rolling out-of-sample — fixed benchmark
Common NDAX BTC/ETH 4h history, training 1200 bars, test 400 bars, embargo 28 bars.

- Base-cost chained OOS: **+69.65%**
- 1.5x-cost chained OOS: **+59.12%**
- 2x-cost chained OOS: **+49.26%**
- Positive folds: **9 / 17**

A training-selected adaptive-weight version performed materially worse than the fixed 45/5/50 benchmark, which is evidence against relying on continuous weight optimization.

### Cross-venue price-pattern portability
Kraken public BTC/ETH reference data, same EMA50/150 portfolio logic. This is a portability proxy, not a Kraken executable fee model.

- 1.5x-cost fold chain: **+38.27%**
- 2x-cost fold chain: **+30.18%**

This supports cross-venue pattern portability, but does not prove executable Kraken profitability.

## Timing-specificity test — FAILED TO PROVE
A retrospective circular-shift null test was run after correcting the candle policy to include only rows with `candle_end <= invocation time`.

Model:
- fixed 45% BTC / 5% ETH / 50% cash
- next-bar execution
- 1.5x NDAX cost proxy
- actual descriptive return over the test span: +71.01%
- actual max drawdown: 20.83%

Two null models were tested:

1. Independent BTC and ETH circular signal shifts:
   - 250 simulations
   - empirical one-sided **p = 0.1394**

2. Common portfolio circular shift preserving cross-asset timing relationship:
   - 250 simulations
   - empirical one-sided **p = 0.1355**

Promotion rule required both p-values < 0.05.

**Result: timing specificity is NOT established by this test.**

This does not erase the rolling-OOS results, but it is a material limitation and is one reason the strategy remains PARTIALLY VERIFIED.

## Moving-block bootstrap — partial support, material tail risk
Retrospective moving-block bootstrap of realized portfolio log returns:
- 300 simulations
- 42-bar blocks = 7 days of 4h bars
- 1.5x cost model

Results:
- Probability terminal return > 0: **90.0%**
- Terminal return p05: **-16.28%**
- Median: **+68.42%**
- p95: **+267.13%**
- Median max drawdown: **24.93%**
- p95 max drawdown: **45.08%**
- Worst simulated max drawdown: **63.59%**

Interpretation: the historical return process is not uniformly fragile, but tail drawdown risk is materially larger than the realized 20.83% drawdown. This is a retrospective resampling diagnostic, not a forecast or independent holdout.

## Current live paper state
Both BTC and ETH are currently **CASH** on the latest verified completed 4h candle.

Current Quant Intelligence classification:
- Primary regime: `RISK_OFF_TREND`
- Structure: `TRANSITIONAL`
- Volatility: `LOW_VOL`
- Allocator: `LOCKED_BENCHMARK`
- Deployable weights under current signals: BTC 0%, ETH 0%, Cash 100%

The regime layer is observational only. It cannot override validated benchmark weights until stressed OOS plus prospective forward-paper evidence demonstrates an improvement.

Forward paper account is normalized to 68 CAD research capital only:
- Equity: 68 CAD
- Closed forward trades: 0
- Open forward trades: 0
- Real orders: false

Therefore forward win rate, profit factor and expectancy remain N/A rather than being inferred from backtests.

## Other strategy status
### BTC Donchian breakout
**RESEARCH ONLY.**

Later stressed adaptive rolling walk-forward overrode earlier favorable dense-grid evidence:
- Base chain: +5.36%
- 1.5x chain: **-5.43%**
- 2x chain: **-15.11%**
- Positive folds: 4 / 10

Do not promote Donchian based on older research notes.

### Hyperliquid short-basket hypothesis
**REJECTED.**
- 144 parameter configurations screened
- Training survivors at 1.5x costs: **0**
- 2026 survivors positive at both 1.5x and 2x: **0**
- Funding was not included, so failure occurred even before adding that extra cost/risk dimension

### Hyperliquid elite-trader 95–100% fill-level screen
**NOT CONFIRMED at completed trade-cycle level.**

Five top-100 wallets passed the initial closing-fill screen, but independent position-cycle reconstruction found:
- two wallets: 0 exact reconstructable cycles in truncated samples
- one wallet: 3 exact cycles, 3 wins — insufficient sample
- one wallet: 1 exact cycle, 1 win — insufficient sample
- one wallet: 3 exact cycles, 2 wins / 1 loss = 66.7%

Conclusion: fill-level win rate must not be treated as trade-cycle win rate.

### Binance Web3 Gold #2 BSC
**NOT ENOUGH DATA.**
A public sampled watcher is active, but no transaction events have yet been captured in the sampled windows. No strategy is inferred until transaction-level evidence exists.

### ZzzzzSol
**REJECTED as a copyable trading strategy.**
Its apparent edge materially involved creator-fee / token-launch privileges unavailable to an ordinary external trader.

### Other rejected paths
- Dual momentum: 0/24 strict training survivors
- Long-horizon trend variants: insufficient stability
- Binance triangular arbitrage: no net-positive observed edge after realistic costs
- Binance/Kraken taker arbitrage: raw discrepancies did not survive modeled fees/slippage
- XRP dense mean-reversion grid: rejected under strict holdout/cost gate

## Security and execution controls
- Real trading remains OFF
- Paper fills use observed ask on entry and observed bid on exit plus 0.20% fee/side
- A paper fill is blocked when observed Level-1 depth is insufficient
- Quant internal SECURITY DEFINER RPCs are restricted to `service_role`; anon/authenticated direct execution is revoked
- Regime snapshots and paper research tables use RLS and are service-managed

## What is still required before any higher status
1. Prospective forward-paper trades across actual future signal transitions
2. Enough closed forward trades to estimate expectancy, win rate, drawdown and execution quality
3. Multiple-testing correction / deflated-Sharpe or equivalent family-level correction
4. More execution-tail stress: spread spikes, gaps, delayed fills, missed fills and deeper-book impact
5. Regime attribution based on sufficient historical and forward sample, without allowing regime labels to overfit allocation
6. A second independent strategy that survives stressed rolling OOS and forward-paper validation and adds diversification

## Final judgment
The EMA portfolio is the current benchmark because it has the strongest combined rolling-OOS, cost-stress and cross-venue evidence. However, the failed-to-prove random-timing gate, bootstrap tail drawdowns, zero forward closed trades, and multiple-testing risk prevent any honest upgrade to VERIFIED.

**Future profitability: UNKNOWN.**
