// Browser API stubs exercise data handling and rendering; this is not visual QA.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const path = require('node:path');
const root = path.join(__dirname, '..');
class Element {
  constructor(tag='div') { this.tag=tag;this.children=[];this.value='';this.style={};this.files=[];this.textContent=''; }
  append(...nodes) { this.children.push(...nodes); }
  replaceChildren(...nodes) { this.children=nodes; }
  add(node) { this.children.push(node); }
  setAttribute() {}
  addEventListener() {}
  scrollIntoView() {}
  focus() {}
  click() {}
}
const nodes = new Map();
const storage = new Map();
const calls = [];
const getNode = id => { if(!nodes.has(id)) nodes.set(id,new Element()); return nodes.get(id); };
getNode('coverage').value='0';getNode('sort').value='score';
getNode('application-form').elements=Object.fromEntries(['offer_id','company','title','sent_at'].map(k=>[k,new Element('input')]));
const publicData=JSON.parse(fs.readFileSync(path.join(root,'docs/data/matches.json'),'utf8'));
const context=vm.createContext({
  document:{getElementById:getNode,createElement:tag=>new Element(tag),createTextNode:value=>({textContent:value})},
  Option:class extends Element {constructor(label,value){super('option');this.textContent=label;this.value=value;}},
  localStorage:{getItem:k=>storage.get(k)||null,setItem:(k,v)=>storage.set(k,v)},
  fetch:async url=>{calls.push(url);return {ok:true,json:async()=>publicData};},
  URL,Blob,crypto:require('node:crypto').webcrypto,setTimeout,confirm:()=>true,console,
});
const run = source => vm.runInContext(source,context);
async function main() {
  run(fs.readFileSync(path.join(root,'docs/dashboard.js'),'utf8'));
  await new Promise(resolve=>setImmediate(resolve));
  assert.match(getNode('message').textContent,/Données publiques/);
  assert.equal(getNode('offers').children.length,1); // informative empty state
  const localPath=path.join(root,'data/offers/matches_all_local.json');
  const local=fs.existsSync(localPath)?JSON.parse(fs.readFileSync(localPath,'utf8')):{offers:[{id:'test',title:'Synthetic',source:'test',score:.4,coverage:1,required_skills:['Python'],matched:['Python'],gaps:[],publishable:false}]};
  getNode('offers-file').files=[{size:1000,text:async()=>JSON.stringify(local)}];
  await getNode('offers-file').onchange();
  assert.equal(getNode('offers').children.length,local.offers.length);
  assert.match(getNode('message').textContent,/Mode local privé/);
  assert.deepEqual(calls,['data/matches.json']); // import has no network write
  getNode('search').value='no-such-title-0a1b2c';run('renderOffers()');
  assert.equal(getNode('offers').children[0].className,'empty');
  getNode('search').value='';
  assert.throws(()=>run('validateOffers({offers:[{id:"x"}]})'));
  assert.equal(run('validDate("2026-02-30")'),false);
  assert.equal(run('validDate("2026-02-28")'),true);
  assert.equal(run('saveTracker([{id:"t",offer_id:"x",company:"<script>bad()</script>",title:"Test",sent_at:today(),status:"sent",response_at:""}])'),true);
  assert.equal(storage.size,1);
  assert.equal(getNode('applications').children[0].children[0].textContent,'<script>bad()</script>');
  assert.equal(run('saveTracker([{id:"t",offer_id:"x",company:"Test",title:"Test",sent_at:today(),status:"response",response_at:""}])'),false);
  assert.equal(run('applications[0].status'),'sent'); // failed save preserves tracker
  assert.equal(run('saveTracker([])'),true);
  assert.equal(getNode('outcome-kpis').children[1].children[0].textContent,'—');
  console.log('Dashboard checks passed: public empty state, private import, filters, malformed data, safe text, tracker consistency and persistence.');
}
main().catch(error=>{console.error(error);process.exitCode=1;});
