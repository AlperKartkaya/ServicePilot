import { FALLBACK_CATALOG, FALLBACK_SCENARIOS, jsDecide } from './app.js';

// Fixture probabilities, real policy. This story never calls Jev or saves a case.
export function buildLandingCase() {
  const scenario = FALLBACK_SCENARIOS.find((item) => item.id === 'can_comm');
  const settings = { ...FALLBACK_CATALOG.default_settings };
  const initialCase = { ...structuredClone(scenario), evidence: [] };
  const initialSignals = scenario.fixture_signals.initial;
  const initial = jsDecide(initialCase, initialSignals, settings);
  const result = scenario.answers[initial.evidence_id];
  const completedCase = {
    ...initialCase,
    evidence: [{ id: initial.evidence_id, result }],
  };
  const finalSignals = scenario.fixture_signals.after[initial.evidence_id];
  const final = jsDecide(completedCase, finalSignals, settings);
  const critical = jsDecide({
    ...initialCase,
    technician_note: `${initialCase.technician_note} Ayrıca yanık kokusu var.`,
  }, null, settings);
  return { scenario, settings, initialSignals, initial, result, finalSignals, final, critical };
}
