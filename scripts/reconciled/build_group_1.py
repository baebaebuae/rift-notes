"""Reviewed patch reconciliation for champion group 1. Do not infer absent values."""
from pathlib import Path
import json,re,copy,hashlib
ROOT=Path(__file__).resolve().parents[2]; DATA=ROOT/'dist/data'
IDS=['Aatrox','Ambessa','Ashe','Belveth','Caitlyn','Darius','Elise','Fizz','Gragas','Hwei','JarvanIV','KSante','Kassadin','Khazix','LeeSin','Lucian','Maokai','MonkeyKing','Nasus','Nocturne','Pantheon','Rakan','Renekton','Samira','Shaco','Sivir','Swain','Talon','Trundle','Urgot','Vex','Volibear','Yasuo','Zaahen','Zilean']
lex=json.loads((DATA/'localization-ko.json').read_text())
ch={i:json.loads((DATA/'en'/f'{i}.json').read_text()) for i in IDS}
ko={i:json.loads((DATA/f'{i}.json').read_text()) for i in IDS}
raw={i:{a['slot']:copy.deepcopy(a['variants']) for a in ch[i]['formulas']} for i in IDS}
marks={};removed=set();added={};notes={};covered={}
def recent(h):return (25,15)<tuple(map(int,h['patch'].split('.')))<=(26,21) and not h.get('release')
def sources(i,s,p=None):
 hs=[h for h in ch[i]['history'] if recent(h) and (not p or h['patch']==p) and any(c['slot']==s for c in h['changes'])]
 return [{'patch':h['patch'],'date':h['date'],'url':h['url']} for h in hs]
def mark(i,s,v,r,p):marks.setdefault((i,s,v,r),[]).extend(sources(i,s,p))
def mod(i,s,v,r,m,values,p):
 row=raw[i][s][v]['rows'][r];n=len(row['modifiers'][m]['values']);row['modifiers'][m]['values']=values if isinstance(values,list) else [values]*n;mark(i,s,v,r,p)
def scale(i,s,v,r,m,f,p):mod(i,s,v,r,m,[round(n*f,8) for n in raw[i][s][v]['rows'][r]['modifiers'][m]['values']],p)
def remove(i,s,v,*rs):
 for r in rs:removed.add((i,s,v,r))
def cover(i,s,pattern):covered[(i,s)]=pattern

def add(i,s,label_ko,label_en,val_ko,val_en,p,provenance='patch'):
 added.setdefault((i,s),[]).append({'attribute':{'ko':label_ko,'en':label_en},'value':{'ko':val_ko,'en':val_en},'provenance':provenance,'sources':sources(i,s,p)})
def note(i,s,k,e):notes[(i,s)]={'ko':k,'en':e}
# Aatrox: sweetspot multiplier 1.70 -> 1.75, including all derived totals.
for r in [1,3,5,7]:
 for m in [0,1]:scale('Aatrox','Q',0,r,m,1.75/1.7,'26.12')
cover('Aatrox','Q',r'Sweet Spot Bonus Damage|Bonus Monster Damage|Minimum Bonus Monster Damage|Bonus Damage to Monsters')
add('Aatrox','Q','몬스터 추가 피해량 · 최소','Minimum bonus monster damage','25 · 검 끝과 후속 사용 배율 적용','25; multiplied by sweetspots and subsequent casts','26.2')
add('Aatrox','Q','검 끝 추가 피해','Sweetspot bonus damage','75%','75%','26.12')
add('Aatrox','E','챔피언 피해 회복률','Healing from champion damage','16% + 추가 체력 100당 1.3% · 지속 피해 제외, 피해 경감 후 적용','16% + 1.3% per 100 bonus health; non-persistent damage after mitigation','26.19','derived')
cover('Aatrox','E',r'Health Heal Ratio')
# Ambessa: Q health damage changed. Baseline has half-effect and outer hit variants.
for v in [0,1]:
 mod('Ambessa','Q',v,0,2,[2,2.25,2.5,2.75,3],'26.10');mod('Ambessa','Q',v,1,2,[4,4.5,5,5.5,6],'26.10')
