'use strict';
const $=(q,el=document)=>el.querySelector(q),$$=(q,el=document)=>[...el.querySelectorAll(q)];
const esc=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const strip=s=>String(s??'').replace(/%i:[^%]+%/g,'').replace(/<[^>]*>/g,' ').replace(/\s+/g,' ').trim();
const num=n=>Number.isFinite(Number(n))?Number(Number(n).toFixed(2)).toLocaleString('en-US'):String(n);
const norm=s=>String(s??'').toLowerCase().replace(/[\s'’.·\-]/g,'');
const chosung=s=>[...s].map(c=>{const n=c.charCodeAt(0)-44032;return n>=0&&n<=11171?'ㄱㄲㄴㄷㄸㄹㅁㅂㅃㅅㅆㅇㅈㅉㅊㅋㅌㅍㅎ'[Math.floor(n/588)]:c}).join('');
const patchName=v=>{if(!v)return t('미확인','unknown');let[a,b]=v.split('.').map(Number);return `${a>=15&&a<20?a+10:a}.${b}`};
let storedLanguage='ko';try{storedLanguage=localStorage.getItem('rift-language')||'ko'}catch{}
const routeLanguage=()=>{const l=new URLSearchParams(location.search).get('lang');return ['ko','en'].includes(l)?l:null};
let lang=routeLanguage()||(['ko','en'].includes(storedLanguage)?storedLanguage:'ko');
const t=(ko,en)=>lang==='en'?en:ko;
const roleName=r=>lang==='en'?({Marksman:'Marksman'}[r]||r):({Fighter:'전사',Mage:'마법사',Assassin:'암살자',Marksman:'원거리 딜러',Tank:'탱커',Support:'서포터'}[r]||r);
const typeName=k=>({buff:t('상향','Buff'),nerf:t('하향','Nerf'),adjust:t('조정','Adjustment'),fix:t('수정','Fix')})[k];
const officialNews=()=>`https://www.leagueoflegends.com/${lang==='ko'?'ko-kr':'en-us'}/news/game-updates/`;
let index,meta,indexes={},current,chosen=null,role='all',filter='all',year='all',limit=10,skill='all',level=1,requestId=0,overrides={},glossary={},toastTimer;
let favorites=new Set();try{favorites=new Set(JSON.parse(localStorage.getItem('rift-favorites')||'[]'))}catch{}
const cache=new Map(),cdn=(folder,file)=>`https://ddragon.leagueoflegends.com/cdn/${meta.version}/img/${folder}/${file}`,champIcon=id=>`assets/champions/${id}.png`;
function toast(s){$('#toast').textContent=s;$('#toast').classList.add('visible');clearTimeout(toastTimer);toastTimer=setTimeout(()=>$('#toast').classList.remove('visible'),2500)}
async function json(url){const controller=new AbortController(),timeout=setTimeout(()=>controller.abort(),15000);try{const r=await fetch(url,{signal:controller.signal,cache:'no-cache'});if(!r.ok)throw new Error(`${r.status}: ${url}`);return await r.json()}finally{clearTimeout(timeout)}}
function applyStaticLanguage(){
 document.documentElement.lang=lang;document.title=t('RIFT NOTES · 챔피언을 더 깊이','RIFT NOTES · Know your champion');
 $('meta[name="description"]').content=t('챔피언 스킬과 능력치, 공식 패치 기록을 한곳에서.','Champion abilities, stats, and official patch history in one place.');
 const texts={'.brand small':t('리그 오브 레전드 챔피언 기록','LEAGUE OF LEGENDS CHAMPION ARCHIVE'),'.topnav a[href="#overview"]':t('챔피언 도감','Champions'),'.topnav a[href="#history"]':t('패치 기록','Patch history'),'.searchhint':t('이름 · 영문 · 초성으로 검색하세요','Search by English or Korean name'),'.sidebar-foot>div':null,'#footerSources':t('데이터 출처 · 수집 범위','Sources & coverage'),'.dialog-head h2':t('어떤 데이터를 보고 있나요?','About this data'),'.dialog-head .eyebrow':t('데이터 안내','ABOUT THE DATA')};
 for(const [q,value]of Object.entries(texts))if(value!==null)$(q).textContent=value;
 $('.sidebar-title').firstChild.textContent=t('챔피언 ','CHAMPIONS ');
 $('.sidebar-foot>div').innerHTML=t('플레이 전에, 한 번 더.<small>스킬부터 변화의 흐름까지.</small>','One more look before you play.<small>Abilities and how they have changed.</small>');
 $('footer>p').textContent=t('챔피언의 수치와, 쌓여온 변화의 기록.','Champion numbers. A history of change.');
 $('.legal').textContent=t('라이엇 게임즈의 공식 서비스가 아닌 팬 제작 도구입니다. 라이엇 게임즈와 리그 오브 레전드 및 관련 자산의 상표권은 라이엇 게임즈에 있습니다. 본 사이트는 라이엇 게임즈의 견해를 대변하지 않습니다.','RIFT NOTES is not endorsed by Riot Games and does not reflect its views. Riot Games, League of Legends, and all associated properties are trademarks or registered trademarks of Riot Games, Inc.');
 $('#search').placeholder=t('챔피언 검색','Search champions');$('#search').setAttribute('aria-label',t('챔피언 이름, 영문, 초성 검색','Search champion names in English or Korean'));
 $('#championList').setAttribute('aria-label',t('챔피언 목록','Champion list'));
 for(const [id,ko,en]of [['mobileSearch','챔피언 검색 열기','Open champion search'],['closeSidebar','검색 닫기','Close search'],['sidebarOverlay','챔피언 검색 닫기','Close champion search'],['sourcesOpen','데이터 출처 및 기준 보기','View sources and data versions'],['sourcesClose','닫기','Close']])$('#'+id).setAttribute('aria-label',t(ko,en));
 $$('[data-home]').forEach(a=>a.setAttribute('aria-label',t('리프트 노트 홈','Rift Notes home')));
 $$('[data-role]').forEach(b=>b.textContent=b.dataset.role==='all'?t('전체','All'):b.dataset.role==='Marksman'?t('원딜','Marksman'):roleName(b.dataset.role));
 $('#languageToggle').setAttribute('aria-checked',String(lang==='en'));$('#languageToggle').setAttribute('aria-label',t('영어 사용','Use English'));
 $('#versionLabel').textContent=meta?`${t('패치','PATCH')} ${meta.patch}`:t('데이터 불러오는 중','Loading data');
 if(index)$('#championCount').textContent=index.length;
}
function validChampion(id){return Boolean(index?.some(c=>c.id===id))}
function randomChampion(exclude){const candidates=index.filter(c=>c.id!==exclude),list=candidates.length?candidates:index;return list[Math.floor(Math.random()*list.length)].id}
function locationChampion(){const id=new URLSearchParams(location.search).get('champion');if(validChampion(id))return id;const legacy=location.hash.slice(1);return validChampion(legacy)?legacy:null}
function saveHistory(method,state,url=location.href){
 // about:srcdoc and other embedded documents do not have a writable site URL.
 const canChangeURL=/^https?:$/.test(location.protocol);
 try{if(canChangeURL)history[method](state,'',url);else history[method](state,'');return canChangeURL}catch(error){
  if(error.name!=='SecurityError')throw error;
  // A host may also restrict history writes on an HTTP(S) page.
  if(canChangeURL)try{history[method](state,'')}catch(fallbackError){if(fallbackError.name!=='SecurityError')throw fallbackError}
  return false;
 }
}
function rememberChampion(id){saveHistory('replaceState',{...history.state,champion:id,lang})}
function setSidebar(open){$('#sidebar').classList.toggle('open',open);$('#mobileSearch').setAttribute('aria-expanded',String(open));$('#sidebarOverlay').hidden=!(open&&window.innerWidth<=680)}
function syncSectionNav(){const section=location.hash==='#history'?'#history':'#overview';$$('.topnav a,.sectionnav a').forEach(a=>{if(!['#history','#overview'].includes(a.getAttribute('href')))return;const active=a.getAttribute('href')===section;a.classList.toggle(a.closest('.topnav')?'selected':'active',active);if(active)a.setAttribute('aria-current','location');else a.removeAttribute('aria-current')})}
function scrollToSection(){if(['#history','#overview'].includes(location.hash))$(location.hash)?.scrollIntoView?.({block:'start'})}
function matches(c,q){const n=norm(q);return !n||[c.name,c.id,c.englishName,c.koreanName,chosung(c.koreanName||c.name),...(c.aliases||[])].some(v=>norm(v).includes(n))}
function renderList(){if(!index)return;const q=$('#search').value,list=index.filter(c=>matches(c,q)&&(role==='all'||c.tags.includes(role))).sort((a,b)=>a.name.localeCompare(b.name,lang));$('#resultCount').textContent=t(`${list.length}명`,`${list.length}`);$('#listLabel').textContent=q?t('검색 결과','Search results'):role==='all'?t('모든 챔피언','All champions'):roleName(role);$('#championList').innerHTML=list.length?list.map(c=>`<button class="champion-item ${c.id===chosen?'active':''}" data-champion="${esc(c.id)}" aria-label="${esc(t(c.name+' 상세 보기','View '+c.name))}" ${c.id===chosen?'aria-current="true"':''}><img src="${champIcon(c.id)}" alt="" loading="lazy" width="33" height="33"><span><span class="name">${esc(c.name)}</span><small>${esc(c.title)}</small></span></button>`).join(''):`<div class="list-empty">${t('검색 결과가 없어요.','No champions found.')}<br><small>${t('아리, Ahri, ㅇㄹ처럼 검색해 보세요.','Try Ahri, Lux, or a Korean name.')}</small></div>`}
function updateURL(id){const url=new URL(location.href);url.searchParams.set('champion',id);if(lang==='en'||url.searchParams.has('lang'))url.searchParams.set('lang',lang);url.hash='';const same=url.href===location.href||(history.state?.champion===id&&history.state?.lang===lang);saveHistory(same?'replaceState':'pushState',{champion:id,lang},url)}
function setLocale(next){lang=next;index=indexes[lang].champions;meta=indexes[lang].meta;try{localStorage.setItem('rift-language',lang)}catch{}applyStaticLanguage()}
async function changeLanguage(next){
 if(!index||next===lang)return;
 const savedScroll=window.scrollY;setLocale(next);
 const url=new URL(location.href);url.searchParams.set('lang',lang);url.searchParams.set('champion',chosen);saveHistory('replaceState',{...history.state,champion:chosen,lang},url);
 $('#toast').classList.remove('visible');if($('#sourcesDialog').open)openSources();
 const request=requestId+1;await selectChampion(chosen,false,true);if(request===requestId)window.scrollTo({top:savedScroll,behavior:'instant'});
}
async function selectChampion(id,push=true,preserve=false){
 if(!validChampion(id))return;chosen=id;const req=++requestId,requestLanguage=lang;
 if(!preserve){filter='all';year='all';limit=10;skill='all';level=1}
 renderList();setSidebar(false);if(push)updateURL(id);
 $('#main').setAttribute('aria-busy','true');$('#loading').innerHTML=`<span class="spinner" aria-hidden="true"></span>${t('챔피언 기록을 불러오고 있어요.','Loading champion records…')}`;$('#loading').hidden=false;$('#loading').style.display='flex';$('#content').hidden=true;
 try{const cacheKey=requestLanguage+':'+id;let c=cache.get(cacheKey);if(!c){c=await json(`data/${requestLanguage==='en'?'en/':''}${id}.json`);cache.set(cacheKey,c)}if(req!==requestId)return;
  current=c;if(year!=='all'&&!c.history.some(h=>h.patch.startsWith(year+'.')))year='all';renderChampion();syncSectionNav();document.title=t(`${c.name} · 스킬과 패치 기록 | RIFT NOTES`,`${c.name} · Abilities & patch history | RIFT NOTES`);$('#loading').style.display='none';$('#content').hidden=false;
  if(push)window.scrollTo({top:0,behavior:'instant'});else if(!preserve)scrollToSection();
 }catch{if(req!==requestId)return;$('#loading').innerHTML=`<div class="error-box" role="alert">${t('챔피언 데이터를 불러오지 못했어요.<br>잠시 후 다시 시도해 주세요.','Could not load this champion.<br>Please try again.')}<button id="retryChampion">${t('다시 불러오기','Retry')}</button></div>`;$('#retryChampion').onclick=()=>selectChampion(id,false,preserve)}finally{if(req===requestId)$('#main').setAttribute('aria-busy','false')}
}
function verified(){const v=overrides[lang]?.[current.id];return v?.version===meta.version?v:null}
function hero(){const c=current,splash=`https://ddragon.leagueoflegends.com/cdn/img/champion/splash/${c.id}_0.jpg`;return `<div class="breadcrumb"><span>${t('챔피언 도감','Champions')}</span><span>›</span><strong>${esc(c.name)}</strong></div><section class="hero" aria-label="${esc(t(c.name+' 소개','About '+c.name))}"><img class="hero-art" src="${c.id==='Ahri'?'assets/ahri-splash.jpg':splash}" alt="" fetchpriority="high"><div class="hero-shade"></div><div class="hero-content"><div class="eyebrow">${t('오늘 살펴볼 챔피언','CHAMPION SPOTLIGHT')}</div><h1>${esc(c.name)}</h1>${lang==='en'?'':`<div class="english">${t('스킬과 변화의 기록','')}</div>`}<div class="hero-description">${esc(c.title)}</div><div class="tags">${c.tags.map(r=>`<span class="tag">${esc(roleName(r))}</span>`).join('')}<span class="tag patch">${t(meta.patch+' 능력치 기준','Stats: patch '+meta.patch)}</span></div></div><div class="hero-actions"><button id="favorite" aria-label="${favorites.has(c.id)?t('즐겨찾기 해제','Remove favorite'):t('즐겨찾기 저장','Save favorite')}" aria-pressed="${favorites.has(c.id)}">${favorites.has(c.id)?'★':'☆'}</button><button id="share" aria-label="${t('챔피언 링크 복사','Copy champion link')}">↗</button></div><div class="hero-caption">${t('챔피언을 더 깊이.','KNOW YOUR CHAMPION.')}</div></section><nav class="sectionnav"><a class="active" href="#overview">${t('스킬 · 능력치','Abilities & stats')}</a><a href="#history">${t('패치 기록','Patch history')} <span class="muted">${c.history.length}</span></a><a class="patchlink" target="_blank" rel="noopener" href="${officialNews()}">${t('공식 패치 노트','Official patch notes')} ↗</a></nav>`}
function growth(l){return(.7025+.0175*(l-1))*(l-1)}
function statValue(key){const s=current.effectiveStats||current.stats,g=s[key+'perlevel']??(key==='attackdamage'?current.attackDamageGrowth?.value:undefined);return(s[key]||0)+(g||0)*growth(level)}
function renderStats(){const s=current.effectiveStats||current.stats,defs=[['hp',t('체력','Health'),'♡'],['mp',current.partype||t('자원','Resource'),'◈'],['attackdamage',t('공격력','Attack damage'),'⚔'],['armor',t('방어력','Armor'),'⬡'],['spellblock',t('마법 저항력','Magic resist'),'◇'],['movespeed',t('이동 속도','Move speed'),'↟']];$('#statCards').innerHTML=defs.map(([k,name,icon])=>`<div class="stat"><div class="stat-label"><span class="stat-icon">${icon}</span>${esc(name)}</div><div class="stat-value">${k==='attackdamage'&&level>1&&current.attackDamageGrowth?.value==null?t('확인 필요','Unknown'):num(statValue(k))}</div><div class="stat-sub">${k==='attackdamage'?current.attackDamageGrowth?.value!=null?`${t('보완 성장 계수','Adjusted growth')} <strong>+${num(current.attackDamageGrowth.value)}</strong>`:t('성장값 미제공','Growth unavailable'):s[k+'perlevel']?`${t('성장 계수','Growth')} <strong>+${num(s[k+'perlevel'])}</strong>`:t('고정 기본값','Fixed base value')}</div></div>`).join('');$('#levelLabel').textContent=t(`${level}레벨`,`Lv. ${level}`);$('#statDetails').innerHTML=`<span>${t('기본 공격 속도','Base attack speed')} <b>${num(s.attackspeed)}</b> · ${t('성장','growth')} ${num(s.attackspeedperlevel)}%</span><span>${t('사거리','Attack range')} <b>${num(s.attackrange)}</b></span><span>${t('체력 재생 / 5초','Health regen / 5s')} <b>${num(statValue('hpregen'))}</b></span><span>${t('자원 재생 / 5초','Resource regen / 5s')} <b>${num(statValue('mpregen'))}</b></span>`;if(current.statConflicts?.length)$('#statDetails').innerHTML+=`<span class="stat-source-note">${t('일부 이전 패치의 능력치와 현재 공식 데이터가 다릅니다. 위 표는 현재 공식 데이터를 유지합니다.','Some older patch values differ from current official data. The table retains current official values.')}</span>`}
function label(s){return lang==='en'?s:glossary.labels?.[s]||s}
function unit(s){return lang==='en'?String(s||''):glossary.units?.[s]??String(s||'')}
function historyText(s){return lang==='ko'?glossary.history?.[s]||s:s}
function variant(s){return lang==='en'?s:glossary.variants?.[s]||s}
function modifier(m){const values=m.values||[],units=m.units||[];if(!values.length)return '—';if(values.every(v=>v===values[0])&&units.every(u=>u===units[0]))return esc(num(values[0]))+esc(unit(units[0]));if(units.every(u=>u===units[0]))return values.map(v=>esc(num(v))).join(' / ')+esc(unit(units[0]));return values.map((v,i)=>esc(num(v))+esc(unit(units[i]))).join(' / ')}
function formula(row){if(row.value)return `<span class="formula-value">${esc(row.value)}</span>`;return `<span class="formula-value">${(row.modifiers||[]).map((m,i)=>`<span class="${i?'scaling '+((m.units||[]).some(u=>u.includes('AD'))?'ad':''):'ranks'}">${i?'+ ':''}${modifier(m)}</span>`).join('')}</span>`}
function spellRows(key){const v=verified();if(v?.skills?.[key])return{rows:v.skills[key],isCurrent:true};const a=current.formulas.find(x=>x.slot===key);return{rows:(a?.variants||[]).flatMap(x=>x.rows.map(row=>({...row,variant:a.variants.length>1?x.name:null}))),isCurrent:false}}
function passiveEffects(){
 const archive=current.formulas.find(x=>x.slot==='P');
 const translated=glossary.passives?.[current.id];
 const variants=lang==='en'?archive?.variants:translated?.version===current.formulaVersion?translated.variants:[];
 return(variants||[]).flatMap(v=>(v.effects||[]).map(text=>({text,name:variants.length>1?v.name:null})));
}
function effectText(text){
 // Escape source text before adding numeric emphasis; never render source HTML.
 return String(text).split(/(\d+(?:\.\d+)?%?)/g).map((part,i)=>i%2?`<strong>${esc(part)}</strong>`:esc(part)).join('');
}
function reconciled(){const d=current.details;return d?.version===meta.version&&d.patch===meta.patch?d:null}
const spellFields={
 cooldown:/^(?:재사용 대기시간|Cooldown)$/i,
 cost:/^(?:마나 소모량?|소모량|Mana cost|Cost)$/i,
 range:/^(?:시전 사거리|사거리|Cast range|Range)$/i
};
function ranks(value){
 const numeric=String(value??'').replace(/\b(?:seconds?|mana)\b|초|마나|(?<=\d)s\b|\s/gi,'');
 return /^\d+(?:\.\d+)?(?:\/\d+(?:\.\d+)?)*$/.test(numeric)?numeric:null;
}
function detailValue(rows,field,fallback){
 const row=rows.find(r=>r.provenance!=='baseline'&&spellFields[field].test(r.attribute.trim()));
 return ranks(row?.value)??fallback;
}
function displayDistances(review, rawRange){
 const reviewedCast=detailValue(review?.rows??[],'range',null);
 if(review?.distance && !reviewedCast)return review.distance.rows;
 // Data Dragon also uses tiny and map-scale values for self casts and internal targeting.
 // A distance confirmed in a patch can legitimately be long (e.g. Briar R at 12000).
 const raw=ranks(rawRange);
 const usable=raw && raw.split('/').every(n=>Number(n)>100 && Number(n)<10000);
 const value=reviewedCast??(usable?raw:null);
 return value?[{label:t('사거리','Range'),value}]:[];
}
function effectDetails(effects){
 if(!effects.length)return '';
 const paragraphs=effects.map(e=>`<p class="passive-effect">${e.name?`<b class="passive-variant">${esc(e.name)}</b>`:''}${effectText(e.text)}</p>`);
 const extra=paragraphs.length-3;
 return `<div class="passive-details">${paragraphs.slice(0,3).join('')}${extra>0?`<details class="passive-more"><summary>${t(`상세 설명 ${extra}개 더 보기`,`Show ${extra} more details`)}</summary>${paragraphs.slice(3).join('')}</details>`:''}</div>`;
}
function numericRows(key,rows){
 if(!rows.length)return '';
 const visible=4,extra=rows.length-visible;
 const list=rows.map((row,i)=>`<div${i>=visible?' class="spell-extra"':''}>${row}</div>`).join('');
 return `<div class="spell-rows">${list}</div>${extra>0?`<button class="spell-expander" data-expand="${key}" aria-expanded="false">${t(`세부 수치 ${extra}개 더 보기`,`Show ${extra} more values`)} ⌄</button>`:''}`;
}
function formulaRow(name,value){
 return `<div class="formula-row"><span class="flabel">${esc(name)}</span>${value}</div>`;
}
function reviewedRow(row){
 return formulaRow(row.attribute,`<span class="formula-value">${effectText(row.value)}</span>`);
}
function legacyAbility(key){
 const {rows,isCurrent}=spellRows(key);
 const baseline=patchName(current.formulaVersion);
 const history=isCurrent?[]:current.history.filter(h=>!current.formulaVersion||h.patch.localeCompare(baseline,'en',{numeric:true})>0);
 const changes=history.flatMap(h=>h.changes.filter(ch=>ch.slot===key));
 // With no reviewed profile, prefer known final values over superseded archive formulas.
 if(changes.length){
  const latest=new Map();
  for(const change of changes){
   const text=historyText(change.text),colon=text.indexOf(':'),arrow=text.search(/⇒|→/);
   if(colon<0||arrow<=colon)continue;
   const attribute=text.slice(0,colon).trim(),value=text.slice(arrow+1).trim();
   if(value&&!latest.has(attribute))latest.set(attribute,{attribute,value});
  }
  const finalRows=[...latest.values()];
  return {rows:finalRows.map(reviewedRow),effects:[],cooldown:legacyCooldown(finalRows)};
 }
 return {
  rows:rows.map(r=>formulaRow((r.variant?variant(r.variant)+' · ':'')+label(r.attribute),formula(r))),
  effects:key==='P'&&!isCurrent?passiveEffects().filter(e=>!/^See .* for (more |full )?details|원문.*참고|원본 자료의 소환물/.test(e.text)):[]
 };
}
function legacyCooldown(rows){
 const row=rows.find(r=>/^(?:재사용 대기시간|Cooldown)$/i.test(r.attribute.trim()));
 const value=row?.value.replace(/(?:seconds?|초|s)$|\s+/gi,'');
 return ranks(value);
}
function renderSpell(key,i){
 const passive=key==='P',spell=passive?current.passive:current.spells[i];
 if(!spell)return '';
 const review=reconciled()?.skills?.[key];
 const rawRows=review?.rows??[];
 const legacy=review?null:legacyAbility(key);
 const cooldown=passive?'':detailValue(rawRows,'cooldown',legacy?.cooldown??spell.cooldownBurn);
 const cost=passive?'':detailValue(rawRows,'cost',spell.costBurn);
 const distances=passive?[]:displayDistances(review,spell.rangeBurn);
 const fields={cooldown,cost,range:detailValue(rawRows,'range',null)};
 const rows=review?rawRows.filter(row=>!Object.keys(fields).some(field=>
  spellFields[field].test(row.attribute.trim())&&ranks(row.value)!==null&&ranks(row.value)===ranks(fields[field])
 )).map(reviewedRow):legacy.rows;
 const effects=review?review.effects.map(text=>({text})):legacy.effects;
 const meta=passive?t('기본 지속 효과','Passive'):`<div>${t('재사용','Cooldown')} <b>${esc(cooldown)}${t('초','s')}</b></div><div>${esc(current.partype||t('자원','Resource'))} <b>${esc(cost)}</b></div>`;
 return `<article class="spell${passive?' passive':''}" data-skill="${key}">
  <div class="spell-top"><div class="spell-icon"><img src="${cdn(passive?'passive':'spell',spell.image.full)}" alt="" loading="lazy"><b>${key}</b></div>
   <div class="spell-name">${esc(spell.name)}</div><div class="spell-meta">${meta}</div></div>
  <p class="spell-desc">${esc(strip(spell.description))}</p>
  ${numericRows(key,rows)}${effectDetails(effects)}
  ${distances.map(({label,value})=>`<div class="spell-range formula-row"><span class="flabel">${esc(label)}</span><span class="formula-value">${esc(value)}</span></div>`).join('')}
 </article>`;
}
function renderSpells(){const keys=skill==='all'?['P','Q','W','E','R']:[skill];$('#spells').innerHTML=keys.map(k=>renderSpell(k,['Q','W','E','R'].indexOf(k))).join('');$$('.skill-tabs button').forEach(b=>{b.classList.toggle('active',b.dataset.skill===skill);b.setAttribute('aria-pressed',String(b.dataset.skill===skill))})}
function renderChampion(){
 const c=current;
 $('#content').innerHTML=hero()+`<section id="overview"><div class="section-title"><h2>${t('기본 능력치','Base stats')}</h2><label class="levelcontrol">${t('챔피언 레벨','Level')} <input id="level" type="range" min="1" max="18" value="${level}" aria-label="${t('챔피언 레벨','Champion level')}"><strong id="levelLabel"></strong></label></div><div class="stats" id="statCards"></div><div class="stat-footnote"><span>${t('아이템·룬·특수 패시브 제외 · 공격력 성장값은 보관본과 공식 변경으로 보완','Excludes items, runes, and special passives · AD growth reconciled with archived data and official changes')}</span><span>Data Dragon ${esc(c.version)}</span></div><div class="stat-details" id="statDetails"></div><div class="section-title spells-head"><h2>${t('스킬 상세','Abilities')}</h2><div class="legend"><span><i class="ap"></i>AP ${t('주문력 계수','scaling')}</span><span><i class="ad"></i>AD ${t('공격력 계수','scaling')}</span></div></div><div class="skill-tabs" aria-label="${t('스킬 필터','Ability filter')}"><button data-skill="all">${t('전체 스킬','All abilities')}</button>${['P','Q','W','E','R'].map(k=>`<button data-skill="${k}">${k}</button>`).join('')}</div><div class="spells" id="spells"></div><div class="skills-footer"><span>${t('AP = 주문력 · AD = 공격력 · / 구분 = 스킬 랭크 순서 · 적 방어력 적용 전 수치','AP = ability power · AD = attack damage · / separates ability ranks · Before enemy resistances')}</span></div></section><section id="history"><div class="section-title history-title"><h2>${t('패치 기록','Patch history')} <span class="history-count">${c.history.length}</span></h2><span class="muted history-order">${t('최신순으로 모아보기','Newest first')} ↓</span></div><div class="history-controls"><div class="history-filters" aria-label="${t('패치 변경 유형','Change type')}">${['all','buff','nerf','adjust','fix'].map(k=>`<button data-filter="${k}">${k==='all'?t('전체','All'):typeName(k)}</button>`).join('')}</div><label class="selectwrap">${t('패치 버전','Season')} <select id="yearFilter" aria-label="${t('패치 시즌 필터','Patch season filter')}"><option value="all">${t('전체 시즌','All seasons')}</option>${[...new Set(c.history.map(h=>h.patch.split('.')[0]))].map(y=>`<option value="${esc(y)}" ${y===year?'selected':''}>${esc(y)}.x</option>`).join('')}</select></label></div><div class="timeline" id="timeline"></div><div id="historyMore"></div><div class="history-coverage">${t(`수집 범위 ${meta.earliestPatch}–${meta.latestPatch} · 공식 챔피언 항목 기준, 별도 버그 수정·게임 모드 및 일부 문서 제외`,`Coverage: ${meta.earliestPatch}–${meta.latestPatch} · Champion sections only; excludes separate bug-fix sections, other game modes, and some articles`)}<a target="_blank" rel="noopener" href="https://wiki.leagueoflegends.com/en-us/${encodeURIComponent(c.englishName.replaceAll(' ','_'))}/Patch_history">${t('이전 기록은 LoL 위키에서','Earlier records on the LoL Wiki')} ↗</a></div></section>`;
 renderStats();renderSpells();renderHistory();
 $('#level').oninput=e=>{level=+e.target.value;renderStats()};$('#yearFilter').onchange=e=>{year=e.target.value;limit=10;renderHistory()};
 $('#favorite').onclick=()=>{favorites.has(c.id)?favorites.delete(c.id):favorites.add(c.id);try{localStorage.setItem('rift-favorites',JSON.stringify([...favorites]))}catch{}const yes=favorites.has(c.id);$('#favorite').textContent=yes?'★':'☆';$('#favorite').setAttribute('aria-pressed',yes);$('#favorite').setAttribute('aria-label',yes?t('즐겨찾기 해제','Remove favorite'):t('즐겨찾기 저장','Save favorite'));toast(yes?t('이 브라우저에 즐겨찾기를 저장했어요.','Saved to favorites in this browser.'):t('즐겨찾기를 해제했어요.','Removed from favorites.'))};
 $('#share').onclick=async()=>{
  if(!/^https?:$/.test(location.protocol)){toast(t('미리보기에서는 공유 링크를 만들 수 없어요. 사이트에서 다시 시도해 주세요.','Sharing is unavailable in this preview. Try again on the site.'));return}
  const url=new URL(location.href);url.searchParams.set('champion',c.id);url.searchParams.set('lang',lang);url.hash='';
  try{await navigator.clipboard.writeText(url.href);toast(t('챔피언 링크를 복사했어요.','Champion link copied.'))}catch{
   const saved=saveHistory('replaceState',{...history.state,champion:c.id,lang},url);
   toast(saved?t('주소창의 챔피언 링크를 복사해 주세요.','Copy the champion link from the address bar.'):t('링크를 복사하지 못했어요. 사이트에서 다시 시도해 주세요.','Could not copy the link. Try again on the site.'));
  }
 };
 $('.hero-art').onerror=e=>{e.target.style.display='none'};
}
function delta(text){const parts=text.split(/⇒|→/);if(parts.length!==2)return esc(text);const[a,b]=parts,i=a.indexOf(':');return `${i>=0?esc(a.slice(0,i+1))+' ':''}<span class="oldvalue">${esc(i>=0?a.slice(i+1):a)}</span><span class="arrow">→</span><span class="newvalue">${esc(b)}</span>`}
function patchType(changes){const all=new Set(changes.map(c=>c.kind));return all.size===1?[...all][0]:'adjust'}
function renderHistory(){
 const found=current.history.filter(h=>year==='all'||h.patch.startsWith(year+'.')).map(h=>({...h,changes:h.changes.filter(c=>filter==='all'||c.kind===filter)})).filter(h=>h.changes.length),shown=found.slice(0,limit);
 $('#timeline').innerHTML=shown.length?shown.map((h,i)=>{const type=patchType(h.changes),groups=[];for(const c of h.changes){let group=groups.find(g=>g.title===c.title);if(!group){group={title:c.title,slot:c.slot,changes:[]};groups.push(group)}group.changes.push(c)}return `<article class="patch-card"><div class="patch-info"><div class="patch-version">${esc(h.patch)}</div><div class="patch-date">${esc(h.date.replaceAll('-','.'))||t('게시일 미확인','Date unavailable')}</div>${i===0&&year==='all'&&filter==='all'?`<span class="patch-badge">${t('최근 변경','Latest change')}</span>`:''}</div><div class="patch-body"><div class="patch-body-head"><span>${h.isHotfix?t('추가 패치','Mid-patch update'):t('챔피언 업데이트','Champion update')} <span class="type ${type}">${typeName(type)}</span></span><a href="${esc(h.url)}" target="_blank" rel="noopener">${t('공식 원문','Official notes')} ↗</a></div>${groups.map(g=>`<div class="change"><div class="change-title">${['P','Q','W','E','R'].includes(g.slot)?`<span class="keycap">${g.slot}</span>`:''}${esc(historyText(g.title))}</div>${g.changes.map(ch=>`<p class="${ch.kind}">${delta(historyText(ch.text))}</p>`).join('')}</div>`).join('')}</div></article>`}).join(''):`<div class="history-empty">${t('이 조건에 해당하는 수집 기록이 없어요.','No collected records match these filters.')}<br><small>${t('다른 유형이나 시즌을 선택해 보세요.','Try another change type or season.')}</small></div>`;
 $('#historyMore').innerHTML=found.length>limit?`<button class="loadmore" id="loadMore">${t('이전 기록 더 보기','Load earlier records')} <span class="muted">${Math.min(limit,found.length)} / ${found.length}</span> ↓</button>`:found.length?`<div class="history-end">${t('수집된 기록을 모두 확인했어요.','You have reached the end of the collected records.')}</div>`:'';
 if($('#loadMore'))$('#loadMore').onclick=()=>{limit+=10;renderHistory()};$$('.history-filters button').forEach(b=>{const active=b.dataset.filter===filter;b.classList.toggle('active',active);b.setAttribute('aria-pressed',active)});
}
function openSources(){
 if(!meta)return toast(t('데이터를 불러오는 중이에요.','Data is still loading.'));
 const r=meta.reconciliation;
 const distanceSources=Object.entries(current?.details?.skills??{}).filter(([,skill])=>skill.distance?.source);
 const distanceLinks=distanceSources.map(([slot,skill])=>`<a target="_blank" rel="noopener" href="${esc(skill.distance.source)}">${esc(slot)}</a>`).join(' · ');
 const distanceNote=distanceLinks?`<p>${t('이 챔피언의 스킬별 거리 출처','Distance references for this champion')}: ${distanceLinks}</p>`:'';
 $('#sourceBody').innerHTML=`<h3>${t('능력치 · 스킬 설명','Stats & ability descriptions')}</h3><p><a target="_blank" rel="noopener" href="https://developer.riotgames.com/docs/lol#data-dragon">Riot Games Data Dragon ${esc(meta.version)}</a> · ${t('게임 패치','Game patch')} ${esc(meta.patch)}. ${t('현재 공식 능력치와 스킬 요약을 사용합니다. 공격력 성장값의 일괄 0 문제는 기존 자료 및 이후 공식 변경으로 보완합니다. 재사용 대기시간과 소모량에는 공식 패치에서 확인한 변경값을 우선합니다.','Current official stats and ability summaries are used. The all-zero AD growth issue is reconciled with the original source and later official changes. Cooldown and cost changes confirmed in patch notes take precedence.')}</p><p>${t('능력치는 1~18레벨을 지원합니다. 아이템·룬·특수 패시브 및 역할군 퀘스트는 제외합니다.','Stats support levels 1–18 and exclude items, runes, special passives, and role quests.')}</p>${distanceNote}<h3>${t('상세 수치에 반영한 범위','Detailed-value review coverage')}</h3><p>${r?t(`173명, P/Q/W/E/R ${r.abilities}개 항목에 25.16~${r.throughPatch} 공식 챔피언 변경과 확인된 추가 패치를 누적 반영했습니다. 검토일은 ${r.reviewedAt}입니다.`,`173 champions and ${r.abilities} P/Q/W/E/R entries incorporate official champion changes and identified hotfixes from 25.16 through ${r.throughPatch}. Reviewed ${r.reviewedAt}.`):t('세부 수치는 수집 시점의 자료를 기준으로 합니다.','Ability values use the collected snapshot.')}</p><p>${t('공식 변경: 패치 원문에서 확인한 값. 변경 반영 계산값: 기존 수식·조건에 공식 변경을 적용한 값. 기존 자료: 후속 변경이 발견되지 않아 유지한 값입니다. 후속 변경이 없다는 사실만으로 원본 전체의 정확성이 검증되는 것은 아닙니다. 스킬 카드에는 게임에 필요한 수치와 발동 조건을 표시합니다. 패치별 변경은 아래 패치 기록에서 볼 수 있습니다.','Official change: a value stated in patch notes. Reconciled calculation: an original formula updated using official changes. Baseline: a retained value without a later recorded change. Absence of a later change does not independently verify the entire original source. Ability cards show gameplay values and conditions. The patch history lists changes by version.')}</p><p><a target="_blank" rel="noopener" href="https://github.com/meraki-analytics/lolstaticdata">Meraki Analytics / League of Legends Wiki</a> · ${t('기존 상세 자료의 이미지 버전은 15.15.1이지만, 이는 모든 수치가 25.15에 검증되었다는 뜻이 아닙니다. 한국어 상세 설명은 사이트 번역입니다.','The original detailed source uses image version 15.15.1; this does not prove that every value was verified for patch 25.15. Korean detailed text is translated by this site.')} <a target="_blank" rel="noopener" href="https://creativecommons.org/licenses/by-sa/3.0/">CC BY-SA 3.0</a>.</p><h3>${t('패치 기록','Patch history')}</h3><p>${t(`${meta.earliestPatch}~${meta.latestPatch}, ${meta.patchCount}개 문서와 ${meta.historyCount.toLocaleString()}개 챔피언 기록입니다. 한국어와 영어는 각 공식 문서에 따라 기록 수가 다를 수 있습니다. 다른 게임 모드, 일부 독립 버그 수정 및 인식하지 못한 항목은 제외됩니다.`,`${meta.patchCount} articles and ${meta.historyCount.toLocaleString()} champion records from ${meta.earliestPatch} to ${meta.latestPatch}. The two official locales can have different coverage. Other modes, some separate bug-fix sections, and unrecognized entries are excluded.`)}</p><p>${t('누락 또는 항목 미인식 문서:','Missing or unrecognized articles:')} ${esc(meta.missingPatches.join(', '))}</p><h3>${t('업데이트','Updates')}</h3><p>${t('수집 시각','Collected')}: ${esc(new Date(meta.collectedAt).toLocaleString(lang==='ko'?'ko-KR':'en-US',{timeZone:'Asia/Seoul'}))} KST. ${t('현재는 수집 시점의 고정 데이터이며 자동 갱신은 연결되어 있지 않습니다.','This is a fixed snapshot. Automatic updates are not configured.')}</p>`;
 if(!$('#sourcesDialog').open)$('#sourcesDialog').showModal();
}
document.addEventListener('click',e=>{
 const home=e.target.closest('[data-home]');if(home&&!e.ctrlKey&&!e.metaKey&&!e.shiftKey&&!e.altKey&&e.button===0){if(!index)return;e.preventDefault();$('#search').value='';role='all';$$('[data-role]').forEach(b=>b.classList.toggle('active',b.dataset.role==='all'));selectChampion(randomChampion(current?.id));return}
 const c=e.target.closest('[data-champion]');if(c)selectChampion(c.dataset.champion);
 const r=e.target.closest('[data-role]');if(r){role=r.dataset.role;$$('[data-role]').forEach(b=>b.classList.toggle('active',b===r));renderList()}
 const f=e.target.closest('[data-filter]');if(f&&current){filter=f.dataset.filter;limit=10;renderHistory()}
 const s=e.target.closest('button[data-skill]');if(s&&current){skill=s.dataset.skill;renderSpells()}
 const exp=e.target.closest('[data-expand]');if(exp){const el=exp.closest('.spell');el.classList.toggle('expanded');const expanded=el.classList.contains('expanded'),count=el.querySelectorAll('.spell-extra').length;exp.setAttribute('aria-expanded',expanded);exp.textContent=expanded?t('세부 수치 접기 ⌃','Show fewer values ⌃'):t(`세부 수치 ${count}개 더 보기 ⌄`,`Show ${count} more values ⌄`)}
});
$('#search').oninput=renderList;
$('#search').onkeydown=e=>{if(e.isComposing||e.keyCode===229)return;if(e.key==='Enter'){const first=$('.champion-item');if(first){selectChampion(first.dataset.champion);$('#search').blur();e.preventDefault()}}if(e.key==='ArrowDown'){$('.champion-item')?.focus();e.preventDefault()}};
$('#championList').onkeydown=e=>{if(!['ArrowDown','ArrowUp'].includes(e.key))return;const list=$$('.champion-item');if(!list.length)return;const i=list.indexOf(document.activeElement);list[(i+(e.key==='ArrowDown'?1:-1)+list.length)%list.length]?.focus();e.preventDefault()};
document.addEventListener('keydown',e=>{if(e.isComposing||e.ctrlKey||e.metaKey||e.altKey||$('#sourcesDialog').open)return;if(e.key==='/'&&!['INPUT','TEXTAREA','SELECT'].includes(document.activeElement.tagName)&&!document.activeElement.isContentEditable){setSidebar(true);$('#search').focus();e.preventDefault()}if(e.key==='Escape'){setSidebar(false);if(window.innerWidth<=680)$('#mobileSearch').focus()}});
$('#sourcesOpen').onclick=openSources;$('#footerSources').onclick=openSources;$('#sourcesClose').onclick=()=>$('#sourcesDialog').close();
$('#sourcesDialog').addEventListener('click',e=>{if(e.target!==$('#sourcesDialog'))return;const r=e.target.getBoundingClientRect();if(e.clientX<r.left||e.clientX>r.right||e.clientY<r.top||e.clientY>r.bottom)e.target.close()});
$('#mobileSearch').onclick=()=>{const open=!$('#sidebar').classList.contains('open');setSidebar(open);if(open)$('#search').focus()};$('#closeSidebar').onclick=()=>{setSidebar(false);$('#mobileSearch').focus()};$('#sidebarOverlay').onclick=()=>{setSidebar(false);$('#mobileSearch').focus()};
$('#languageToggle').onclick=()=>changeLanguage(lang==='ko'?'en':'ko');
window.addEventListener('resize',()=>setSidebar($('#sidebar').classList.contains('open')));
function syncRoute(){if(!index)return;const next=routeLanguage()||history.state?.lang||lang,changed=next!==lang;if(changed)setLocale(next);const id=locationChampion()||(validChampion(history.state?.champion)?history.state.champion:chosen)||randomChampion();rememberChampion(id);syncSectionNav();if(changed||id!==chosen||current?.id!==id)selectChampion(id,false)}
window.addEventListener('popstate',syncRoute);window.addEventListener('hashchange',syncRoute);
async function init(){
 try{
  const [ko,en,lex,verifiedKo,verifiedEn]=await Promise.all([json('data/index.json'),json('data/en/index.json'),json('data/localization-ko.json'),json('data/verified.json').catch(()=>({})),json('data/verified-en.json').catch(()=>({}))]);
  const koreanNames=new Map(ko.champions.map(c=>[c.id,c.name]));
  for(const data of [ko,en])for(const c of data.champions)c.koreanName=koreanNames.get(c.id)||c.name;
  indexes={ko,en};glossary=lex;overrides={ko:verifiedKo,en:verifiedEn};setLocale(lang);if(!index.length)throw new Error('Empty champion index');
  chosen=locationChampion()||randomChampion();const url=new URL(location.href);
  if(url.searchParams.has('champion')&&!validChampion(url.searchParams.get('champion')))url.searchParams.delete('champion');
  if(url.searchParams.has('lang')&&!routeLanguage())url.searchParams.set('lang',lang);
  if(validChampion(url.hash.slice(1))){url.searchParams.set('champion',chosen);url.hash=''}
  saveHistory('replaceState',{...history.state,champion:chosen,lang},url);renderList();await selectChampion(chosen,false);
 }catch{$('#main').setAttribute('aria-busy','false');$('#loading').innerHTML=`<div class="error-box" role="alert">${t('데이터를 불러오지 못했어요. 네트워크 연결을 확인해 주세요.','Could not load the data. Check your connection.')}<button id="retryInit">${t('다시 시도','Retry')}</button></div>`;$('#retryInit').onclick=()=>location.reload()}
}
applyStaticLanguage();$('#loading').innerHTML=`<span class="spinner" aria-hidden="true"></span>${t('챔피언 기록을 불러오고 있어요.','Loading champion records…')}`;init();
