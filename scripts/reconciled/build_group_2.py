"""Reviewed 25.16–26.21 reconciliation for group 2. Run from any directory."""
import json,copy,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]; DATA=ROOT/'dist/data'
IDS=['Ahri','Amumu','AurelionSol','Blitzcrank','Camille','Diana','Evelynn','Galio','Graves','Illaoi','Jax','Kaisa','Katarina','Kindred','Leona','Lulu','MasterYi','Mordekaiser','Nautilus','Nunu','Poppy','Rammus','Rengar','Sejuani','Shen','Skarner','Sylas','Taric','Tryndamere','Varus','Vi','Warwick','Yone','Zac','Zoe']
LEX=json.loads((DATA/'localization-ko.json').read_text()); RAW={i:json.loads((DATA/f'{i}.json').read_text()) for i in IDS}; EN={i:json.loads((DATA/'en'/f'{i}.json').read_text()) for i in IDS}
OUT={}; WORK={}; MARK={}; SKIP=set()
def pk(p):return tuple(map(int,p.split('.')))
def histories(i,lang='en'):return [h for h in (EN if lang=='en' else RAW)[i]['history'] if (25,15)<pk(h['patch'])<=(26,21) and not h.get('release')]
def sources(i,s,p=None):
 hs=[h for h in histories(i) if (not p or h['patch']==p) and (s=='*' or any(c['slot']==s for c in h['changes']))]
 return [dict(patch=h['patch'],date=h['date'],url=h['url']) for h in hs]
def fmt(m,l):
 v=m['values'];u=m['units'];un=lambda x:LEX['units'].get(x,x) if l=='ko' else x
 num=lambda x:format(x,'.5f').rstrip('0').rstrip('.') if isinstance(x,float) else str(x)
 if len(v)==18 and len(set(u))==1:return num(v[0])+'–'+num(v[-1])+un(u[0])+(' (챔피언 레벨에 따라)' if l=='ko' else ' (by champion level)')
 if len(set(v))==1 and len(set(u))==1:return num(v[0])+un(u[0])
 if len(set(u))==1:return ' / '.join(map(num,v))+un(u[0])
 return ' / '.join(num(x)+un(u[min(j,len(u)-1)]) for j,x in enumerate(v))
for i in IDS:
 skills={};WORK[i]={}
 for s in 'PQWER':
  f=next((f for f in RAW[i]['formulas'] if f['slot']==s),{'variants':[]}); rows=[]
  for vi,v in enumerate(f['variants']):
   for ri,r in enumerate(v['rows']):
    rr=copy.deepcopy(r);rr['_pos']=(vi,ri);rr['_variant']=v['name'] if len(f['variants'])>1 else None;rows.append(rr)
  WORK[i][s]=rows
  effects={'en':[e for v in f['variants'] for e in v.get('effects',[])] if s=='P' else [],'ko':[e for v in LEX.get('passives',{}).get(i,{}).get('variants',[]) for e in v.get('effects',[])] if s=='P' else []}
  skills[s]={'rows':[],'effects':effects,'status':'baseline','notes':{'ko':'','en':''},'sources':sources(i,s)}
 OUT[i]={'skills':skills,'audit':{'reviewedPatches':sorted(set(h['patch'] for h in histories(i)),key=pk),'notes':[]}}
def mark(i,s,r,p=None,derived=False):
 r['_provenance']='derived' if derived else 'patch';r['_sources']=sources(i,s,p);OUT[i]['skills'][s]['status']='reconciled'
def mod(i,s,pos,m,values,p=None,unit=None,derived=False):
 r=next(r for r in WORK[i][s] if r['_pos']==pos);v=r['modifiers'][m];a=values if isinstance(values,list) else [values]*len(v['values']);v['values']=a
 if unit is not None:v['units']=[unit]*len(a)
 elif len(v['units'])!=len(a):v['units']=[v['units'][0]]*len(a)
 mark(i,s,r,p,derived)
def add(i,s,ko,en,kv,ev,p=None,derived=False):
 r={'_pos':None,'_attribute':{'ko':ko,'en':en},'_value':{'ko':kv,'en':ev}};mark(i,s,r,p,derived);WORK[i][s].append(r)
def remove(i,s,positions):WORK[i][s]=[r for r in WORK[i][s] if r['_pos'] not in positions]
def effects_replace(i,en_old,en_new,ko_old,ko_new):
 e=OUT[i]['skills']['P']['effects'];assert any(en_old in x for x in e['en']),(i,en_old);assert any(ko_old in x for x in e['ko']),(i,ko_old)
 e['en']=[x.replace(en_old,en_new) for x in e['en']];e['ko']=[x.replace(ko_old,ko_new) for x in e['ko']];OUT[i]['skills']['P']['status']='reconciled'
