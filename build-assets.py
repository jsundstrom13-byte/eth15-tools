#!/usr/bin/env python3
"""Stamp the Kalshi 15-minute app out for other assets.

eth15m-kalshi-lead.html is the template. Each variant gets its own asset config
(feeds, Kalshi history file, price decimals, storage key) and has the asset
symbol swapped into the page text. Run after editing the ETH file:

    python3 build-assets.py
"""
import re, pathlib

HERE = pathlib.Path(__file__).parent
TEMPLATE = HERE / "eth15m-kalshi-lead.html"

ASSETS = {
    # sym: (Kalshi series, history file, Coinbase, OKX perp, Kraken perp, Kalshi perp, perp multiplier, decimals, demo price)
    "BTC": ("KXBTC15M", "btc_history.json", "BTC-USD", "BTC-USDT-SWAP", "PF_XBTUSD", "", 1, 2, 120000),
    "SOL": ("KXSOL15M", "sol_history.json", "SOL-USD", "SOL-USDT-SWAP", "PF_SOLUSD", "", 1, 4, 120.5),
    "XRP": ("KXXRP15M", "xrp_history.json", "XRP-USD", "XRP-USDT-SWAP", "PF_XRPUSD", "", 1, 4, 1.5),
}

CONFIG_RE = re.compile(r"/\* ASSET-CONFIG \*/ var A = \{.*?\}; /\* /ASSET-CONFIG \*/")


def build(sym, spec):
    series, hist, cb, okx, krf, kx, mult, dp, demo = spec
    src = TEMPLATE.read_text(encoding="utf-8")
    m = CONFIG_RE.search(src)
    assert m, "config block not found"
    cfg = ('/* ASSET-CONFIG */ var A = {sym: "%s", series: "%s", hist: "%s", cb: "%s", okx: "%s", krf: "%s", '
           'kxPerp: "%s", kxMult: %d, dp: %d, demo: %s, key: "%s15kl"}; /* /ASSET-CONFIG */'
           % (sym, series, hist, cb, okx, krf, kx, mult, dp, demo, sym.lower()))
    head, tail = src[:m.start()], src[m.end():]
    # The whole-word ETH in page text becomes the asset symbol; feed identifiers live only in the config block.
    head = re.sub(r"\bETH\b", sym, head)
    tail = re.sub(r"\bETH\b", sym, tail)
    tail = tail.replace("Ethereum", {"BTC": "Bitcoin", "SOL": "Solana", "XRP": "XRP"}[sym])
    out = head + cfg + tail
    if not kx:
        # No Kalshi perp for this asset: drop the proxy option and field from the picker.
        out = re.sub(r'\s*<option value="kx">[^<]*</option>', "", out)
    path = HERE / ("%s15m-kalshi-lead.html" % sym.lower())
    path.write_text(out, encoding="utf-8")
    return path


if __name__ == "__main__":
    for sym, spec in ASSETS.items():
        print("wrote", build(sym, spec).name)
