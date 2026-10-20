// Check both languages against real shipped data and the existing DOM harness.
const assert=require('node:assert/strict');
const {create,until,pause,data,champions,closeAll}=require('./verify.cjs');
async function main(){
 const glossary=data('localization-ko.json');
 const allowed=/AP|AD|[QWERP]{1,2}|FPS|WASD|PC|VFX|SFX|CC|UI|PBE|HP|LCK|MSI|LoL|SKT T1|KDA|K\/DA|RNG|LPL|LCS|LEC|CH-2|CTRL|Shift|Ctrl|DJ|III/gi;
 for(const champion of champions)for(const h of data(champion.id+'.json').history)for(const ch of h.changes)for(const field of ['title','text']){
  const text=glossary.history[ch[field]]||ch[field];assert(!/[A-Za-z]{2,}/.test(text.replace(allowed,'')),champion.id+' untranslated history: '+text);
 }
 const ko=create(),en=create({url:'https://rift.example/?champion=Ahri&lang=en'});
 await Promise.all([ko.ready('Ahri'),en.ready('Ahri')]);
 const leftovers=[];
 for(const champion of champions){
  await ko.select(champion.id);await en.select(champion.id);
  const a=data(champion.id+'.json'),b=data('en/'+champion.id+'.json');
  assert.deepEqual(b.stats,a.stats,champion.id+' numerical stats');assert.deepEqual(b.formulas,a.formulas,champion.id+' formula integrity');assert.equal(b.attackDamageGrowth.value,a.attackDamageGrowth.value);
  assert.equal(en.$$('.spell').length,5);assert(!/\b(?:undefined|NaN)\b|\{\{|%i:/.test(en.$('#content').textContent),champion.id+' unresolved English content');
  const englishBody=en.d.body.cloneNode(true);englishBody.querySelector('#languageToggle').remove();assert(!/[가-힣]/.test(englishBody.textContent),champion.id+' Korean leak into English');
  for(const el of ko.$$('.spell-desc,.flabel,.formula-value,.spell-name')){
   const text=el.textContent.replace(/\b(?:AP|AD|Q|W|E|R|P|H-28G|H-28Q|CH-2|CH-3X)\b/g,'');
   if(/[A-Za-z]{2,}/.test(text)||/%i:/.test(text))leftovers.push([champion.id,text]);
  }
  const tags=ko.$$('.stat-value').map(x=>x.textContent);assert.deepEqual(en.$$('.stat-value').map(x=>x.textContent),tags,champion.id+' displayed level1 stats');
 }
 assert.deepEqual(leftovers,[],'Korean untranslated skill details');
 ko.close();en.close();console.log('PASS: 173 champions in both languages; no unintended language in skills; identical base stats and formulas.');
 const page=create({url:'https://rift.example/?champion=Ahri'});await page.ready('Ahri');
 page.$('[data-skill="Q"]').click();const lv=page.$('#level');lv.value=18;lv.dispatchEvent(new page.w.Event('input'));
 page.$('[data-filter="nerf"]').click();const years=page.$('#yearFilter');years.value='26';years.dispatchEvent(new page.w.Event('change'));
 const stats=page.$$('.stat-value').map(x=>x.textContent),values=page.$$('.formula-value').map(x=>x.textContent),search=page.$('#search');search.value='아리';search.dispatchEvent(new page.w.Event('input'));
 page.$('#languageToggle').click();await until(()=>page.$('.spell-name')?.textContent==='Orb of Deception'&&!page.$('#content').hidden,'English switch');
 assert.equal(page.d.documentElement.lang,'en');assert.equal(page.w.localStorage.getItem('rift-language'),'en');assert.equal(new URL(page.w.location).searchParams.get('lang'),'en');assert.equal(page.$('#level').value,'18');assert.equal(page.$('#yearFilter').value,'26');assert.equal(page.$('[data-filter="nerf"]').getAttribute('aria-pressed'),'true');assert.equal(page.$$('.spell').length,1);assert.equal(page.$('.spell').dataset.skill,'Q');assert.deepEqual(page.$$('.stat-value').map(x=>x.textContent),stats);assert.equal(search.value,'아리');assert(page.$('[data-champion="Ahri"]'));
 assert.deepEqual(page.$$('.formula-value').slice(0,2).map(x=>x.textContent),values.slice(0,2),'verified Q damage identical');
 page.$('#share').click();await pause();assert.equal(new URL(page.copied).searchParams.get('lang'),'en');assert.equal(new URL(page.copied).searchParams.get('champion'),'Ahri');
 page.$('#sourcesOpen').click();assert(!/[가-힣]/.test(page.$('#sourceBody').textContent));page.$('#sourcesClose').click();
 page.$('#languageToggle').click();await until(()=>page.$('.spell-name')?.textContent==='현혹의 구슬'&&!page.$('#content').hidden,'Korean switch');assert.equal(page.$('#levelLabel').textContent,'18레벨');assert.equal(page.$('#yearFilter').value,'26');assert.deepEqual(page.$$('.formula-value').map(x=>x.textContent),values);page.close();
 const saved=create({url:'https://rift.example/?champion=Ashe',savedLanguage:'en'});await saved.ready('Ashe');assert.equal(saved.d.documentElement.lang,'en');saved.close();
 const explicit=create({url:'https://rift.example/?champion=Ashe&lang=ko',savedLanguage:'en'});await explicit.ready('Ashe');assert.equal(explicit.d.documentElement.lang,'ko');explicit.close();
 const mobile=create({url:'https://rift.example/?champion=Lux&lang=en',width:390});await mobile.ready('Lux');mobile.$('#mobileSearch').click();assert(!mobile.$('#sidebarOverlay').hidden);mobile.$('#languageToggle').click();await until(()=>mobile.$('h1')?.textContent==='럭스'&&!mobile.$('#content').hidden,'mobile language switch');assert(mobile.$('#sidebarOverlay').hidden);mobile.close();
 const route=create();await route.ready('Ahri');route.$('#languageToggle').click();await until(()=>route.$('.spell-name')?.textContent==='Essence Theft'&&!route.$('#content').hidden,'route English');await route.select('Lux');route.$('#languageToggle').click();await until(()=>route.$('h1')?.textContent==='럭스'&&!route.$('#content').hidden,'route Korean');route.w.history.back();await until(()=>route.d.documentElement.lang==='en'&&route.$('h1')?.textContent==='Ahri'&&!route.$('#content').hidden,'restore language with history');route.close();
 // Late response from the other language cannot repaint the current locale.
 let release;const race=create({fetchOverride:(url,opts,read)=>url==='data/en/Ahri.json'?new Promise(resolve=>{release=()=>read(url).then(resolve)}):undefined});await race.ready('Ahri');race.$('#languageToggle').click();race.$('#languageToggle').click();await race.ready('Ahri');release();await pause();assert.equal(race.d.documentElement.lang,'ko');assert.equal(race.$('h1').textContent,'아리');race.close();
 console.log('PASS: language preference/deep links; preserved champion, level, skill, season, filter, search; localized share/dialog; mobile toggle; back/forward; language request races.');
}
main().catch(e=>{console.error(e);process.exitCode=1}).finally(closeAll);
