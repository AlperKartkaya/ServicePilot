// No browser dependency: lock the existing local policy and lifecycle before UI changes.
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import vm from 'node:vm';
import test from 'node:test';

const elements = new Map();
const storage = new Map();
const context = vm.createContext({
  console, setTimeout, clearTimeout,
  document: { querySelector: (key) => elements.get(key) || null, querySelectorAll: () => [] },
  localStorage: { getItem: (key) => storage.get(key), setItem: (key, value) => storage.set(key, value) },
});
vm.runInContext(readFileSync(new URL('../static/app.js', import.meta.url), 'utf8').split('// ---------- Bootstrap ----------')[0], context);
const run = (code) => vm.runInContext(code, context);

function reset() {
  run('S.mode = "local"; S.settings = {...FALLBACK_CATALOG.default_settings}; S.cases = buildFallbackDemoCases(S.settings);');
}

test('representative cases retain evidence, route, and escalation outcomes', () => {
  reset();
  assert.deepEqual(Array.from(run('S.cases.map(c => c.status)')), ['awaiting_evidence', 'awaiting_evidence', 'escalated', 'routed', 'routed']);
});

test('critical case blocks dangerous field tests and normal route confirmation', async () => {
  reset();
  assert.ok(run('validateEvidenceForCase(S.cases[2], "road_test")'));
  await assert.rejects(run('localApi("/cases/SP-0003/review", {method:"POST", body:{action:"confirm_route"}})'));
});

test('requested evidence progresses without rewriting old decisions', async () => {
  reset();
  const before = run('JSON.stringify(S.cases[0].steps[0])');
  await run('localApi("/cases/SP-0001/evidence", {method:"POST", body:{evidence_id:S.cases[0].pending_evidence,result:"CAN hattı 120 ohm ölçüldü."}})');
  assert.equal(run('S.cases[0].evidence.length'), 1);
  assert.equal(run('S.cases[0].steps.length'), 2);
  assert.equal(run('JSON.stringify(S.cases[0].steps[0])'), before);
});

test('recompute preserves a confirmed human assignment', async () => {
  reset();
  await run('localApi("/cases/SP-0004/review", {method:"POST", body:{action:"confirm_route"}})');
  const before = run('JSON.stringify(S.cases[3].final)');
  await run('localApi("/cases/SP-0004/recompute", {method:"POST"})');
  assert.equal(run('JSON.stringify(S.cases[3].final)'), before);
  assert.equal(run('S.cases[3].review_status'), 'confirmed');
});

test('unknown detail never substitutes another case; user content is escaped', () => {
  reset();
  const target = { innerHTML: '' };
  elements.set('#case-detail-view', target);
  run('S.selected = "SP-9999"; renderCaseDetail()');
  assert.match(target.innerHTML, /Vaka bulunamadı/);
  run('S.selected = "SP-0001"; S.cases[0].technician_note = "<script>unsafe<\/script>"; renderCaseDetail()');
  assert.ok(!target.innerHTML.includes('<script>unsafe'));
  assert.match(target.innerHTML, /&lt;script&gt;/);
});

test('confirmed demo seed stays confirmed, not pending again', () => {
  reset();
  assert.equal(run('S.cases[4].review_status'), 'confirmed');
  assert.equal(run('caseCategory(S.cases[4])'), 'routed');
});

test('trace uses historical policy and distinguishes local signals from live Jev', () => {
  reset();
  run('S.settings.lambda = 99');
  const html = run('technicalTraceHtml(S.cases[0].steps[0])');
  assert.match(html, /Yerel demo · canlı Jev değil/);
  assert.ok(!html.includes('99.00'));
  assert.match(run('signalSource(S.cases[2].steps[0])'), /Jev çağrılmadı/);
});

test('legacy demo flag cannot mislabel an old API step as a fixture', () => {
  reset();
  run('S.mode = "api"; S.cases[0].is_demo = true; delete S.cases[0].steps[0].signal_source');
  assert.match(run('signalSource(S.cases[0].steps[0])'), /bilinmiyor/);
});