def note(i,s,ko,en,partial=True):
 OUT[i]['skills'][s]['notes']={'ko':ko,'en':en}
 if partial:OUT[i]['skills'][s]['status']='partial'
def effect_add(i,ko,en):OUT[i]['skills']['P']['effects']['ko'].append(ko);OUT[i]['skills']['P']['effects']['en'].append(en);OUT[i]['skills']['P']['status']='reconciled'
# Update underlying values and dependent totals. Source-only presentation rows below
# retain conditions not represented by the archive's rank tables.
mod('Ahri','Q',(0,0),0,[35,60,85,110,135],'26.6');mod('Ahri','Q',(0,1),0,[70,120,170,220,270],'26.6',derived=True)
for ri,vals,ap in [(1,[16,24,32,40,48],16),(2,[72,108,144,180,216],72),(4,[32,48,64,80,96],32)]:
 mod('Ahri','W',(0,ri),0,vals,'25.23',derived=ri!=2);mod('Ahri','W',(0,ri),1,ap,'25.23',derived=ri!=2)
mod('Ahri','R',(0,0),0,[75,125,175],'25.19')
mod('AurelionSol','Q',(0,3),0,[60,70,80,90,100],'25.22')
mod('Camille','W',(0,0),0,[60,85,110,135,160],'25.20');mod('Camille','W',(0,2),0,[30,42.5,55,67.5,80],'25.20',derived=True)
mod('Camille','W',(0,1),0,[7,7.5,8,8.5,9],'26.16');mod('Camille','W',(0,3),0,[3.5,3.75,4,4.25,4.5],'26.16',derived=True)
effects_replace('Camille','20% of her maximum health','10 / 15 / 20 / 25% of her maximum health at levels 1 / 7 / 13 / 19','최대 체력의 20%','1 / 7 / 13 / 19레벨에 최대 체력의 10% / 15% / 20% / 25%')
effect_add('Camille','재사용 대기시간은 1 / 7 / 13레벨에 14 / 11 / 8초입니다.','Cooldown is 14 / 11 / 8 seconds at levels 1 / 7 / 13.')
effects_replace('Diana','260%','270%','260%','270%');OUT['Diana']['skills']['P']['sources']+=sources('Diana','S','26.11')
mod('Diana','W',(0,0),2,14,'26.20');mod('Diana','W',(0,3),2,28,'26.20',derived=True)
effects_replace('Galio','45% AP','40% AP','주문력의 45%','주문력의 40%')
# Global critical-strike changes cannot safely be inferred from old item-specific alternatives.
e=OUT['Galio']['skills']['P']['effects'];e['en']=e['en'][:2];e['ko']=e['ko'][:2]
note('Galio','P','공격력 부분의 치명타 배율은 보관본에 아이템 조건이 누락되어 있어 표시하지 않습니다.','The critical multiplier on the AD portion is omitted because the archive lacks its item conditions.')
add('Galio','Q','소용돌이 주기당 최대 체력 피해','Tornado maximum-health damage per tick','대상 최대 체력의 2%','2% target maximum health','25.18')
mod('Galio','E',(0,0),0,[100,135,170,205,240],'26.10');mod('Galio','E',(0,0),1,100,'26.10');mod('Galio','E',(0,1),0,[80,108,136,164,192],'26.10',derived=True);mod('Galio','E',(0,1),1,80,'26.10',derived=True)
add('Galio','R','추가 마법 저항력 계수','Additional bonus MR scaling','기존 피해량 + 추가 마법 저항력의 100%','Existing damage + 100% bonus magic resistance','26.10')
# Graves Q final coefficients and sum; E stacking cap remains eight.
for ri,vals,ratio in [(0,[50,75,100,125,150],55),(1,[80,125,170,215,260],[45,60,75,90,105]),(2,[130,200,270,340,410],[100,115,130,145,160])]:
 mod('Graves','Q',(0,ri),0,vals,'26.17',derived=ri==2);mod('Graves','Q',(0,ri),1,ratio,'26.17',derived=ri==2)
