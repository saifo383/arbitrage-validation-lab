type Candle = { t: number; c: number };

const n = (x: unknown) => {
  const y = Number(x);
  return Number.isFinite(y) ? y : 0;
};

function ema(values: number[], period: number) {
  const out = new Array(values.length).fill(Number.NaN);
  if (values.length < period) return out;
  let seed = 0;
  for (let i = 0; i < period; i++) seed += values[i];
  out[period - 1] = seed / period;
  const k = 2 / (period + 1);
  for (let i = period; i < values.length; i++) out[i] = values[i] * k + out[i - 1] * (1 - k);
  return out;
}

const ymd = (d: Date) => d.toISOString().slice(0, 10);

async function history(instrumentId: number) {
  const to = new Date(Date.now() + 86_400_000);
  const from = new Date(Date.now() - 190 * 86_400_000);
  const now = Date.now();
  const response = await fetch("https://api.ndax.io/AP/GetTickerHistory", {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify({
      InstrumentId: instrumentId,
      Interval: 14_400,
      FromDate: ymd(from),
      ToDate: ymd(to),
      OMSId: 1,
    }),
  });
  if (!response.ok) throw new Error(`NDAX history ${instrumentId} HTTP ${response.status}`);
  const rows: unknown[][] = await response.json();
  return rows
    .map((x) => ({ t: n(x[0]), c: n(x[4]) }))
    .filter((x) => x.c > 0 && x.t <= now)
    .sort((a, b) => a.t - b.t) as Candle[];
}

async function level1(instrumentId: number) {
  const response = await fetch("https://api.ndax.io/AP/GetLevel1", {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify({ OMSId: 1, InstrumentId: instrumentId }),
  });
  if (!response.ok) throw new Error(`NDAX L1 ${instrumentId} HTTP ${response.status}`);
  return await response.json();
}

function signal(candles: Candle[]) {
  const closes = candles.map((x) => x.c);
  const fast = ema(closes, 50);
  const slow = ema(closes, 150);
  const i = candles.length - 1;
  if (i < 149) throw new Error("insufficient completed candles");

  let lastCross: { at: string; type: string } | null = null;
  for (let j = i; j >= 150; j--) {
    const nowLong = fast[j] > slow[j];
    const prevLong = fast[j - 1] > slow[j - 1];
    if (nowLong !== prevLong) {
      lastCross = {
        at: new Date(candles[j].t).toISOString(),
        type: nowLong ? "BULLISH_CROSS" : "BEARISH_CROSS",
      };
      break;
    }
  }

  return {
    latest_completed_candle_end: new Date(candles[i].t).toISOString(),
    close: +closes[i].toFixed(8),
    ema50: +fast[i].toFixed(8),
    ema150: +slow[i].toFixed(8),
    distance_pct: +((fast[i] / slow[i] - 1) * 100).toFixed(4),
    signal: fast[i] > slow[i] ? "LONG" : "CASH",
    last_cross: lastCross,
  };
}

function asset(symbol: string, l1: any, sig: any, weight: number, minimumQuantity: number) {
  const bid = n(l1.BestBid);
  const ask = n(l1.BestOffer);
  const bidQty = n(l1.BidQty);
  const askQty = n(l1.AskQty);
  const mid = (bid + ask) / 2;
  return {
    asset: symbol,
    weight,
    signal: sig,
    level1: {
      bid,
      ask,
      spread_pct: mid ? +(((ask - bid) / mid) * 100).toFixed(4) : 0,
      bid_depth_cad: +(bid * bidQty).toFixed(2),
      ask_depth_cad: +(ask * askQty).toFixed(2),
    },
    minimum_order: {
      minimum_quantity: minimumQuantity,
      approx_min_notional_at_ask_cad: +(minimumQuantity * ask).toFixed(4),
    },
  };
}

export async function getLiveState() {
  const [btcHistory, ethHistory, btcL1, ethL1] = await Promise.all([
    history(1),
    history(3),
    level1(1),
    level1(3),
  ]);

  return {
    status: "LIVE_PAPER_SIGNAL",
    strategy: "EMA50/150 4H long-only",
    candle_policy: "ONLY_ROWS_WITH_END_TIME_LTE_NOW",
    weights: { BTC: 0.45, ETH: 0.05, CASH: 0.5 },
    BTC: asset("BTC/CAD", btcL1, signal(btcHistory), 0.45, 0.00001),
    ETH: asset("ETH/CAD", ethL1, signal(ethHistory), 0.05, 0.0001),
    real_orders: false,
    exchange_api_keys_used: false,
  };
}
