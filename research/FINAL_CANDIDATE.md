# Final Paper-Trading Candidate — 2026-10-26

## Status
PARTIALLY VERIFIED. This is the strongest candidate found in the research run, but it is **not verified profitable in forward live trading** and **real trading remains disabled**.

## Candidate
- Venue used for historical/live validation: NDAX public market data
- Timeframe: 4-hour candles
- Signal: EMA(50) / EMA(150), long-only
- Entry: EMA50 > EMA150 on the last completed 4h candle; execute model at the next 4h open
- Exit: EMA50 < EMA150 on the last completed 4h candle; execute model at the next 4h open
- Portfolio weights selected under stressed training costs:
  - BTC/CAD: 45%
  - ETH/CAD: 5%
  - Cash: 50%
- Real orders: DISABLED
- Exchange API keys: NOT REQUIRED / NOT USED

## Cost model
NDAX fee model used: 0.20% per side. Live Level-1 sampling was used to estimate crossing-spread friction.
- BTC modeled round-trip friction: ~0.83%
- ETH modeled round-trip friction: ~0.99%
- Stress selection repeated at 1.5x modeled costs.

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

## Current live signal at validation time
Both sleeves are in CASH state.
- BTC/CAD: EMA50 below EMA150; last bearish cross observed 2026-10-18.
- ETH/CAD: EMA50 below EMA150; last bearish cross observed 2026-10-11.

No paper entry should be created until the relevant completed 4h candle produces EMA50 > EMA150.

## Rejected approaches
- Binance triangular arbitrage: no positive net edge in live tested samples after costs.
- Binance/Kraken taker arbitrage: raw price discrepancies existed, but none remained positive after modeled fees/slippage.
- NDAX DOGE mean-reversion: historical backtest looked promising, but live spread/depth made the original cost model too optimistic.
- ATR(3x/4x) trailing-stop variants on ETH trend strategy: degraded stability and/or returns.
- ETH 4h+6h dual-confirmation: did not improve risk-adjusted performance versus the simpler 4h signal.

## Evidence limitations / risks
- Backtests are not proof of future profitability.
- Strategy family and parameters were researched on historical data; multiple-testing / data-mining risk remains.
- Historical NDAX bid/ask fields were not trusted for historical spread reconstruction. Costs use current live Level-1 spread sampling plus fees, with a 1.5x stress test.
- No authenticated orders, partial-fill behavior, real account fee statements, tax treatment, transfer/rebalancing costs, outages, or real execution latency were tested.
- Forward paper trading is still required before considering any real-money deployment.
