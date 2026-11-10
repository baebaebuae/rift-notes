'use strict';

const formProfiles={
 Jayce:{forms:[['hammer','해머','Hammer'],['cannon','캐논','Cannon']]},
 Gnar:{forms:[['mini','미니','Mini'],['mega','메가','Mega']]},
 Nidalee:{forms:[['human','인간','Human'],['cougar','쿠거','Cougar']]},
 Elise:{forms:[['human','인간','Human'],['spider','거미','Spider']]},
 Shyvana:{forms:[['human','인간','Human'],['dragon','용','Dragon']],unlock:6},
 Rell:{forms:[['mounted','기마','Mounted'],['dismounted','중갑','Dismounted']]},
 Kled:{forms:[['mounted','탑승','Mounted'],['dismounted','비탑승','Dismounted']]},
 RekSai:{forms:[['surface','돌출','Unburrowed'],['burrow','매복','Burrowed']]},
 KSante:{forms:[['normal','기본','Normal'],['all-out','총공세','All Out']],unlock:6}
};
let selectedForm=null;

function validStatForm(id,requested,lvl){
 const profile=formProfiles[id];
 if(!profile)return null;
 return requested===profile.forms[1][0] && lvl>=(profile.unlock||1)?requested:profile.forms[0][0];
}
function formSwitch(id){
 const profile=formProfiles[id];
 if(!profile)return '';
 return `<div class="form-switch" role="group" aria-label="${t('챔피언 폼','Champion form')}">${profile.forms.map(([form,ko,en])=>`<button type="button" data-form="${form}">${t(ko,en)}</button>`).join('')}</div>`;
}
function syncFormButtons(){
 const profile=formProfiles[current.id];
 if(!profile)return;
 selectedForm=validStatForm(current.id,selectedForm,level);
 for(const btn of $$('.form-switch button')){
  btn.setAttribute('aria-pressed',String(selectedForm===btn.dataset.form));
  btn.disabled=btn.dataset.form===profile.forms[1][0] && level<(profile.unlock||1);
  btn.title=btn.disabled?t(`${profile.unlock}레벨에 해금`,`Unlocks at level ${profile.unlock}`):'';
 }
}
// Project the equipped form onto base stats before applying the ordinary level-growth curve.
function statsForForm(base,id,form,lvl){
 const s={...base},notes={};
 const tier=Number(lvl>=6)+Number(lvl>=11)+Number(lvl>=16);
 switch(id){
  case 'Jayce':
   if(form==='hammer'){
    s.armor+=[5,12,19,26][tier];
    s.spellblock+=[5,12,19,26][tier];
   }else s.attackrange=500;
   break;
  case 'Gnar':
   if(form==='mini'){
    s.attackrange=400+100*(lvl-1)/17;
    s.movespeed+=lvl-1+Math.max(0,lvl-15);
    notes.movespeed=t('레벨에 따라 증가','Scales with level');
   }else{
    s.attackrange=175;s.hp+=100;s.hpperlevel+=43;
    s.attackdamage+=6;s.attackdamageperlevel+=2.5;
    s.armor+=3.5;s.armorperlevel+=3;
    s.spellblock+=3.5;s.spellblockperlevel+=3.5;
    s.attackspeedperlevel=0.5;
   }
   break;
  case 'Nidalee':
   if(form==='cougar')s.attackrange=125;
   break;
  case 'Elise':
   if(form==='spider'){s.movespeed+=25;s.attackrange=125}
   break;
  case 'Shyvana':
   if(form==='dragon'){s.attackrange+=25*tier;s.hp+=[0,150,250,350][tier]}
   break;
  case 'Rell':
   if(form==='dismounted'){
    s.armor*=1.15;s.armorperlevel*=1.15;
    s.spellblock*=1.15;s.spellblockperlevel*=1.15;s.attackrange+=75;
   }else{
    s.movespeed+=20;
    notes.movespeed=t('W 1랭크 기준','Rank 1 W');
   }
   break;
  case 'Kled':
   if(form==='mounted'){s.hp+=400;s.hpperlevel+=1000/17}
   else{
    s.movespeed-=40;s.attackrange+=125;s.armor+=4;s.spellblock+=4;
    notes.armor=notes.spellblock=t('주변 적 0명 기준','No nearby enemies');
   }
   break;
  case 'RekSai':
   if(form==='burrow'){
    s.attackrange=null;s.movespeed+=5;
    notes.movespeed=t('W 1랭크 기준','Rank 1 W');
   }
   break;
  case 'KSante':
   if(form==='all-out'){
    notes.hp=t('현재 체력 상한 65%','Current health capped at 65%');
    notes.armor=notes.spellblock=t('추가 저항력 0 기준','No bonus resists');
   }
   break;
 }
 return {s,notes};
}