mod('Ambessa','E',0,0,1,50,'25.24');mod('Ambessa','E',0,1,1,100,'25.24')
mod('Ambessa','R',0,1,0,[15,17.5,20],'26.10');mod('Ambessa','R',0,2,0,[3.75,4.375,5],'26.10');mod('Ambessa','R',0,3,0,[3.75,4.375,5],'26.10');mod('Ambessa','R',0,3,1,12.5,'26.10')
cover('Ambessa','Q',r'Target Max Health Damage');cover('Ambessa','E',r'^Damage$');cover('Ambessa','R',r'^Healing Percentage$')
# Ashe.
mod('Ashe','Q',0,0,0,[20,30,40,50,60],'25.23');mod('Ashe','Q',0,1,0,[22,23,24,25,26],'26.10');mod('Ashe','Q',0,2,0,[110,115,120,125,130],'26.10');mod('Ashe','W',0,1,1,100,'26.1')
cover('Ashe','Q',r'Attack Speed|Total Damage');cover('Ashe','W',r'^Damage$')
# Bel'Veth large update: preserve no superseded numerical derived tables.
for s in 'QWER':
 for v,x in enumerate(raw['Belveth'][s]):remove('Belveth',s,v,*range(len(x['rows'])))
note('Belveth','P','26.15의 기본 공격 배율 100% 및 패시브 변경을 반영했습니다. 공격 속도 상한 등 패치에서 재명시하지 않은 정보는 보관 자료입니다.','Includes the 26.15 basic-attack modifier and passive changes. Details not restated in the notes, such as the attack-speed cap, remain archive sourced.')
# Caitlyn basic/secondary Q damage.
mod('Caitlyn','Q',0,0,0,[50,95,140,185,230],'26.21');mod('Caitlyn','Q',0,1,0,[30,57,84,111,138],'26.21');cover('Caitlyn','Q',r'Base Damage')
# Elise: human Q cap only; official total line has malformed English token.
mod('Elise','Q',0,1,0,[65,85,105,125,145],'26.1');raw['Elise']['Q'][0]['rows'][1]['modifiers'].append({'values':[90]*5,'units':['% AP']*5});mark('Elise','Q',0,1,'26.1')
remove('Elise','Q',1,1)
mod('Elise','W',1,1,0,[70,85,100,115,130],'26.19')
cover('Elise','Q',r'Monster Damage Cap|Maximum Damage to Monsters');cover('Elise','W',r'Bonus Attack Speed')
note('Elise','Q','영문 26.1 원문의 총 몬스터 피해량에 “105155” 오기가 있어 총합 표는 표시하지 않았습니다. 인간 형상 상한을 반영하고, 같은 제목에 포함된 거미 형상의 상한은 적용 범위가 불명확하여 이전 값을 제외했습니다.','The English 26.1 total-monster-damage line contains “105155”. The human-form cap is applied. The heading also names spider form but the listed total matches human form; its spider-form application is unclear, so the old spider cap is omitted.')
# Fizz total, per-tick and active/on-hit changes.
for r,m,vals in [(0,0,[30,45,60,75,90]),(0,1,25),(1,0,[5,7.5,10,12.5,15]),(1,1,25/6),(2,0,[50,75,100,125,150]),(4,0,[20,25,30,35,40]),(4,1,30)]:mod('Fizz','W',0,r,m,vals,'25.20')
for r,b,ap in [(0,[180,300,420],60),(1,[225,375,525],75),(2,[270,450,630],90)]:mod('Fizz','R',0,r,0,b,'25.20');mod('Fizz','R',0,r,1,ap,'25.20')
cover('Fizz','W',r'Passive Damage over Time|Active Burst Damage|On-Hit Damage|Active and on-hit');cover('Fizz','R',r'Guppy Damage|Chomper Damage|Gigalodon Damage')
mod('Gragas','W',0,0,0,[10,14,18,22,26],'26.9');cover('Gragas','W',r'Damage Reduction')
# Hwei variant-specific updates and derived shield totals.
mod('Hwei','Q',1,0,1,80,'26.12');mod('Hwei','Q',2,0,1,30,'26.12');mod('Hwei','Q',2,2,1,[60,71.25,82.5,93.75,105],'26.12')
for r,m,val in [(0,0,[20,35,50,65,80]),(1,0,[5,8.75,12.5,16.25,20]),(1,1,6),(2,0,[50,87.5,125,162.5,200]),(2,1,60),(3,0,[70,122.5,175,227.5,280]),(3,1,90)]:mod('Hwei','Q',3,r,m,val,'25.23')
mod('Hwei','W',1,1,0,[30,32.5,35,37.5,40],'25.18');mod('Hwei','W',1,1,1,3,'25.18')
for r,m,val in [(0,0,[50,70,90,110,130]),(1,0,[50/6,70/6,90/6,110/6,130/6]),(2,0,[100,140,180,220,260]),(3,0,[42.5,59.5,76.5,93.5,110.5]),(3,1,25.5),(4,0,[42.5/6,59.5/6,76.5/6,93.5/6,110.5/6]),(4,1,4.25),(5,0,[85,119,153,187,221]),(5,1,51)]:mod('Hwei','W',2,r,m,val,'26.4')
for v in [1,2,3]:mod('Hwei','E',v,0,1,65,'25.18')
cover('Hwei','Q',r'Hit Damage|Damage over time|Total Damage|QQ Damage|QW Damage');cover('Hwei','W',r'Base Bonus Movement Speed|Bonus Movement Speed AP Ratio|Maximum Shield Value|Ally Shield Mod');cover('Hwei','E',r'AP Ratio')
# K'Sante, Kassadin.
mod('KSante','E',0,0,0,[70,112.5,155,197.5,240],'26.13');mod('KSante','E',0,0,1,13.5,'26.13');cover('KSante','E',r'^Shield$')
mod('Kassadin','Q',0,0,1,80,'26.18');mod('Kassadin','E',0,0,1,70,'25.17');mod('Kassadin','E',0,1,0,[50,55,60,65,70],'26.4');mod('Kassadin','R',0,0,0,[80,95,110],'26.18');mod('Kassadin','R',0,3,0,[220,275,330],'26.18')
cover('Kassadin','Q',r'^Damage$|Ability Power Ratio');cover('Kassadin','E',r'^Damage$|^Slow$');cover('Kassadin','R',r'Base Damage')
# Kha'Zix.
mod('Khazix','Q',0,0,1,105,'26.5');mod('Khazix','Q',0,1,1,220.5,'26.5');mod('Khazix','W',0,0,0,[75,105,135,165,195],'25.24');cover('Khazix','Q',r'Bonus AD');cover('Khazix','W',r'Base Damage')
# Lee Sin Q1/Q2, omnivamp and kick.
for v,r,m,val in [(0,0,0,[60,90,120,150,180]),(0,0,1,90),(1,0,0,[60,90,120,150,180]),(1,0,1,90),(1,1,0,[120,180,240,300,360]),(1,1,1,180)]:mod('LeeSin','Q',v,r,m,val,'26.12')
mod('LeeSin','W',0,0,0,[60,105,150,195,240],'26.10');raw['LeeSin']['W'][1]['rows'][0]['attribute']='Omnivamp';mark('LeeSin','W',1,0,'26.4')
mod('LeeSin','E',0,0,1,90,'26.10')
for r in [0,1]:mod('LeeSin','R',0,r,0,[150,350,550],'26.21')
cover('LeeSin','Q',r'^Damage$|Base Damage');cover('LeeSin','W',r'^Shield$|Spell Vamp No More');cover('LeeSin','E',r'Magic Damage');cover('LeeSin','R',r'Kick Damage|Collision Damage')
# Lucian. Remove old crit-dependent total rows rather than carrying old bolt formula.
mod('Lucian','Q',0,0,0,[90,130,170,210,250],'26.19');mod('Lucian','Q',0,0,1,100,'26.19');cover('Lucian','Q',r'^Damage$|Base Damage')
remove('Lucian','R',0,1,2,4,5)
# Maokai Q.
mod('Maokai','Q',0,0,0,[75,120,165,210,255],'26.3');mod('Maokai','Q',0,0,2,50,'26.15');mod('Maokai','Q',0,1,0,[150,160,170,180,190],'26.15');mod('Maokai','Q',0,2,0,[225,280,335,390,445],'26.15');mod('Maokai','Q',0,2,2,50,'26.15');cover('Maokai','Q',r'Flat Damage|Bonus Monster Damage|Monster Damage Modifier|Ability Power Ratio')
# Wukong.
mod('MonkeyKing','Q',0,1,1,50,'25.20');mod('MonkeyKing','W',0,0,0,[40,45,50,55,60],'26.10');mod('MonkeyKing','E',0,0,0,[80,120,160,200,240],'25.20');mod('MonkeyKing','E',0,1,0,[40,45,50,55,60],'26.10')
cover('MonkeyKing','Q',r'Bonus Damage Bonus AD Ratio');cover('MonkeyKing','W',r'Clone Damage');cover('MonkeyKing','E',r'Base Damage|Bonus Attack Speed')
mod('Nasus','Q',0,0,0,[30,50,70,90,110],'26.19');cover('Nasus','Q',r'Base Damage|Bonus Damage')
mod('Nocturne','Q',0,0,0,[65,105,145,185,225],'26.12');mod('Nocturne','Q',0,1,0,[15,25,35,45,55],'25.16');mod('Nocturne','Q',0,2,0,[20,25,30,35,40],'26.5');cover('Nocturne','Q',r'^Damage$|Bonus AD|Bonus move speed')
# Samira and Shaco.
mod('Samira','Q',0,0,0,[0,5,10,15,20],'26.1');mod('Samira','Q',0,0,1,110,'26.1')
for r,b,ad in [(0,[20,40,60],30),(1,[200,400,600],300),(2,[5,10,15],7.5),(3,[50,100,150],75)]:mod('Samira','R',0,r,0,b,'26.1');mod('Samira','R',0,r,1,ad,'26.1')
cover('Samira','Q',r'Q Non-Crit Damage');cover('Samira','R',r'R Non-Crit Damage')
mod('Shaco','Q',0,1,1,60,'25.16');cover('Shaco','Q',r'Bonus AD Ratio')
# Sivir: damage changes leave AP ratio in baseline untouched; crit derivations outdatedglobally.
for r,f in [(0,1),(1,.4),(2,2)]:mod('Sivir','Q',0,r,1,70*f,'26.1')
cover('Sivir','Q',r'Initial Damage|^Damage$')
remove('Sivir','W',0,2,4)
note('Sivir','W','26.1의 전역 치명타 체계 변경에 따라 예전 고정 치명타 피해 계산은 제외했습니다. 튕김 피해에 현재 치명타 배율을 적용하세요.','Old fixed critical-damage calculations are omitted after the global 26.1 critical-strike changes. Apply the current critical multiplier to bounce damage.')
# Swain.
mod('Swain','E',0,0,0,[90,130,170,210,250],'25.23');mod('Swain','W',0,0,0,[70,115,160,205,250],'26.20');mod('Swain','W',0,1,0,[35,57.5,80,102.5,125],'26.20');mod('Swain','W',0,2,0,50,'26.4');mod('Swain','R',0,0,1,2,'26.4');mod('Swain','R',1,0,1,40,'26.4')
cover('Swain','E',r'^Damage$');cover('Swain','W',r'^Damage$|^Slow$');cover('Swain','R',r'Damage per Second Scaling|Demonflare Damage Scaling')
mod('Trundle','W',0,0,0,[30,50,70,90,110],'26.17');cover('Trundle','W',r'Attack Speed')
# Volibear.
mod('Volibear','Q',0,0,0,[12,15.5,19,22.5,26],'25.22');mod('Volibear','Q',0,1,0,[24,31,38,45,52],'25.22');mod('Volibear','Q',0,2,0,[10,20,30,40,50],'26.3');mod('Volibear','Q',0,2,1,160,'26.5');mod('Volibear','W',0,0,1,110,'25.24');mod('Volibear','E',0,0,1,70,'25.20')
cover('Volibear','Q',r'Minimum Movement Speed|Maximum Movement Speed|Bonus [Pp]hysical [Dd]amage');cover('Volibear','W',r'^Damage$');cover('Volibear','E',r'AP Ratio')
# Resolve names that changed between patch articles; match within champion+slot.
ALIASES={
('Ambessa','Q'):{'Monster Damage':'bonus-monster','Bonus Damage to Monsters':'bonus-monster','Bonus Monster Damage':'bonus-monster'},
('Belveth','R'):{'True Damage on attack per stack':'passive-damage','Passive True Damage':'passive-damage','Total Attack Speed':'attack-speed','True Form Total Attack Speed':'attack-speed'},
('Caitlyn','P'):{'Champion Damage Increase':'damage','Damage':'damage','Crit Scaling':'damage'},
('Shaco','P'):{'Bonus AD Ratio':'damage','Damage':'damage'},
('LeeSin','W'):{'Flat Cooldown':'cooldown','Cooldown':'cooldown'},
('Pantheon','Q'):{'Monster Modifier':'monster','Monster Damage Modifier':'monster'},
('Pantheon','W'):{'Minion/Monster damage cap':'cap','Minion/Monster Damage Cap':'cap'},
('Volibear','P'):{'Attack Speed AP Ratio':'speed','Attack Speed per Stack':'speed','AP Ratio':'lightning','Lightning On-Hit Damage':'lightning'},
('Volibear','E'):{'Damage Cap Against Non-Champions':'cap','Non-champion damage cap':'cap'},
('Zaahen','Q'):{'AD Ratio (25.23)':'q1-ratio','Q1 Bonus Damage Ratio':'q1-ratio','Q2 Bonus Damage Ratio':'q2-damage','Second Cast Base Damage (25.23)':'q2-damage','Q2 Damage':'q2-damage','Monster Damage Modifier (25.24)':'monster','Monster Modifier':'monster'},
('Zaahen','E'):{'Bonus Monster Damage':'monster','Bonus Damage to Monsters':'monster'},
}
# Passive text receives precise replacements; uncertain flattened crit expressions are removed.
effects={i:{'en':[text for v in raw[i].get('P',[]) for text in v.get('effects',[])], 'ko':[text for v in lex.get('passives',{}).get(i,{}).get('variants',[]) for text in v.get('effects',[])]} for i in IDS}
def rep(i,l,old,new):
 assert any(old in t for t in effects[i][l]),(i,l,old)
 effects[i][l]=[t.replace(old,new) for t in effects[i][l]]
