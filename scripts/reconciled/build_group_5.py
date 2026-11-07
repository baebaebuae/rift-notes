"""Reviewed reconstruction for group 5; original archive remains unmodified."""
import json, copy, re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]; D=ROOT/'dist/data'
IDS=['Alistar','Aphelios','Bard','Briar','Corki','Ekko','Fiora','Gnar','Heimerdinger','Janna','Jinx','Karthus','Kennen','Leblanc','Locke','Malzahar','MissFortune','Nami','Nilah','Ornn','Quinn','Renata','Ryze','Sett','Sion','Soraka','Taliyah','Tristana','Udyr','Velkoz','Vladimir','XinZhao','Yuumi','Ziggs']
LEX=json.loads((D/'localization-ko.json').read_text()); CH={i:json.loads((D/f'{i}.json').read_text()) for i in IDS}; EN={i:json.loads((D/'en'/f'{i}.json').read_text()) for i in IDS}
OUT={};RAW={}; MARK={}; EXTRA={}; DELETED=set()
def pkey(s):return tuple(map(int,s.split('.')))
def refs(id,patch=None,slot=None):
 return [dict(patch=h['patch'],date=h['date'],url=h['url']) for h in EN[id]['history'] if (25,15)<pkey(h['patch'])<=(26,21) and not h.get('release') and (not patch or h['patch']==patch) and (not slot or any(c['slot'] in (slot,'A') for c in h['changes']))]
def mark(id,s,vi,ri,patch,prov='derived'):MARK[id,s,vi,ri]=(refs(id,patch),prov)
def mod(id,s,ri,mi,vals,patch,unit=None,vi=0,prov='derived'):
 r=RAW[id,s][vi]['rows'][ri];m=r['modifiers'][mi];vals=vals if isinstance(vals,list) else [vals]*len(m['values']);m['values']=vals
 if unit is not None:m['units']=[unit]*len(vals)
 mark(id,s,vi,ri,patch,prov)
def delete(id,s,ri,vi=0):DELETED.add((id,s,vi,ri))
def extra(id,s,ko,en,kval,eval,patch,prov='patch'):
 EXTRA.setdefault((id,s),[]).append({'attribute':{'ko':ko,'en':en},'value':{'ko':kval,'en':eval},'provenance':prov,'sources':refs(id,patch)})
def note(id,s,ko,en):OUT[id]['skills'][s]['notes']={'ko':ko,'en':en};OUT[id]['skills'][s]['status']='partial'
def effect(id,vi,ei,ko=None,en=None,patch=None):
 if ko is not None:OUT[id]['skills']['P']['effects']['ko'][sum(len(v['effects']) for v in RAW[id,'P'][:vi])+ei]=ko
 if en is not None:OUT[id]['skills']['P']['effects']['en'][sum(len(v['effects']) for v in RAW[id,'P'][:vi])+ei]=en
 if patch:OUT[id]['skills']['P']['sources']+=refs(id,patch)
def replace_effect(id,vi,ei,ko_pairs=[],en_pairs=[],patch=None):
 k=sum(len(v['effects']) for v in RAW[id,'P'][:vi])+ei;es=OUT[id]['skills']['P']['effects']
 for a,b in ko_pairs:
  assert a in es['ko'][k],(id,a);es['ko'][k]=es['ko'][k].replace(a,b)
 for a,b in en_pairs:
  assert a in es['en'][k],(id,a);es['en'][k]=es['en'][k].replace(a,b)
 if patch:OUT[id]['skills']['P']['sources']+=refs(id,patch)
for id in IDS:
 OUT[id]={'skills':{},'audit':{'reviewedPatches':sorted({h['patch'] for h in EN[id]['history'] if (25,15)<pkey(h['patch'])<=(26,21) and not h.get('release')},key=pkey),'notes':['Official champion-section changes after 25.15, including dated hotfixes, compared chronologically. Unchanged values retain archive provenance; the archive icon version is not proof of complete baseline verification.']}}
 for s in 'PQWER':
  RAW[id,s]=copy.deepcopy(next((f['variants'] for f in CH[id]['formulas'] if f['slot']==s),[]))
  effects={'ko':[],'en':[]}
  if s=='P':
   effects['en']=[e for v in RAW[id,s] for e in v['effects']]
   effects['ko']=[e for v in LEX.get('passives',{}).get(id,{}).get('variants',[]) for e in v['effects']]
  OUT[id]['skills'][s]={'rows':[],'effects':effects,'status':'baseline','notes':{'ko':'','en':''},'sources':[]}
