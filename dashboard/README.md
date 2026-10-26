# Quant Command Center

Evidence-first paper-research dashboard for the crypto strategy lab.

## Safety invariants

- `REAL ORDERS OFF`
- No private exchange credentials are used.
- Live market data is public NDAX data.
- Only completed 4H candles are eligible for signal generation. NDAX history rows whose candle end time is later than `now` are excluded.
- Paper decisions are persisted separately in `public.quant_paper_journal`.
- A strategy is not promoted from research unless it survives stressed rolling out-of-sample validation and adds a credible edge/diversification benefit.

## Current benchmark

- Strategy: BTC/ETH EMA50/150 4H long-only
- Allocation: 45% BTC / 5% ETH / 50% cash
- Status: `PARTIALLY_VERIFIED`
- Forward paper: no closed trades yet at the time this dashboard was introduced.

## Components

- `index.ts` — dashboard and JSON API router
- `live.ts` — NDAX completed-candle signal and Level1 microstructure feed
- `research.ts` — evidence-backed research state/ranking
- `page.ts` — responsive dashboard UI
- Supabase Edge Function: `quant-command-center`
- Paper journal Edge Function: `quant-paper-journal`
- Paper journal schedule: every two hours; duplicates are ignored by a database uniqueness constraint

## Public staging URL

`https://ksjbxxqyihjjrexwgcrr.supabase.co/functions/v1/quant-command-center`

This is a research console, not a claim of live profitability.
