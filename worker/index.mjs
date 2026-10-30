import contract from './contract.json' with { type: 'json' };

async function readJson(request, limit) {
  const reader = request.body?.getReader();
  if (!reader) throw Error('invalid');
  const chunks = [];
  let size = 0;
  while (true) {
    const { value, done } = await reader.read();
    if (done) break;
    size += value.byteLength;
    if (size > limit) { await reader.cancel(); throw Error('oversize'); }
    chunks.push(value);
  }
  const bytes = new Uint8Array(size);
  let offset = 0;
  for (const chunk of chunks) { bytes.set(chunk, offset); offset += chunk.byteLength; }
  return JSON.parse(new TextDecoder().decode(bytes));
}

function stateFrom(body) {
  const text = (v, max, min = 0) => {
    if (typeof v !== 'string' || v.trim().length < min || v.length > max) throw Error('invalid');
    return v.trim();
  };
  const vehicle = body.vehicle;
  if (!vehicle || !['diesel', 'electric'].includes(vehicle.fuel) || !Number.isInteger(vehicle.km) || vehicle.km < 0 || vehicle.km > 5000000) throw Error('invalid');
  const dtcs = body.dtc_codes ?? [];
  const evidence = body.evidence ?? [];
  if (!Array.isArray(dtcs) || dtcs.length > 20 || !Array.isArray(evidence) || evidence.length > 12) throw Error('invalid');
  const state = {
    vehicle: { family: text(vehicle.family, 80, 2), fuel: vehicle.fuel, km: vehicle.km },
    technician_note: text(body.technician_note, 4000, 5),
    initial_measurements: text(body.initial_measurements ?? '', 2000),
    dtc_codes: dtcs.map(d => text(d, 16, 1)),
    recent_repairs: text(body.recent_repairs ?? '', 2000),
    collected_evidence: evidence.map(e => {
      if (!Object.hasOwn(contract.evidence, e.id)) throw Error('invalid');
      return { evidence: contract.evidence[e.id], result: text(e.result, 2000, 2) };
    }),
  };
  return state;
}

function signalsFrom(answers) {
  const probability = v => {
    if (typeof v !== 'number' || !Number.isFinite(v) || v < 0 || v > 1) throw Error('invalid');
    return v;
  };
  const route = Object.fromEntries(contract.leaves.map(l => [l, probability(answers.route.probabilities[l])]));
  if (Object.values(route).reduce((a,b) => a+b, 0) <= 0) throw Error('invalid');
  const score = answers.priority.score;
  if (typeof score !== 'number' || !Number.isFinite(score) || score < 0 || score > 4) throw Error('invalid');
  const priorities = Object.fromEntries(Object.entries(answers.priority.probabilities).map(([k,v]) => [k,probability(v)]));
  return { route, sufficient: probability(answers.sufficient.noul), critical: probability(answers.critical.noul),
    priority: {score, probabilities: priorities},
    has: Object.fromEntries(Object.keys(contract.evidence).map(id => [id, probability(answers['has_'+id].noul)])) };
}

export async function handle(request, env, send) {
  const path = new URL(request.url).pathname;
  const origin = request.headers.get('Origin');
  const reply = (body, status = 200) => Response.json(body, {status, headers: {
    'Access-Control-Allow-Origin': origin === env.ALLOWED_ORIGIN ? origin : 'null',
    'Access-Control-Allow-Methods': 'POST, GET, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type',
    'Cache-Control': 'no-store', 'Vary': 'Origin', 'X-Content-Type-Options': 'nosniff',
  }});
  if (path === '/health' && request.method === 'GET') return reply({ok:true});
  if (origin !== env.ALLOWED_ORIGIN) return reply({detail:'Origin izinli değil.'},403);
  if (request.method === 'OPTIONS') return reply({ok:true});
  if (path !== '/infer') return reply({detail:'Bulunamadı.'},404);
  if (request.method !== 'POST') return reply({detail:'POST gerekli.'},405);
  if (!request.headers.get('Content-Type')?.startsWith('application/json')) return reply({detail:'JSON gerekli.'},415);
  let state;
  try { state = stateFrom(await readJson(request, 32768)); }
  catch (error) { return reply({detail:'Vaka verisi geçersiz veya çok büyük.'},error.message === 'oversize' ? 413 : 422); }
  const safetyText = [state.technician_note,state.initial_measurements,state.recent_repairs,...state.dtc_codes,...state.collected_evidence.map(e=>e.result)].join(' ').toLowerCase();
  if (contract.safety_rules.some(r => safetyText.includes(r))) return reply({signals:null,latency_ms:0,signal_source:'safety'});
  if (!(await env.JEV_LIMIT.limit({key:'demo-inference'})).success) return reply({detail:'Dakikalık Jev sınırı doldu. Bir dakika sonra yeniden deneyin.'},429);
  const start = Date.now();
  let failure = "configuration";
  try {
    if (!env.TYPESAFE_API_KEY) throw Error('unconfigured');
    failure = "request";
    const response = await send(contract.url, {method:'POST',redirect:'manual',signal:AbortSignal.timeout(15000),
      headers:{Authorization:`Bearer ${env.TYPESAFE_API_KEY}`,'Content-Type':'application/json'},
      body:JSON.stringify({model:contract.model,state,questions:contract.questions})});
    if (!response.ok) { failure = `provider_${response.status}`; throw Error("upstream"); }
    failure = "invalid_response";
    const data = await readJson(response, 262144);
    return reply({signals:signalsFrom(data.answers),latency_ms:Date.now()-start,signal_source:'jev'});
  } catch {
    return reply({signals:null,latency_ms:Date.now()-start,signal_source:'unavailable',failure,detail:'Jev erişilemedi; insan uzman değerlendirmesi gerekli.'},503);
  }
}

export default { fetch: (request, env) => handle(request, env, fetch) };
