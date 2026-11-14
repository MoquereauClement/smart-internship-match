/* All imported personal data stays in this browser. No analytics or uploads. */
'use strict';
const $ = id => document.getElementById(id);
const KEY = 'sim-applications-v1';
const STATUSES = {sent:'Envoyée',response:'Réponse reçue',interview:'Entretien',rejected:'Refus',accepted:'Acceptée',withdrawn:'Retirée'};
const DAY = 86400000;
let dataset = {offers:[]};
let applications = [];
const text = (tag, value, cls) => { const el = document.createElement(tag); el.textContent = value; if(cls) el.className = cls; return el; };
const pct = n => `${Math.round(n * 100)} %`;
const today = () => { const d = new Date(); return `${d.getFullYear()}-${String(d.getMonth()+1).padStart(2,'0')}-${String(d.getDate()).padStart(2,'0')}`; };
function validDate(value) { return typeof value === 'string' && /^\d{4}-\d{2}-\d{2}$/.test(value) && Number.isFinite(Date.parse(value)) && new Date(value).toISOString().slice(0,10) === value; }
function validateOffers(data) {
  if(!data || !Array.isArray(data.offers)) throw Error('Le fichier doit contenir une liste « offers ».');
  const ids = new Set();
  for(const o of data.offers) {
    if(!o || typeof o.id !== 'string' || ids.has(o.id) || typeof o.title !== 'string' || !['score','coverage'].every(k => Number.isFinite(o[k]) && o[k]>=0 && o[k]<=1) || !['required_skills','matched','gaps'].every(k => Array.isArray(o[k]) && o[k].every(s=>typeof s==='string')) || (o.responsibilities!=null && (!Array.isArray(o.responsibilities) || !o.responsibilities.every(s=>typeof s==='string')))) throw Error('Offre invalide : identifiant unique, titre, score, couverture et compétences sont requis.');
    ids.add(o.id);
  }
  return data;
}
function validateTracker(rows) {
  if(!Array.isArray(rows)) throw Error('Liste de candidatures attendue.');
  const ids = new Set();
  return rows.map(a => {
    if(!a || !['id','offer_id','company','title'].every(k => typeof a[k]==='string' && a[k].trim() && a[k].length<=300) || ids.has(a.id) || !Object.hasOwn(STATUSES,a.status) || !validDate(a.sent_at) || a.sent_at>today() || (a.response_at && (!validDate(a.response_at) || a.response_at<a.sent_at || a.response_at>today())) || (['response','interview','rejected','accepted'].includes(a.status) && !a.response_at) || (a.status==='sent' && a.response_at)) throw Error('Suivi invalide : vérifier les identifiants, statuts et dates. Une réponse doit avoir une date.');
    ids.add(a.id);
    return Object.fromEntries(['id','offer_id','company','title','sent_at','status','response_at'].map(k=>[k,a[k] || '']));
  });
}
function kpis(id, values) { $(id).replaceChildren(...values.map(([number,label]) => { const el=text('div','','kpi'); el.append(text('strong',number),text('span',label)); return el; })); }
function bars(id, entries, gap=false) {
  const max = Math.max(1,...entries.map(e=>e[1]));
  $(id).replaceChildren(...entries.map(([label,n])=>{const row=text('div','',`bar-row${gap?' gap':''}`); const track=text('div','','track'); const bar=text('div','','bar'); bar.style.width=`${n/max*100}%`; track.append(bar); row.append(text('span',label,'bar-label'),track,text('b',n)); return row;}));
  if(!entries.length) $(id).append(text('p','Aucune donnée disponible.','muted'));
}
function counts(field) { const c=new Map(); for(const o of dataset.offers) for(const s of new Set(o[field])) c.set(s,(c.get(s)||0)+1); return [...c].sort((a,b)=>b[1]-a[1] || a[0].localeCompare(b[0])).slice(0,10); }
function chip(skill,gap=false) { return text('span',skill,`chip${gap?' gap':''}`); }
function renderDataset() {
  const offers=dataset.offers;
  const sources=new Map(); for(const o of offers) sources.set(o.source||'Non renseignée',(sources.get(o.source||'Non renseignée')||0)+1);
  const empty=offers.filter(o=>!o.required_skills.length).length;
  kpis('pipeline-kpis',[[offers.length,'offres dans le jeu actif'],[sources.size,'sources représentées'],[empty,'offres sans compétence extraite'],[offers.length?pct(offers.filter(o=>o.coverage>=.3).length/offers.length):'—','offres couvrant au moins 30 %']]);
  bars('sources',[...sources]);
  $('quality').textContent=`${empty} offre(s) sans compétence extraite. ${offers.filter(o=>o.compensation_mentioned).length} offre(s) avec une rémunération chiffrée extraite. Taux d’erreur IA : non mesuré.`;
  $('freshness').textContent=dataset.generated_at ? `Calcul du matching : ${dataset.generated_at}. Cette date n’est pas la date de publication des annonces.`:'Date de calcul non renseignée.';
  const bins=[['0–19 %',0],['20–39 %',0],['40–59 %',0],['60–79 %',0],['80–100 %',0]];
  for(const o of offers) bins[Math.min(4,Math.floor(o.score*5))][1]++;
  bars('distribution', offers.length?bins:[]); bars('gaps',counts('gaps'),true);
  const strengths=counts('matched'); $('strengths').replaceChildren(...strengths.map(([s,n])=>chip(`${s} · ${n} offre(s)`)));
  if(!strengths.length) $('strengths').append(text('p','Aucune correspondance disponible.','muted'));
  $('source').replaceChildren(new Option('Toutes les sources',''),...[...sources.keys()].map(s=>new Option(s,s)));
  renderOffers();
}
function renderOffers() {
  const q=$('search').value.toLocaleLowerCase('fr');
  const rows=dataset.offers.filter(o=>(!$('source').value||(o.source||'Non renseignée')===$('source').value) && o.coverage>=Number($('coverage').value) && [o.title,o.company,o.location,...o.required_skills].join(' ').toLocaleLowerCase('fr').includes(q)).sort((a,b)=>b[$('sort').value]-a[$('sort').value] || a.title.localeCompare(b.title));
  $('result-count').textContent=`${rows.length} offre(s) affichée(s) sur ${dataset.offers.length}.`;
  $('offers').replaceChildren(...rows.map(o=>{
    const card=text('article','','offer'); const body=text('div','');
    body.append(text('h3',o.title),text('div',`${o.company||'Entreprise non renseignée'} · ${o.location||'Lieu non renseigné'} · ${o.source||'Source inconnue'}`,'meta'));
    const skills=text('div','','chips'); skills.append(...o.matched.map(s=>chip(s)),...o.gaps.map(s=>chip(s,true))); body.append(skills);
    if(!o.required_skills.length) body.append(text('p','Compétences non renseignées : score 0 par absence d’information.','muted'));
    const details=text('details',''); details.append(text('summary','Missions et exigences'));
    details.append(text('p',(o.responsibilities||[]).join('\n')||'Missions non renseignées.'),text('p',`Formation / expérience : ${o.experience_required||'Non renseignée'}`),text('p',`Rémunération : ${o.compensation_mentioned||'Non renseignée'}`));
    if(o.url) { try { const url=new URL(o.url); if(['https:','http:'].includes(url.protocol)) {const a=text('a','Consulter l’annonce ↗'); a.href=url.href; a.target='_blank'; a.rel='noopener noreferrer'; details.append(a);} } catch {} }
    body.append(details);
    const add=text('button','Préremplir une candidature'); add.type='button'; add.onclick=()=>{const f=$('application-form'); f.elements.offer_id.value=o.id;f.elements.company.value=o.company||'';f.elements.title.value=o.title;f.scrollIntoView({behavior:'smooth',block:'center'});f.elements.sent_at.focus();}; body.append(add);
    const score=text('div',pct(o.score),'score'); score.append(text('small',`Couverture ${pct(o.coverage)}`)); card.append(body,score);return card;
  }));
  if(!rows.length) $('offers').append(text('p',dataset.offers.length?'Aucune offre ne correspond à ces filtres.':'Aucune offre publique disponible. Tu peux importer ton fichier local pour explorer tes résultats.','empty'));
}
async function loadPublic() {
  try {
    const response=await fetch('data/matches.json'); if(!response.ok) throw Error(`HTTP ${response.status}`);
    const data=validateOffers(await response.json());
    if(data.offers.some(o=>o.publishable!==true)) throw Error('Le fichier public contient une offre non publiable.');
    dataset=data; renderDataset(); $('message').textContent=`Données publiques · ${dataset.offers.length} offre(s). ${dataset.offers.length?'':'Les offres locales privées peuvent être importées ci-dessus.'}`;
  } catch(e) { $('message').textContent=`Chargement impossible : ${e.message}. Utilise un serveur HTTP ou importe ton fichier local.`; }
}
function saveTracker(next) {
  try { const valid=validateTracker(next); localStorage.setItem(KEY,JSON.stringify(valid)); applications=valid; $('tracker-message').textContent='Suivi enregistré dans ce navigateur.'; renderTracker(); return true; }
  catch(e) { $('tracker-message').textContent=`Enregistrement impossible : ${e.message}`; return false; }
}
function download(name,contents,type) { const url=URL.createObjectURL(new Blob([contents],{type})); const a=text('a','');a.href=url;a.download=name;a.click();setTimeout(()=>URL.revokeObjectURL(url),1000); }
function renderTracker() {
  const n=applications.length, responded=applications.filter(a=>a.response_at).length;
  const overdue=applications.filter(a=>a.status==='sent'&&!a.response_at&&(Date.parse(today())-Date.parse(a.sent_at))/DAY>=10);
  kpis('outcome-kpis',[[n,'candidatures envoyées'],[n?pct(responded/n):'—','taux de réponse (tous retours)'],[applications.filter(a=>['interview','accepted'].includes(a.status)).length,'entretiens / acceptations (statut actuel)'],[overdue.length,'candidatures à relancer']]);
  $('applications').replaceChildren(...applications.map(a=>{
    const row=text('tr','');const job=text('td',a.company);job.append(text('small',a.title),text('small',a.offer_id));
    const status=text('select','');status.setAttribute('aria-label',`Statut chez ${a.company}`);for(const [value,label]of Object.entries(STATUSES))status.add(new Option(label,value));status.value=a.status;
    const date=text('input','');date.type='date';date.min=a.sent_at;date.max=today();date.value=a.response_at;date.setAttribute('aria-label',`Première réponse chez ${a.company}`);
    // Both fields are saved together so the date can be entered before a new status.
    const actions=text('td','');const save=text('button','Enregistrer');save.onclick=()=>saveTracker(applications.map(x=>x.id===a.id?{...x,status:status.value,response_at:date.value}:x));
    const remove=text('button','Supprimer','secondary');remove.onclick=()=>{if(confirm(`Supprimer la candidature chez ${a.company} ?`))saveTracker(applications.filter(x=>x.id!==a.id));};actions.append(save,document.createTextNode(' '),remove);
    const statusCell=text('td','');statusCell.append(status);const dateCell=text('td','');dateCell.append(date);row.append(job,text('td',a.sent_at),statusCell,dateCell,actions);return row;
  }));
  if(!n){const row=text('tr','');const cell=text('td','Aucune candidature enregistrée. Les chiffres apparaîtront après ta première saisie.');cell.colSpan=5;row.append(cell);$('applications').append(row);}
  $('alerts').replaceChildren(...overdue.map(a=>text('div',`${a.company} · ${a.title} · ${Math.floor((Date.parse(today())-Date.parse(a.sent_at))/DAY)} jours sans réponse`,'alert')));
  if(!overdue.length)$('alerts').append(text('p',n?'Aucune relance déclenchée.':'Aucune candidature à contrôler. Ce résultat ne mesure pas encore ta recherche.'));
}
async function readFile(input) {const file=input.files[0];if(!file)throw Error('Aucun fichier sélectionné.');if(file.size>20*1024*1024)throw Error('Fichier trop volumineux (maximum 20 Mo).');return JSON.parse(await file.text());}
$('offers-file').onchange=async function(){try{const data=validateOffers(await readFile(this));dataset=data;renderDataset();$('message').textContent=`Mode local privé · ${data.offers.length} offre(s). Aucune donnée importée n’a été envoyée au serveur. Recharge la page pour revenir au jeu public.`;}catch(e){$('message').textContent=`Import impossible : ${e.message}`;}};
$('public-data').onclick=loadPublic;
for(const id of ['search','source','coverage','sort'])$(id).addEventListener('input',renderOffers);
$('application-form').elements.sent_at.value=today();$('application-form').elements.sent_at.max=today();
$('application-form').onsubmit=e=>{e.preventDefault();const f=e.currentTarget;const a=Object.fromEntries(new FormData(f));a.id=crypto.randomUUID();a.status='sent';a.response_at='';if(saveTracker([...applications,a])){f.reset();f.elements.sent_at.value=today();}};
$('export-tracker').onclick=()=>download(`candidatures-${today()}.json`,JSON.stringify({version:1,applications},null,2),'application/json');
$('export-csv').onclick=()=>{const keys=['id','offer_id','company','title','sent_at','status','response_at'];const quote=v=>`"${String(v).replaceAll('"','""')}"`;download('applications.csv',[keys.join(','),...applications.map(a=>keys.map(k=>quote(a[k])).join(','))].join('\r\n'),'text/csv;charset=utf-8');};
$('tracker-file').onchange=async function(){try{const data=await readFile(this);const next=validateTracker(data.applications);if(applications.length&&!confirm('Remplacer le suivi actuel par cette sauvegarde ? Exporte-le d’abord pour le conserver.'))return;saveTracker(next);}catch(e){$('tracker-message').textContent=`Import impossible : ${e.message}`;}};
try{applications=validateTracker(JSON.parse(localStorage.getItem(KEY)||'[]'));}catch(e){$('tracker-message').textContent=`Suivi non chargé : ${e.message} Les données existantes n’ont pas été effacées.`;}
renderTracker();loadPublic();
