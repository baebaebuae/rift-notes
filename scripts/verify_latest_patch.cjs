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
   await page.select(id);assert.equal(page.$$('#spells article[data-skill]').length,5,id+' reviewed display');
   const c=data(prefix+id+'.json');
   for(const [slot,ability] of Object.entries(c.details.skills)){
    const el=page.$('article[data-skill="'+slot+'"]');
    for(const row of ability.rows){
     const numeric=row.value.replace(/\s|seconds?|mana|초|마나|(?<=\d)s\b/gi,'');
     const table=Array.from(el.querySelectorAll('.spell-rows .formula-row'));
     const inTable=table.some(node=>node.querySelector('.flabel').textContent===row.attribute&&node.querySelector('.formula-value').textContent===row.value);
     const inMeta=[...el.querySelectorAll('.spell-meta b,.spell-range .formula-value')].some(node=>node.textContent.replace(/초|s$/g,'')===numeric);
     assert(inTable||inMeta,id+slot+' missing '+row.attribute);
    }
   }
  }
  await page.select('Darius');assert(page.$('article[data-skill="Q"] .spell-meta').textContent.includes('9/8/7/6/4'));assert(!page.$('article[data-skill="Q"]').textContent.includes('9/7.75/6.5/5.25/4'));
  const distanceRows=slot=>page.$$('article[data-skill="'+slot+'"] .spell-range').map(row=>[
   row.querySelector('.flabel').textContent,row.querySelector('.formula-value').textContent
  ]);
  const ko=language==='ko';
  assert.deepEqual(distanceRows('Q'),[[ko?'전체 타격 반경':'Outer hit radius','460'],[ko?'도끼자루 반경':'Handle radius','240']]);
  assert.deepEqual(distanceRows('W'),[[ko?'기본 공격 추가 사거리':'Bonus attack range','+25']]);
  assert.deepEqual(distanceRows('R'),[[ko?'시전 사거리':'Cast range','475']]);
  await page.select('Janna');assert.deepEqual(distanceRows('W'),[[ko?'시전 사거리':'Cast range','550']]);
  await page.select('Hecarim');assert.equal(distanceRows('R')[0][1],'300–1000');
  await page.select('Gwen');assert.deepEqual(distanceRows('W'),[[ko?'안개 반경':'Mist radius','480']]);
  await page.select('Garen');assert.deepEqual(distanceRows('W'),[],'no cast range for a self buff');
  await page.select('Soraka');assert.deepEqual(distanceRows('R'),[[ko?'효과 범위':'Area of effect',ko?'전역':'Global']]);
  await page.select('Briar');assert.equal(distanceRows('R')[0][1],'12000','confirmed long range');
  await page.select('Jinx');assert.equal(page.$('.stat-value').textContent,'610');page.$('#level').value=18;page.$('#level').dispatchEvent(new page.w.Event('input'));assert.equal(page.$$('.stat-value')[2].textContent,'110');
  await page.select('MissFortune');const r=page.$('article[data-skill="R"]');r.querySelector('[data-expand]').click();assert.equal(r.querySelector('[data-expand]').getAttribute('aria-expanded'),'true');assert(r.textContent.includes('145%'));assert(!r.textContent.match(/25000|Global|전역/));
  await page.select('Shyvana');assert.equal(page.$$('article[data-skill]').length,5,'all reworked abilities shown');
  for(const id of ['Locke','Shyvana']) {
   const release=data(prefix+id+'.json').history.find(h=>h.release);
   assert.deepEqual(new Set(release.changes.map(c=>c.slot)),new Set('PQWER'));
  }
  await page.select('Mel');
  assert.equal(page.$('article[data-skill="W"] .spell-meta div:last-child b').textContent,'100/80/60/40/0');
  assert(!page.$('article[data-skill="W"]').textContent.includes('100/75/50/25/0'));
  assert.match(page.$('article[data-skill="Q"]').textContent,/85[~–]285/);
  assert.match(page.$('article[data-skill="W"] .spell-meta').textContent,/30\/28.5\/27\/25.5\/24/);
  assert.equal(data(prefix+'Mel.json').effectiveStats.attackspeedperlevel,2.75);
  assert(!data(prefix+'Mel.json').statConflicts.some(c=>c.field==='attackspeed'));
  await page.select('Zaahen');
  assert.match(page.$('article[data-skill="Q"] .spell-meta').textContent,/8\/7.5\/7\/6.5\/6/);
  await page.select('Gwen');assert(page.$('.stat-source-note'),'source conflict visible');page.close();
  const legacy=create({url:'https://rift.example/?champion=Darius&lang='+language,fetchOverride:url=>{
   if(url!=='data/'+prefix+'Darius.json')return;
   const champion=data(prefix+'Darius.json');delete champion.details;
   return Promise.resolve({ok:true,json:async()=>champion});
  }});
  await legacy.ready('Darius');
  assert(!legacy.$('article[data-skill="Q"] .spell-range'),'old data must not expose range 1');
  assert.match(legacy.$('article[data-skill="Q"] .spell-meta').textContent,/9\/8\/7\/6\/4/);
  assert(!legacy.$('#spells').querySelector('a,details.archive-details'));
  assert(!/⇒|→|보관본|archived values/i.test(legacy.$('#spells').textContent));
  legacy.close();
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
 console.log('PASS: 26.22 14 champions, 44 changes; release kits; Mel cost conflict; 173 champions / 865 skills in KO+EN; 26.21 58 changes including October 22 hotfix; independent damage fixtures; clean skill cards; Darius/stat conflicts; rework gaps; expanded values and range placeholders.');
}
main().catch(e=>{console.error(e);process.exitCode=1}).finally(closeAll);