rep('Aatrox','en','4% : 8%','4% : 10%');rep('Aatrox','en','capped at 100 against monsters','capped at 100–320 (based on level) against monsters');rep('Aatrox','ko','4%~8%','4%~10%');rep('Aatrox','ko','최대 100입니다','레벨에 따라 최대 100~320입니다')
rep('Ambessa','en','5 : 30 (based on level) (+ 30% bonus AD)','5 : 25 (based on level) (+ 20% bonus AD)');rep('Ambessa','ko','5~30(레벨에 따라) + 추가 AD의 30%','5~25(레벨에 따라) + 추가 AD의 20%')
effects['Ashe']['en'][0]='Critical scaling follows 100% of bonus critical damage (up to 2 / 2.3 times with the item condition stated in the 26.1 notes). Critical strikes do not add a separate critical damage instance.'
effects['Ashe']['ko'][0]='26.1 패치의 치명타 계수는 추가 치명타 피해의 100%이며, 원문에는 아이템 조건에 따라 최대 2 / 2.3배로 표기되어 있습니다. 치명타 자체가 별도의 치명타 피해를 추가하지는 않습니다.'
note('Ashe','P','예전 원본의 “75% + 40%”는 아이템 조건이 빠진 식이므로 제외했습니다. 패치 원문의 치명타 보정만 반영했으며, 완전한 서리 추가 피해 식은 추가 검증이 필요합니다.','The flattened “75% + 40%” archive expression lacks item conditions and is omitted. The patch crit adjustment is included; the complete Frost bonus-damage formula still needs verification.')
effects['Belveth']['en'][0]="Her basic attacks now deal 100% damage; the former 75% attack damage modifier was removed in 26.15. She does not gain attack speed from levels."
effects['Belveth']['ko'][0]='26.15부터 기본 공격 피해 배율은 100%이며, 이전의 75% 피해 배율이 제거되었습니다. 레벨 상승으로 공격 속도가 증가하지 않습니다.'
effects['Belveth']['en'][1]='Casting an ability grants 20% bonus attack speed for 3 seconds (26.15).'
effects['Belveth']['ko'][1]='스킬을 사용하면 3초 동안 공격 속도가 20% 증가합니다(26.15).'
rep('Belveth','en','0.28% : 1.1%','0.1% : 2%');rep('Belveth','ko','0.28%~1.1%','0.1%~2%')
effects['Caitlyn']['en'][1]='Headshot: the 26.21 notes give 60–80% AD (+0.8% AD per 1% critical strike chance) (+0.8% AD per 1% bonus critical damage). The latest separately stated non-champion base modifier is 110% total AD (25.23).'
effects['Caitlyn']['ko'][1]='헤드샷: 26.21 원문의 추가 피해는 공격력의 60~80% (+치명타 확률 1%당 공격력의 0.8%) (+추가 치명타 피해 1%당 공격력의 0.8%)입니다. 챔피언이 아닌 대상의 기본 배율은 마지막으로 따로 명시된 25.23 기준 총 공격력의 110%입니다.'
note('Caitlyn','P','26.21 원문은 헤드샷 피해 식을 제시하지만 비챔피언 치명타 적용 식을 별도로 구분하지 않습니다. 25.23의 비챔피언 기본 배율과 구분해 표시합니다.','The 26.21 notes state Headshot damage without a separate non-champion critical formula. The last separately stated non-champion base modifier is identified as 25.23.')
rep('Darius','en','200% damage against monsters','250% damage against monsters');rep('Darius','ko','몬스터에게는 200%','몬스터에게는 250%')
rep('Elise','en','12 / 22 / 32 / 42','14 / 24 / 34 / 44');rep('Elise','ko','12 / 22 / 32 / 42','14 / 24 / 34 / 44')
effects['Fizz']['en'].append('Against jungle monsters, the flat reduction is increased by 10 to 14 (+1% AP), still capped at 50% of the incoming damage (25.23).')
effects['Fizz']['ko'].append('정글 몬스터에게 받는 피해는 감소량이 10 증가해 14 + 주문력의 1%만큼 감소하며, 원래 피해의 50%라는 상한은 유지됩니다(25.23).')
rep('Hwei','en','35 : 230 (based on level) (+ 30% AP)','40 : 285 (based on level) (+ 35% AP)');rep('Hwei','ko','35~230(레벨에 따라) + AP의 30%','40~285(레벨에 따라) + AP의 35%')
rep('Khazix','en','17 : 136','22 : 141');rep('Khazix','ko','17~136','22~141')
rep('Lucian','en','15 (+ 20% AD)','5 (+ 15% AD)');rep('Lucian','ko','15 + 총 공격력의 20%','5 + 총 공격력의 15%')
rep('MonkeyKing','en','6 : 10','4.5 : 10');rep('MonkeyKing','en','36 : 60','27 : 60');rep('MonkeyKing','ko','6~10','4.5~10');rep('MonkeyKing','ko','36~60','27~60')
rep('Nasus','en','12% / 18% / 24%','10% / 15% / 20%');rep('Nasus','ko','12% / 18% / 24%','10% / 15% / 20%')
effects['Nocturne']['en'][1]='The empowered attack can critically strike against its primary target. The archive’s fixed critical-damage expression is omitted because its item conditions are missing and the global crit system changed in 26.1.'
effects['Nocturne']['ko'][1]='주 대상에게는 치명타가 발생할 수 있습니다. 원본의 고정 치명타 피해 식은 아이템 조건이 누락되어 있고 26.1에서 전역 치명타 체계가 바뀌었으므로 제외했습니다.'
note('Nocturne','P','재사용 대기시간은 12초로 갱신했습니다. 패시브의 정확한 치명타 피해 식은 추가 검증이 필요합니다.','The cooldown is updated to 12 seconds. The passive’s exact critical-damage formula still requires verification.')
rep('Shaco','en','(+ 30% bonus AD)','(+ 20% bonus AD)');rep('Shaco','ko','추가 공격력의 30%','추가 공격력의 20%')
rep('Swain','en','3% : 6% (based on level)','6%');rep('Swain','ko','3%~6%(레벨에 따라)','6%')
rep('Talon','en','increased to 110% damage against monsters','dealing 100% damage against monsters');rep('Talon','ko','몬스터에게는 피해가 110%로 증가합니다','몬스터에게는 피해가 100% 적용됩니다')
rep('Volibear','en','(+ 50% AP)','(+ 45% AP) (+ 20% bonus AD)');rep('Volibear','ko','주문력의 50%','주문력의 45% + 추가 공격력의 20%')
effects['Yasuo']['en'].append('Critical strikes deal 5% reduced damage (26.17), replacing the former 10% reduction. With the 200% standard critical multiplier, this is 190% before item-specific bonus critical damage.')
effects['Yasuo']['ko'].append('26.17부터 치명타 피해 감소율은 기존 10%에서 5%로 바뀝니다. 기본 치명타 배율 200%에 적용하면 아이템의 추가 치명타 피해를 제외한 배율은 190%입니다.')
# A malformed or under-specified source must not become a false full-current claim.
for i,s in [('Ashe','P'),('Caitlyn','P'),('Elise','Q'),('Nocturne','P')]:pass
# Formatting preserves full available precision (round only derived arithmetic noise).
def number(n):return format(round(float(n),8),'.8f').rstrip('0').rstrip('.') if isinstance(n,(int,float)) else str(n)
def fmt(row,l):
 parts=[]
 for m in row.get('modifiers',[]):
  vs=m.get('values',[]);us=m.get('units',[])
  if l=='ko':us=[lex['units'].get(u,u) for u in us]
  if len(set(vs))==1 and len(set(us))==1:part=number(vs[0])+us[0]
  elif len(set(us))==1:part=' / '.join(number(x) for x in vs)+(us[0] if us else '')
  else:part=' / '.join(number(v)+(us[j] if j<len(us) else '') for j,v in enumerate(vs))
  parts.append(part)
 return ' + '.join(parts)
