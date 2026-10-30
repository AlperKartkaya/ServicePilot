"""Exercise live-sensor UI boundaries with fixtures; never consumes Jev credits."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from playwright.sync_api import sync_playwright, expect

from app.scenarios import SCENARIOS

can = next(s for s in SCENARIOS if s['id'] == 'can_comm')['fixture_signals']
url = 'http://127.0.0.1:5187'
with sync_playwright() as p:
    browser = p.chromium.launch()
    context = browser.new_context(viewport={'width': 1440, 'height': 1000}, reduced_motion='reduce')
    page = context.new_page()
    errors = []
    page.on('pageerror', lambda e: errors.append(str(e)))
    requests = []
    outcome = {'status': 200}

    def sensor(route):
        request = route.request
        headers = {'Access-Control-Allow-Origin': '*', 'Access-Control-Allow-Headers': 'authorization, content-type'}
        if request.method == 'OPTIONS' or request.url.endswith('/auth'):
            route.fulfill(json={'ok': True}, headers=headers)
            return
        body = request.post_data_json
        assert set(body['vehicle']) == {'family', 'fuel', 'km'}
        assert 'attachments' not in body
        requests.append(body)
        status = outcome['status']
        if status == 429:
            data = {'detail': 'Test: limit doldu'}
        elif status == 503:
            data = {'signals': None, 'signal_source': 'unavailable', 'latency_ms': 20}
        else:
            data = {'signals': can['after']['can_resistance'] if body['evidence'] else can['initial'], 'signal_source': 'jev', 'latency_ms': 123}
        route.fulfill(status=status, json=data, headers=headers)

    page.route('https://servicepilot-jev.alperkartkaya.workers.dev/**', sensor)
    page.goto(url, wait_until='networkidle')
    page.locator('#jev-connect').click()
    assert page.locator('#jev-access-code').bounding_box()['height'] >= 40
    page.locator('#jev-access-code').fill('fixture-code-not-a-secret')
    page.locator('#jev-access-submit').click()
    expect(page.locator('#env-label')).to_contain_text('Canlı Jev')
    page.locator('[data-start-demo="can_comm"]').click()
    expect(page.locator('#next-evidence-form')).to_be_visible()
    expect(page.locator('.sensor-stage')).to_contain_text('Canlı Jev')
    page.locator('#fill-next-evidence').click()
    outcome['status'] = 429
    page.locator('#submit-next-evidence').click()
    expect(page.locator('#next-evidence-error')).to_contain_text('limit doldu')
    expect(page.locator('.step-count')).to_have_text('Adım 1')
    assert page.locator('#next-evidence-result').input_value()
    outcome['status'] = 200
    page.locator('#submit-next-evidence').click()
    expect(page.locator('.next-action-panel')).to_contain_text('Yönlendirmeyi onayla')
    before = len(requests)
    page.locator('#technical-details > summary').click()
    page.locator('#recompute-btn').click()
    expect(page.locator('.step-count')).to_have_text('Adım 3')
    assert len(requests) == before
    page.reload(wait_until='networkidle')
    expect(page.locator('#env-label')).to_contain_text('Canlı Jev')
    page.goto(url + '/#overview', wait_until='networkidle')
    outcome['status'] = 503
    page.locator('[data-start-demo="can_comm"]').click()
    expect(page.locator('.sensor-stage')).to_contain_text('Jev erişilemedi')
    expect(page.locator('.next-action-panel')).to_contain_text('Uzman')
    before = len(requests)
    page.goto(url + '/#overview', wait_until='networkidle')
    page.locator('[data-start-demo="critical_fire"]').click()
    expect(page.locator('.sensor-stage')).to_contain_text('Jev çağrılmadı')
    assert len(requests) == before
    page.locator('#jev-connect').click()
    for width in [390, 768, 1440]:
        page.set_viewport_size({'width': width, 'height': 900})
        assert page.evaluate('document.documentElement.scrollWidth <= innerWidth'), width
    page.set_viewport_size({'width': 390, 'height': 844})
    page.screenshot(path='/tmp/servicepilot-jev-dialog-mobile.png', full_page=True)
    page.locator('#jev-disconnect').click()
    expect(page.locator('#env-label')).to_contain_text('Statik')
    assert not page.evaluate('sessionStorage.getItem("servicepilot_jev_access")')
    assert 'fixture-code' not in page.evaluate('JSON.stringify(localStorage)')
    assert not errors, errors
    browser.close()
print('PASS: fixture-only live UI, source/latency, quota retry, provider failure, safety, reload, disconnect, responsive dialog')
