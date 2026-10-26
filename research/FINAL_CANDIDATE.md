# Final Paper-Trading Candidate — 2026-10-26

## Status
PARTIALLY VERIFIED. This is the strongest candidate found in the research run, but it is **not verified profitable in forward live trading** and **real trading remains disabled**.

## Candidate
- Venue used for historical/live validation: NDAX public market data
- Timeframe: 4-hour candles
- Signal: EMA(50) / EMA(150), long-only
- Entry: EMA50 > EMA150 on the last completed 4h candle; execute model at the next 4h open
- Exit: EMA50 < EMA150 on the last completed 4h candle; execute model at the next 4h open
- Stress-selected portfolio weights:
  - BTC/CAD: 45%
  - ETH/CAD: 5%
  - Cash: 50%
- Real orders: DISABLED
- Exchange API keys: NOT REQUIRED / NOT USED

## Cost model
NDAX fee model used: 0.20% per side. Live Level-1 sampling was used to estimate crossing-spread friction.
- BTC modeled round-trip friction: ~0.83%
- ETH modeled round-trip friction: ~0.99%
- Selection was repeated at 1.5x modeled costs.

## Selection methodology
Weights were selected using 2024 and 2025 only. Requirements:
1. Positive modeled return in both 2024 and 2025 at 1.5x modeled costs.
2. Maximum yearly modeled drawdown <= 20%.
3. Among eligible weights, choose highest stressed 2024+2025 return sum.
4. 2026 was held out from weight selection.

Selected weights at 1.5x training costs:
- 2024: +45.537%, max DD 18.49%
- 2025: +0.181%, max DD 10.21%

Held-out 2026 evaluation through 2026-10-26:
- Base modeled costs: +3.787%, max DD 8.72%
- 1.5x modeled costs: +2.464%, max DD 9.06%

Full 2024-2026-10-26 (descriptive, not independent OOS):
- Base costs: +55.778%, max DD 18.91%
- 1.5x costs: +47.657%, max DD 19.70%

## Same-weight Buy & Hold benchmark
Using the same BTC 45% / ETH 5% / Cash 50% allocation and the same cost proxy:
- Full period base: +43.107%, max DD 40.22%
- 2024: +64.605%, max DD 18.40%
- 2025: -6.093%, max DD 19.65%
- Held-out 2026: -4.804%, max DD 21.16%
- 1.5x-cost full period: +42.716%, max DD 40.17%

This benchmark supports the conclusion that the trend filter added downside control in the tested period; it does not prove future outperformance.

## Current live signal at validation time
Both sleeves are in CASH state.
- BTC/CAD: EMA50 below EMA150; last bearish cross observed 2026-10-18. Live spread observed ~0.432% during the final signal check.
- ETH/CAD: EMA50 below EMA150; last bearish cross observed 2026-10-11. Live spread observed ~0.688% during the final signal check.

At a normalized 68 CAD test balance, the 45% BTC sleeve and 5% ETH sleeve were above NDAX minimum quantity and within observed top-of-book depth at the validation snapshot. This is a point-in-time liquidity check only.

No paper entry should be created until the relevant completed 4h candle produces EMA50 > EMA150.

## Rejected approaches
- Binance triangular arbitrage: no positive net edge in live tested samples after costs.
- Binance/Kraken taker arbitrage: raw price discrepancies existed, but none remained positive after modeled fees/slippage.
- NDAX DOGE mean-reversion: historical backtest looked promising, but live spread/depth made the original cost model too optimistic.
- ATR(3x/4x) trailing-stop variants on ETH trend strategy: degraded stability and/or returns.
- ETH 4h+6h dual-confirmation: did not improve risk-adjusted performance versus the simpler 4h signal.
- BTC/ETH relative-strength rotation: zero candidates passed the stressed 2024+2025 positive-return and <=20% yearly drawdown gate.

## Forward paper monitoring
A 4-hour condition watch is configured to check completed NDAX BTC/CAD and ETH/CAD EMA50/EMA150 signals. It notifies only on signal changes and is prohibited from placing real trades.

## Evidence limitations / risks
- Backtests are not proof of future profitability.
- Strategy family, parameters and portfolio weights were researched on historical data; multiple-testing / data-mining risk remains.
- Historical NDAX bid/ask fields were not trusted for historical spread reconstruction. Costs use current live Level-1 spread sampling plus fees, with a 1.5x stress test.
- The 2026 result is historical held-out data, not a prospective forward test.
- No authenticated orders, real partial-fill behavior, real account fee statements, tax treatment, transfer/rebalancing costs, outages, or real execution latency were tested.
- Forward paper trading through future signal changes is still required before considering any real-money deployment.