def unique(xs):
 out=[]
 for x in xs:
  if x not in out:out.append(x)
 return out

def norm(x):return re.sub(r'\W+','',x).lower()
def paired(i,h,c,idx):
 hs=[x for x in ko[i]['history'] if x['patch']==h['patch'] and x['isHotfix']==h['isHotfix']]
 if not hs:return None
 exact=[x for x in hs if x['date']==h['date']];hh=(exact or hs)[0]
 if len(hh['changes'])==len(h['changes']):return hh['changes'][idx]
 cand=[x for x in hh['changes'] if x['slot']==c['slot']]
 ec=[x for x in h['changes'] if x['slot']==c['slot']]
 if len(cand)==len(ec):return cand[ec.index(c)]
 return None

def field(text):return text.split(':',1)[0].strip() if ':' in text else text

def value(text):
 if re.search('⇒|→',text):return re.split('⇒|→',text,maxsplit=1)[1].strip()
 return text.split(':',1)[1].strip() if ':' in text else text

def latest_patch_rows(i):
 result={};missing=[]
 for h in reversed(ch[i]['history']):
  if not recent(h):continue
  for idx,c in enumerate(h['changes']):
   s=c['slot']
   if i=='LeeSin' and h['patch']=='26.5' and s=='A':s='Q'
   if s not in 'PQWER' or len(s)!=1:continue
   label=field(c['text']);key=ALIASES.get((i,s),{}).get(label,norm(label))
   # Current Q2 full damage supersedes older ratio-only and base-only lines.
   if re.search(covered.get((i,s),r'(?!)'),label,re.I):continue
   k=paired(i,h,c,idx)
   if not k:
    missing.append((h['patch'],s,c['text']));continue
   row={'attribute':{'ko':field(k['text']),'en':label},'value':{'ko':value(k['text']),'en':value(c['text'])},'provenance':'patch','sources':[{'patch':h['patch'],'date':h['date'],'url':h['url']}]}
   result[(s,key)]=row
 return result,missing

