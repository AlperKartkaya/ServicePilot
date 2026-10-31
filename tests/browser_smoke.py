"""Real Chromium smoke checks; run only against disposable loopback demo servers.
uv run --with playwright python tests/browser_smoke.py
For isolated API fixture: add --api-fixture --url http://127.0.0.1:5188
"""
import argparse
from pathlib import Path
from urllib.parse import urlparse

from playwright.sync_api import expect, sync_playwright

parser = argparse.ArgumentParser()
parser.add_argument("--url", default="http://127.0.0.1:5187")
parser.add_argument("--api-fixture", action="store_true")
parser.add_argument("--artifacts", default="/tmp/servicepilot-browser")
args = parser.parse_args()
assert urlparse(args.url).hostname in {"127.0.0.1", "localhost"}, "Disposable loopback servers only"
artifacts = Path(args.artifacts)
artifacts.mkdir(parents=True, exist_ok=True)

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    context = browser.new_context(viewport={"width": 1440, "height": 1000}, reduced_motion="reduce")
    page = context.new_page()
    errors = []
    page.on("pageerror", lambda error: errors.append(str(error)))

    def go(route):
        page.goto(args.url + "/demo/" + route)
        page.wait_for_load_state("networkidle")
        assert page.evaluate("scrollY") == 0, "Navigation must start at the top"

    def no_overflow():
        assert page.evaluate("document.documentElement.scrollWidth <= innerWidth"), page.url

    go("")
    expect(page.locator("#env-label")).to_contain_text("Canlı API" if args.api_fixture else "Statik")
    if args.api_fixture:
        assert context.request.post(args.url + "/api/cases/seed").ok
        page.reload(wait_until="networkidle")
    expect(page.locator(".method-strip")).to_contain_text("Jev okur")
    page.screenshot(path=str(artifacts / "overview-desktop.png"), full_page=True)

    # Real case POST from the overview; no expected-outcome shortcut.
    page.locator('[data-start-demo="can_comm"]').click()
    expect(page.locator(".next-action-panel")).to_contain_text("Sıradaki işlem")
    expect(page.locator("#next-evidence-form")).to_be_visible()
    page.locator("#fill-next-evidence").click()
    page.locator("#submit-next-evidence").click()
    expect(page.locator(".next-action-panel")).to_contain_text("Yönlendirmeyi onayla")
    expect(page.locator(".signal-change")).to_contain_text("92%")
    page.locator('[data-case-action="confirm_route"]').click()
    expect(page.locator("#next-action-heading")).to_have_text("Yönlendirme tamamlandı")
    page.reload(wait_until="networkidle")
    expect(page.locator("#next-action-heading")).to_have_text("Yönlendirme tamamlandı")

    # Historical policy snapshot and human assignment survive recompute.
    page.locator("#technical-details > summary").click()
    page.locator("#recompute-btn").click()
    expect(page.locator(".step-count")).to_have_text("Adım 3")
    expect(page.locator(".human-lock-note")).to_contain_text("İnsan ataması değişmedi")
    page.locator("#trace-step").select_option("0")
    expect(page.locator("#technical-trace")).to_contain_text("Kanıt")
    page.screenshot(path=str(artifacts / "trace-desktop.png"), full_page=True)

    # Both secondary demo buttons use the same real creation endpoint, with different outcomes.
    go("#overview")
    page.locator('[data-start-demo="hv_propulsion"]').click()
    expect(page.locator('[data-case-action="confirm_route"]')).to_be_visible()
    go("#overview")
    page.locator('[data-start-demo="critical_fire"]').click()
    expect(page.locator(".signal-source")).to_contain_text("Jev çağrılmadı")
    expect(page.locator('[data-open-override="approve"]')).to_be_visible()

    go("#cases/SP-0001")
    expect(page.locator(".signal-source")).to_contain_text("Temsili" if args.api_fixture else "Yerel demo")
    expect(page.locator(".next-action-panel .btn-primary:visible")).to_have_count(1)
    page.screenshot(path=str(artifacts / "evidence-desktop.png"), full_page=True)
    if args.api_fixture:
        # Server failure keeps the typed evidence, error in context, no fake success/local fallback.
        page.route("**/api/cases/SP-0001/evidence", lambda route: route.fulfill(
            status=503, content_type="application/json", body='{"detail":"Test sunucusu erişilemiyor"}'))
        page.locator("#next-evidence-result").fill("CAN hattı 120 ohm ölçüldü.")
        page.locator("#submit-next-evidence").click()
        expect(page.locator("#next-evidence-error")).to_contain_text("Test sunucusu erişilemiyor")
        expect(page.locator("#next-evidence-result")).to_have_value("CAN hattı 120 ohm ölçüldü.")
        expect(page.locator(".step-count")).to_have_text("Adım 1")
        expect(page.locator("#env-label")).to_have_text("Canlı API")
        page.unroute("**/api/cases/SP-0001/evidence")

    # Critical case: no normal approval, dangerous tests absent, explicit human target + reason.
    go("#cases/SP-0003")
    expect(page.locator(".signal-source")).to_contain_text("Jev çağrılmadı")
    expect(page.locator('[data-case-action="confirm_route"]')).to_have_count(0)
    page.locator(".secondary-actions summary").click()
    page.locator("[data-open-ev-modal]").click()
    assert "road_test" not in page.locator("#ev-modal-select option").evaluate_all("xs => xs.map(x => x.value)")
    page.locator('[data-close-modal="evidence-modal"]').first.click()
    page.locator('[data-open-override="approve"]').click()
    expect(page.locator("#ov-modal-target")).to_have_value("")
    page.locator("#ov-modal-submit").click()
    expect(page.locator("#ov-modal-error")).to_contain_text("ekibi seçin")
    page.locator("#ov-modal-target").select_option("lv_electrical")
    page.locator("#ov-modal-submit").click()
    expect(page.locator("#ov-modal-error")).to_contain_text("gerekçe")
    page.locator("#ov-modal-reason").fill("Yetkili uzman incelemesi sonrası elektrik ekibine devredildi.")
    page.locator("#ov-modal-submit").click()
    expect(page.locator("#override-modal")).not_to_be_visible()
    expect(page.locator("#next-action-heading")).to_have_text("Yönlendirme tamamlandı")

    # Three-step form validates, saves a draft, restores it and creates an actual case.
    go("#new")
    page.locator("#family").fill("")
    page.locator('[data-next-step="2"]').click()
    expect(page.locator("#err-family")).not_to_be_empty()
    page.locator('[data-fill-scenario="can_comm"]').first.click()
    page.locator('[data-next-step="2"]').click()
    page.locator("#note").fill("Özel servis gözlemi: gösterge uyarıları birlikte yanıyor.")
    page.locator('[data-save-draft]').filter(visible=True).first.click()
    page.reload(wait_until="networkidle")
    expect(page.locator("#note")).to_have_value("Özel servis gözlemi: gösterge uyarıları birlikte yanıyor.")
    page.locator('[data-next-step="3"]').click()
    page.locator("#submit-case-btn").click()
    expect(page.locator(".case-complaint")).to_have_text("Özel servis gözlemi: gösterge uyarıları birlikte yanıyor.")

    # Keyboard skip link does not change routes; missing IDs do not show a random case.
    route = page.url
    page.locator(".skip-link").focus()
    page.keyboard.press("Enter")
    expect(page.locator("#main")).to_be_focused()
    assert page.url == route
    go("#cases/SP-9999")
    expect(page.locator("#case-detail-view h1")).to_have_text("Vaka bulunamadı")

    go("#replay")
    page.locator("#run-replay").click()
    expect(page.locator("#replay-out")).to_contain_text("ServicePilot")
    expect(page.locator("#replay-out tbody tr")).to_have_count(13)

    # Render every surface at phone, tablet, and desktop sizes, including open technical tables.
    for width in (390, 768, 1440):
        page.set_viewport_size({"width": width, "height": 900})
        for route in ("#overview", "#cases", "#new", "#review", "#queues", "#policy", "#cases/SP-0001"):
            go(route)
            no_overflow()
        if width <= 900:
            assert page.locator(".next-action-panel").bounding_box()["y"] < page.locator(".decision-explanation").bounding_box()["y"]
            page.locator("#sidebar-open").click()
            expect(page.locator("#sidebar-close")).to_be_focused()
            page.keyboard.press("Escape")
            expect(page.locator("#sidebar-open")).to_be_focused()
            expect(page.locator("#sidebar-backdrop")).to_be_hidden()
        page.evaluate("window.scrollTo(0, 0)")
        assert page.locator("#submit-next-evidence").bounding_box()["height"] >= 40
        page.screenshot(path=str(artifacts / f"evidence-{width}.png"), full_page=True)
        page.locator("#technical-details > summary").click()
        no_overflow()
    assert not errors, errors
    print(f"PASS: {'API fixture' if args.api_fixture else 'static local'} flows; 390/768/1440px; no JS errors. Artifacts: {artifacts}")
    browser.close()
