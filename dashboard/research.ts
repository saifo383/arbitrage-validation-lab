export function researchSnapshot() {
  return {
    mode: "PAPER_ONLY",
    real_orders: false,
    benchmark: {
      name: "BTC/ETH EMA50/150 4H",
      status: "PARTIALLY_VERIFIED",
      weights: { BTC: 45, ETH: 5, CASH: 50 },
      validation: {
        ndax_rolling_oos_base_pct: 69.65,
        ndax_rolling_oos_1_5x_cost_pct: 59.12,
        ndax_rolling_oos_2x_cost_pct: 49.26,
        positive_folds: 9,
        total_folds: 17,
        kraken_portability_1_5x_pct: 38.27,
        kraken_portability_2x_pct: 30.18,
      },
      note: "Strongest repeatable benchmark found so far; forward-paper validation is still required before live-money consideration.",
    },
    forwardPaper: {
      closed_trades: 0,
      status: "WAITING_FOR_SIGNAL_TRANSITIONS",
      note: "No forward result is invented before an actual paper entry and exit occur.",
    },
    agents: [
      { id: "SCAN", label: "Market Scan", state: "ACTIVE", purpose: "Markets, regime shifts and candidate setups" },
      { id: "FLOW", label: "Volume / Flow", state: "ACTIVE", purpose: "Abnormal volume, liquidity and order-flow changes" },
      { id: "RISK", label: "Risk Gate", state: "ACTIVE", purpose: "Reject liquidity, concentration, contract and structure risks" },
      { id: "SIZE", label: "Position Sizer", state: "PAPER", purpose: "Risk- and liquidity-aware paper sizing" },
      { id: "EXEC", label: "Execution Sim", state: "PAPER", purpose: "Bid/ask, depth, slippage, latency and fee simulation" },
      { id: "LOG", label: "Research Log", state: "ACTIVE", purpose: "Record ENTER / SKIP / WAIT / EXIT and evidence" },
    ],
    strategies: [
      { name: "BTC/ETH EMA50/150 4H", class: "Trend", status: "PARTIALLY_VERIFIED", rank: 1, reason: "Passed stressed rolling OOS and independent Kraken price-pattern portability." },
      { name: "BTC Donchian Breakout", class: "Breakout", status: "RESEARCH_ONLY", rank: 2, reason: "Adaptive walk-forward failed at 1.5x and 2x modeled costs." },
      { name: "Gold #2 BSC", class: "Elite reverse engineering", status: "NOT_ENOUGH_DATA", rank: 3, reason: "100% reported win rate / 764 trades; transaction history not yet reconstructed." },
      { name: "ZzzzzSol", class: "Elite research", status: "REJECTED", rank: 99, reason: "Edge materially depends on creator-fee/token-launch privileges." },
      { name: "Dual Momentum", class: "Cross-sectional", status: "REJECTED", rank: 99, reason: "0/24 configurations passed the 2024+2025 gate." },
      { name: "Triangular / Cross-exchange Arb", class: "Arbitrage", status: "REJECTED", rank: 99, reason: "No net-positive observed opportunities after realistic costs." },
    ],
    elite: {
      unique_wallets_screened: 171,
      win_rate_98_plus: 79,
      gold: 2,
      silver: 1,
      current_focus: "Gold #2 BSC transaction-level reconstruction",
      rule: "Creator/LP/privileged-role economics are excluded from copyable edges.",
    },
    milestones: [
      { ts: new Date().toISOString(), action: "FIX", title: "Live signals exclude NDAX candles whose end time is in the future", status: "VERIFIED_RULE" },
      { ts: "2026-10-26T17:17:48Z", action: "SYSTEM", title: "Six-agent research architecture activated", status: "ACTIVE" },
      { ts: "2026-10-26T17:02:14Z", action: "RISK", title: "Donchian removed from active paper watch", status: "RESEARCH_ONLY" },
      { ts: "2026-10-26T07:46:07Z", action: "REJECT", title: "Creator-privilege wallets excluded from copyable strategies", status: "ENFORCED" },
    ],
  };
}