out={}
for i in IDS:
 patchrows,missing=latest_patch_rows(i)
 if missing:raise RuntimeError(('Unpaired Korean lines',i,missing))
 skills={}
 for s in 'PQWER':
  rows=[]
  for vi,v in enumerate(raw[i].get(s,[])):
   for ri,r in enumerate(v.get('rows',[])):
    if (i,s,vi,ri) in removed:continue
    source=unique(marks.get((i,s,vi,ri),[]));enattr=r['attribute'];koattr=lex['labels'].get(enattr, {'Omnivamp':'모든 피해 흡혈'}.get(enattr,enattr))
    if len(raw[i][s])>1:
     enattr=v['name']+' · '+enattr;koattr=lex['variants'].get(v['name'],v['name'])+' · '+koattr
    rows.append({'attribute':{'ko':koattr,'en':enattr},'value':{'ko':fmt(r,'ko'),'en':fmt(r,'en')},'provenance':'derived' if source else 'baseline','sources':source})
  rows.extend(r for (ss,key),r in patchrows.items() if ss==s)
  rows.extend(added.get((i,s),[]))
  ssources=unique(sources(i,s)+[src for row in rows for src in row['sources']])
  status='reconciled' if ssources else 'baseline'
  if (i,s) in notes or not raw[i].get(s):status='partial'
  skills[s]={'rows':rows,'effects':effects[i] if s=='P' else {'ko':[],'en':[]},'status':status,'notes':notes.get((i,s),{'ko':'','en':''}),'sources':ssources}
 for row in skills['P']['rows']:
  if i=='Hwei' and row['value']['en']=='40 - 285 (Levels 1 - 18)':row['value']['ko']='40~285 (1~18레벨)'
 out[i]={'skills':skills,'audit':{'reviewedPatches':unique(h['patch'] for h in reversed(ch[i]['history']) if recent(h)),'notes':['Unchanged values retain baseline provenance. Updated full formulas that retain archive components use derived provenance.'],'historySha256':hashlib.sha256(json.dumps([h for h in ch[i]['history'] if recent(h)],ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest(),'changeCount':sum(len(h['changes']) for h in ch[i]['history'] if recent(h))}}
(ROOT/'scripts/reconciled/group-1.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
print('group1',len(out),'champions',sum(len(v['rows']) for c in out.values() for v in c['skills'].values()),'rows')
