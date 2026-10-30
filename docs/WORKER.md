# GitHub Pages + public live Jev sensor [FR-22, ADR-12]

- UI: https://alperkartkaya.github.io/ServicePilot/
- Sensor: https://servicepilot-jev.alperkartkaya.workers.dev
- Every visitor uses live Jev automatically for new cases and evidence. No login, access code, browser token or client API key. Old synthetic records and replay retain their original sources.
- Worker runs fixed TypeSafe questions only. It cannot forward arbitrary URLs, models or questions. RAEP and case persistence stay in the browser; this is not a shared service backend. Existing FastAPI/SQLite remains available locally. Loopback/static development stays offline so tests do not spend provider credits.

## Set your private key — Cloudflare only
In Cloudflare **Workers & Pages → servicepilot-jev → Settings → Variables and Secrets**, add/edit `TYPESAFE_API_KEY`, type **Secret**, paste your private key, then **Deploy**. Do not put it in a plain-text variable, the UI, GitHub Pages or committed configuration. The existing secret is preserved until you replace it. [Official secret instructions](https://developers.cloudflare.com/workers/configuration/secrets/).

CLI alternative, prompts securely for the value:
```sh
wrangler secret put TYPESAFE_API_KEY --config worker/wrangler.toml
```
This is the only credential the app needs. The rejected `DEMO_ACCESS_TOKEN`, `/auth` and access dialog were removed. No access code needs distributing.

## Public usage boundaries
- Endpoint is intentionally anonymous. Origin/CORS restricts browsers, **not** scripted clients: they can forge Origin. Anyone can consume your provider credits through valid fixed-question requests.
- Existing approximate shared limit: 5 inference attempts / 60s / Cloudflare location. This is not a strict global/daily spending cap or authentication. See [rate-limit locality](https://developers.cloudflare.com/workers/runtime-apis/bindings/rate-limit/). Add provider-side spend controls if needed.
- Only vehicle family/fuel/km, note, measurements, DTCs, repairs and evidence text go to TypeSafe; not VIN, location, images, audit or history. Text itself can contain sensitive data. No automatic redaction or real customer data usage claimed.
- Body <=32 KiB; bounded schema/evidence catalog, fixed prompts, bounded upstream response, 15s timeout, no followed redirects. Deterministic safety bypasses the provider. Rate-limit errors retain typed evidence; provider/missing-key errors fail closed to human escalation, never silently to fixtures.
- `TYPESAFE_API_KEY` is a Worker encrypted secret. No request-body/provider-response logging, database or analytics resource added. To stop live inference, remove this Worker secret; the provider path then returns unavailable.
- Designed for Workers Free limits; no subscription upgrade, paid database or paid add-on created. Billing subscription inspection returned 403 for available OAuth permissions: account plan/zero invoice is not verified. Usage model is `standard`. Cloudflare free quotas do not make Jev inference free. [Workers limits](https://developers.cloudflare.com/workers/platform/limits/).

## Maintain and test
Use existing Wrangler or `npx wrangler@4.155.0`; check `wrangler whoami` before mutation. From repo root:
```sh
uv run python -m worker.export_contract
uv run pytest -q
node --test tests/test_frontend.mjs tests/test_worker.mjs
wrangler deploy --config worker/wrangler.toml --dry-run
wrangler deploy --config worker/wrangler.toml
uv run --with playwright python tests/browser_jev_smoke.py
```
The browser test serves local checkout assets at the production hostname and intercepts sensor requests with fixtures; no live provider/server data is touched. Static loopback behavior remains covered by `tests/browser_smoke.py`. Live verification is recorded separately in VALIDATION.md.

Worker deployment remains manual. Pages Actions validates both JS suites and publishes only `static/`; it never receives your Cloudflare OAuth token or TypeSafe secret. The public sensor URL in `static/app.js` is not a credential. Contract drift is tested against authoritative Python sources.

Runtime finding: Workers rejects Fetch `redirect:error` before sending; transport uses `manual` and rejects non-2xx without forwarding credentials. [Official runtime behavior](https://developers.cloudflare.com/workers/runtime-apis/request/).