mod('Graves','E',(0,0),0,[7,10,13,16,19],'26.4');mod('Graves','E',(0,1),0,[56,80,104,128,152],'26.4',derived=True)
add('Graves','E','중첩당 추가 마법 저항력','Bonus MR per stack','3.5 / 5 / 6.5 / 8 / 9.5','3.5 / 5 / 6.5 / 8 / 9.5','26.4')
add('Graves','E','최대 추가 마법 저항력 · 8중첩','Maximum bonus MR · 8 stacks','28 / 40 / 52 / 64 / 76','28 / 40 / 52 / 64 / 76','26.4',True)
e=OUT['Graves']['skills']['P']['effects'];e['ko'][2]='치명타는 25% 더 넓은 원뿔 범위에 6개의 산탄을 발사합니다. 산탄의 피해 증가량은 추가 치명타 피해의 50%이며, 모든 산탄을 적중시켰을 때 일반 공격 대비 최대 피해량은 2배입니다.';e['en'][2]='Critical strikes spray 6 pellets over a 25% wider cone. Pellet damage scales with 50% of bonus critical damage; maximum damage relative to a non-critical attack is 2x.';OUT['Graves']['skills']['P']['status']='reconciled'
effects_replace('Illaoi','9 : 162','9 : 200','9~162','9~200');effects_replace('Illaoi','105% AD','110% AD','총 공격력의 105%','총 공격력의 110%')
effect_add('Illaoi','촉수 생성 재사용 대기시간은 레벨에 따라 18~7초입니다. 소환사 주문 순간이동 도중에는 생성을 멈추고 이동이 끝난 뒤 재개합니다.','Tentacle spawn cooldown is 18–7 seconds by level. Spawning pauses during Summoner Teleport and resumes afterwards.')
mod('Illaoi','W',(0,0),1,3.5,'25.18')
add('Illaoi','E','숙주 효과 지속시간','Vessel effect duration','4초','4 seconds','25.18')
effect_add('Jax','19레벨에는 중첩당 추가 공격 속도를 1.5% 더 얻습니다.','At level 19, each stack grants an additional 1.5% attack speed.')
mod('Jax','E',(0,0),2,4,'26.12');mod('Jax','E',(0,1),2,8,'26.12',derived=True)
mod('Jax','R',(0,2),0,[45,60,75],'25.19');mod('Jax','R',(0,3),0,[27,36,45],'25.19',derived=True)
mod('Kaisa','R',(0,0),0,[100,150,200],'26.13')
effects_replace('Kaisa','4 : 24 (based on level)','4 : 30 (based on level)','4~24(레벨에 따라)','4~30(레벨에 따라)');effects_replace('Kaisa','1 : 6 (based on level)','1 : 8 (based on level)','중첩당 1~6(레벨에 따라)','중첩당 1~8(레벨에 따라)')
for m in range(4):
 old=next(r for r in WORK['Kindred']['W'] if r['_pos']==(0,0))['modifiers'][m]
 mod('Kindred','W',(0,1),m,[round(v*1.65,6) for v in old['values']],'26.20',unit="% (+ 1.65% per mark) of target's current health" if m==3 else None,derived=True)
remove('Kindred','E',[(0,1)])
add('Kindred','E','치명타 확률·피해 계수','Critical chance and damage scaling','잃은 체력 피해와 늑대 도약 피해에 추가 치명타 확률·피해의 50%를 항상 적용 (최대 1.5 / 1.65배)','50% of bonus critical chance and critical damage always applies to missing-health and pounce damage (up to 1.5 / 1.65x)','26.1')
note('Kindred','E','1.5 / 1.65배는 공식 문서의 표기입니다. 각 값의 장비 조건은 원문에 명시되지 않아 추정하지 않았습니다.','1.5 / 1.65x is the official wording; the article does not specify the item condition for each value, so none is inferred.')
add('Kindred','E','몬스터 체력 비례 피해 상한','Monster health-scaling cap','체력 비례 피해 부분만 최대 200','200, applied only to the percent-health portion','26.1')
for ri in [0,1]:mod('Lulu','E',(0,ri),0,[70,110,150,190,230],'25.16')
mod('Lulu','E',(0,1),1,50,'25.16')
mod('MasterYi','R',(0,1),0,[40,50,60],'26.18')
add('MasterYi','Q','적중 시 효과 효율','On-hit effectiveness','75%','75%','26.2')
add('Mordekaiser','Q','추가 공격력 계수','Bonus AD scaling','기존 피해량 + 추가 공격력의 120%','Existing damage + 120% bonus AD','25.16')
# Archive level curve disagrees with patch's level 10–20 scaling. Do not retain it as a verified number.
r=next(r for r in WORK['Mordekaiser']['Q'] if r['_pos']==(0,0));r['modifiers']=r['modifiers'][1:]
add('Mordekaiser','Q','10~20레벨 추가 성장 피해','Additional damage growth at levels 10–20','해당 구간에서 레벨당 +7','+7 per level in this interval','26.20')
note('Mordekaiser','Q','공식 패치에 명시된 10~20레벨 구간은 반영했습니다. 기존 보관본의 전체 레벨 성장식과 차이가 있어 전체 합계는 표시하지 않습니다.','The stated level 10–20 growth is applied. The archive disagrees on the full level curve, so a combined level-dependent total is not shown.')
mod('Mordekaiser','E',(0,1),0,[60,80,100,120,140],'26.14');mod('Mordekaiser','E',(0,1),1,45,'26.14')
add('Mordekaiser','R','능력치 강탈','Stats stolen','10%','10%','26.15')
mod('Nautilus','Q',(0,0),0,[85,125,165,205,245],'26.18')
# New monster bonus only occurs on the first wave; subsequent waves keep normal half damage.
for ri,vals,ap in [(4,[180,255,330,405,480],100),(5,[27.5,45,62.5,80,97.5],25),(6,[235,345,455,565,675],150)]:
 mod('Nautilus','E',(0,ri),0,vals,'25.16',derived=True);mod('Nautilus','E',(0,ri),1,ap,'25.16',derived=True)
