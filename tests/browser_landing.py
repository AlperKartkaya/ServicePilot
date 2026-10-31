"""Loopback-only landing interaction, motion and fallback checks.
uv run --with playwright python tests/browser_landing.py
"""
from pathlib import Path
from playwright.sync_api import sync_playwright, expect

URL = 'http://127.0.0.1:5187'
artifacts = Path('.impeccable/review')
artifacts.mkdir(parents=True, exist_ok=True)
(artifacts / '.gitignore').write_text('*\n!.gitignore\n')

with sync_playwright() as p:
    browser = p.chromium.launch()
    for width, height in [(1440, 960), (768, 1024), (390, 844)]:
        context = browser.new_context(viewport={'width': width, 'height': height})
        page = context.new_page()
        errors, provider_calls = [], []
        page.on('pageerror', lambda error: errors.append(str(error)))
        page.on('request', lambda request: provider_calls.append(request.url) if 'workers.dev' in request.url or 'typesafe' in request.url else None)
        page.goto(URL, wait_until='networkidle')
        expect(page.locator('body')).to_have_class('motion')
        assert page.evaluate('localStorage.length') == 0
        page.screenshot(path=str(artifacts / f'hero-{width}.png'))
        for selector in ['.header-action', '.restart-link']:
            expect(page.locator(selector)).to_have_text('Demoyu dene')
            expect(page.locator(selector)).to_have_attribute('href', 'demo/')
        scenes = page.locator('[data-scene]')
        for index in range(6):
            page.locator('[data-step]').nth(index).evaluate("el => el.scrollIntoView({behavior:'instant',block:'start'})")
            page.wait_for_function("i => Number(getComputedStyle(document.querySelector(`[data-scene=\"${i}\"]`)).opacity) > .98", arg=index)
            expect(scenes.nth(index)).to_be_visible()
            assert page.evaluate('document.documentElement.scrollWidth <= innerWidth'), (width, index)
            assert scenes.nth(index).evaluate('(el) => el.getBoundingClientRect().bottom <= innerHeight + 2'), (width, index, 'scene extends beyond viewport')
            if index == 3:
                page.wait_for_function("getComputedStyle(document.querySelector('.measurement>strong')).clipPath === 'none'")
            if index in (0, 2, 3, 5):
                page.screenshot(path=str(artifacts / f'step-{index}-{width}.png'))
        page.locator('#risk-toggle').focus()
        page.keyboard.press('Space')
        expect(page.locator('#safety-result')).to_contain_text('ESCALATE')
        expect(page.locator('#safety-title')).to_contain_text('İnsan devreye girer.')
        page.screenshot(path=str(artifacts / f'risk-{width}.png'))
        page.locator('#risk-toggle').click()
        expect(page.locator('#risk-toggle')).to_have_attribute('aria-pressed', 'false')
        # Chapter navigation and backtracking work without a custom scroll container.
        page.locator('.chapter-nav a').nth(2).focus()
        page.keyboard.press('Enter')
        expect(page.locator('.chapter-nav a').nth(2)).to_have_attribute('aria-current', 'step')
        page.wait_for_function("Number(getComputedStyle(document.querySelector('[data-scene=\"2\"]')).opacity) > .98")
        assert page.evaluate('localStorage.length') == 0
        assert not provider_calls, provider_calls
        assert not errors, errors
        # Switching motion preference tears down Lenis and exposes all scene content.
        page.emulate_media(reduced_motion='reduce')
        expect(page.locator('body')).not_to_have_class('motion')
        for index in range(6):
            expect(scenes.nth(index)).to_be_visible()
        context.close()
        print(f'PASS {width}x{height}: six steps, risk, reverse navigation, zero provider calls and motion toggle')

    for width, height in [(390, 667), (1440, 650)]:
        context = browser.new_context(viewport={'width': width, 'height': height})
        page = context.new_page()
        page.goto(URL, wait_until='networkidle')
        expect(page.locator('body')).not_to_have_class('motion')
        assert page.locator('.reading-title:visible').count() == 6
        assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
        context.close()

    context = browser.new_context(viewport={'width': 390, 'height': 844}, reduced_motion='reduce')
    page = context.new_page()
    page.goto(URL, wait_until='networkidle')
    expect(page.locator('body')).not_to_have_class('motion')
    for index in range(6):
        expect(page.locator('[data-scene]').nth(index)).to_be_visible()
    page.screenshot(path=str(artifacts / 'reduced-motion.png'), full_page=True)
    page.locator('#risk-toggle').click()
    expect(page.locator('#safety-result')).to_contain_text('ESCALATE')
    assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
    context.close()

    context = browser.new_context(viewport={'width': 390, 'height': 844}, java_script_enabled=False)
    page = context.new_page()
    page.goto(URL, wait_until='networkidle')
    expect(page.locator('.no-script')).to_contain_text('statik senaryo')
    expect(page.locator('#risk-toggle')).to_be_disabled()
    assert page.locator('.reading-title:visible').count() == 6
    assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
    context.close()

    context = browser.new_context(viewport={'width': 1440, 'height': 960})
    page = context.new_page()
    page.route('**/vendor/**', lambda route: route.abort())
    page.goto(URL, wait_until='networkidle')
    expect(page.locator('body')).not_to_have_class('motion')
    assert page.locator('.reading-title:visible').count() == 6
    page.locator('#risk-toggle').click()
    expect(page.locator('#safety-result')).to_contain_text('ESCALATE')
    context.close()

    context = browser.new_context()
    page = context.new_page()
    page.goto(URL + '/#cases/SP-0001', wait_until='networkidle')
    assert '/demo/#cases/SP-0001' in page.url
    expect(page.locator('.next-action-panel')).to_be_visible()
    page.goto(URL + '/app.html?legacy=1#cases/SP-0001', wait_until='networkidle')
    assert '/demo/?legacy=1#cases/SP-0001' in page.url
    expect(page.locator('.next-action-panel')).to_be_visible()
    for selector in ['.header-action', '.restart-link']:
        page.goto(URL, wait_until='networkidle')
        page.locator(selector).click()
        page.wait_for_url('**/demo/')
        expect(page.locator('.app-shell')).to_be_visible()
        expect(page.locator('#env-label')).to_contain_text('Demo Ortamı (Statik)')
    context.close()
    browser.close()
    print('PASS short screens, reduced motion, no JS, unavailable vendors and legacy app deep link')
