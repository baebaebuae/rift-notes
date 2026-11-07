// Independent regression fixtures for the reviewed 26.21 changes and October 22 hotfix.
const assert=require('node:assert/strict');
const {create,data,closeAll}=require('./verify.cjs');
const expected={Azir:1,Caitlyn:2,Darius:1,Jinx:2,LeeSin:4,Locke:6,MissFortune:2,Nidalee:2,Nunu:1,Orianna:2,Qiyana:1,Rammus:2,Ryze:3,Sion:3,Taliyah:3,Taric:4,Tristana:1,TwistedFate:1,Varus:8,Velkoz:1,Viktor:2,MonkeyKing:2,XinZhao:2,Yone:1,Zyra:1};
const values=(id,slot)=>data('en/'+id+'.json').details.skills[slot].rows.map(r=>r.value).join(' | ');
async function main(){
 for(const language of ['ko','en']){
  const prefix=language==='en'?'en/':'',index=data(prefix+'index.json'),found={};
  assert.equal(index.meta.patch,'26.22');assert.equal(index.meta.version,'16.22.1');assert.deepEqual(index.meta.failures,[]);
  for(const champion of index.champions){
   const c=data(prefix+champion.id+'.json'),entries=c.history.filter(h=>h.patch==='26.21');
   if(entries.length){assert.equal(entries.length,champion.id==='Varus'?2:1,champion.id+' latest entries');found[champion.id]=entries.reduce((n,h)=>n+h.changes.length,0);assert(['26.22','26.21'].includes(c.history[0].patch));}
   assert.equal(c.details.version,index.meta.version);assert.equal(c.details.patch,index.meta.patch);assert.deepEqual(Object.keys(c.details.skills).sort(),['E','P','Q','R','W']);
   for(const [slot,skill] of Object.entries(c.details.skills))for(const row of skill.rows){assert(row.attribute&&row.value,champion.id+slot);if(row.provenance!=='baseline')assert(row.sources.length,champion.id+slot+' source');}
  }
  assert.deepEqual(found,expected,'25 champions / 58 changes including hotfix');
  const latest = {AurelionSol:1,Corki:2,Kayle:2,Locke:3,Maokai:1,Mel:23,Naafiri:2,Rumble:2,Shen:1,Smolder:1,Thresh:2,Viktor:2,Yasuo:1,Zaahen:1};
  const currentEvents = {};
  for (const champion of index.champions) {
   const entry=data(prefix+champion.id+'.json').history.filter(h=>h.patch==='26.22');
   if (entry.length) {
    assert.equal(entry.length,1);
    assert.equal(entry[0].date,'2026-11-03');
    currentEvents[champion.id]=entry[0].changes.length;
   }
  }
  assert.deepEqual(currentEvents,latest);
  const page=create({url:'https://rift.example/?champion=Varus&lang='+language});await page.ready('Varus');
  assert.equal(data(prefix+'Varus.json').history[0].date,'2026-10-22');
  for(const id of Object.keys(expected)){
   await page.select(id);assert.equal(page.$$('.reconciled-spell').length,5,id+' reviewed display');
   const c=data(prefix+id+'.json');for(const [slot,s] of Object.entries(c.details.skills)){const el=page.$('article[data-skill="'+slot+'"]');assert.equal(el.querySelectorAll('.reconciled-row').length,s.rows.length,id+slot+' every reviewed row available');}
  }
  await page.select('Darius');assert(page.$('article[data-skill="Q"] .spell-meta').textContent.includes('9/8/7/6/4'));assert(page.$('article[data-skill="Q"]').textContent.includes('9/7.75/6.5/5.25/4'));
  await page.select('Jinx');assert.equal(page.$('.stat-value').textContent,'610');page.$('#level').value=18;page.$('#level').dispatchEvent(new page.w.Event('input'));assert.equal(page.$$('.stat-value')[2].textContent,'110');
  await page.select('MissFortune');const r=page.$('article[data-skill="R"]');r.querySelector('[data-expand]').click();assert.equal(r.querySelector('[data-expand]').getAttribute('aria-expanded'),'true');assert(r.textContent.includes('145%'));assert(!r.querySelector('.spell-range').textContent.match(/Global|전역/));
  await page.select('Shyvana');assert.equal(page.$$('.spell[data-review-status="partial"]').length,4,'rework gaps explicit');
  for(const id of ['Locke','Shyvana']) {
   const release=data(prefix+id+'.json').history.find(h=>h.release);
   assert.deepEqual(new Set(release.changes.map(c=>c.slot)),new Set('PQWER'));
  }
  await page.select('Mel');
  assert.equal(page.$('article[data-skill="W"] .spell-meta div:last-child b').textContent,'100/80/60/40/0');
  assert(page.$('article[data-skill="W"] .spell-data-note').textContent.includes('100/75/50/25/0'));
  assert.equal(page.$('article[data-skill="Q"]').dataset.reviewStatus,'reconciled');
  assert.match(page.$('article[data-skill="Q"]').textContent,/85[~–]285/);
  assert.match(page.$('article[data-skill="W"]').textContent,/30 \/ 28.5 \/ 27 \/ 25.5 \/ 24/);
  assert.equal(data(prefix+'Mel.json').effectiveStats.attackspeedperlevel,2.75);
  assert(!data(prefix+'Mel.json').statConflicts.some(c=>c.field==='attackspeed'));
  await page.select('Zaahen');
  assert.match(page.$('article[data-skill="Q"] .spell-meta').textContent,/8\/7.5\/7\/6.5\/6/);
  await page.select('Gwen');assert(page.$('.stat-source-note'),'source conflict visible');page.close();
  assert.equal(data(prefix+'Azir.json').stats.mpperlevel,50);assert.equal(data(prefix+'Sion.json').stats.hpperlevel,95);assert.equal(data(prefix+'Viktor.json').stats.movespeed,330);assert.equal(data(prefix+'MonkeyKing.json').stats.hpregen,5.5);
  assert.equal(data(prefix+'LeeSin.json').spells[1].cooldownBurn,'8');assert.equal(data(prefix+'Locke.json').spells[1].costBurn,'60/65/70/75/80');
 }
 assert.match(values('MissFortune','E'),/90 \/ 120 \/ 150 \/ 180 \/ 210.*120%/);
 assert.match(values('MissFortune','R'),/20 \/ 30 \/ 40 \+ 60% total AD \+ 25% AP/);
 assert.match(values('Varus','Q'),/50–250.*80% bonus AD/);assert.match(values('Varus','Q'),/85–425.*136% bonus AD/);
 assert.match(values('Caitlyn','P'),/60 - 80%/);assert.match(values('Yone','Q'),/105% AD/);assert.match(values('Yone','P'),/5% less/);
 assert.equal(data('en/Viego.json').details.skills.R.rows.find(r=>r.attribute==='Base AD damage').provenance,'derived');
 assert.match(values('Viktor','R'),/270% AP/);
 assert.match(values('Locke','Q'),/63 \/ 92.4 \/ 121.8 \/ 151.2 \/ 180.6/);
 console.log('PASS: 26.22 14 champions, 44 changes; release kits; Mel cost conflict; 173 champions / 865 skills in KO+EN; 26.21 58 changes including October 22 hotfix; independent damage fixtures; source badges; Darius/stat conflicts; rework gaps; expanded values and range placeholders.');
}
main().catch(e=>{console.error(e);process.exitCode=1}).finally(closeAll);
