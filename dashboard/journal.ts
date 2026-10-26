import "jsr:@supabase/functions-js/edge-runtime.d.ts";

const SUPABASE_URL = Deno.env.get("SUPABASE_URL")!;
const SERVICE_KEY = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!;
const DASHBOARD_FEED = `${SUPABASE_URL}/functions/v1/quant-command-center?api=1`;
const STRATEGY = "BTC/ETH EMA50/150 4H";

const restHeaders = {
  apikey: SERVICE_KEY,
  authorization: `Bearer ${SERVICE_KEY}`,
  "content-type": "application/json",
};

async function previousSignal(asset: string) {
  const q = new URL(`${SUPABASE_URL}/rest/v1/quant_paper_journal`);
  q.searchParams.set("strategy", `eq.${STRATEGY}`);
  q.searchParams.set("asset", `eq.${asset}`);
  q.searchParams.set("select", "signal,candle_end");
  q.searchParams.set("order", "candle_end.desc");
  q.searchParams.set("limit", "1");
  const r = await fetch(q, { headers: restHeaders });
  if (!r.ok) throw new Error(`journal read ${asset}: HTTP ${r.status}`);
  const rows = await r.json();
  return rows?.[0] ?? null;
}

function actionFor(previous: string | null, current: string) {
  if (!previous) return current === "LONG" ? "ENTER" : "WAIT";
  if (previous === current) return "HOLD";
  if (previous === "CASH" && current === "LONG") return "ENTER";
  if (previous === "LONG" && current === "CASH") return "EXIT";
  return "WAIT";
}

async function insertDecision(assetKey: "BTC" | "ETH", live: any) {
  const item = live[assetKey];
  const prev = await previousSignal(item.asset);
  const current = item.signal.signal;
  const payload = {
    candle_end: item.signal.latest_completed_candle_end,
    source: "NDAX",
    strategy: STRATEGY,
    asset: item.asset,
    previous_signal: prev?.signal ?? null,
    signal: current,
    action: actionFor(prev?.signal ?? null, current),
    close_price: item.signal.close,
    bid: item.level1.bid,
    ask: item.level1.ask,
    spread_pct: item.level1.spread_pct,
    ema50: item.signal.ema50,
    ema150: item.signal.ema150,
    target_weight: item.weight,
    real_orders: false,
    evidence: {
      last_cross: item.signal.last_cross,
      distance_pct: item.signal.distance_pct,
      bid_depth_cad: item.level1.bid_depth_cad,
      ask_depth_cad: item.level1.ask_depth_cad,
      candle_policy: live.candle_policy,
      exchange_api_keys_used: false,
    },
  };

  const r = await fetch(`${SUPABASE_URL}/rest/v1/quant_paper_journal?on_conflict=strategy,asset,candle_end,signal`, {
    method: "POST",
    headers: { ...restHeaders, prefer: "resolution=ignore-duplicates,return=representation" },
    body: JSON.stringify(payload),
  });
  if (!r.ok) throw new Error(`journal insert ${item.asset}: HTTP ${r.status} ${await r.text()}`);
  const rows = await r.json();
  return { asset: item.asset, action: payload.action, signal: current, inserted: rows.length > 0, candle_end: payload.candle_end };
}

async function readRecent(limit = 50) {
  const q = new URL(`${SUPABASE_URL}/rest/v1/quant_paper_journal`);
  q.searchParams.set("select", "id,observed_at,candle_end,asset,previous_signal,signal,action,close_price,bid,ask,spread_pct,ema50,ema150,target_weight,real_orders,evidence");
  q.searchParams.set("order", "candle_end.desc,asset.asc");
  q.searchParams.set("limit", String(Math.max(1, Math.min(100, limit))));
  const r = await fetch(q, { headers: restHeaders });
  if (!r.ok) throw new Error(`journal list HTTP ${r.status}`);
  return await r.json();
}

Deno.serve(async (req) => {
  try {
    const url = new URL(req.url);
    if (url.searchParams.get("read") === "1") {
      return Response.json({ status: "OK", real_orders: false, events: await readRecent(Number(url.searchParams.get("limit") || 50)) }, {
        headers: { "cache-control": "no-store", "access-control-allow-origin": "*" },
      });
    }

    const feed = await fetch(DASHBOARD_FEED, { headers: { accept: "application/json" } });
    if (!feed.ok) throw new Error(`dashboard feed HTTP ${feed.status}`);
    const data = await feed.json();
    if (!data.live || data.live_error) throw new Error(`live state unavailable: ${data.live_error || "unknown"}`);
    if (data.live.real_orders !== false) throw new Error("safety invariant violated: real_orders must be false");

    const results = [];
    for (const assetKey of ["BTC", "ETH"] as const) results.push(await insertDecision(assetKey, data.live));
    return Response.json({ status: "PAPER_JOURNAL_OK", results, real_orders: false });
  } catch (error) {
    return Response.json({ status: "PAPER_JOURNAL_ERROR", error: String(error), real_orders: false }, { status: 500 });
  }
});