for ri,vals in [(0,[15,22.5,30,37.5,45]),(1,[45,67.5,90,112.5,135]),(3,[135,202.5,270,337.5,405])]:mod('Nunu','E',(0,ri),0,vals,'26.3',derived=ri!=0)
mod('Nunu','R',(0,1),0,[750,1100,1450],'26.21')
# Nunu W reverted in26.3 to archive values; mark them reconciled explicitly.
for r in WORK['Nunu']['W']:mark('Nunu','W',r,'26.3',r['_pos']!=(0,1))
for ri,vals,ad,hp in [(0,[30,55,80,105,130],75,[7,7.5,8,8.5,9]),(4,[60,110,160,210,260],150,[14,15,16,17,18])]:
 mod('Poppy','Q',(0,ri),0,vals,'26.16',derived=ri==4);mod('Poppy','Q',(0,ri),1,ad,'26.16',derived=ri==4);mod('Poppy','Q',(0,ri),2,hp,'26.16',derived=ri==4)
mod('Poppy','Q',(0,1),0,[70,105,140,175,210],'26.19')
for ri,vals,ad in [(2,[100,160,220,280,340],75),(5,[200,320,440,560,680],150)]:mod('Poppy','Q',(0,ri),0,vals,'26.19',derived=True);mod('Poppy','Q',(0,ri),1,ad,'26.16',derived=True)
mod('Poppy','Q',(0,3),0,[20,23,26,29,32],'26.16');add('Poppy','Q','둔화 추가 체력 계수','Slow bonus-health scaling','추가 체력 1,000당 +8%','+8% per 1,000 bonus health','26.16')
add('Poppy','W','총 방어력·마법 저항력 증가','Total armor and MR increase','16% · 체력 40% 미만이면 두 배','16%; doubled below 40% health','26.16')
mod('Rammus','W',(0,0),0,[25,30,35,40,45],'26.21');mod('Rammus','W',(0,0),1,[30,35,40,45,50],'26.21');mod('Rammus','W',(0,1),0,[20,25,30,35,40],'26.21');mod('Rammus','W',(0,1),1,[30,35,40,45,50],'26.21')
remove('Rengar','Q',[(0,0)])
add('Rengar','Q','기본 공격을 포함한 물리 피해','Physical damage including the attack','20 / 55 / 90 / 125 / 160 + 총 공격력의 105%','20 / 55 / 90 / 125 / 160 + 105% total AD','26.4')
add('Rengar','Q','강화 물리 피해','Ferocity damage','35~240 (레벨에 따라) + 총 공격력의 120%','35–240 (by level) + 120% total AD','26.4')
add('Rengar','Q','치명타 발생 시 추가 피해','Additional damage when the attack crits','총 공격력의 100% / 130%','100% / 130% total AD','26.1')
note('Rengar','Q','치명타 추가 피해 100% / 130%는 공식 패치 표기이며 각 값의 장비 조건은 생략되어 있습니다.','The official notes state 100% / 130% bonus damage on crit but omit the item condition for each value.')
mod('Sejuani','Q',(0,0),1,75,'25.24');mod('Sejuani','W',(0,0),1,30,'25.24');mod('Sejuani','W',(0,2),1,90,'25.24',derived=True);mod('Sejuani','E',(0,0),1,70,'25.24')
mod('Shen','Q',(0,5),0,[100,125,150,175,200],'26.6')
for pos,val in [((0,0),90),((0,1),270),((1,0),90),((1,1),90)]:mod('Skarner','Q',pos,1,val,'25.22',derived=pos==(0,1))
mod('Skarner','Q',(1,0),3,11,'26.6')
add('Skarner','E','추가 공격력 계수','Bonus AD scaling','기존 피해량 + 추가 공격력의 120%','Existing damage + 120% bonus AD','25.22')
effect_add('Sylas','몬스터 대상 피해량은 115%입니다.','Damage against monsters is 115%.')
e=OUT['Sylas']['skills']['P']['effects'];e['ko']=[x for x in e['ko'] if '(175% + 40%)' not in x];e['en']=[x for x in e['en'] if '(175% + 40%)' not in x]
note('Sylas','P','주 대상 치명타 배율의 보관본 장비 조건이 누락되어 있어 해당 배율은 표시하지 않습니다.','The archive omits the item conditions for the primary-target critical multiplier, so that multiplier is not shown.')
for ri,ap in [(1,30),(2,60)]:mod('Sylas','W',(0,ri),1,ap,'26.12',derived=ri==2)
# First lash reverted to the original base/AP values in26.15; combined rows remain equal.
for ri in [0,3,5]:mark('Sylas','Q',next(r for r in WORK['Sylas']['Q'] if r['_pos']==(0,ri)),'26.15',ri!=0)
remove('Tryndamere','Q',[(0,0),(0,1),(0,2)])
add('Tryndamere','Q','잃은 체력 비례 추가 공격력','Bonus AD from missing health','최대 20 / 35 / 50 / 65 / 80 · 남은 체력 10% 이하에서 최대','Up to 20 / 35 / 50 / 65 / 80; reaches maximum at 10% remaining health','26.1')
mod('Tryndamere','W',(0,1),0,[30,35,40,45,50],'26.1')
mod('Tryndamere','E',(0,0),0,[80,120,160,200,240],'26.1');mod('Tryndamere','E',(0,0),1,100,'26.1')
# Preserve AP coefficient omitted from the change note; explicitly derived from baseline.
mark('Tryndamere','E',WORK['Tryndamere']['E'][0],'26.1',True)
# Varus: exact published endpoints; avoid inventing intermediate rank interpolation.
remove('Varus','Q',[(0,0),(0,1),(0,2),(0,3)])
add('Varus','Q','최소 물리 피해','Minimum physical damage','50~250 (스킬 랭크에 따라) + 추가 공격력의 80%','50–250 (by ability rank) + 80% bonus AD','26.21')
add('Varus','Q','최대 물리 피해','Maximum physical damage','85~425 (스킬 랭크에 따라) + 추가 공격력의 136%','85–425 (by ability rank) + 136% bonus AD','26.21',True)
add('Varus','Q','정신 집중에 따른 피해 증가','Damage increase with channel','최대 70%','Up to 70%','26.21')
add('Varus','Q','다수 관통 후 최소 피해 비율','Minimum damage after piercing targets','최소 원래 피해의 33% (기존 자료 조건)','At least 33% of original damage (archived condition)','26.21',True)
note('Varus','Q','최대 피해는 10월 22일 최소 피해(50~250)에 공식 최대 증가량 70%를 적용해 계산했습니다. 중간 랭크 수치는 문서에 없어 보간하지 않았습니다.','Maximum damage is calculated from the October 22 minimum (50–250) and the official 70% maximum increase. Intermediate rank values are not interpolated.',False)
for ri,vals,ap in [(0,[4,10,16,22,28],30),(1,[2.5,3,3.5,4,4.5],1.4),(2,[7.5,9,10.5,12,13.5],4.2),(3,[4.25,5.1,5.95,6.8,7.65],2.38),(4,[12.75,15.3,17.85,20.4,22.95],7.14)]:
 mod('Varus','W',(0,ri),0,vals,'26.21',derived=ri>1);mod('Varus','W',(0,ri),1,ap,'26.21',derived=ri>1)
