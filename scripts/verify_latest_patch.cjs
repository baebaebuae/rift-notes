// Snapshot-specific checks against the independently reviewed 26.21 notes.
const assert=require('node:assert/strict');
const {create,data,until,closeAll}=require('./verify.cjs');
const expected={Azir:1,Caitlyn:2,Darius:1,Jinx:2,LeeSin:4,Locke:6,MissFortune:2,Nidalee:2,Nunu:1,Orianna:2,Qiyana:1,Rammus:2,Ryze:3,Sion:3,Taliyah:3,Taric:4,Tristana:1,TwistedFate:1,Varus:6,Velkoz:1,Viktor:2,MonkeyKing:2,XinZhao:2,Yone:1,Zyra:1};
async function main(){
 for(const language of ['ko','en']){
  const prefix=language==='en'?'en/':'',index=data(prefix+'index.json');
  assert.equal(index.meta.patch,'26.21');assert.equal(index.meta.version,'16.21.1');assert.deepEqual(index.meta.failures,[]);
  const found={};
  for(const champion of index.champions){const c=data(prefix+champion.id+'.json'),entries=c.history.filter(h=>h.patch==='26.21');if(entries.length){assert.equal(entries.length,1,champion.id+' duplicate latest record');found[champion.id]=entries[0].changes.length;assert.equal(c.history[0].patch,'26.21');assert.equal(entries[0].date,'2026-10-20')}}
  assert.deepEqual(found,expected,'25 champions / 56 official SR changes');
  const page=create({url:'https://rift.example/?champion=Varus&lang='+language});await page.ready('Varus');
  for(const id of Object.keys(expected)){
   await page.select(id);const c=data(prefix+id+'.json'),changes=c.history[0].changes.filter(ch=>'PQWER'.includes(ch.slot));
   assert.equal(page.$$('.current-change').length,changes.length,id+' all new skill changes visible');
   const text=page.$$('.spell-current').map(el=>el.textContent).join(' ');
   for(const ch of changes)if(/[⇒→]/.test(ch.text))assert(text.includes(ch.text.split(/[⇒→]/)[1].trim()),id+' updated value');
   for(const archive of page.$$('.archive-details'))assert.equal(archive.open,false,'outdated rows collapsed');
  }
  await page.select('Darius');assert(page.$('article[data-skill="Q"] .spell-meta').textContent.includes('9/8/7/6/4'));assert(page.$('.spell-data-note').textContent.includes('9/7.75/6.5/5.25/4'));
  await page.select('Jinx');assert.equal(page.$('.stat-value').textContent,'610');page.$('#level').value=18;page.$('#level').dispatchEvent(new page.w.Event('input'));assert.equal(page.$$('.stat-value')[2].textContent,'110');
  await page.select('Varus');page.$('button[data-skill="W"]').click();assert.equal(page.$$('.current-change').length,4);const details=page.$('.archive-details');details.querySelector('summary').click();assert(details.open);
  page.close();
  assert.equal(data(prefix+'Azir.json').stats.mpperlevel,50);assert.equal(data(prefix+'Sion.json').stats.hpperlevel,95);assert.equal(data(prefix+'Viktor.json').stats.movespeed,330);assert.equal(data(prefix+'MonkeyKing.json').stats.hpregen,5.5);
  assert.equal(data(prefix+'LeeSin.json').spells[1].cooldownBurn,'8');assert.equal(data(prefix+'Locke.json').spells[1].costBurn,'60/65/70/75/80');
  assert.equal(data(prefix+'Nunu.json').history[0].changes[0].kind,'buff');assert.equal(data(prefix+'XinZhao.json').history[0].changes.find(ch=>ch.slot==='E').kind,'buff');
 }
 console.log('PASS: 26.21, all 25 champions / 56 changes in KO+EN; new stats, growth, cooldown/cost; all current ability values visible; dated archives; Darius source discrepancy.');
}
main().catch(e=>{console.error(e);process.exitCode=1}).finally(closeAll);
