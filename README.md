# ETH 15m Tools

Two single-file web apps for the 15-minute Ethereum Up/Down markets:

- `eth15m-kalshi-lead.html` (Kalshi): settlement probability, target throttle, perp lead measured live.
- `xrp15m-kalshi-lead.html`, `sol15m-kalshi-lead.html`, `btc15m-kalshi-lead.html`: the same Kalshi engine for XRP, SOL and BTC (CF Benchmarks index, 60-second settlement average, OKX / Kraken / Coinbase feeds). These are generated from the ETH file by `python3 build-assets.py`; edit the ETH file, run the script, commit all four.
- `eth15m-fair-value.html` (Polymarket): probability against the order book, live scorecard.
- `index.html`: launcher page that links to both.

They need no build step, account or key. Each page connects to the public feeds from the browser it runs in.

## Run on your computer

    python serve.py

Opens http://localhost:8000/ and prints the address for an iPad or phone on the same Wi-Fi. Leave the window open; Ctrl+C stops it. Windows may ask to allow Python through the firewall the first time.

## Put it online (works from anywhere, no computer needed)

Either of these hosts static files for free:

- **GitHub Pages:** create a repository, upload this folder, then Settings -> Pages -> Deploy from branch (main, root). The app appears at `https://<you>.github.io/<repo>/`.
- **Netlify Drop:** drag this folder onto https://app.netlify.com/drop. The app appears at the address it gives you.

The files hold no personal data or keys, but anyone with the address can open them.

## Install on an iPad

Open the address in Safari, tap Share, then Add to Home Screen. Do this on the launcher for one icon, or on each tool for its own icon (ETH Kalshi, ETH Poly). iPadOS pauses a page that is off screen or locked, so keep the tool visible and set Auto-Lock to Never while trading.

## Kalshi perp and index feed (optional)

Kalshi's API refuses browser pages, so the Kalshi feed needs a tiny proxy you host. `kalshi-proxy.js` is a Cloudflare Worker that forwards read-only GET requests and adds the cross-origin header:

1. Sign in at dash.cloudflare.com (free), open Workers & Pages, create a Worker, paste `kalshi-proxy.js`, deploy.
2. Copy the worker address (`https://<name>.<you>.workers.dev`) into the "Kalshi proxy" box on the Kalshi page. It is remembered in that browser.
3. Pick "Kalshi ETH perp" in the perp feed list. The page then reads the perp's bid and ask and Kalshi's own index value once a second.