r=WORK['Varus']['W'][0];r['modifiers'].append({'values':[20]*5,'units':['% bonus AD']*5})
mod('Varus','W',(0,5),0,[6,7,8,9,10],'26.21');mod('Varus','W',(0,6),0,[10.2,11.9,13.6,15.3,17],'26.21',derived=True)
mod('Varus','E',(0,0),0,[60,90,120,150,180],'25.16');mod('Varus','E',(0,0),1,90,'25.16')
OUT['Varus']['skills']['P']['effects']={'ko':['적을 처치하면 레벨에 따라 5 / 7 / 9 / 11초 동안 죽지 않는 복수심 효과를 얻습니다. 26.12 공식 문서는 챔피언이 아닌 유닛 처치 시 공격 속도 증가량을 30%로 기재합니다.','26.21 10월 22일 추가 패치는 처치/처치 관여 시 공격 속도 10%당 추가 공격력과 주문력을 각각 1.4 얻는다고 기재합니다. 챔피언 처치 효과와의 구분이 명확하지 않아 이전 26.12의 33%와 합쳐 하나의 수식으로 단정하지 않습니다.','효과가 활성화된 동안 공격 속도 상한은 3.33입니다 (기존 자료).'],'en':['Killing an enemy grants Living Vengeance for 5 / 7 / 9 / 11 seconds by level. The official 26.12 notes state 30% bonus attack speed on non-champion kills.','The October 22 hotfix states 1.4 bonus AD and AP per 10% attack speed on a kill/takedown. Its distinction from the champion-takedown modifier is unclear, so it is not combined with the older 26.12 value of 33% into a single claimed formula.','While the effect is active, the attack-speed cap is 3.33 (archived detail).']}
note('Varus','P','최신 추가 패치의 처치/처치 관여 구분이 이전 문서와 명확히 대응하지 않아 최종 통합 계수는 확인이 필요합니다.','The latest kill/takedown wording does not map unambiguously to the previous modifiers; the fully combined multiplier remains unverified.')
effects_replace('Vi','12%','10%','12%','10%')
effects_replace('Warwick','12 : 46 (based on level)','6 / 18.25 / 30.5 / 42.75 / 55 (based on level)','12~46(레벨에 따라)','6 / 18.25 / 30.5 / 42.75 / 55(레벨에 따라)')
effect_add('Yone','치명타 피해량은 일반 치명타 피해량보다 5% 감소합니다.','Critical strike damage is reduced by 5%.')
mod('Yone','Q',(0,0),0,[25,50,75,100,125],'26.21');mod('Yone','Q',(0,0),1,105,'26.21')
for ri,vals,hp in [(0,[60,90,120,150,180],3),(1,[120,180,240,300,360],6)]:
 mod('Zac','Q',(0,ri),0,vals,'26.4',derived=ri==1);mod('Zac','Q',(0,ri),2,hp,'26.4',unit="% of Zac's bonus health",derived=ri==1)
