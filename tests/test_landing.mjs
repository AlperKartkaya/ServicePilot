import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import vm from 'node:vm';
import test from 'node:test';

const app = readFileSync(new URL('../static/app.js', import.meta.url), 'utf8');
const model = readFileSync(new URL('../static/landing-case.js', import.meta.url), 'utf8');
const context = vm.createContext({ structuredClone, document: { querySelector: () => null } });
vm.runInContext(app.split('// ---------- Bootstrap ----------')[0], context);
vm.runInContext(model.replace(/^import .*\n/, '').replace('export function', 'function'), context);
const result = vm.runInContext('buildLandingCase()', context);

test('scroll story uses actual RAEP for evidence selection and final routing', () => {
  assert.equal(result.initial.action, 'REQUEST_EVIDENCE');
  assert.equal(result.initial.evidence_id, 'can_resistance');
  assert.equal(result.initial.candidates[0].id, result.initial.evidence_id);
  assert.ok(result.initial.candidates[0].U > 0);
  assert.ok(result.result.includes('120Ω'));
  assert.equal(result.final.action, 'ROUTE');
  assert.equal(result.final.target, 'ecu_comm');
  assert.ok(result.finalSignals.sufficient >= result.settings.tau_suff);
});

test('risk alternative bypasses missing Jev signals via the existing safety gate', () => {
  assert.equal(result.critical.action, 'ESCALATE');
  assert.equal(result.critical.target, 'expert_desk');
  assert.ok(result.critical.safety_hits.includes('yanık kokusu'));
  assert.equal(result.critical.evidence_id, null);
});

test('replaying the story is isolated from application cases and fixture mutations', () => {
  const before = vm.runInContext('JSON.stringify(FALLBACK_SCENARIOS)', context);
  vm.runInContext('buildLandingCase(); buildLandingCase()', context);
  assert.equal(vm.runInContext('JSON.stringify(FALLBACK_SCENARIOS)', context), before);
  assert.equal(vm.runInContext('S.cases.length', context), 0);
});

test('landing ships local animation runtimes, six chapters and no live-provider request', () => {
  const html = readFileSync(new URL('../static/index.html', import.meta.url), 'utf8');
  assert.equal((html.match(/data-step="/g) || []).length, 6);
  for (const library of ['gsap.min.js', 'ScrollTrigger.min.js', 'lenis.min.js']) {
    assert.ok(html.includes(`vendor/${library}`));
  }
  assert.doesNotMatch(model, /fetch\(|localStorage|sessionStorage/);
  assert.ok(app.includes('if (!document.querySelector(".app-shell")) return;'));
});


test('demo has a directory entrypoint and both landing CTAs preserve relative Pages paths', () => {
  const html = readFileSync(new URL('../static/index.html', import.meta.url), 'utf8');
  const demo = readFileSync(new URL('../static/demo/index.html', import.meta.url), 'utf8');
  const legacy = readFileSync(new URL('../static/app.html', import.meta.url), 'utf8');
  assert.match(html, /class="header-action" href="demo\/">Demoyu dene/);
  assert.match(html, /href="demo\/" class="restart-link">Demoyu dene/);
  assert.match(demo, /href="\.\.\/style.css"/);
  assert.match(demo, /src="\.\.\/app.js" type="module"/);
  for (const page of [html, legacy]) {
    assert.ok(page.includes("location.replace('demo/' + location.search + location.hash)"));
  }
});