# Aphelios: weapon-labelled changes are recorded as A in official article headings.
mod('Aphelios','P',0,0,[4,8,12,16,20,24],'26.4',prov='patch');mod('Aphelios','P',2,0,[4.5,9,13.5,18,22.5,27],'26.1',prov='derived')
replace_effect('Aphelios',1,1,[('추가 공격력의 20%','추가 공격력의 15%')],[('20% bonus AD','15% bonus AD')],'26.13')
replace_effect('Aphelios',2,0,[('7.1%','8%'),('17.75%','20%')],[('7.1%','8%'),('17.75%','20%')],'26.19')
replace_effect('Aphelios',3,0,[('후 10%','후 15%')],[('to 10%','to 15%')],'26.19')
effect('Aphelios',5,2,ko='반월검 공격은 환영 반월검마다 추가 물리 피해를 입힙니다. 첫 반월검은 총 공격력의 16%, 이후 반월검마다 1.5%p씩 감소하여 9번째부터는 각각 총 공격력의 5%입니다. 공격 준비 시간은 공격 주기의 10.67%이며 치명타 시 6.67%로 감소합니다. 추가 피해에는 치명타 피해 보정이 적용됩니다.',en='Crescendum attacks deal bonus physical damage for each spectral Chakram: 16% total AD for the first, decreasing by 1.5 percentage points per additional Chakram to 5% total AD for the 9th and later Chakrams. The windup is 10.67% of the attack cycle, reduced to 6.67% on critical strikes. Chakram bonus damage is affected by critical strike modifiers.',patch='26.19')
extra('Aphelios','Q','만월총 · 달빛탄 피해량','Calibrum · Moonshot damage','80~170 + 추가 공격력의 42~60% + AP의 100% (레벨 비례)','80–170 + 42–60% bonus AD + 100% AP (level based)','26.19')
extra('Aphelios','Q','절단검 · 맹공 타격당 피해량','Severum · Onslaught damage per attack','총 공격력의 20 / 25.25 / 30.5 / 35.75 / 41%','20 / 25.25 / 30.5 / 35.75 / 41% total AD','26.13')
extra('Aphelios','Q','화염포 · 황혼파 피해량','Infernum · Duskwave damage','20~110 + 추가 공격력의 15~21% (1~18레벨)','20–110 + 15–21% bonus AD (levels 1–18)','26.13')
extra('Aphelios','Q','화염포 · 황혼파 재사용','Infernum · Duskwave cooldown','8 / 7.25 / 6.5 / 5.75 / 5초','8 / 7.25 / 6.5 / 5.75 / 5 seconds','26.19')
extra('Aphelios','Q','반월검 · 파수탑 피해량','Crescendum · Sentry damage','35~125 + 추가 공격력의 34~52% (1~18레벨)','35–125 + 34–52% bonus AD (levels 1–18)','26.13')
extra('Aphelios','Q','추가 공격 치명타','Follow-up attack critical strikes','해당 무기 공격은 기본 공격 치명타 피해의 100%를 적용','Applicable weapon attacks use 100% of basic-attack critical strike damage','26.1')
extra('Aphelios','R','후속 공격 치명타 피해','Follow-up attack critical damage','기본 피해 × (1 + 추가 치명타 피해의 30%)','Base damage × (1 + 30% of bonus critical strike damage)','26.1')
note('Aphelios','Q','공식 변경에 명시된 무기별 수치를 반영했습니다. 원자료에 없는 무기의 전체 수치는 아직 미확보입니다.','Weapon-specific published changes are applied. Complete values for weapons absent from the baseline remain unavailable.')
# Bard
for ri,coef in [(0,40),(1,70),(2,6)]:mod('Bard','W',ri,1,coef,'25.21')
replace_effect('Bard',0,1,[('35 + (수집한 종 5개당 10)','30 + (수집한 종 5개당 6)')],[('35 (+ 10 per 5 Chimes','30 (+ 6 per 5 Chimes')],'26.13')
extra('Bard','P','정령 추가 마법 피해','Meep bonus magic damage','30 + 수집한 종 5개당 6 + AP의 40%','30 + 6 per 5 Chimes collected + 40% AP','26.13')
# Briar: 5 stacks = 2x single-stack bleed; original archive maximum assumed 7 stacks.
mod('Briar','Q',0,0,[60,85,110,135,160],'25.18');RAW['Briar','Q'][0]['rows'][0]['attribute']='Physical Damage'
mod('Briar','R',0,1,0,'25.18');mod('Briar','R',0,2,130,'25.18');RAW['Briar','R'][0]['rows'][0]['modifiers'].pop(1)
for s in 'QWER':extra('Briar',s,'체력 소모','Health cost','현재 체력의 5%','5% current health','26.3')
extra('Briar','R','사거리','Range','12000','12000','25.18')
extra('Briar','R','전체 효과음','Global sound','시전 후 재생','Plays after the cast','25.18')
replace_effect('Briar',0,0,[('최대 7중첩','최대 5중첩'),('최대 25~125','최대 20~100'),('추가 공격력의 125%입니다','추가 공격력의 100%입니다'),('주기당 최대 2.5~12.5','주기당 최대 2~10'),('추가 공격력의 12.5%입니다','추가 공격력의 10%입니다')],[('up to 7 times','up to 5 times'),('maximum of 25 : 125','maximum of 20 : 100'),('(+ 125% bonus AD)','(+ 100% bonus AD)'),('maximum of 2.5 : 12.5','maximum of 2 : 10'),('(+ 12.5% bonus AD) per tick','(+ 10% bonus AD) per tick')],'25.20')
# Corki
mod('Corki','Q',0,0,[60,105,150,195,240],'25.19');mod('Corki','Q',0,1,125,'25.19')
note('Corki','Q','25.19 공식 문서는 공격력 계수라고만 표기하고 기존 자료는 추가 공격력 계수로 표기합니다. 계수 125%를 반영했지만 총/추가 공격력 구분은 추가 확인이 필요합니다.','The 25.19 notes say AD while the baseline specifies bonus AD. The coefficient is updated to 125%; total versus bonus AD requires further verification.')
mod('Corki','W',0,0,[30,45,60,75,90],'26.1');mod('Corki','W',1,0,[150,225,300,375,450],'26.1')
extra('Corki','R','기본 공격의 남은 충전 시간 감소','Recharge time reduction from attacks','치명타 확률에 따라 2~6초','2–6 seconds based on critical strike chance','26.14')
# Ekko
replace_effect('Ekko',0,0,[('AP의 90%','AP의 80%'),('300%','270%')],[('90% AP','80% AP'),('300%','270%')],'26.3')
effect('Ekko',0,1,'같은 대상에게 공진을 다시 발동하기까지 4초가 필요합니다.','Resonance has a 4-second cooldown per target.','26.11')
mod('Ekko','Q',2,1,70,'26.18');mod('Ekko','Q',3,1,100,'26.18')
extra('Ekko','Q','마나 소모','Mana cost','40 / 50 / 60 / 70 / 80','40 / 50 / 60 / 70 / 80','26.18')
# Fiora
mod('Fiora','R',1,0,[20,26.25,32.5],'26.19');mod('Fiora','R',1,1,17.5,'26.19')
mod('Fiora','R',2,0,[80,105,130],'26.19');mod('Fiora','R',2,1,70,'26.19')
mod('Fiora','R',3,0,[400,525,650],'26.19');mod('Fiora','R',3,1,350,'26.19')
extra('Fiora','R','회복 범위','Heal range','600','600','26.19')
extra('Gnar','Q','미니 나르 · 재사용 대기시간','Mini Gnar · cooldown','16 / 14.5 / 13 / 11.5 / 10초','16 / 14.5 / 13 / 11.5 / 10 seconds','25.16')
# Heimerdinger
mod('Heimerdinger','W',0,0,[50,75,100,125,150],'26.3')
mod('Heimerdinger','W',3,0,[90,135,180,225,270],'26.3');mod('Heimerdinger','W',6,0,[170,255,340,425,510],'26.3')
extra('Heimerdinger','Q','포탑 공격 사거리','Turret attack range','550','550','26.11');extra('Heimerdinger','Q','포탑 시야 범위','Turret vision range','650','650','26.11')
extra('Heimerdinger','Q','미니언 대상 추가 사거리','Additional range against minions','다른 대상이 사거리 안에 없으면 +50','+50 when no other target is in range','26.11')
extra('Heimerdinger','E','대상 위치 시야','Target-location vision','1.25초','1.25 seconds','26.11')
# Jinx
mod('Jinx','Q',3,0,[100,125,150,175,200],'25.19');mod('Jinx','E',0,0,[90,140,190,240,290],'25.19')
for ri,b,coef in [(0,[200,350,500],120),(1,[20,35,50],12),(2,[160,280,400],96),(3,[16,28,40],9.6)]:mod('Jinx','R',ri,0,b,'26.1');mod('Jinx','R',ri,1,coef,'26.1')
# Kennen
extra('Kennen','W','준비된 기본 지속 효과 적용','Ready passive application','첫 적중 효과에만 적용하지 않고 공격 전체의 적중 효과로 적용','Applies as an on-hit to the entire attack, rather than only its first on-hit trigger','26.9')
extra('Kennen','W','기본 지속 효과 치명타 피해','Passive critical strike damage','140% + 추가 치명타 피해의 40%','140% + 40% of bonus critical strike damage','26.9')
extra('Kennen','E','치명타 시 공격 속도 지속시간 연장','Critical strike attack-speed extension','치명타마다 1초 연장, 남은 시간 최대 4초; 횟수 제한 없음','Each critical strike adds 1 second, up to 4 seconds remaining; no limit on triggers','26.9')
mod('Kennen','E',2,0,[50,60,70,80,90],'26.20')
mod('Kennen','R',0,0,[25,50,75],'26.16');mod('Kennen','R',1,0,[40,80,120],'26.16');mod('Kennen','R',1,1,25,'26.16');mod('Kennen','R',2,0,[300,600,900],'26.16');mod('Kennen','R',2,1,187.5,'26.16')
extra('Kennen','R','재사용 대기시간','Cooldown','120초','120 seconds','26.4')
# LeBlanc
mod('Leblanc','W',0,1,90,'26.17')
for ri,b in [(0,[70,150,230]),(1,[140,300,460]),(2,[210,450,690]),(3,[150,315,480]),(4,[70,150,230]),(5,[140,300,460]),(6,[210,450,690])]:mod('Leblanc','R',ri,0,b,'26.13')
mod('Leblanc','R',3,1,90,'26.17')
# Locke: full baseline not available; only explicitly published current values.
for s in 'PQWER':note('Locke',s,'보관본에 없는 신규 챔피언입니다. 공식 패치에 명시된 항목만 확보했으며 전체 수치는 아직 미확보입니다.','This champion is absent from the archive. Only values explicitly published in official patches are available; the full ability data is incomplete.')
for s,ko,en,kv,ev,pa in [
('Q','재사용 입력 유지 시간','Recast hold time','4초','4 seconds','26.14'),('Q','대못 1개 피해량','Damage per nail','40 / 48 / 56 / 64 / 72 + AP의 20%','40 / 48 / 56 / 64 / 72 + 20% AP','26.15'),('Q','대못 3개 피해량','Three-nail damage','120 / 144 / 168 / 192 / 216 + AP의 60%','120 / 144 / 168 / 192 / 216 + 60% AP','26.15'),('Q','표식 기본 추가 피해량','Mark base bonus damage','18 / 26 / 34 / 42 / 50','18 / 26 / 34 / 42 / 50','26.14'),('Q','미사용 충전 반환','Unused charge refund','마나와 재사용 대기시간 10~40%','10–40% mana and cooldown','26.21'),('W','추가 이동 속도','Bonus move speed','40% + AP 100당 2%','40% + 2% per 100 AP','26.15'),('W','회색 체력 기본값','Grey health base value','40 / 60 / 80 / 100 / 120 + AP의 100%','40 / 60 / 80 / 100 / 120 + 100% AP','26.15'),('W','마나 소모','Mana cost','60 / 65 / 70 / 75 / 80','60 / 65 / 70 / 75 / 80','26.21'),('W','현재 체력 비례 회색 체력 저장량','Grey health storage from current health','20~200 (레벨 비례)','20–200 (level based)','26.21'),('W','현재 체력 비례 저장량','Current health storage','100~500 (레벨 비례) + AP의 60%','100–500 (level based) + 60% AP','26.21'),('E','순간이동 피해량','Blink damage','40 / 55 / 70 / 85 / 100 + AP의 50%','40 / 55 / 70 / 85 / 100 + 50% AP','26.21')]:extra('Locke',s,ko,en,kv,ev,pa)
# Miss Fortune
extra('MissFortune','Q','치명타 피해 배율','Critical damage multiplier','1 + 추가 치명타 피해의 50%','1 + 50% of bonus critical strike damage','26.1')
mod('MissFortune','E',0,0,[11.25,15,18.75,22.5,26.25],'26.21');mod('MissFortune','E',1,0,[90,120,150,180,210],'26.21')
delete('MissFortune','R',1)
extra('MissFortune','R','파동당 물리 피해량','Physical damage per wave','20 / 30 / 40 + 총 공격력의 60% + AP의 25%','20 / 30 / 40 + 60% total AD + 25% AP','26.1')
extra('MissFortune','R','전체 파동 물리 피해 · 치명타 제외','All-wave physical damage · no critical strikes','280 / 480 / 720 + 총 공격력의 840 / 960 / 1080% + AP의 350 / 400 / 450%','280 / 480 / 720 + 840 / 960 / 1080% total AD + 350 / 400 / 450% AP','26.1','derived')
extra('MissFortune','R','치명타 피해 배율','Critical strike damage','145% + 추가 치명타 피해 1%당 0.45%','145% + 0.45% per 1% bonus critical strike damage','26.21')
# Nami: old minimum derived rows aren't full AP-dependent bounce expressions.
delete('Nami','W',1);delete('Nami','W',3)
extra('Nami','W','튕길 때마다 효과 배율','Effect multiplier per bounce','0.8 + AP 100당 0.15 (첫 대상 효과에 순차 적용)','0.8 + 0.15 per 100 AP (applied successively from the first target)','26.7','derived')
mod('Nami','E',0,0,[20,35,50,65,80],'26.14');mod('Nami','E',1,0,[60,105,150,195,240],'26.14')
# Nilah: post-hotfix crit multiplier; do not retain old fixed 2x maximum.
mod('Nilah','Q',0,0,[0,10,20,30,40],'26.1');mod('Nilah','Q',0,1,100,'26.1');delete('Nilah','Q',1)
extra('Nilah','Q','치명타 확률 비례 피해 증폭','Critical-chance damage scaling','추가 치명타 피해의 70%를 치명타 확률에 비례해 적용','70% of bonus critical strike damage, scaled by critical strike chance','26.1')
extra('Nilah','Q','치명타 확률 비례 방어구 관통력','Armor penetration from critical chance','0~30%','0–30%','26.1')
extra('Nilah','Q','몬스터 대상 2차 피해','Secondary damage to monsters','총 공격력의 100%','100% total AD','25.17')
extra('Nilah','R','마나 소모','Mana cost','100','100','26.1')
# Ornn: Brittle belongs to passive prose despite W heading in patch notes.
mod('Ornn','W',4,0,[260,320,380,440,500],'25.23');mod('Ornn','W',5,0,[52,64,76,88,100],'25.23')
replace_effect('Ornn',0,2,[('10%~18%','9%~17%'),('최대 250','W 스킬 레벨에 따라 최대 260 / 320 / 380 / 440 / 500')],[('10% : 18%','9% : 17%'),('capped at 250 against monsters','capped at 260 / 320 / 380 / 440 / 500 against monsters based on W rank')],'26.7')
extra('Ornn','W','불안정 피해','Brittle proc damage','대상 최대 체력의 9~17% (1~18레벨)','9–17% target maximum health (levels 1–18)','26.7')
extra('Ornn','W','불안정 몬스터 피해 한도','Brittle monster damage cap','260 / 320 / 380 / 440 / 500','260 / 320 / 380 / 440 / 500','25.23')
# Quinn
replace_effect('Quinn',0,1,[('10~95(레벨에 따라) + 총 공격력의 16%~50%(레벨에 따라)','15~120(레벨에 따라) + 추가 공격력의 40%')],[('10 : 95 (based on level) (+ 16% : 50% (based on level) AD)','15 : 120 (based on level) (+ 40% bonus AD)')],'26.1')
OUT['Quinn']['skills']['P']['effects']['ko']+=['기본 재사용 대기시간은 7초이며, 몬스터에게 추가로 75의 피해를 입힙니다.'];OUT['Quinn']['skills']['P']['effects']['en']+=['The base cooldown is 7 seconds. Deals 75 additional damage to monsters.'];OUT['Quinn']['skills']['P']['sources']+=refs('Quinn','26.11')
mod('Quinn','Q',0,1,[80,85,90,95,100],'25.21')
extra('Quinn','Q','몬스터 피해 배율','Monster damage modifier','200%','200%','26.11')
extra('Quinn','R','공중 강습 피해량','Skystrike damage','60 / 90 / 120 + 추가 공격력의 35%','60 / 90 / 120 + 35% bonus AD','25.21');extra('Quinn','R','마나 소모','Mana cost','50 / 25 / 0','50 / 25 / 0','26.10')
# Ryze
mod('Ryze','Q',1,0,[30,35,40,45,50],'26.21');mod('Ryze','W',0,1,70,'26.21');mod('Ryze','W',0,2,3,'26.21')
delete('Ryze','R',0)
for s in ['Q','R']:extra('Ryze',s,'전이 대상 과부하 추가 피해','Bonus Overload damage on Flux targets','10 / 40 / 70 / 100% (R 0 / 1 / 2 / 3레벨)','10 / 40 / 70 / 100% (R rank 0 / 1 / 2 / 3)','26.21')
extra('Ryze','E','마나 소모','Mana cost','40 / 50 / 60 / 70 / 80','40 / 50 / 60 / 70 / 80','26.19')
extra('Ryze','R','원 가장자리 이동 대상','Targets pathing at the circle edge','원 밖으로 이동 중인 가장자리 챔피언도 순간이동 대상에 포함','Includes champions near the edge even when pathing out of the circle','26.4')
# Sett
delete('Sett','E',1);extra('Sett','E','몬스터 대상 물리 피해','Physical damage to monsters','50 / 70 / 90 / 110 / 130 + 총 공격력의 60% + 125~250 (챔피언 레벨 비례)','50 / 70 / 90 / 110 / 130 + 60% total AD + 125–250 (champion level based)','25.17','derived')
# Sion
replace_effect('Sion',0,0,[('2.3~24.4','2~19'),('1.61~17.08','1.4~13.3')],[('2.3 : 24.4','2 : 19'),('1.61 : 17.08','1.4 : 13.3')],'25.16')
mod('Sion','Q',1,0,[30,45,60,75,90],'26.13');delete('Sion','Q',0)
# Fully charged damage is unchanged; recalculate all derived target modifiers.
mod('Sion','Q',3,0,[49.5,74.25,99,123.75,148.5],'26.13');mod('Sion','Q',3,1,[66,82.5,99,115.5,132],'25.23')
mod('Sion','Q',4,0,[148.5,255.75,363,470.25,577.5],'25.23');mod('Sion','Q',4,1,[198,247.5,297,346.5,396],'25.23')
mod('Sion','Q',5,0,[18,27,36,45,54],'26.13')
extra('Sion','Q','몬스터 피해 배율','Monster damage modifier','165%','165%','25.23')
extra('Sion','W','마나 소모','Mana cost','75 / 80 / 85 / 90 / 95','75 / 80 / 85 / 90 / 95','26.13');extra('Sion','E','방어력 감소','Armor reduction','25%','25%','25.16')
mod('Sion','R',1,0,[450,900,1350],'26.21');mod('Sion','R',1,1,120,'26.21')
extra('Sion','R','첫 3초 동안 피해 증가','Damage increase over first 3 seconds','최소 피해량 대비 0~200% 증가','0–200% increase over minimum damage','26.21')
OUT['Sion']['skills']['R']['notes']={'ko':'26.21 정정에 따라 최소 추가 공격력 계수는 40%, 최대는 120%입니다. 25.16의 60% 표기는 실제 변경이 아닌 툴팁 오류였습니다.','en':'The 26.21 correction confirms 40–120% bonus AD. The 60% minimum shown in 25.16 was a tooltip error, not an actual change.'}
# Taliyah
for ri,b in [(0,[55,72.5,90,107.5,125]),(1,[22,29,36,43,50]),(2,[143,188.5,234,279.5,325]),(3,[99,130.5,162,193.5,225])]:mod('Taliyah','Q',ri,0,b,'26.9')
extra('Taliyah','Q','마나 소모','Mana cost','55 / 60 / 65 / 70 / 75','55 / 60 / 65 / 70 / 75','25.18');extra('Taliyah','Q','다져진 땅 마나 소모','Worked Ground mana cost','10','10','25.18')
extra('Taliyah','Q','바위당 추가 몬스터 피해','Bonus monster damage per rock','20 / 25 / 30 / 35 / 40; 강화 바위 주 대상은 80% 증가','20 / 25 / 30 / 35 / 40; empowered boulder primary target increases this by 80%','26.9')
mod('Taliyah','E',0,0,[70,115,160,205,250],'26.21');mod('Taliyah','E',0,1,70,'26.21');mod('Taliyah','E',1,0,[30,45,60,75,90],'26.21');mod('Taliyah','E',2,0,[75,112.5,150,187.5,225],'26.21')
extra('Taliyah','E','몬스터 피해 배율','Monster damage modifier','225%','225%','26.21');extra('Taliyah','E','마나 소모','Mana cost','90','90','25.18')
# Tristana
mod('Tristana','Q',0,0,[40,60,80,100,120],'26.21');extra('Tristana','Q','마나 소모','Mana cost','15 / 20 / 25 / 30 / 35','15 / 20 / 25 / 30 / 35','26.12')
for ri,b,coef in [(1,[60,85,110,135,160],80),(2,[15,21.25,27.5,33.75,40],20),(3,[60,85,110,135,160],80),(4,[120,170,220,270,320],160)]:mod('Tristana','E',ri,0,b,'26.1');mod('Tristana','E',ri,1,coef,'26.1')
extra('Tristana','E','치명타 피해 계수','Critical strike damage scaling','추가 치명타 피해의 40%를 치명타 확률에 비례해 적용','40% of bonus critical strike damage, scaled by critical strike chance','26.1')
# Udyr
mod('Udyr','Q',0,1,3.5,'26.9');mod('Udyr','Q',1,1,7,'26.9');mod('Udyr','Q',3,0,[6,12,18,24,30,36],'26.9');mod('Udyr','Q',3,1,20,'26.9')
RAW['Udyr','Q'][0]['rows'][3]['modifiers'].append({'values':[1,2],'units':['% bonus health','% bonus health']})
extra('Udyr','Q','각성 · 첫 두 공격 추가 피해','Awakened first two attacks additional damage','대상 최대 체력의 2~4% (레벨 비례) + 추가 공격력 100당 1.5% + 추가 체력 1000당 1%','2–4% target maximum health (level based) + 1.5% per 100 bonus AD + 1% per 1000 bonus health','26.9')
extra('Udyr','Q','각성 · 연쇄 번개 타격당 피해','Awakened lightning damage per bounce','대상 최대 체력의 1.5~3% (레벨 비례) + AP 100당 0.6%','1.5–3% target maximum health (level based) + 0.6% per 100 AP','26.9')
mod('Udyr','W',1,0,[45,65,85,105,125,145],'26.4');RAW['Udyr','W'][0]['rows'][1]['modifiers'].append({'values':[50],'units':['% bonus AD']});mark('Udyr','W',0,1,'26.9')
mod('Udyr','W',2,1,[45,65,85,105,125,145],'26.4');RAW['Udyr','W'][0]['rows'][2]['modifiers'].append({'values':[100],'units':['% bonus AD']});mark('Udyr','W',0,2,'26.9')
mod('Udyr','W',3,1,[22.5,32.5,42.5,52.5,62.5,72.5],'26.4');RAW['Udyr','W'][0]['rows'][3]['modifiers'].append({'values':[50],'units':['% bonus AD']});mark('Udyr','W',0,3,'26.9')
delete('Udyr','W',4)
extra('Udyr','W','각성 회복 주기','Awakened healing ticks','총 회복량을 지속시간에 걸쳐 나누어 적용','Total healing is distributed over the effect duration','26.9','derived')
extra('Udyr','E','기본 이동 속도 추가 계수','Additional normal move-speed scaling','추가 공격력 100당 이동 속도 5%','5% move speed per 100 bonus AD','26.9');extra('Udyr','E','각성 이동 속도 추가 계수','Additional awakened move-speed scaling','추가 공격력 100당 이동 속도 10%','10% move speed per 100 bonus AD','26.9')
# Updated normal decay also carries the same 30% multiplier as the baseline.
RAW['Udyr','E'][0]['rows'][0]['modifiers'].append({'values':[5],'units':['% per 100 bonus AD']});mark('Udyr','E',0,0,'26.9')
RAW['Udyr','E'][0]['rows'][1]['modifiers'].append({'values':[1.5],'units':['% per 100 bonus AD']});mark('Udyr','E',0,1,'26.9')
# Vel'Koz
replace_effect('Velkoz',0,1,[('35~180','35~205'),('AP의 60%','AP의 65%')],[('35 : 180','35 : 205'),('60% AP','65% AP')],'26.21')
mod('Velkoz','R',1,0,[450,700,925],'25.18');mod('Velkoz','R',0,0,[450/13,700/13,925/13],'25.18')
extra('Velkoz','E','재사용 대기시간','Cooldown','12 / 11.5 / 11 / 10.5 / 10초','12 / 11.5 / 11 / 10.5 / 10 seconds','25.18')
# Xin Zhao: source explicitly calls new damage ratio bonus AD; avoid old total-AD prose.
effect('XinZhao',0,0,ko='기본 공격 적중과 풍전참뢰(W)의 타격이 결심 중첩을 쌓습니다. 세 번째 중첩을 소모해 추가 공격력의 15 / 30 / 45 / 60% + AP의 5 / 10 / 15 / 20%(1 / 6 / 11 / 16레벨)에 해당하는 추가 물리 피해를 입힙니다. 동시에 최대 체력의 2 / 3.5 / 5% + AP의 40 / 50 / 70%(1 / 6 / 11레벨)만큼 회복합니다.',en='Basic attacks on-hit and Wind Becomes Lightning strikes generate Determination stacks. The third stack is consumed to deal bonus physical damage equal to 15 / 30 / 45 / 60% bonus AD + 5 / 10 / 15 / 20% AP at levels 1 / 6 / 11 / 16, and heal for 2 / 3.5 / 5% maximum health + 40 / 50 / 70% AP at levels 1 / 6 / 11.',patch='26.12')
OUT['XinZhao']['skills']['P']['sources']+=refs('XinZhao','26.11')
mod('XinZhao','Q',0,0,[15,30,45,60,75],'26.21');mod('XinZhao','Q',0,1,45,'26.21');mod('XinZhao','Q',1,0,[45,90,135,180,225],'26.21');mod('XinZhao','Q',1,1,135,'26.21')
extra('XinZhao','W','찌르기 둔화','Thrust slow','50% · 1.5초 + AP 100당 0.5초','50% for 1.5 seconds + 0.5 seconds per 100 AP','26.9');extra('XinZhao','W','마나 소모','Mana cost','60','60','26.12')
mod('XinZhao','E',0,1,120,'26.9');delete('XinZhao','E',1)
extra('XinZhao','E','추가 공격 속도 · 5초','Bonus attack speed · 5 seconds','38 / 46 / 54 / 62 / 70% + 영구적 추가 공격 속도 4%당 1% + AP 100당 10%','38 / 46 / 54 / 62 / 70% + 1% per 4% permanent bonus attack speed + 10% per 100 AP','26.21','derived');extra('XinZhao','E','마나 소모','Mana cost','60','60','26.12')
# Yuumi
replace_effect('Yuumi',0,0,[('25% AP','30% AP')],[('25% AP','30% AP')],'26.12')
mod('Yuumi','Q',1,0,[80,135,190,245,300,355],'25.16');mod('Yuumi','W',0,0,[4,5,6,7,8],'25.16');mod('Yuumi','W',1,0,[3,4,5,6,7],'25.16');mod('Yuumi','W',1,1,3,'25.16');mod('Yuumi','E',0,1,40,'26.12')
mod('Yuumi','R',0,0,[30,50,70],'26.8');mod('Yuumi','R',0,1,12,'26.8');mod('Yuumi','R',1,0,[150,250,350],'26.8');mod('Yuumi','R',1,1,60,'26.8');delete('Yuumi','R',5);delete('Yuumi','R',6)
extra('Yuumi','R','단짝 회복 배율','Best Friend heal multiplier','1.3~1.6배 (6~12레벨)','×1.3–1.6 (levels 6–12)','26.8')
extra('Yuumi','R','단짝 총 회복량','Total Best Friend healing','(150 / 250 / 350 + AP의 60%) × 1.3~1.6 (6~12레벨)','(150 / 250 / 350 + 60% AP) × 1.3–1.6 (levels 6–12)','26.8','derived')
extra('Yuumi','R','초과 회복 보호막','Overheal shield','회복 및 보호막 효과와 고통스러운 상처를 반영','Accounts for heal/shield power and Grievous Wounds','26.8')
extra('Yuumi','R','밀착 아군 추가 회복 수정','Attached-ally healing fix','다른 아군 회복 시 밀착 아군이 추가로 회복되지 않음','Healing another ally no longer grants an additional heal to the attached ally','26.8')
# Formatting retains the existing Korean terminology dictionary.
def number(n):return f'{n:.4f}'.rstrip('0').rstrip('.') if isinstance(n,float) else str(n)
def fmt(m,lang):
 values=m.get('values',[]);units=m.get('units',[])
 if not values:return '—'
 units=units or ['']*len(values)
 if lang=='ko':units=[LEX['units'].get(u,u) for u in units]
 if len(set(values))==1 and len(set(units))==1:return number(values[0])+units[0]
 if len(set(units))==1:return ' / '.join(number(v) for v in values)+units[0]
 return ' / '.join(number(v)+(units[i] if i<len(units) else units[-1]) for i,v in enumerate(values))