for ri,vals in [(0,[120,190,260]),(1,[60,95,130]),(2,[300,475,650])]:mod('Zac','R',(0,ri),0,vals,'26.4',derived=ri==1)
for ri,vals,ap in [(2,[15,25,35,45,55],10),(3,[45,75,105,135,165],30)]:mod('Zoe','W',(0,ri),0,vals,'26.9');mod('Zoe','W',(0,ri),1,ap,'26.9')

# Integrate new coefficients into the affected full row, not a second ambiguous
# damage row. The archived components retain derived provenance.
for i,s,pos,values,unit,p in [
 ('Galio','R',(0,0),[100]*3,'% bonus magic resistance','26.10'),
 ('Mordekaiser','Q',(0,0),[120]*5,'% bonus AD','25.16'),
 ('Skarner','E',(0,0),[120]*5,'% bonus AD','25.22')]:
 r=next(r for r in WORK[i][s] if r['_pos']==pos)
 r['modifiers'].append({'values':values,'units':[unit]*len(values)});mark(i,s,r,p,True)
 WORK[i][s]=[r for r in WORK[i][s] if r.get('_attribute',{}).get('en') not in ['Additional bonus MR scaling','Bonus AD scaling']]
WORK['Mordekaiser']['Q'][0]['attribute']='Rank Damage excluding Level Growth'
LEX['labels']['Rank Damage excluding Level Growth']='레벨 성장 피해를 제외한 랭크 피해'
LEX['units']["% (+ 1.65% per mark) of target's current health"]='% (+ 표식당 1.65%) 대상 현재 체력'
LEX['units']["% of Zac's bonus health"]='% 추가 체력'
LEX['units']['% bonus magic resistance']='% 추가 마법 저항력'
# Third Q attack receives this separately from the three basic-hit subtotal.
add('Skarner','Q','세 번째 기본 공격 추가 피해','Third attack additional damage','대상 최대 체력의 11%','11% target maximum health','26.6')
# Written conditions not captured by the archive's leveling tables.
CONDITIONS=[
 ('Camille','E','추가 공격 속도 획득 조건','Bonus attack-speed trigger','벽에서 돌진할 때 획득하며 적 챔피언 적중 여부와 무관','Granted when dashing off a wall, regardless of hitting an enemy champion','26.4'),
 ('Graves','P','치명타 산탄 피해 증가 계수','Critical pellet damage scaling','추가 치명타 피해의 50%','50% of bonus critical damage','26.1'),
 ('Graves','P','일반 공격 대비 최대 치명타 배율','Maximum critical/noncritical damage ratio','2배','2x','26.1'),
 ('Illaoi','P','촉수 생성 재사용 대기시간','Tentacle spawn cooldown','레벨에 따라 18~7초','18–7 seconds by level','25.16'),
 ('Jax','P','19레벨 중첩당 추가 공격 속도','Additional attack speed per stack at level 19','1.5%','1.5%','26.1'),
 ('Kindred','E','둔화 지속시간','Slow duration','1.5초','1.5 seconds','26.20'),
 ('Kindred','E','소형 몬스터 대상 지정','Small-monster targeting','불가','Disabled','26.20'),
 ('MasterYi','Q','적중 시 중첩 적용','On-hit stack interactions','크라켄 학살자와 경계의 중첩을 쌓음','Stacks Kraken Slayer and Terminus','25.16'),
 ('MasterYi','Q','기본 공격 적중 시 재사용 감소','On-hit cooldown refund','1초 · 스킬 가속에 따라 감소하지 않음','1 second; no reduction from ability haste','26.19'),
 ('Mordekaiser','R','최대 체력 감소 판정','Maximum-health reduction behavior','감소 후 최대 체력을 초과한 대상에게 과도한 피해를 주던 오류 수정','Fixed excess damage against targets above their reduced maximum health','26.15'),
 ('Nautilus','E','첫 파동 몬스터 추가 피해','First-wave bonus monster damage','125 / 165 / 205 / 245 / 285 + 50% AP','125 / 165 / 205 / 245 / 285 + 50% AP','25.16'),
 ('Poppy','R','정신 집중 중단 시 재사용 대기시간','Interrupted-channel cooldown','30초','30 seconds','25.19'),
 ('Rengar','Q','식물 공격','Attacking plants','식물 공격 시에도 사용 효과 소모','Consumes the effect when attacking a plant','26.1'),
 ('Rengar','Q','치명타 판정','Critical-strike behavior','항상 치명타로 판정되지 않으며 실제 치명타 발생 시 추가 피해 적용','No longer always treated as a critical strike; extra damage requires the attack to crit','26.1'),
 ('Skarner','Q','재사용 대기시간 시작','Cooldown begins','마지막 공격용 사용 동작부터','From the last offensive Q action','25.22'),
 ('Skarner','R','시전 시간','Cast time','0.75초','0.75 seconds','25.22'),
 ('Taric','Q','대상 지정 불가 아군','Untargetable linked ally','아군이 대상 지정 불가 상태여도 스킬 발동','The spell still fires from untargetable allies','26.21'),
 ('Taric','E','대상 지정 불가 아군','Untargetable linked ally','아군이 대상 지정 불가 상태여도 발동하지만 사라진 아군에게서는 발동하지 않음','Fires from untargetable allies, but not from vanished allies','26.21'),
 ('Taric','R','대상 지정 불가 아군','Untargetable linked ally','아군이 대상 지정 불가 상태여도 스킬 발동','The spell still fires from untargetable allies','26.21'),
 ('Tryndamere','W','둔화 적용 조건·지속시간','Slow condition and duration','3.25초의 약화 효과 동안 트린다미어에게 등을 돌린 적을 둔화','Slows enemies while they face away during the 3.25-second debuff','26.1'),
 ('Tryndamere','W','공격력 감소 지속시간','Attack-damage reduction duration','4초','4 seconds','26.1'),
 ('Varus','W','기본 스킬 재사용 반환','Basic-ability cooldown refund','중첩당 11%, Q 정신 집중 시간에 따라 최대 70% 증가','11% per stack, increased by up to 70% with Q channel time','26.21'),
 ('Varus','R','전염 피해','Spread damage','주 대상에서 전염된 대상도 보유한 역병 중첩에 따라 피해를 받음','Targets reached by spread also take damage per Blight stack','25.16'),
 ('Yone','P','치명타 피해 감소','Critical-strike damage reduction','일반 치명타 피해보다 5% 감소','5% less than normal critical-strike damage','26.17'),
 ('Zac','R','유닛 충돌','Unit collision','궁극기 사용 중 유닛 통과','Ghosted during the ultimate','25.18'),
 ('Zoe','E','챔피언 적중 시 재사용 반환','Cooldown refund on champion hit','16 / 19.5 / 23 / 26.5 / 30%','16 / 19.5 / 23 / 26.5 / 30%','26.9')]
