const assert=require('node:assert/strict');
const {create,data,until,closeAll}=require('./verify.cjs');

async function checkForms(lang){
 const page=create({url:'https://rift.example/?champion=Jayce&lang='+lang});
 await page.ready('Jayce');
 const value=key=>page.$('[data-stat="'+key+'"] .stat-value').textContent;
 const button=key=>page.$('.stats-heading [data-form="'+key+'"]');
 const changeLevel=n=>{const slider=page.$('#level');slider.value=n;slider.dispatchEvent(new page.w.Event('input'))};
 assert(!page.$('#forms,.form-link,.form-controls,[data-form-input]'));
 assert(!page.$('#overview').hidden && !page.$('#history').hidden);
 assert.equal(page.$$('#statCards .stat').length,7);
 page.$('button[data-skill="Q"]').click();
 const q=page.$('#spells article'),history=page.$('#timeline'),cards=page.$('#statCards');
 const initial=page.w.location.href;
 assert.deepEqual([value('armor'),value('spellblock'),value('attackrange')],['27','35','125']);
 button('cannon').click();
 assert.equal(button('cannon').getAttribute('aria-pressed'),'true');
 assert.equal(page.w.location.href,initial);
 assert.equal(page.$('#spells article'),q);assert.equal(page.$('#timeline'),history);assert.equal(page.$('#statCards'),cards);
 assert.deepEqual([value('armor'),value('spellblock'),value('attackrange')],['22','30','500']);
 changeLevel(6);button('hammer').click();assert.equal(value('armor'),'53.75');
 page.$('#languageToggle').click();
 await until(()=>!page.$('#content').hidden && page.d.documentElement.lang!==lang,'change language');
 assert.equal(value('armor'),'53.75');
 page.$('#share').click();
 await until(()=>page.copied,'share');
 const shared=create({url:page.copied});await shared.ready('Jayce');assert.equal(shared.$('[data-stat="armor"] .stat-value').textContent,'53.75');shared.close();
 await page.select('Nidalee');button('cougar').click();
 assert.deepEqual([value('armor'),value('spellblock'),value('attackrange')],['32','30','125']);
 await page.select('Elise');button('spider').click();assert.deepEqual([value('movespeed'),value('attackrange')],['355','125']);
 await page.select('Gnar');assert.equal(value('attackrange'),'400');changeLevel(18);
 assert.deepEqual([value('attackrange'),value('movespeed')],['500','355']);
 button('mega').click();assert.deepEqual([value('armor'),value('spellblock'),value('attackrange'),value('hp'),value('attackdamage')],['149.4','115.1','175','2,714','162.9']);
 await page.select('Shyvana');assert(button('dragon').disabled);changeLevel(6);button('dragon').click();
 assert.equal(value('attackrange'),'175');changeLevel(16);assert.equal(value('attackrange'),'225');
 changeLevel(5);assert(button('dragon').disabled);assert.equal(value('attackrange'),'150');assert.equal(button('human').getAttribute('aria-pressed'),'true');
 await page.select('Rell');button('dismounted').click();assert.deepEqual([value('armor'),value('spellblock'),value('attackrange')],['34.5','32.2','250']);
 await page.select('RekSai');button('burrow').click();assert(['공격 불가','Unavailable'].includes(value('attackrange')));
 await page.select('Kled');assert.equal(value('hp'),'810');button('dismounted').click();assert.deepEqual([value('hp'),value('armor'),value('movespeed'),value('attackrange')],['410','39','305','250']);
 await page.select('KSante');changeLevel(6);button('all-out').click();assert(page.$('[data-stat="hp"] .stat-sub').textContent.includes('65%'));
 await page.select('Ahri');assert(!page.$('.form-switch,.form-link,#forms'));assert.equal(page.$$('#spells article').length,5);
 page.close();
}
async function main(){
 for(const lang of ['ko','en'])await checkForms(lang);
 const old=create({url:'https://rift.example/?champion=Jayce#forms/cannon?level=11'});await old.ready('Jayce');
 assert.equal(old.w.location.hash,'#overview');assert(!old.$('#overview').hidden);
 assert.equal(old.$('[data-form="cannon"]').getAttribute('aria-pressed'),'true');assert.equal(old.$('#level').value,'11');old.close();
 const embedded=create({url:'about:srcdoc',fetchOverride:url=>Promise.resolve({ok:true,json:async()=>data(url.replace(/^data\//,''))})});
 await until(()=>!embedded.$('#content').hidden,'embedded ready');await embedded.select('Jayce');embedded.$('[data-form="cannon"]').click();
 assert.equal(embedded.$('[data-stat="attackrange"] .stat-value').textContent,'500');embedded.close();
 console.log('PASS: inline form buttons; 9 champions; both languages; unchanged skill/history nodes; legacy links and embedded view.');
}
main().catch(error=>{console.error(error);process.exitCode=1}).finally(closeAll);
