import "jsr:@supabase/functions-js/edge-runtime.d.ts";
import { getLiveState } from "./live.ts";
import { researchSnapshot } from "./research.ts";
import { PAGE } from "./page.ts";

const JSON_HEADERS = {
  "content-type": "application/json; charset=utf-8",
  "cache-control": "no-store",
  "access-control-allow-origin": "*",
  "x-content-type-options": "nosniff",
};

const HTML_HEADERS = {
  "content-type": "text/html; charset=utf-8",
  "cache-control": "no-store",
  "x-content-type-options": "nosniff",
  "referrer-policy": "no-referrer",
  "content-security-policy": "default-src 'self'; style-src 'unsafe-inline'; script-src 'unsafe-inline'; connect-src 'self'; img-src 'self' data:; frame-ancestors 'none'",
};

Deno.serve(async (req) => {
  if (req.method === "OPTIONS") return new Response(null, { status: 204, headers: JSON_HEADERS });
  const url = new URL(req.url);

  if (url.searchParams.get("api") === "1") {
    let live: unknown = null;
    let live_error: string | null = null;
    try {
      live = await getLiveState();
    } catch (error) {
      live_error = String(error);
    }

    return new Response(
      JSON.stringify({
        generated_at: new Date().toISOString(),
        research: researchSnapshot(),
        live,
        live_error,
      }),
      { headers: JSON_HEADERS },
    );
  }

  return new Response(PAGE, { headers: HTML_HEADERS });
});