for x in CONDITIONS:add(*x)
for r in WORK['Varus']['R']:
 if r.get('_attribute',{}).get('en')=='Spread damage':r['_sources']=sources('Varus','*','25.16')
# A source says 33% for Varus after piercing targets; this unchanged condition
# is baseline, not a value verified by the26.21 update.
for r in WORK['Varus']['Q']:
 if r.get('_attribute',{}).get('en')=='Minimum damage after piercing targets':r['_provenance']='baseline';r['_sources']=[]
# Correct false confidence on whole formulas with retained archived components.
for i in IDS:
 for s in 'QWER':
  for r in WORK[i][s]:
   if r.get('_pos') is not None and r.get('_provenance')=='patch':r['_provenance']='derived'

# Latest cooldown and resource values, with all repeated changes folded into the
# final dated value. These use paired primary KO/EN source lines.
def pair(i,h,c):
 candidates=[v for v in histories(i,'ko') if v['patch']==h['patch'] and v['isHotfix']==h['isHotfix']]
 candidates=sorted(candidates,key=lambda v:(v['date']!=h['date'],v['date']))
 for v in candidates:
  if len(v['changes'])==len(h['changes']):return v['changes'][h['changes'].index(c)]
  es=[x for x in h['changes'] if x['slot']==c['slot']];ks=[x for x in v['changes'] if x['slot']==c['slot']]
  if len(es)==len(ks):return ks[es.index(c)]
 raise ValueError(('Unpaired official text',i,h['patch'],c['text']))
