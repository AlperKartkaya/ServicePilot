# GitHub Pages + live Jev sensor [FR-22]

- UI: https://alperkartkaya.github.io/ServicePilot/
- Sensor: https://servicepilot-jev.alperkartkaya.workers.dev
- Worker runs fixed TypeSafe questions only. It cannot forward arbitrary URLs, models or questions. RAEP and case persistence stay in the browser; this is not a shared service backend. Existing FastAPI/SQLite remains available for local use.

## Use
Open **Canlı Jev'i aç**, enter the demo access code, then create a new case. Existing historical steps and the synthetic replay stay unchanged. The code is stored only in sessionStorage; disconnect clears it. Browser storage is not a secure vault: do not use real customer data or share the demo code publicly.

The local operator code is `~/.config/servicepilot/demo-access-code` (mode 600), outside Git. It is a separate random credential, **not** the TypeSafe key. Copy locally if needed:
```sh
pbcopy < ~/.config/servicepilot/demo-access-code
```
Only minimized vehicle family/fuel/km, note, measurements, DTCs, repairs and evidence text go to TypeSafe. VIN, location, images and audit/history are not transmitted by this path. Text itself can contain sensitive information; the UI does not promise automatic redaction.

## Security / usage boundaries
- `TYPESAFE_API_KEY` and `DEMO_ACCESS_TOKEN` are Cloudflare encrypted secret bindings, never public configuration or Pages artifacts. No request-body/provider-response logging, database or analytics resources added.
- Bearer access code is required. Origin/CORS is additional browser restriction, not authentication.
- Body <=32 KiB; bounded fields and evidence catalog, fixed prompts, bounded upstream response, 15s provider timeout. Redirects are not followed (`manual`), so Authorization is not forwarded elsewhere. Invalid provider output fails closed.
- Binding permits 5 inference attempts per 60s **per Cloudflare location, approximately**. It is not a strict global/daily spending cap. Auth/health and deterministic safety do not call Jev. Trusted code holders can consume your provider credits; rotate the code if leaked.
- Designed for Workers Free limits; no subscription upgrade, paid database or paid add-on was requested/created. Cloudflare billing-subscription inspection returned 403 for the available OAuth permission; account plan/zero invoice is **not verified**. Current Worker usage model is `standard`. Cloudflare free quotas do not make Jev inference free. See [Workers limits](https://developers.cloudflare.com/workers/platform/limits/) and [rate-limit locality](https://developers.cloudflare.com/workers/runtime-apis/bindings/rate-limit/).

## Maintain
Use existing Wrangler or `npx wrangler@4.155.0` (the version used here). Run `wrangler whoami` before mutation. From repo root:
```sh
uv run python -m worker.export_contract
uv run pytest -q
node --test tests/test_frontend.mjs tests/test_worker.mjs
wrangler deploy --config worker/wrangler.toml --dry-run
wrangler deploy --config worker/wrangler.toml
```
Worker deployment is manual; Pages Actions validates both JS test suites but does not receive your Cloudflare OAuth token. API URL is public in `static/app.js`; the TypeSafe key must never be placed there.

Set/rotate secrets via stdin, never command arguments or committed files:
```sh
wrangler secret put TYPESAFE_API_KEY --config worker/wrangler.toml
wrangler secret put DEMO_ACCESS_TOKEN --config worker/wrangler.toml
```
When rotating the demo code, update the private operator file too. Reconnect clients; old tokens should fail 401. To stop live inference, remove/revoke the Worker demo access secret. Static demo and local records remain available.

## Tests
```sh
uv run --with playwright python tests/browser_jev_smoke.py
```
Requires the local static server on 127.0.0.1:5187. Routes only the sensor requests to fixtures; proves UI/error/privacy boundaries without consuming provider credits. `tests/browser_smoke.py` covers unchanged static flow. Live deployed checks are recorded separately in VALIDATION.md, not inferred from mocks.

Runtime integration finding: Workers does not support Fetch `redirect: "error"`; an initial real call failed closed before sending. The fixed transport uses `manual`, checks non-2xx and never follows redirects. [Official runtime behavior](https://developers.cloudflare.com/workers/runtime-apis/request/).