for id in IDS:
 for s in 'PQWER':
  skill=OUT[id]['skills'][s];vs=RAW[id,s]
  for vi,v in enumerate(vs):
   for ri,r in enumerate(v['rows']):
    if (id,s,vi,ri) in DELETED:continue
    prefix=(v['name']+' · ') if len(vs)>1 else ''
    kprefix=(LEX['variants'].get(v['name'],v['name'])+' · ') if len(vs)>1 else ''
    source,prov=MARK.get((id,s,vi,ri),([], 'baseline'))
    skill['rows'].append({'attribute':{'ko':kprefix+LEX['labels'].get(r['attribute'],r['attribute']),'en':prefix+r['attribute']},'value':{lang:' + '.join(fmt(m,lang) for m in r.get('modifiers',[])) for lang in ['ko','en']},'provenance':prov,'sources':source})
  skill['rows']+=EXTRA.get((id,s),[])
  allrefs=skill['sources']+[x for r in skill['rows'] for x in r['sources']]
  skill['sources']=list({(r['patch'],r['date'],r['url']):r for r in allrefs}.values())
  if skill['status']!='partial' and skill['sources']:skill['status']='reconciled'
  if not skill['rows'] and not any(skill['effects'].values()) and not vs:
   skill['status']='partial'
  if len(skill['effects']['ko'])!=len(skill['effects']['en']):raise ValueError(id+' effects lengths')
# Source hashes make changes in the reviewed input detectable on rebuild.
import hashlib
for id in IDS:
 history=[h for h in EN[id]['history'] if (25,15)<pkey(h['patch'])<=(26,21) and not h.get('release')]
 OUT[id]['audit']['historySha256']=hashlib.sha256(json.dumps(history,sort_keys=True,separators=(',',':')).encode()).hexdigest()
 OUT[id]['audit']['changeCount']=sum(len(h['changes']) for h in history)
path=Path(__file__).with_name('group-5.json');path.write_text(json.dumps(OUT,ensure_ascii=False,indent=2)+'\n')
print('Wrote',len(OUT),'champions',sum(len(s['rows']) for c in OUT.values() for s in c['skills'].values()),'rows',sum(c['audit']['changeCount'] for c in OUT.values()),'reviewed changes')
