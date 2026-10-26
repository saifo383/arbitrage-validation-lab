# Independent Edge Search — 2026-10-26

## Scope
Paper-only research. Public data only. Real orders OFF.

The existing benchmark remains BTC/ETH EMA50/150 4H at nominal 45% BTC / 5% ETH / 50% cash. This file records attempts to find a genuinely independent second edge.

## Rejected families

### NDAX volatility-compression breakout
Rolling walk-forward, train-only selection, 28-bar embargo, next-4H-open execution.
- BTC: 1.5x OOS chain -25.86%; 2x -33.73%; positive 1.5x folds 3/11.
- ETH: 1.5x OOS chain -49.41%; 2x -58.28%; positive 1.5x folds 4/13.
Status: REJECTED.

### Structural mean reversion
Z-score oversold + RSI + realized-vol ceiling, no EMA trend filter, 216 configurations.
- BTC: 1.5x OOS -25.67%; 2x -33.00%; 5/14 positive 1.5x folds.
- ETH: 1.5x OOS -50.87%; 2x -55.49%; 1/11 positive 1.5x folds.
Status: REJECTED.

### Weekly/calendar timing
21 weekday/holding-period hypotheses per asset, with 1.5x cost training gate and planned Bonferroni-corrected permutation test.
- BTC: 0/21 training survivors.
- ETH: 0/21 training survivors.
Permutation/OOS stage was not run because the training gate failed.
Status: REJECTED.

### Hyperliquid cross-sectional long/short factor
Universe: BTC, ETH, SOL, XRP, DOGE, SUI, HYPE, LINK, AVAX, AAVE. Dollar-neutral 50% long / 50% short; 90 momentum/contrarian lookback-rebalance-basket configurations; conservative full liquidation/reopen cost model.
- 1.5x OOS chain: -43.23%
- 2x OOS chain: -49.05%
- Positive 1.5x folds: 1/6
- Funding was omitted, so including it would not rescue the observed failure without new evidence.
Status: REJECTED.

## Not enough data / not promotable

### Hyperliquid BTC/ETH residual pair
Nested hedge-model fitting plus parameter selection.
- Only 2/8 folds found a training candidate.
- 1.5x OOS chain +1.17%
- 2x +0.50%
- Positive selected folds 1/2
- Funding omitted.
Status: NOT ENOUGH DATA / NOT PROMOTABLE.

## Funding carry
Initial train-2024/2025 screen selected a very high positive-funding threshold on BTC and ETH, but produced zero 2026 opportunities. A rolling walk-forward was then run using actual hourly Hyperliquid funding and an assumed combined perp+spot hedge roundtrip cost of 0.49%.

BTC rolling walk-forward:
- selected candidate folds: 1/8
- folds with OOS opportunities: 1
- 1.5x chain: -0.89%
- 2x chain: -1.86%
- positive 1.5x folds: 0/1

ETH rolling walk-forward:
- selected candidate folds: 1/8
- folds with OOS opportunities: 1
- 1.5x chain: -0.25%
- 2x chain: -0.50%
- positive 1.5x folds: 0/1

These idealized screens omit basis drift, hedge tracking error, borrow/transfer costs, outage risk, depth and liquidation/margin risk. Since the idealized stressed OOS was already negative and opportunities were not repeatable, BTC/ETH funding carry is REJECTED in this formulation.

## Forward microstructure dataset
A public Hyperliquid L2 collector is now ACTIVE every 5 minutes for BTC and ETH. It stores:
- best bid/ask and spread bps
- top-1 and top-5 USD depth
- top-1/top-5 imbalance
- microprice
- first five book levels per side
- book timestamp
- `real_orders=false`

The first snapshots were successfully captured. This dataset is observation-only. No maker/order-book edge will be inferred until sufficient forward sample exists to evaluate queue/fill feasibility and adverse selection.

## Promotion rule
A second strategy remains LOCKED until it has:
1. positive stressed rolling OOS at 1.5x and 2x costs;
2. adequate sample and majority-positive folds;
3. parameter stability / no single-island result;
4. realistic execution, funding or depth economics as applicable;
5. permutation/random-timing or multiple-testing correction where applicable;
6. independent-source portability where feasible;
7. prospective forward-paper evidence;
8. demonstrable diversification or better return/drawdown versus the EMA benchmark.
