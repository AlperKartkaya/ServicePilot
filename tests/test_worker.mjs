import assert from 'node:assert/strict';
import test from 'node:test';
import { handle } from '../worker/index.mjs';
import { readFileSync } from 'node:fs';
const contract = JSON.parse(readFileSync(new URL('../worker/contract.json', import.meta.url)));
const origin = 'https://alperkartkaya.github.io';
const env = {ALLOWED_ORIGIN: origin, DEMO_ACCESS_TOKEN:'test-access', TYPESAFE_API_KEY:'server-only',
  JEV_LIMIT:{limit: async () => ({success:true})}};
const body = {vehicle:{family:'Isuzu NPR',fuel:'diesel',km:1000},technician_note:'Marş motoru dönmüyor.',evidence:[]};
const request = (path='/infer', data=body, headers={}) => new Request('https://worker.test'+path, {
  method:'POST', headers:{Origin:origin,Authorization:'Bearer test-access','Content-Type':'application/json',...headers},body:JSON.stringify(data)});
let calls=0;
const answers = {route:{probabilities:Object.fromEntries(contract.leaves.map(l=>[l,1/9]))},
  sufficient:{noul:0.3},critical:{noul:0.1},priority:{score:2,probabilities:{}}};
for(const id of Object.keys(contract.evidence)) answers['has_'+id]={noul:0.1};
const upstream = async (url, options) => {
  calls++;
  assert.equal(url,contract.url);
  assert.equal(options.redirect,'manual');
  assert.equal(options.headers.Authorization,'Bearer server-only');
  const sent=JSON.parse(options.body);
  assert.deepEqual(sent.questions,contract.questions);
  assert.equal(sent.model,contract.model);
  assert.equal(sent.state.vehicle.vin,undefined);
  assert.equal(sent.state.attachments,undefined);
  return Response.json({answers});
};
test('auth and origin reject before any paid inference', async()=>{
  calls=0;
  assert.equal((await handle(request('/infer',body,{Authorization:''}),env,upstream)).status,401);
  assert.equal((await handle(request('/infer',body,{Origin:'https://evil.test'}),env,upstream)).status,403);
  assert.equal((await handle(request('/auth',{}),env,upstream)).status,200);
  assert.equal(calls,0);
});
test('rejects oversized/invalid/custom evidence before inference',async()=>{
  calls=0;
  for(const input of [{...body,technician_note:'a'}, {...body,evidence:[{id:'invented',result:'ok'}]}, {...body,vehicle:{...body.vehicle,km:-1}}])
    assert.equal((await handle(request('/infer',input),env,upstream)).status,422);
  assert.equal((await handle(request('/infer',{...body,technician_note:'a'.repeat(40000)}),env,upstream)).status,413);
  assert.equal(calls,0);
});
test('safety bypasses model; rate limit denies before model',async()=>{
  calls=0;
  const r=await handle(request('/infer',{...body,technician_note:'Araçta yangın var'}),env,upstream);
  assert.equal((await r.json()).signal_source,'safety');
  const denied={...env,JEV_LIMIT:{limit:async()=>({success:false})}};
  assert.equal((await handle(request(),denied,upstream)).status,429);
  assert.equal(calls,0);
});
test('fixed server questions and minimized state produce typed live signals',async()=>{
  calls=0;
  const r=await handle(request('/infer',{...body,vehicle:{...body.vehicle,vin:'PRIVATE'},questions:{},attachments:['PRIVATE']}),env,upstream);
  assert.equal(r.status,200);
  const data=await r.json();
  assert.equal(data.signal_source,'jev');
  assert.equal(data.signals.sufficient,0.3);
  assert.equal(calls,1);
  assert.equal(r.headers.get('access-control-allow-origin'),origin);
  assert.equal(r.headers.get('cache-control'),'no-store');
});
test('provider and malformed answers fail closed, never return provider details',async()=>{
  for(const send of [async()=>new Response('secret upstream details',{status:401}),async()=>Response.json({answers:{}}),async()=>{throw Error('server-only');}]){
    const r=await handle(request(),env,send);
    assert.equal(r.status,503);
    const text=await r.text();
    assert.doesNotMatch(text,/server-only|secret upstream/);
    assert.equal(JSON.parse(text).signal_source,'unavailable');
  }
});

test('preflight grants only configured origin; redirect and invalid probabilities fail closed',async()=>{
  const preflight = new Request('https://worker.test/infer',{method:'OPTIONS',headers:{Origin:origin}});
  assert.equal((await handle(preflight,env,upstream)).status,200);
  assert.equal((await handle(request('/infer',body,{Origin:'null'}),env,upstream)).status,403);
  for(const send of [async()=>new Response('',{status:302,headers:{Location:'https://evil.test'}}),
    async()=>Response.json({answers:{...answers,sufficient:{noul:-1}}})]){
    const r=await handle(request(),env,send);
    assert.equal(r.status,503);
    assert.equal((await r.json()).signal_source,'unavailable');
  }
});
