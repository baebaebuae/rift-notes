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
  for(const el of ko.$$('.spell-desc,.flabel,.formula-value,.spell-name,.passive-effect,.passive-variant')){
   const text=el.textContent.replace(/(?<![A-Za-z])(?:AP|AD|[PQWER]{1,2}|H-28G|H-28Q|CH-2|CH-3X)(?![A-Za-z])/g,'');
   if(/[A-Za-z]{2,}/.test(text)||/%i:/.test(text))leftovers.push([champion.id,text]);
  }
  const distanceText=page=>page.$$('.spell-range .formula-value').map(node=>node.textContent.replace('전역','Global'));
  assert.deepEqual(distanceText(ko),distanceText(en),champion.id+' localized distances');
  for(const page of [ko,en]){
   const cards=page.$('#spells');
   for(const row of cards.querySelectorAll('.spell-range .formula-value')){
    assert(!/^(?:0|1|20|40|100|25000|4294967295)$/.test(row.textContent),champion.id+' raw cast parameter shown');
   }

   assert(!cards.querySelector('a,.spell-source,.spell-data-note,.value-provenance,.review-sources,.passive-baseline'));
   assert(!page.$('.quality-note'));
   assert(!/(공식 (변경|문서|패치)|기존 자료|후속 변경|반영한 공식|보관본|patch notes|changes applied through|archived (?:detail|condition)|\b(?:25|26)\.\d+ (?=notes|patch|원문|공식)|\((?:25|26)\.\d+\))/i.test(cards.textContent),champion.id+' card includes patch commentary');
   assert.equal(page.$$('#timeline .patch-card').length>0,(page===ko?a:b).history.length>0);
  }
  const tags=ko.$$('.stat-value').map(x=>x.textContent);assert.deepEqual(en.$$('.stat-value').map(x=>x.textContent),tags,champion.id+' displayed level1 stats');
  // Prose-only passives were silently dropped when their table rows were empty.
  const sourceEffects=a.details.skills.P.effects;
  const koEffects=ko.$$('article[data-skill="P"] .passive-effect'),enEffects=en.$$('article[data-skill="P"] .passive-effect');
  assert.equal(koEffects.length,sourceEffects.length,champion.id+' all passive paragraphs available');
  assert.equal(enEffects.length,koEffects.length,champion.id+' translated passive coverage');
  if(koEffects.length){
   const numbers=s=>(s.match(/\d+(?:\.\d+)?/g)||[]).sort();
   for(let n=0;n<koEffects.length;n++)assert.deepEqual(numbers(koEffects[n].textContent),numbers(enEffects[n].textContent),champion.id+' passive numeric integrity '+n);
   const passive=ko.$('.spell[data-skill="P"]');
   assert(!passive.textContent.includes('세부 수치 미확보'),champion.id+' prose is data, not unavailable');
  }
 }
 assert.deepEqual(leftovers,[],'Korean untranslated skill details');
 await ko.select('MissFortune');
 const fortune=ko.$('.spell[data-skill="P"]');
 assert.match(fortune.textContent,/50%.*100%/);assert.match(fortune.textContent,/25%.*50%/);
 assert.match(fortune.textContent,/총 공격력/);assert.match(fortune.textContent,/미니언/);
 assert(!fortune.textContent.includes('현재 수집 자료에 상세 수치가 포함되어 있지 않습니다.'));
 await ko.select('Aphelios');const more=ko.$('.passive-more');assert(more,'long passive has disclosure');more.open=true;assert(more.querySelectorAll('.passive-effect').length>0);
 ko.close();en.close();console.log('PASS: 173 champions in both languages; no unintended language in skills; identical base stats and formulas.');
 console.log('PASS: all reconciled passive prose and numbers; Miss Fortune total AD/minion ratios; patch history separated from cards; long-passive disclosure.');
 const page=create({url:'https://rift.example/?champion=Ahri'});await page.ready('Ahri');
 page.$('[data-skill="Q"]').click();const lv=page.$('#level');lv.value=18;lv.dispatchEvent(new page.w.Event('input'));
 page.$('[data-filter="nerf"]').click();const years=page.$('#yearFilter');years.value='26';years.dispatchEvent(new page.w.Event('change'));
 const stats=page.$$('.stat-value').map(x=>x.textContent),values=page.$$('.formula-value').map(x=>x.textContent),search=page.$('#search');search.value='아리';search.dispatchEvent(new page.w.Event('input'));
 page.$('#languageToggle').click();await until(()=>page.$('.spell-name')?.textContent==='Orb of Deception'&&!page.$('#content').hidden,'English switch');
 assert.equal(page.d.documentElement.lang,'en');assert.equal(page.w.localStorage.getItem('rift-language'),'en');assert.equal(new URL(page.w.location).searchParams.get('lang'),'en');assert.equal(page.$('#level').value,'18');assert.equal(page.$('#yearFilter').value,'26');assert.equal(page.$('[data-filter="nerf"]').getAttribute('aria-pressed'),'true');assert.equal(page.$$('.spell').length,1);assert.equal(page.$('.spell').dataset.skill,'Q');assert.deepEqual(page.$$('.stat-value').map(x=>x.textContent),stats);assert.equal(search.value,'아리');assert(page.$('[data-champion="Ahri"]'));
 assert.deepEqual(page.$$('.formula-value').slice(0,2).map(x=>x.textContent.match(/\d+(?:\.\d+)?/g)),values.slice(0,2).map(x=>x.match(/\d+(?:\.\d+)?/g)),'verified Q damage identical');
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
 // Inline previews cannot rewrite about:srcdoc URLs when the language changes.
 const preview=create({url:'about:srcdoc',random:0,fetchOverride:url=>Promise.resolve({ok:true,json:async()=>data(url.replace(/^data\//,''))})});
 await preview.ready(champions[0].id);preview.$('#languageToggle').click();
 await until(()=>preview.d.documentElement.lang==='en'&&preview.$('h1')?.textContent===data('en/'+champions[0].id+'.json').name&&!preview.$('#content').hidden,'preview English switch');
 assert.equal(preview.$('#languageToggle').getAttribute('aria-checked'),'true');assert.equal(preview.w.location.href,'about:srcdoc');assert.equal(preview.w.history.state.lang,'en');
 await preview.select('Ahri');const previewLength=preview.w.history.length;await preview.select('Ahri');assert.equal(preview.w.history.length,previewLength);
 await preview.select('Lux');preview.w.history.back();await preview.ready('Ahri');preview.w.history.forward();await preview.ready('Lux');
 preview.$('#languageToggle').click();await until(()=>preview.$('h1')?.textContent==='럭스'&&!preview.$('#content').hidden,'preview Korean switch');
 assert.equal(preview.$('#languageToggle').getAttribute('aria-checked'),'false');assert.equal(preview.w.history.state.lang,'ko');
 preview.$('#share').click();await until(()=>preview.$('#toast').textContent.includes('미리보기'),'preview share feedback');assert.equal(preview.copied,'');
 // Some hosts disable history writes entirely; the content must still switch.
 for(const method of ['pushState','replaceState'])preview.w.history[method]=()=>{throw new preview.w.DOMException('History is unavailable','SecurityError')};
 preview.$('#languageToggle').click();await until(()=>preview.$('h1')?.textContent==='Lux'&&!preview.$('#content').hidden,'history-disabled language switch');await preview.select('Ahri');
 preview.close();console.log('PASS: embedded preview language/champion switching; state-only history; blocked history fallback; unsupported share feedback.');
}
main().catch(e=>{console.error(e);process.exitCode=1}).finally(closeAll);