def after(txt):return re.split('⇒|→',txt,maxsplit=1)[1].strip()
for i in IDS:
 latest={}
 for h in sorted(histories(i),key=lambda h:(pk(h['patch']),h['date'])):
  for c in h['changes']:
   if c['slot'] not in 'PQWER':continue
   label=c['text'].split(':',1)[0].strip().lower()
   k={'cooldown':'cooldown','mana cost':'mana','mana cost per second':'mana_per_second'}.get(label)
   if k and re.search('⇒|→',c['text']):latest[c['slot'],k]=(h,c)
 for (s,key),(h,c) in latest.items():
  ko=pair(i,h,c)
  add(i,s,ko['text'].split(':',1)[0].strip(),c['text'].split(':',1)[0].strip(),after(ko['text']),after(c['text']),h['patch'])
  WORK[i][s][-1]['_sources']=[dict(patch=h['patch'],date=h['date'],url=h['url'])]

# Preserve unresolved original source conditions instead of presenting them as
# a verified current formula. This applies to unaffected details too.
for i in IDS:
 original=LEX.get('passiveNotes',{}).get(i)
 if original and not OUT[i]['skills']['P']['notes']['en']:
  note(i,'P',original['ko'],original['en'])
# Same numeric date notation in both locale strings; source wording stays in notes.
for l in ['ko','en']:
 OUT['Varus']['skills']['P']['effects'][l]=[x.replace('10월 22일','2026-10-22').replace('October 22','26.21 2026-10-22') for x in OUT['Varus']['skills']['P']['effects'][l]]

import hashlib
for i in IDS:
 for s in 'PQWER':
  skill=OUT[i]['skills'][s];rows=[]
  for r in WORK[i][s]:
   if '_attribute' in r:
    attr=r['_attribute'];value=r['_value']
   else:
    attr={'en':r['attribute'],'ko':LEX['labels'].get(r['attribute'],r['attribute'])}
    if r.get('_variant'):
     attr={l:(LEX['variants'].get(r['_variant'],r['_variant']) if l=='ko' else r['_variant'])+' · '+attr[l] for l in ['ko','en']}
    value={l:' + '.join(fmt(m,l) for m in r['modifiers']) for l in ['ko','en']}
   rows.append({'attribute':attr,'value':value,'provenance':r.get('_provenance','baseline'),'sources':r.get('_sources',[])})
  skill['rows']=rows
  if skill['notes']['en']:skill['status']='partial'
  elif skill['sources'] or any(r['provenance']!='baseline' for r in rows):skill['status']='reconciled'
  else:skill['status']='baseline'
  extra=[v for r in rows for v in r['sources']]
  skill['sources']=list({(v['patch'],v['date'],v['url']):v for v in skill['sources']+extra}.values())
 OUT[i]['audit']['notes'].append('All official champion-section changes after25.15 reviewed chronologically; unchanged source values retain baseline provenance, and mixed formulas are derived rather than wholly official.')
 OUT[i]['audit']['changeCount']=sum(len(h['changes']) for h in histories(i))
 OUT[i]['audit']['historySha256']=hashlib.sha256(json.dumps(histories(i),sort_keys=True,ensure_ascii=False,separators=(',',':')).encode()).hexdigest()
(Path(__file__).parent/'group-2.json').write_text(json.dumps(OUT,ensure_ascii=False,indent=2)+'\n')
print('Wrote',len(OUT),'champions',sum(len(s['rows']) for c in OUT.values() for s in c['skills'].values()),'rows')
