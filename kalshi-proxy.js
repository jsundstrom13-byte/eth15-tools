// Cloudflare Worker: lets the ETH 15m page read Kalshi's public market data from a browser.
// Deploy: dash.cloudflare.com -> Workers & Pages -> Create -> paste this file -> Deploy.
// Then put the worker's address (https://<name>.<you>.workers.dev) in the page's "Kalshi proxy" box.
// It forwards only read-only GET requests under /trade-api/v2/ and adds the cross-origin header.
export default {
  async fetch(request) {
    const url = new URL(request.url);
    const cors = { "Access-Control-Allow-Origin": "*", "Access-Control-Allow-Methods": "GET, OPTIONS", "Access-Control-Allow-Headers": "*" };
    if (request.method === "OPTIONS") return new Response(null, { headers: cors });
    if (request.method !== "GET" || !url.pathname.startsWith("/trade-api/v2/")) return new Response("Only GET /trade-api/v2/... is allowed", { status: 403, headers: cors });
    const host = url.pathname.startsWith("/trade-api/v2/margin/") ? "https://external-api.kalshi.com" : "https://api.elections.kalshi.com";
    const upstream = host + url.pathname + url.search;
    const r = await fetch(upstream, { headers: { "Accept": "application/json" }, cf: { cacheTtl: 0 } });
    const body = await r.arrayBuffer();
    return new Response(body, { status: r.status, headers: { ...cors, "Content-Type": r.headers.get("Content-Type") || "application/json", "Cache-Control": "no-store" } });
  }
};
