'use strict';

// Each profile is scoped to the PC Summoner's Rift stats in this snapshot.
// Form-only bonuses are applied after the champion's normal level growth.
const formProfiles = {
 Jayce: {forms:[['hammer','해머','Hammer'],['cannon','캐논','Cannon']], inputs:['bonusAD']},
 Gnar: {forms:[['mini','미니 나르','Mini Gnar'],['mega','메가 나르','Mega Gnar']]},
 Nidalee: {forms:[['human','인간','Human'],['cougar','쿠거','Cougar']]},
 Elise: {forms:[['human','인간','Human'],['spider','거미','Spider']], extraStat:'movespeed'},
 Shyvana: {forms:[['human','인간','Human'],['dragon','용','Dragon']], unlock:6, extraStat:'hp'},
 Rell: {forms:[['mounted','기마','Mounted'],['dismounted','중갑','Dismounted']]},
 Kled: {forms:[['mounted','탑승','Mounted'],['dismounted','비탑승','Dismounted']], inputs:['bonusHP','enemies']},
 RekSai: {forms:[['surface','돌출','Unburrowed'],['burrow','매복','Burrowed']]},
 KSante: {forms:[['normal','기본','Normal'],['all-out','총공세','All Out']], unlock:6, inputs:['bonusArmor','bonusMR']}
};
const formInputLabels={
 bonusAD:['추가 공격력','Bonus attack damage'],bonusHP:['추가 체력','Bonus health'],
 enemies:['주변 적 챔피언 수','Nearby enemy champions'],bonusArmor:['추가 방어력','Bonus armor'],
 bonusMR:['추가 마법 저항력','Bonus magic resist']
};
const formStatLabels={
 armor:['방어력','Armor'],spellblock:['마법 저항력','Magic resist'],attackrange:['기본 공격 사거리','Basic attack range'],
 movespeed:['이동 속도','Move speed'],hp:['최대 체력','Maximum health']
};
function formStatValues(id,form,base,lvl,inputs){
 const values={...base};
 const tier=Number(lvl>=6)+Number(lvl>=11)+Number(lvl>=16);
 let resist=0;
 switch(id){
  case 'Jayce':
   if(form==='hammer')resist=[5,12,19,26][tier]+0.075*inputs.bonusAD;
   values.attackrange=form==='hammer'?125:500;
   break;
  case 'Gnar':
   if(form==='mini')values.attackrange=400+100*(lvl-1)/17;
   else{
    values.armor+=3.5+3*growth(lvl);
    values.spellblock+=3.5+3.5*growth(lvl);
    values.attackrange=175;
   }
   break;
  case 'Nidalee':
   values.attackrange=form==='cougar'?125:525;
   break;
  case 'Elise':
   if(form==='spider'){
    values.movespeed+=25;
    values.attackrange=125;
   }
   break;
  case 'Shyvana':
   if(form==='dragon'){
    values.attackrange+=25*tier;
    values.hp+=[0,150,250,350][tier];
   }
   break;
  case 'Rell':
   if(form==='dismounted'){
    values.armor*=1.15;
    values.spellblock*=1.15;
    values.attackrange+=75;
   }
   break;
  case 'Kled':
   if(form==='dismounted'){
    values.attackrange+=125;
    resist=(4+0.01*inputs.bonusHP)*(1+0.3*inputs.enemies);
   }
   break;
  case 'RekSai':
   if(form==='burrow')values.attackrange=null;
   break;
  case 'KSante':{
   const retained=form==='all-out'?0.15:1;
   values.armor+=retained*inputs.bonusArmor;
   values.spellblock+=retained*inputs.bonusMR;
   break;
  }
 }
 values.armor+=resist;
 values.spellblock+=resist;
 return values;
}
let localFormRoute=null;
function formRoute(){
 return localFormRoute && localFormRoute.champion===current?.id?localFormRoute.hash:location.hash;
}
function formHashActive(){
 const route=formRoute();
 return !!formProfiles[current?.id] && (route==='#forms'||route.startsWith('#forms/'));
}
function writeFormRoute(hash,method){
 const url=new URL(location.href);
 url.searchParams.set('champion',current.id);
 url.hash=hash;
 const state={...history.state,champion:current.id,lang,formHash:hash};
 const wroteURL=saveHistory(method,state,url);
 localFormRoute=wroteURL?null:{champion:current.id,hash};
}
function formControls(profile){
 const inputs=(profile.inputs||[]).map(key=>{
  const label=t(...formInputLabels[key]);
  if(key==='enemies')return `<label>${label}<select data-form-input="${key}">${[0,1,2,3,4,5].map(n=>`<option>${n}</option>`).join('')}</select></label>`;
  return `<label>${label}<input type="number" data-form-input="${key}" min="0" step="any" inputmode="decimal" value="0"></label>`;
 }).join('');
 return `<div class="form-switch" role="group" aria-label="${t('챔피언 폼','Champion form')}">${profile.forms.map(([id,ko,en])=>`<button type="button" data-form="${id}">${t(ko,en)}</button>`).join('')}</div>
 <div class="form-controls"><label class="levelcontrol">${t('챔피언 레벨','Champion level')} <input type="range" id="formLevel" min="1" max="18" value="${level}"><output for="formLevel"></output></label>${inputs}</div>
 <div class="form-stats" aria-live="polite"></div>`;
}
function readFormRoute(){
 const [path,query]=formRoute().split('?');
 return {form:path.split('/')[1],params:new URLSearchParams(query)};
}
function renderFormNumbers(){
 const panel=$('#forms'),profile=formProfiles[current.id];
 const options={};
 for(const input of panel.querySelectorAll('[data-form-input]')){
  options[input.dataset.formInput]=Math.max(0,Number(input.value)||0);
 }
 const available=!profile.unlock||level>=profile.unlock;
 const second=profile.forms[1][0];
 const selected=available&&readFormRoute().form===second?1:0;
 const base={};
 for(const key of ['armor','spellblock','attackrange',...(profile.extraStat?[profile.extraStat]:[])])base[key]=statValue(key);
 const stats=profile.forms.map(([id])=>formStatValues(current.id,id,base,level,options));
 const format=v=>v==null?t('공격 불가','Unavailable'):num(v);
 panel.querySelector('output').textContent=t(`${level}레벨`,`Lv. ${level}`);
 panel.querySelector('#formLevel').value=level;
 for(const [i,btn] of [...panel.querySelectorAll('[data-form]')].entries()){
  btn.setAttribute('aria-pressed',String(selected===i));
  btn.disabled=i===1&&!available;
 }
 const other=1-selected,otherName=t(...profile.forms[other].slice(1));
 panel.querySelector('.form-stats').innerHTML=Object.keys(base).map(key=>{
  const reference=available?format(stats[other][key]):t(`${profile.unlock}레벨에 해금`,`Unlocks at level ${profile.unlock}`);
  return `<div class="form-stat" data-form-stat="${key}"><span>${t(...formStatLabels[key])}</span><strong>${format(stats[selected][key])}</strong><small>${otherName} · ${reference}</small></div>`;
 }).join('');
}
function syncFormPage(){
 const panel=$('#forms');
 if(!panel)return;
 const active=formHashActive();
 panel.hidden=!active;
 $('#overview').hidden=active;
 $('#history').hidden=active;
 if(!active)return;
 const profile=formProfiles[current.id];
 if(!panel.hasChildNodes()){
  const note=profile.unlock?t(`변신은 ${profile.unlock}레벨부터 사용할 수 있습니다.`,`Transformation unlocks at level ${profile.unlock}.`):'';
  const sourceName=encodeURIComponent(current.englishName.replaceAll(' ','_').replace('’',"'"));
  panel.innerHTML=`<div class="section-title"><h2>${t('폼별 능력치','Form stats')}</h2></div>${formControls(profile)}
  <div class="form-foot"><span>${note} ${t('아이템·룬 제외 · 별도 입력한 능력치만 반영','Excludes items and runes except bonuses entered here.')}</span><a target="_blank" rel="noopener" href="https://wiki.leagueoflegends.com/en-us/${sourceName}">${t('챔피언 자료','Champion reference')} ↗</a></div>`;
  panel.oninput=e=>{
   if(e.target.id==='formLevel'){
    level=Number(e.target.value);
    $('#level').value=level;
    renderStats();
    
   }
   const second=profile.forms[1][0];
   const chosen=readFormRoute().form===second && level>=(profile.unlock||1)?second:profile.forms[0][0];
   setFormHash(chosen);
   renderFormNumbers();
  };
  panel.onclick=e=>{
   const btn=e.target.closest('[data-form]');
   if(!btn||btn.disabled)return;
   setFormHash(btn.dataset.form);
   renderFormNumbers();
  };
 }
 const route=readFormRoute();
 const urlLevel=Number(route.params.get('level'));
 if(Number.isInteger(urlLevel) && urlLevel>=1 && urlLevel<=18)level=urlLevel;
 else if(profile.unlock && route.form===profile.forms[1][0])level=Math.max(level,profile.unlock);
 $('#level').value=level;
 renderStats();
 for(const input of panel.querySelectorAll('[data-form-input]')){
  const value=Number(route.params.get(input.dataset.formInput));
  input.value=Number.isFinite(value)&&value>=0?value:0;
  if(input.tagName==='SELECT' && !input.value)input.value=0;
 }
 renderFormNumbers();
}
function setFormHash(form){
 const params=new URLSearchParams({level:String(level)});
 for(const input of $('#forms').querySelectorAll('[data-form-input]')){
  if(Number(input.value)>0)params.set(input.dataset.formInput,input.value);
 }
 writeFormRoute('#forms/'+form+'?'+params,'replaceState');
}
