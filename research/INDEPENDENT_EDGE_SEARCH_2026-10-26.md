# Independent Edge Search — 2026-10-26

## Scope
Paper-only research. Public data only. Real orders OFF.

The existing benchmark remains BTC/ETH EMA50/150 4H at nominal 45% BTC / 5% ETH / 50% cash. This file records attempts to find a genuinely independent second edge and to reverse-engineer elite-trader behavior without trusting fill-level leaderboard metrics.

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
21 weekday/holding-period hypotheses per asset.
- BTC: 0/21 training survivors at 1.5x costs.
- ETH: 0/21 training survivors.
Permutation/OOS stage was not run because the training gate failed.
Status: REJECTED.

### Hyperliquid cross-sectional long/short factor
Universe: BTC, ETH, SOL, XRP, DOGE, SUI, HYPE, LINK, AVAX, AAVE. Dollar-neutral 50% long / 50% short; 90 momentum/contrarian configurations; conservative full liquidation/reopen cost model.
- 1.5x OOS chain: -43.23%
- 2x OOS chain: -49.05%
- Positive 1.5x folds: 1/6
- Funding omitted; the price-only result already fails badly.
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
Rolling walk-forward uses actual hourly Hyperliquid funding, 180-day training, 60-day OOS, 24-hour embargo, train-only parameter selection at 1.5x costs and an idealized combined perp+spot hedge roundtrip cost of 0.49%.

BTC:
- selected folds 1/8; active OOS folds 1
- 1.5x chain -0.89%; 2x -1.86%; 0/1 positive

ETH:
- selected folds 1/8; active OOS folds 1
- 1.5x chain -0.25%; 2x -0.50%; 0/1 positive

SOL:
- selected folds 2/8; only 1 fold had OOS opportunities
- 1.5x chain +0.40%
- 2x chain -0.33%
- fails strict 2x repeatability gate

DOGE:
- selected folds 4/8; active OOS folds 4
- 1.5x chain -0.56%
- 2x chain -2.73%
- only 1/4 positive at 1.5x

SUI:
- selected folds 1/8
- 1.5x chain -0.12%
- 2x chain -0.85%

HYPE:
- 0/5 training survivors

These are idealized delta-hedge economics screens. Basis drift, hedge tracking, borrow/transfer costs, venue outages, depth and margin/liquidation risks are omitted. Since the strict stressed gate already fails, the current funding-carry formulation is REJECTED. XRP was not judged because a later request hit an API-rate/boot error; that technical failure is not a strategy result.

## Elite trader cycle audit
Hyperliquid leaderboard closing-fill win rate is treated as a screen only. The reconstruction now uses paginated `userFillsByTime` data, up to 10,000 fills, and counts only exact zero-position -> position -> zero-position cycles.

Five wallets that passed the initial >=95% closing-fill screen were rechecked:

- Rank 10: 10,000 fills, 0 exact cycles. NOT ENOUGH DATA for true trade-cycle win rate.
- Rank 23: 10,000 fills, 0 exact cycles. NOT ENOUGH DATA.
- Rank 25: 2,652 fills, 3 exact cycles, 3 wins / 0 losses, longest streak 3, net cycle PnL +20,614.59. Sample far too small to validate the 96.23% fill-level claim.
- Rank 40: 1,157 fills, 1 exact cycle, 1 win. Sample insufficient.
- Rank 42: 10,000 fills, 21 exact cycles, 12 wins / 9 losses = **57.14% cycle win rate**, longest winning streak 5, net cycle PnL +9,685.51. The original 98.06% fill-level screen is therefore **SCREEN_NOT_CONFIRMED** at trade-cycle level.

Conclusion: none of these five currently validates a true 95–98% trade-cycle win rate.

A persistent Top-100 cycle-audit queue has been created. A wallet can be labeled `CANDIDATE_95` only if it has at least 20 exact cycles and >=95% cycle win rate. Even then, it still requires copyability, privilege, liquidity, latency, fee and forward-paper checks before promotion.

## Forward microstructure dataset
A public Hyperliquid L2 collector is ACTIVE every 5 minutes for BTC and ETH. It stores:
- best bid/ask and spread bps
- top-1 and top-5 USD depth
- top-1/top-5 imbalance
- microprice
- first five book levels per side
- book timestamp
- `real_orders=false`

Initial snapshots were captured successfully. No maker/order-book edge will be inferred until at least 2,016 snapshots per asset (~7 days at 5-minute cadence) are available, followed by train/holdout, queue/fill uncertainty, adverse-selection and multiple-testing checks.

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
