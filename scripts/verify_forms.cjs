// Compare both forms at the same level using independent PC gameplay fixtures.
const assert=require('node:assert/strict');
const {create,data,until,closeAll}=require('./verify.cjs');
async function checkForms(lang){
 const page=create({url:'https://rift.example/?champion=Jayce&lang='+lang});
 await page.ready('Jayce');
 const value=key=>page.$('[data-form-stat="'+key+'"] strong').textContent;
 const button=key=>page.$('[data-form="'+key+'"]');
 const enter=()=>page.$('.form-link').click();
 const change=(selector,val)=>{
  const el=page.$(selector);el.value=val;el.dispatchEvent(new page.w.Event('input',{bubbles:true}));
 };
 const open=async id=>{await page.select(id);enter();assert(!page.$('#forms').hidden)};
 enter();
 assert(page.$('#overview').hidden && page.$('#history').hidden);
 assert.deepEqual([value('armor'),value('spellblock'),value('attackrange')],['27','35','125']);
 button('cannon').click();
 assert.deepEqual([value('armor'),value('spellblock'),value('attackrange')],['22','30','500']);
 change('#formLevel',6);change('[data-form-input="bonusAD"]',40);
 button('hammer').click();assert.equal(value('armor'),'56.75');
 const link=page.w.location.href;
 page.$('#languageToggle').click();
 await until(()=>!page.$('#content').hidden && page.d.documentElement.lang!==lang,'translated form page');
 assert.equal(value('armor'),'56.75');assert.equal(page.$('[data-form-input="bonusAD"]').value,'40');
 const direct=create({url:link});await direct.ready('Jayce');assert.equal(direct.$('[data-form-stat="armor"] strong').textContent,'56.75');direct.close();
 page.w.history.back();await until(()=>!page.$('#overview').hidden,'back to champion stats');
 await open('Gnar');assert.equal(value('attackrange'),'400');change('#formLevel',18);assert.equal(value('attackrange'),'500');
 button('mega').click();assert.deepEqual([value('armor'),value('spellblock'),value('attackrange')],['149.4','115.1','175']);
 await open('Elise');const armor=value('armor');button('spider').click();
 assert.deepEqual([value('armor'),value('attackrange'),value('movespeed')],[armor,'125','355']);
 await open('Nidalee');button('cougar').click();
 assert.deepEqual([value('armor'),value('spellblock'),value('attackrange')],['32','30','125']);
 await open('Shyvana');assert(button('dragon').disabled);change('#formLevel',6);button('dragon').click();assert.equal(value('attackrange'),'175');
 change('#formLevel',16);assert.equal(value('attackrange'),'225');change('#formLevel',5);assert(button('dragon').disabled);assert.equal(value('attackrange'),'150');
 await open('RekSai');button('burrow').click();assert(['공격 불가','Unavailable'].includes(value('attackrange')));
 await open('Rell');button('dismounted').click();assert.deepEqual([value('armor'),value('spellblock'),value('attackrange')],['34.5','32.2','250']);
 await open('Kled');button('dismounted').click();change('[data-form-input="bonusHP"]',400);change('[data-form-input="enemies"]',5);assert.equal(value('armor'),'55');assert.equal(value('attackrange'),'250');
 await open('KSante');change('#formLevel',6);change('[data-form-input="bonusArmor"]',100);const normal=Number(value('armor'));button('all-out').click();assert(Math.abs(Number(value('armor'))-(normal-85))<0.001);
 await page.select('Ahri');assert(!page.$('.form-link'));assert(!page.$('#overview').hidden);
 page.close();
}
async function main(){
 for(const lang of ['ko','en'])await checkForms(lang);
 const embedded=create({url:'about:srcdoc',fetchOverride:url=>Promise.resolve({
  ok:true,json:async()=>data(url.replace(/^data\//,''))
 })});
 await until(()=>!embedded.$('#content').hidden,'embedded ready');
 await embedded.select('Jayce');
 embedded.$('.form-link').click();
 assert(!embedded.$('#forms').hidden);
 embedded.$('[data-form="cannon"]').click();
 assert.equal(embedded.$('[data-form-stat="attackrange"] strong').textContent,'500');
 embedded.$('.sectionnav [href="#overview"]').click();assert(!embedded.$('#overview').hidden);
 embedded.close();
 console.log('PASS: 9 form profiles, both languages, level thresholds, conditions, direct links, history and embedded view.');
}
main().catch(e=>{console.error(e);process.exitCode=1}).finally(closeAll);
