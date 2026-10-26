# Current Paper-Trading Benchmark — 2026-10-26

## Status
**PARTIALLY VERIFIED — not VERIFIED.**

This remains the strongest repeatable candidate in the research program, but future profitability is unknown. Real trading is disabled. No private exchange credentials are required or used.

## Benchmark
- Venue for primary historical/live paper validation: NDAX public market data
- Timeframe: 4-hour completed candles only
- Signal: EMA(50) / EMA(150), long-only
- Entry: EMA50 > EMA150 on the last completed 4h candle; execution on the next tradable bar
- Exit: EMA50 < EMA150 on the last completed 4h candle
- Nominal weights: BTC/CAD 45%, ETH/CAD 5%, Cash 50%
- Allocator: `LOCKED_BENCHMARK`
- Real orders: OFF

## Strongest robustness evidence
### Strict rolling OOS — fixed benchmark
- Base chained OOS: **+69.65%**
- 1.5x-cost chained OOS: **+59.12%**
- 2x-cost chained OOS: **+49.26%**
- Positive folds: **9 / 17**

A training-selected adaptive-weight version performed materially worse than fixed 45/5/50, which is evidence against continuous weight optimization.

### Cross-venue portability
Kraken public BTC/ETH reference data, same EMA logic. Portability proxy only, not an executable Kraken fee model.
- 1.5x fold chain: **+38.27%**
- 2x fold chain: **+30.18%**

## Timing-specificity test — FAILED TO PROVE
Corrected candle policy: only `candle_end <= invocation time`.

Retrospective circular-shift nulls:
- Independent BTC/ETH shifts: **p = 0.1394**
- Common portfolio shift: **p = 0.1355**
- Promotion requirement: both p-values < 0.05

**Timing specificity is not statistically established by these tests.** This does not erase rolling-OOS evidence, but prevents an upgrade to VERIFIED.

## Moving-block bootstrap — partial support, material tail risk
300 simulations, 42-bar (7-day) moving blocks, 1.5x costs:
- Probability terminal-positive: **90.0%**
- Terminal p05: **-16.28%**
- Median: **+68.42%**
- p95: **+267.13%**
- Median max DD: **24.93%**
- p95 max DD: **45.08%**
- Worst simulated max DD: **63.59%**

This is retrospective resampling, not a forecast.

## Tail / execution stress
48 scenarios combined:
- cost multipliers: 1x / 1.5x / 2x / 3x
- execution delay: 0 / 1 / 2 four-hour bars
- extra adverse transition shock: 0 / 25 / 50 / 100 bps

Results:
- **46 / 48 scenarios remained positive** over the historical span
- reference 1.5x-cost / no-delay / no-extra-shock: **+72.35%**
- 2x costs + 2-bar delay + 100 bps adverse transition shock: **+2.04%**
- severe 3x costs + 2-bar delay + 100 bps shock: **-8.21%**
- worst observed scenario: **-8.21%**

Interpretation: the benchmark is tolerant of substantial modeled execution degradation, but sufficiently severe combined friction and delay can destroy the edge. Component-sleeve drawdowns under these severe scenarios were large, so this is not evidence of low tail risk.

## Regime attribution — observational only
Ex-ante labels use prior completed-bar EMA state, 30-bar realized-volatility percentile and EMA-gap structure. Costs use the 1.5x NDAX proxy.

Historical attribution:
- `RISK_ON_TREND`: **+76.88%** compound contribution across 3,870 bars
- `MIXED`: **+19.97%** across 1,296 bars
- `RISK_OFF_TREND`: **0.00%** because the long-only sleeves were in cash
- `VOL:HIGH_VOL`: **+63.01%**
- `VOL:MID_VOL`: **+8.64%**
- `VOL:LOW_VOL`: **+19.83%**
- `STRUCT:TRANSITIONAL`: **+64.18%**
- `STRUCT:STRONG_TREND`: **+35.79%**
- `STRUCT:CHOPPY`: **-4.81%**

This is descriptive, not causal. The regime layer cannot alter allocation until a separate train/OOS plus forward-paper test proves improvement.

## Current live paper state
Latest verified completed 4h state:
- BTC: **CASH**
- ETH: **CASH**
- Quant Intelligence: `RISK_OFF_TREND / TRANSITIONAL / LOW_VOL`
- Deployable under current signals: BTC 0%, ETH 0%, Cash 100%
- Forward research equity: 68 CAD normalized
- Closed forward trades: 0
- Open forward trades: 0
- Win rate / profit factor / expectancy: N/A
- Real orders: false

