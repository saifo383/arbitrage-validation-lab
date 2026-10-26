# Current Paper-Trading Benchmark — 2026-10-26

## Status
**PARTIALLY VERIFIED — not VERIFIED.**

Research focus is now intentionally narrowed to improving the existing BTC/ETH EMA benchmark. Other strategy-family discovery, elite-wallet research, Gold #2 BSC sampling and Hyperliquid microstructure collection are paused until explicitly reopened. Real trading remains disabled.

## Benchmark
- Primary venue: NDAX public market data
- Timeframe: 4-hour completed candles only
- Signal: EMA(50) / EMA(150), long-only
- Entry: EMA50 > EMA150 on the last completed 4h candle; next tradable bar
- Exit: EMA50 < EMA150 on the last completed 4h candle
- Weights: BTC/CAD 45%, ETH/CAD 5%, Cash 50%
- Allocator: `LOCKED_BENCHMARK`
- Real orders: OFF

## Strongest robustness evidence
### Strict rolling OOS — fixed benchmark
- Base chained OOS: **+69.65%**
- 1.5x-cost chained OOS: **+59.12%**
- 2x-cost chained OOS: **+49.26%**
- Positive folds: **9 / 17**

### Cross-venue portability
Kraken public BTC/ETH reference data, same EMA logic; portability proxy only.
- 1.5x fold chain: **+38.19% to +38.27%** depending on the exact completed-candle cut
- 2x fold chain: **about +30%**

### Timing-specificity test — FAILED TO PROVE
- Independent BTC/ETH circular shifts: **p = 0.1394**
- Common portfolio shift: **p = 0.1355**

Timing specificity is not statistically established. This is a material reason the strategy remains PARTIALLY VERIFIED.

### Moving-block bootstrap
300 simulations, 42-bar / 7-day blocks, 1.5x costs:
- terminal-positive: **90.0%**
- terminal p05: **-16.28%**
- median: **+68.42%**
- p95: **+267.13%**
- median max DD: **24.93%**
- p95 max DD: **45.08%**
- worst simulated max DD: **63.59%**

### Tail / execution stress
48 scenarios across 1x/1.5x/2x/3x costs, 0/1/2-bar delays and 0/25/50/100 bps adverse transition shocks:
- **46 / 48 remained positive**
- severe 3x + 2-bar delay + 100bps shock: **-8.21%**

Interpretation: the historical edge tolerates substantial modeled degradation, but sufficiently poor execution can destroy it.

## Signal-enhancement screening — no replacement adopted
The current EMA strategy was screened against conservative modifications on the same 17 rolling OOS folds.

### Best NDAX-only candidate: 10bp entry buffer
Rule: enter only when `EMA50 > EMA150 × 1.001`; exit unchanged at `EMA50 < EMA150`.

NDAX screen:
- 1.5x OOS: **+62.51%** vs baseline **+59.12%**
- 2x OOS: **+53.00%** vs baseline **+49.26%**
- mean fold DD: **5.56%** vs **5.75%**
- transitions: **95** vs **99**

However, independent Kraken portability deteriorated:
- 1.5x: **+34.80%** vs baseline **+38.19%**
- 2x: **+26.88%** vs baseline **+30.05%**

The 10bp candidate also failed to establish timing specificity:
- independent-shift p: **0.1235**
- common-shift p: **0.1195**

Neighborhood results were mixed: 10–25bp improved NDAX to varying degrees, but none improved the baseline on Kraken. Therefore **the original EMA rule remains the benchmark**. No entry-buffer modification is adopted.

## Execution-policy upgrade — adopted for forward paper
The signal remains unchanged, but new entries now require an execution-quality gate before a paper fill is allowed.

### BTC/CAD entry gate
- historical spread p95 proxy: **0.4319%**
- max allowed entry spread: **0.64785%** = 1.5× p95
- top ask depth must be at least **5×** the intended sleeve notional

### ETH/CAD entry gate
- historical spread p95 proxy: **0.5885%**
- max allowed entry spread: **0.88275%** = 1.5× p95
- top ask depth must be at least **5×** the intended sleeve notional

### Exit policy
Spread does **not** block exits. An exit uses the observed bid and still requires enough top bid depth for the intended notional. This prevents a risk-control rule from trapping the strategy inside a position merely because the spread widened.

The upgraded Paper Engine was re-run successfully after the change:
- HTTP status: **200**
- mode: `PAPER_ONLY`
- equity: **68 CAD** normalized research capital
- BTC state: **CASH**
- ETH state: **CASH**
- open trades: **0**
- closed trades: **0**
- real orders: **false**

## Current live execution context
Latest journal snapshot used during the execution-policy upgrade:
- BTC/CAD spread: **0.6585%** — slightly above the new **0.64785%** entry limit, so a hypothetical new BTC entry at that snapshot would be blocked
- ETH/CAD spread: **0.4360%** — within the **0.88275%** entry limit

This is an execution-quality check, not a trading signal. Both assets remain CASH on the latest verified completed 4h EMA state.

## Current live paper state
- BTC: **CASH**
- ETH: **CASH**
- Deployable now: BTC 0%, ETH 0%, Cash 100%
- Forward research equity: 68 CAD normalized
- Closed forward trades: 0
- Open forward trades: 0
- Win rate / profit factor / expectancy: N/A
- Real orders: false

## Research focus from this point
Only the EMA benchmark is active for improvement work. Priority order:
1. Forward-paper evidence across real future signal transitions
2. Execution-gate performance: accepted vs blocked entries and subsequent outcomes
3. Missed-fill / spread-spike / deeper-book sensitivity
4. Conservative sizing changes only if they can be tested without fold-boundary or sleeve-accounting artifacts
5. Any signal modification must beat the original benchmark on NDAX **and** preserve independent-source portability before adoption

Other strategy families remain frozen until explicitly reopened.

## Final judgment
The original EMA50/150 45/5/50 strategy remains the strongest and most portable version. A 10bp entry buffer improved NDAX but weakened Kraken portability, so it was rejected as a replacement. The meaningful improvement adopted now is execution discipline: new entries are blocked when spread or top-book depth falls outside the validated envelope.

**Future profitability: UNKNOWN. Real trading remains OFF.**
