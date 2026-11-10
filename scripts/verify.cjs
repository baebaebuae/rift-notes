// DOM integration checks, without a browser install or external network.
const fs=require('fs'),path=require('path'),assert=require('node:assert/strict');
const {JSDOM}=require(process.env.RIFT_JSDOM||'jsdom');
const root=path.resolve(__dirname,'../dist'),html=fs.readFileSync(path.join(root,'index.html'),'utf8'),script=['forms.js','app.js'].map(file=>fs.readFileSync(path.join(root,file),'utf8')).join('\n');
// JSDOM's default resource loader leaves external @imports unfetched.
const css=fs.readFileSync(path.join(root,'styles.css'),'utf8');
const data=file=>JSON.parse(fs.readFileSync(path.join(root,'data',file),'utf8')),champions=data('index.json').champions;
const pause=()=>new Promise(r=>setTimeout(r,10)),active=new Set();
async function until(test,label){for(let n=0;n<100;n++){if(test())return;await pause()}throw new Error('Timed out: '+label)}
function create({url='https://rift.example/?champion=Ahri',random=.5,width=1200,fetchOverride,fastTimeout=false,savedLanguage}={}){
 const dom=new JSDOM(html,{url,runScripts:'outside-only',pretendToBeVisual:true});active.add(dom);
 const w=dom.window,d=w.document,errors=[],scrolls=[];w.Math.random=()=>random;w.innerWidth=width;if(savedLanguage)w.localStorage.setItem('rift-language',savedLanguage);
 const style=d.createElement('style');style.textContent=css;d.head.append(style);
 const read=async u=>{try{return{ok:true,json:async()=>JSON.parse(fs.readFileSync(path.join(root,new URL(u,w.location.href).pathname),'utf8'))}}catch{return{ok:false,status:404}}};
 w.fetch=(u,o)=>fetchOverride?.(u,o,read)??read(u);
 if(fastTimeout){const timeout=w.setTimeout.bind(w);w.setTimeout=(f,ms,...args)=>timeout(f,ms===15000?20:ms,...args)}
 w.scrollTo=()=>{};w.HTMLElement.prototype.scrollIntoView=function(){scrolls.push(this.id)};
 w.HTMLDialogElement.prototype.showModal=function(){this.open=true};w.HTMLDialogElement.prototype.close=function(){this.open=false};
 let copied='';Object.defineProperty(w.navigator,'clipboard',{value:{writeText:async text=>{copied=text}}});
 w.addEventListener('error',e=>errors.push(e.message));w.eval(script);
 const $=q=>d.querySelector(q),$$=q=>[...d.querySelectorAll(q)];
 return{w,d,$,$$,errors,scrolls,get copied(){return copied},close(){assert.deepEqual(errors,[]);w.close();active.delete(dom)},async ready(id){await until(()=>!$('#content').hidden&&(!id||$('h1')?.textContent===data((d.documentElement.lang==='en'?'en/':'')+id+'.json').name),'render '+id)},async select(id){$(`[data-champion="${id}"]`).click();await this.ready(id)}};
}
async function main(){
 const app=create(),{w,d,$,$$}=app;await app.ready('Ahri');
 assert.equal($$('.spell').length,5);assert.equal($$('.stat').length,7);assert.equal($$('.champion-item').length,173);assert($$('.patch-card').length>0);
 assert.equal(w.getComputedStyle($('.spell-desc')).fontSize,'14px');assert.equal(w.getComputedStyle($('.formula-value')).fontSize,'15px');
 const search=$('#search');for(const query of ['아리','Ahri','ㅇㄹ']){search.value=query;search.dispatchEvent(new w.Event('input'));assert($('[data-champion="Ahri"]'),query)}
 search.value='없는챔피언';search.dispatchEvent(new w.Event('input'));assert($('.list-empty'));search.value='';search.dispatchEvent(new w.Event('input'));
 $('[data-role="Mage"]').click();for(const item of $$('.champion-item'))assert(champions.find(c=>c.id===item.dataset.champion).tags.includes('Mage'));$('[data-role="all"]').click();
 for(const key of ['P','Q','W','E','R']){$(`button[data-skill="${key}"]`).click();assert.equal($$('.spell').length,1);assert.equal($('.spell').dataset.skill,key)}$('button[data-skill="all"]').click();
 const lv=$('#level');lv.value=18;lv.dispatchEvent(new w.Event('input'));assert.equal($('#levelLabel').textContent,'18레벨');assert.equal($('.stat-value').textContent,'2,358');
 $('[data-filter="nerf"]').click();assert(!$('.change p.buff'));$('[data-filter="all"]').click();const old=$$('.patch-card').length;$('#loadMore')?.click();assert($$('.patch-card').length>=old);
 const years=$('#yearFilter');years.value=years.options[1].value;years.dispatchEvent(new w.Event('change'));for(const patch of $$('.patch-version'))assert(patch.textContent.startsWith(years.value+'.'));
 $('#favorite').click();assert.equal($('#favorite').getAttribute('aria-pressed'),'true');assert(JSON.parse(w.localStorage.getItem('rift-favorites')).includes('Ahri'));$('#favorite').click();assert.equal($('#favorite').getAttribute('aria-pressed'),'false');
 $('#share').click();await pause();assert.equal(new URL(app.copied).searchParams.get('champion'),'Ahri');
 $('#sourcesOpen').click();const dialog=$('#sourcesDialog');assert(dialog.open);assert($('#sourceBody').textContent.includes('자동 갱신'));
 dialog.getBoundingClientRect=()=>({left:100,right:500,top:100,bottom:500});dialog.dispatchEvent(new w.MouseEvent('click',{bubbles:true,clientX:120,clientY:120}));assert(dialog.open,'dialog padding should not dismiss');dialog.dispatchEvent(new w.MouseEvent('click',{bubbles:true,clientX:50,clientY:50}));assert(!dialog.open,'dialog backdrop should dismiss');
 for(const champion of champions){await app.select(champion.id);assert.equal($$('.spell').length,5,champion.id);assert(!/\b(?:undefined|NaN)\b|\{\{/.test($('#content').textContent),champion.id+' unresolved values');const expand=$('[data-expand]');if(expand){const label=expand.textContent;expand.click();assert.equal(expand.getAttribute('aria-expanded'),'true');expand.click();assert.equal(expand.textContent,label)}}
 app.close();console.log('PASS: all 173 champions; search/roles; P/Q/W/E/R; level stats; history filters; expanders; favorites/share; larger text; source dialog.');
 for(const random of [0,.5,.999999]){const page=create({url:'https://rift.example/',random}),id=champions[Math.floor(random*champions.length)].id;await page.ready(id);assert.equal(page.w.location.search,'');assert.equal(page.w.history.state.champion,id);page.close()}
 for(const url of ['https://rift.example/?champion=Ahri','https://rift.example/#Ahri']){const page=create({url,random:0});await page.ready('Ahri');assert.equal(new URL(page.w.location).searchParams.get('champion'),'Ahri');page.close()}
 const bad=create({url:'https://rift.example/?champion=not-real',random:0});await bad.ready(champions[0].id);assert.equal(bad.w.location.search,'');bad.close();
 const share=create({url:'https://rift.example/',random:0});await share.ready(champions[0].id);share.w.navigator.clipboard.writeText=async()=>{throw new Error('clipboard denied')};share.$('#share').click();await until(()=>new URL(share.w.location).searchParams.get('champion')===champions[0].id,'share fallback preserves random champion');share.close();
 const route=create({url:'https://rift.example/',random:0});await route.ready(champions[0].id);await route.select('Ahri');const length=route.w.history.length;await route.select('Ahri');assert.equal(route.w.history.length,length,'no duplicate champion history');
 route.w.history.back();await route.ready(champions[0].id);assert.equal(route.w.location.search,'');route.w.history.forward();await route.ready('Ahri');
 route.w.location.hash='history';await until(()=>route.$('.sectionnav a[href="#history"]').classList.contains('active'),'section highlight');assert(route.$('.topnav a[href="#history"]').classList.contains('selected'));
 route.$('[data-home]').click();await route.ready(champions[0].id);assert.equal(route.w.location.hash,'');
 const input=route.$('#search');input.value='아리';input.dispatchEvent(new route.w.Event('input'));input.dispatchEvent(new route.w.KeyboardEvent('keydown',{key:'Enter',isComposing:true,bubbles:true}));await pause();assert.equal(route.$('h1').textContent,champions[0].name);input.dispatchEvent(new route.w.KeyboardEvent('keydown',{key:'Enter',bubbles:true}));await route.ready('Ahri');route.close();
 const anchor=create({url:'https://rift.example/?champion=Ahri#history'});await anchor.ready('Ahri');assert(anchor.scrolls.includes('history'));anchor.close();console.log('PASS: random entry; deep/legacy links; invalid links; back/forward; home; section links; Korean IME.');
 const mobile=create({width:390});await mobile.ready('Ahri');mobile.$('#mobileSearch').click();assert.equal(mobile.$('#mobileSearch').getAttribute('aria-expanded'),'true');assert(!mobile.$('#sidebarOverlay').hidden);assert.equal(mobile.d.activeElement,mobile.$('#search'));
 mobile.$('#sidebarOverlay').click();assert(!mobile.$('#sidebar').classList.contains('open'));assert(mobile.$('#sidebarOverlay').hidden);mobile.$('#mobileSearch').click();mobile.d.dispatchEvent(new mobile.w.KeyboardEvent('keydown',{key:'Escape',bubbles:true}));assert.equal(mobile.$('#mobileSearch').getAttribute('aria-expanded'),'false');mobile.$('#mobileSearch').click();await mobile.select('Ashe');assert(mobile.$('#sidebarOverlay').hidden);mobile.close();
 let pending,failed=true;
 const network=create({fetchOverride:(url,opts,read)=>{if(url==='data/Ashe.json'&&failed)return Promise.resolve({ok:false,status:503});if(url==='data/Ashe.json')return new Promise(resolve=>{pending=()=>read(url).then(resolve)});if(url==='data/Yasuo.json')return new Promise((resolve,reject)=>{pending=()=>reject(new Error('late failure'))})}});
 await network.ready('Ahri');network.$('[data-champion="Ashe"]').click();await until(()=>network.$('#retryChampion'),'failed-request UI');failed=false;network.$('#retryChampion').click();assert(network.$('.spinner'),'retry resets old error');assert.equal(network.$('#main').getAttribute('aria-busy'),'true');pending();await network.ready('Ashe');network.$('[data-champion="Yasuo"]').click();await network.select('Ahri');pending();await pause();assert.equal(network.$('h1').textContent,'아리');assert(!network.$('#retryChampion'));assert.equal(network.$('#main').getAttribute('aria-busy'),'false');network.close();
 let resolveOld;const race=create({fetchOverride:(url,opts,read)=>url==='data/Ashe.json'?new Promise(resolve=>{resolveOld=()=>read(url).then(resolve)}):undefined});await race.ready('Ahri');race.$('[data-champion="Ashe"]').click();await race.select('Lux');resolveOld();await pause();assert.equal(race.$('h1').textContent,'럭스');race.close();
 const timeout=create({fastTimeout:true,fetchOverride:(url,opts)=>url==='data/Ashe.json'?new Promise((resolve,reject)=>opts.signal.addEventListener('abort',()=>reject(new Error('aborted')))):undefined});await timeout.ready('Ahri');timeout.$('[data-champion="Ashe"]').click();await until(()=>timeout.$('#retryChampion'),'request timeout');assert.equal(timeout.$('#main').getAttribute('aria-busy'),'false');timeout.close();
 console.log('PASS: mobile controls; failed-request retry; timeouts; late success/failure isolation.');
}
const closeAll=()=>{for(const dom of active)dom.window.close();active.clear()};
module.exports={create,until,pause,data,champions,closeAll};
if(require.main===module)main().catch(error=>{console.error(error);process.exitCode=1}).finally(closeAll);