## Independent strategy search — latest results
### Volatility-compression breakout
**REJECTED.** Strict rolling walk-forward, completed bars, training-only selection, 28-bar embargo.

BTC:
- 1.5x OOS chain: **-25.86%**
- 2x OOS chain: **-33.73%**
- Positive 1.5x folds: **3 / 11**

ETH:
- 1.5x OOS chain: **-49.41%**
- 2x OOS chain: **-58.28%**
- Positive 1.5x folds: **4 / 13**

### Structural mean reversion — no EMA trend filter
**REJECTED.** Z-score oversold + RSI + realized-vol ceiling, 216 configurations, rolling train/OOS.

BTC:
- 1.5x OOS chain: **-25.67%**
- 2x OOS chain: **-33.00%**
- Positive 1.5x folds: **5 / 14**

ETH:
- 1.5x OOS chain: **-50.87%**
- 2x OOS chain: **-55.49%**
- Positive 1.5x folds: **1 / 11**

### Hyperliquid BTC/ETH market-neutral residual pair
**NOT ENOUGH DATA / NOT PROMOTABLE.**

Nested design:
- first 60% of each training window fits the hedge model
- last 40% selects parameters at 1.5x costs
- full pre-test window re-fits beta
- next-4h-open execution
- 48 parameter combinations

Available history produced only 8 OOS folds; 6/8 had no train candidate passing the gate. Of the two selected folds, only one produced an actual positive OOS cycle:
- chained 1.5x OOS: **+1.17%**
- chained 2x OOS: **+0.50%**
- positive folds: **1 / 2**
- funding was **not included**

Therefore it is not a second strategy. It would still require funding, depth, margin/liquidation stress, parameter stability, permutation/timing tests and forward paper even if the sample improved.

## Other strategy status
### BTC Donchian breakout
**RESEARCH ONLY.** Later stressed adaptive rolling walk-forward overrides earlier favorable dense-grid evidence:
- Base chain: +5.36%
- 1.5x chain: **-5.43%**
- 2x chain: **-15.11%**
- Positive folds: 4 / 10

### Hyperliquid short-basket hypothesis
**REJECTED.**
- 144 configurations
- 1.5x training survivors: **0**
- 2026 survivors positive at 1.5x and 2x: **0**
- Funding was not included, so it failed before adding funding drag

### Hyperliquid elite-trader 95–100% fill-level screen
**NOT CONFIRMED at trade-cycle level.**
Five wallets passed the initial closing-fill screen, but exact position-cycle reconstruction found:
- two wallets: 0 exact cycles in truncated samples
- one: 3 exact cycles, 3 wins — insufficient
- one: 1 exact cycle, 1 win — insufficient
- one: 3 exact cycles, 2 wins / 1 loss = **66.7%**

Fill-level win rate is not accepted as trade-cycle win rate.

### Binance Web3 Gold #2 BSC
**NOT ENOUGH DATA.** Public sampled watcher active; no transaction events captured yet. No strategy inferred without transaction-level evidence.

### ZzzzzSol
**REJECTED as copyable.** Apparent edge materially involved creator-fee / token-launch privileges unavailable to an ordinary external trader.

### Other rejected paths
- Dual momentum: 0/24 strict training survivors
- Long-horizon trend: insufficient stability
- Binance triangular arbitrage: no net-positive observed edge after realistic costs
- Binance/Kraken taker arbitrage: discrepancies did not survive modeled costs
- XRP dense mean-reversion grid: rejected under strict holdout/cost gate

## Security / execution controls
- Real trading remains OFF
- Paper fills use observed ask on entry and observed bid on exit plus 0.20% fee/side
- Paper fill is blocked when observed Level-1 depth is insufficient
- Internal quant SECURITY DEFINER RPCs restricted to `service_role`
- Research tables use RLS and service-managed writes

## Remaining gates before any higher status
1. Prospective forward-paper trades across real future signal transitions
2. Enough closed forward trades for expectancy, win rate, DD and execution-quality estimates
3. Multiple-testing correction / deflated-Sharpe or equivalent family-level correction
4. Missed-fill and deeper-book impact stress beyond Level1
5. Regime-conditioned train/OOS test before any regime-based allocation change
6. A second independent strategy that survives stressed rolling OOS, portability and forward paper

## Final judgment
EMA50/150 45/5/50 remains the benchmark because it has the strongest combined rolling-OOS, cost-stress and cross-venue evidence. However, failed-to-prove timing specificity, bootstrap tail drawdowns, execution failure under sufficiently severe stress, zero prospective closed trades and unresolved multiple-testing risk prevent an honest upgrade to VERIFIED.

**Future profitability: UNKNOWN.**
