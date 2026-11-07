"""Reviewed champion-specific reconciliation, group 3. Original archives stay untouched."""
import json,re,copy,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]; DATA=ROOT/'dist/data'
IDS=['Akali', 'Anivia', 'Aurora', 'Brand', 'Cassiopeia', 'DrMundo', 'Ezreal', 'Gangplank', 'Gwen', 'Irelia', 'Jayce', 'Kalista', 'Kayle', 'Kled', 'Lillia', 'Lux', 'Mel', 'Morgana', 'Neeko', 'Olaf', 'Pyke', 'RekSai', 'Riven', 'Senna', 'Shyvana', 'Smolder', 'Syndra', 'Teemo', 'TwistedFate', 'Vayne', 'Viego', 'Xayah', 'Yorick', 'Zed', 'Zyra']
LEX=json.loads((DATA/'localization-ko.json').read_text()); OUT={}; RAW={}; HIST={}

def loc(ko,en):return {'ko':ko,'en':en}
def nm(n):return str(round(n,4)).rstrip('0').rstrip('.') if isinstance(n,float) else str(n)
def fmtmod(m,l):
 vs=m['values'];us=m['units']; u=lambda s: LEX['units'].get(s,s) if l=='ko' else s
 if len(set(map(str,vs)))==1 and len(set(us))==1:return nm(vs[0])+u(us[0])
 if len(set(us))==1:return ' / '.join(map(nm,vs))+u(us[0])
 return ' / '.join(nm(v)+u(x) for v,x in zip(vs,us))
def src(h):return {k:h[k] for k in ['patch','date','url']}
def sources(id,slot):return [src(h) for h in HIST[id] if any(c['slot']==slot for c in h['changes'])]
def add(id,k,ko,en,vko,ven=None,prov='patch',ss=None):
 r={'attribute':loc(ko,en),'value':loc(vko,ven or vko),'provenance':prov,'sources':ss or sources(id,k)}
 OUT[id]['skills'][k]['rows'].append(r);return r

def mod(id,k,v,r,m,values):
 a=next(x for x in RAW[id] if x['slot']==k)['variants'][v]['rows'][r]
 old=a['modifiers'][m]['values'];a['modifiers'][m]['values']=values if isinstance(values,list) else [values]*len(old);a['_updated']=True

def units(id,k,v,r,m,ko,en):
 a=next(x for x in RAW[id] if x['slot']==k)['variants'][v]['rows'][r]
 a['modifiers'][m]['units']=[en]*len(a['modifiers'][m]['values']);LEX['units'][en]=ko;a['_updated']=True

def remove(id,k,v,rs):
 a=next(x for x in RAW[id] if x['slot']==k)['variants'][v]
 for r in rs:a['rows'][r]['_remove']=True

def clear(id,k):
 for a in RAW[id]:
  if a['slot']==k:
   for v in a['variants']:v['rows']=[]

def note(id,k,ko,en):OUT[id]['skills'][k]['notes']=loc(ko,en);OUT[id]['skills'][k]['status']='partial'
def effects(id,ko,en):OUT[id]['skills']['P']['effects']=loc(ko,en)
def rep(id,ko_pairs,en_pairs):
 for l,ps in [('ko',ko_pairs),('en',en_pairs)]:
  es=OUT[id]['skills']['P']['effects'][l]
  for old,new in ps:
   assert any(old in e for e in es),(id,l,old)
   es=[e.replace(old,new) for e in es]
  OUT[id]['skills']['P']['effects'][l]=es

for id in IDS:
 c=json.loads((DATA/(id+'.json')).read_text());e=json.loads((DATA/'en'/(id+'.json')).read_text());RAW[id]=copy.deepcopy(c['formulas'])
 HIST[id]=sorted([h for h in e['history'] if (25,15)<tuple(map(int,h['patch'].split('.')))<=(26,21) and not h.get('release')],key=lambda h:(tuple(map(int,h['patch'].split('.'))),h['date']))
 skills={}
 for k in 'PQWER':
  a=next((a for a in c['formulas'] if a['slot']==k),{})
  es=[s for v in a.get('variants',[]) for s in v['effects']] if k=='P' else []
  ks=[s for v in LEX['passives'].get(id,{}).get('variants',[]) for s in v['effects']] if k=='P' else []
  skills[k]={'rows':[],'effects':loc(ks,es),'status':'reconciled' if sources(id,k) else 'baseline','notes':loc('',''),'sources':sources(id,k)}
 OUT[id]={'skills':skills,'audit':{'reviewedPatches':list(dict.fromkeys(h['patch'] for h in HIST[id])),'notes':[]}}

# Update every affected archived numeric row, including totals, before formatting.
mod('Anivia','E',0,0,0,[55,80,105,130,155]);mod('Anivia','E',0,1,0,[110,160,210,260,310])
mod('Aurora','E',0,0,0,[80,120,160,200,240]);mod('Aurora','R',0,1,0,[2.25,2.75,3.25])
mod('Brand','W',0,0,1,70);mod('Brand','W',0,1,1,87.5);mod('Brand','R',0,0,1,30);mod('Brand','R',0,1,1,90)
mod('Cassiopeia','Q',0,0,0,[65,100,135,170,205]);mod('Cassiopeia','Q',0,0,1,75);remove('Cassiopeia','Q',0,[1])
mod('Cassiopeia','E',0,0,0,[20,45,70,95,120]);mod('Cassiopeia','E',0,0,1,45);remove('Cassiopeia','E',0,[1])
mod('Cassiopeia','R',0,0,0,[125,225,325]);mod('Cassiopeia','R',0,0,1,75)
mod('DrMundo','Q',0,2,0,[250,325,400,475,550]);mod('DrMundo','E',0,0,0,[2,2.3,2.6,2.9,3.2]);mod('DrMundo','E',0,1,1,5);mod('DrMundo','E',0,2,1,7)
mod('Ezreal','Q',0,0,2,40);mod('Ezreal','W',0,0,2,90);mod('Ezreal','E',0,0,1,60);mod('Ezreal','R',0,0,2,110)
mod('Ezreal','R',0,1,0,[150,225,300]);mod('Ezreal','R',0,1,1,100);mod('Ezreal','R',0,1,2,110)
mod('Gangplank','E',0,2,0,[75,95,115,135,155])
for r in [0,1]:mod('Gwen','Q',0,r,0,[10,14,18,22,26]);mod('Gwen','Q',0,r,1,5)
for r in [4,5]:mod('Gwen','Q',0,r,0,[70,99,128,157,186]);mod('Gwen','Q',0,r,1,40)
for r in [6,7]:mod('Gwen','Q',0,r,0,[110,155,200,245,290]);mod('Gwen','Q',0,r,1,60)
for r,n in [(1,0.6),(3,0.6),(5,1.2),(7,3.6)]:
 units('Gwen','Q',0,r,2,f'% (+ AP 100당 {n}%) 대상 최대 체력',f"% (+ {n}% per 100 AP) of the target's maximum health")
mod('Gwen','E',0,0,0,15);mod('Gwen','E',0,0,1,20);mod('Gwen','E',0,1,0,[30,42.5,55,67.5,80])
for r,n in [(0,1),(1,1),(2,3),(3,5),(4,9)]:
 mod('Gwen','R',0,r,0,[30*n,50*n,70*n]);mod('Gwen','R',0,r,1,10*n)
 if r:units('Gwen','R',0,r,2,f'% (+ AP 100당 {round(.6*n,2)}%) 대상 최대 체력',f"% (+ {round(.6*n,2)}% per 100 AP) of the target's maximum health")
mod('Irelia','Q',0,0,1,80);mod('Irelia','W',0,0,2,50);mod('Irelia','W',0,1,2,150);mod('Irelia','E',0,0,1,100);mod('Irelia','R',0,0,1,100)
mod('Jayce','Q',0,0,0,[60,110,160,210,260,310]);mod('Jayce','Q',1,0,0,[80,121,162,203,244,285]);mod('Jayce','Q',1,0,1,130)
mod('Jayce','Q',1,1,0,[112,169.4,226.8,284.2,341.6,399]);mod('Jayce','Q',1,1,1,182)
mod('Kalista','E',0,0,2,65);mod('Kalista','E',0,1,1,[20,27.5,35,42.5,50]);mod('Kalista','E',0,1,2,50)
mod('Kayle','Q',0,0,0,[60,90,120,150,180]);mod('Kayle','Q',0,1,0,[25,30,35,40,45])
mod('Lillia','R',0,0,0,[150,200,250]);mod('Lillia','Q',0,2,1,35);mod('Lillia','Q',0,3,1,70)
mod('Lux','Q',0,0,1,75)
# Mel's reworked Q uses initial-hit plus subsequent-hit damage; old per-hit totals are invalid.
clear('Mel','Q');mod('Mel','E',0,0,1,70);mod('Mel','E',0,1,0,1.5)
mod('Mel','E',0,2,0,[2,3.5,5,6.5,8]);mod('Mel','E',0,3,0,[16,28,40,52,64])
mod('Mel','E',0,4,1,35);mod('Mel','E',0,5,0,[1,1.75,2.5,3.25,4]);mod('Mel','E',0,6,0,[8,14,20,26,32])
mod('Mel','R',0,2,0,[125,200,275]);units('Mel','R',0,2,2,' (+ 4% AP) 대상 압도 중첩당',' (+ 4% AP) per Overwhelm stack on the target')
for r,mult in [(0,.5),(1,1),(2,5),(3,10)]:
 mod('Morgana','W',0,r,0,[18*mult,31*mult,44*mult,57*mult,70*mult]);mod('Morgana','W',0,r,1,20*mult)
mod('Neeko','E',0,0,0,[80,115,150,185,220]);mod('Neeko','E',0,2,0,[2,2.25,2.5,2.75,3])
mod('Olaf','Q',0,0,0,[70,120,170,220,270]);remove('Olaf','Q',0,[1]);mod('Olaf','Q',0,2,0,[20,45,70,95,120]);mod('Olaf','Q',0,3,0,[90,165,240,315,390])
mod('RekSai','E',0,0,0,[70,95,120,145,170]);mod('RekSai','E',0,0,1,60);mod('RekSai','E',0,1,0,[84,114,144,174,204]);mod('RekSai','E',0,1,1,72)
mod('Riven','Q',0,0,0,[40,75,105,135,165]);mod('Riven','Q',0,0,1,[60,65,70,75,80]);mod('Riven','Q',0,1,0,[120,225,315,405,495]);mod('Riven','Q',0,1,1,[180,195,210,225,240]);mod('Riven','R',1,0,1,55);mod('Riven','R',1,1,1,165)
mod('Senna','Q',0,0,0,[40,60,80,100,120]);mod('Senna','Q',0,0,2,35);mod('Senna','Q',0,1,0,[30,55,80,105,130]);mod('Senna','Q',0,1,1,60);mod('Senna','W',0,0,0,[70,110,150,190,230]);mod('Senna','W',0,0,1,90)
for k in 'PQWER':clear('Shyvana',k);OUT['Shyvana']['skills'][k]['effects']=loc([],[]);note('Shyvana',k,'26.6 개편 전 자료를 제외했습니다. 이후 공식 패치로 확인한 항목만 표시하며, 개편 당시 전체 수치는 추가 확인이 필요합니다.','Pre-26.6 rework data is excluded. Only values confirmed in subsequent official notes are shown; the full rework baseline still needs verification.')
# Smolder: avoid archived Infinity Edge assumptions, express current general scaling separately.
clear('Smolder','Q');mod('Smolder','W',0,1,1,50);mod('Smolder','W',0,2,1,110)
mod('Smolder','R',0,0,0,[100,175,250]);mod('Smolder','R',0,0,1,75);mod('Smolder','R',0,1,0,[150,250,350]);mod('Smolder','R',0,1,1,100);mod('Smolder','R',0,2,0,[225,375,525]);mod('Smolder','R',0,2,1,150)
mod('Syndra','Q',0,0,0,[90,125,160,195,230]);mod('Syndra','Q',0,0,1,70);mod('Syndra','W',0,0,0,[70,100,130,160,190]);remove('Syndra','W',0,[1,2])
for r,n in [(1,1),(2,3),(3,7)]:mod('Syndra','R',0,r,0,[80*n,120*n,160*n])
# Teemo: per-tick bonus AD conflicts between source patches are exposed, not silently calculated.
for r in [2,3,4,5]:remove('Teemo','E',0,[r])
# Merge the new AD components into the actual on-hit/tick formula rows.
for ri,ratio in [(0,5),(1,10)]:
 r=next(a for a in RAW['Teemo'] if a['slot']=='E')['variants'][0]['rows'][ri]
 r['modifiers'].append({'values':[ratio]*5,'units':['% bonus AD']*5});r['_updated']=True
mod('Vayne','W',0,0,0,[4,5.5,7,8.5,10]);mod('Vayne','W',0,1,0,[40,55,70,85,100])
mod('Viego','Q',0,2,0,[25,40,55,70,85]);remove('Viego','Q',0,[3,4,5])
mod('Xayah','E',0,0,0,[50,65,80,95,110]);mod('Xayah','E',0,0,1,40);mod('Xayah','E',0,1,0,[25,32.5,40,47.5,55]);mod('Xayah','E',0,1,1,20)
mod('Zed','E',0,0,0,[70,92.5,115,137.5,160]);mod('Zed','E',0,0,1,70);mod('Zyra','R',0,0,0,[200,300,400])

# Passive prose, preserving activation conditions while replacing superseded numbers.
rep('Aurora',[('2.5%(주문력 100당 +2%)','1%(주문력 100당 +2.7%)')],[('2.5% (+ 2% per 100 AP)','1% (+ 2.7% per 100 AP)')])
rep('Brand',[('8%~12%(레벨에 따라)','6%~12%(1~18레벨, 18레벨 이후에도 증가)')],[('8% : 12% (based on level)','6% : 12% (levels 1–18, continuing above level 18)')])
OUT['Brand']['skills']['P']['effects']['ko'][1]='불길은 4초 동안 지속되는 중첩형 마법 피해입니다. 몬스터 대상 피해 배율은 270%이며, 일반 몬스터 피해 상한은 공식 26.4 패치에서 50으로 변경되었습니다. 보관 자료의 총 피해량과 주기당 피해량이 서로 일치하지 않아 해당 수치는 확정 표시하지 않습니다.'
OUT['Brand']['skills']['P']['effects']['en'][1]='Ablaze is stacking magic damage over 4 seconds. Its monster damage multiplier is 270%; the non-epic monster cap was changed to 50 in patch 26.4. Archived total and per-tick damage disagree, so those values are not presented as confirmed.'
note('Brand','P','보관본의 지속 피해 총량과 틱 수치가 불일치합니다. 몬스터 상한의 주기별 해석도 추가 확인이 필요합니다.','The archive has inconsistent total/tick damage; the time basis of the non-epic monster cap needs additional verification.')
effects('Cassiopeia',['이동 속도 증가 효과의 효율이 레벨에 따라 5%~36% 증가합니다. 26.1에 고정 이동 속도 증가 및 신발 구매 제한 구조가 개편되었고, 26.18에서 현재 비율로 조정되었습니다.'],['Movement speed buffs have 5%–36% increased effectiveness based on level. The flat movement-speed/no-boots passive was reworked in 26.1 and adjusted to this range in 26.18.'])
rep('Gangplank',[(' + 치명타 확률 1%당 2',''),(' + 치명타 확률 1%당 0.2','')],[(' (+ 2 per 1% critical strike chance)',''),(' (+ 0.2 per 1% critical strike chance)','')])
rep('Gwen',[('0.55%','0.6%'),('피해량의 50%','피해량의 67%'),('10~25','12~40'),('6.5% AP','7% AP'),('최대 5 + 10% AP','최대 3 + 5% AP')],[('0.55%','0.6%'),('for 50%','for 67%'),('10 : 25','12 : 40'),('6.5% AP','7% AP'),('maximum of 5 (+ 10% AP)','maximum of 3 (+ 5% AP)')])
note('Gwen','P','몬스터 피해 상한 3 + 5% AP는 26.2 공식 패치의 표기를 그대로 반영했습니다. 상한의 세부 적용 방식은 추가 확인이 필요합니다.','The monster cap 3 + 5% AP follows the 26.2 official wording. Its precise application still needs verification.')
rep('Jayce',[('이동 속도가 40','이동 속도가 30')],[('40 bonus movement speed','30 bonus movement speed')])
rep('Kayle',[('6%(+ 100 AP당 1%)','6%'),('30%(+ 100 AP당 5%)','30%')],[('6% (+ 1% per 100 AP)','6%'),('30% (+ 5% per 100 AP)','30%')])
OUT['Lillia']['skills']['P']['effects']['ko'][0]='스킬이 적에게 꿈가루를 묻혀 3초 동안 대상 최대 체력의 5% + (AP 100당 1.25%)에 해당하는 총 마법 피해를 입힙니다. 몬스터 대상 피해 상한은 26.8 공식 패치 기준 레벨에 따라 70~180입니다.'
OUT['Lillia']['skills']['P']['effects']['en'][0]="Abilities apply Dream Dust, dealing 5% (+1.25% per 100 AP) of the target's maximum health as total magic damage over 3 seconds. The monster damage cap is 70–180 based on level, as listed in patch 26.8."
rep('Lux',[('AP의 30%','AP의 35%')],[('30% AP','35% AP')])
rep('Mel',[('60%, 즉 30 / 36 / 42 / 48','50%, 즉 25 / 30 / 35 / 40'),('AP의 6%로 감소','AP의 5%로 감소'),('투사체마다 8~25','투사체마다 8~30'),('AP의 1%','AP의 4%')],[('to 60%','to 50%'),('30 / 36 / 42 / 48','25 / 30 / 35 / 40'),('(+ 6% AP)','(+ 5% AP)'),('8 : 25 (based on level) (+ 1% AP)','8 : 30 (based on level) (+ 4% AP)')])
rep('RekSai',[('80% 감소하여 적중당 5','84% 감소하여 적중당 4'),('10%~20%','9%~20%')],[('by 80%','by 84%'),('to 5 per hit','to 4 per hit'),('10% : 20%','9% : 20%')])
rep('Riven',[('30%~50%','30%~45%'),('15%~25%','15%~22.5%')],[('30% : 50%','30% : 45%'),('15% : 25%','15% : 22.5%')])
OUT['Riven']['skills']['P']['effects']['ko'].append('몬스터에게는 50의 고정 추가 피해를 더합니다.')
OUT['Riven']['skills']['P']['effects']['en'].append('Deals an additional flat 50 damage to monsters.')
rep('Senna',[('10% 확률로 생성','5% 확률로 생성'),('28% 확률로 생성','32% 확률로 생성'),(' 아군 챔피언의 서포터 퀘스트 아이템으로 처형된 소형 미니언은 8.4% 확률로 생성합니다.','')],[('have a 10% chance','have a 5% chance'),('have a 28% chance','have a 32% chance'),('\nLesser minions executed by an allied champion\'s Support Quest item have a 8.4% chance to spawn a Mist Wraith.','')])
OUT['Senna']['skills']['P']['effects']['ko'].append('치명타 피해는 일반 치명타 피해의 80%가 적용됩니다.')
OUT['Senna']['skills']['P']['effects']['en'].append('Critical strikes deal 80% of normal critical-strike damage.')
note('Senna','P','이전 보관본의 서포터 아이템 처형 시 망령 생성 확률 8.4%는 현재 조건을 확인할 수 없어 제외했습니다.','The archived 8.4% support-item-execute drop chance is omitted because its current conditions are unverified.')
effects('Shyvana',['개편된 패시브는 중첩마다 방어력과 마법 저항력을 각각 0.3 얻습니다. 개편 전 드래곤 처치당 증가 및 드래곤 추가 피해 설명은 제외했습니다.'],['The reworked passive grants 0.3 armor and magic resistance each per stack. Pre-rework dragon-kill bonuses and dragon damage text are excluded.'])
effects('Smolder',['스킬로 적 챔피언을 맞히거나 초강력 화염 숨결(Q)로 미니언 또는 몬스터를 처치할 때마다 용 훈련 중첩을 얻습니다. 기본 스킬은 중첩 수에 따라 추가 마법 피해를 입힙니다.','Q 추가 마법 피해: 치명타 확률에 따라 용 훈련 중첩의 25%~60%. 무한의 대검으로 0%~10.5%가 추가됩니다.','W 폭발 추가 마법 피해: 용 훈련 중첩의 55%.','E 공격당 추가 마법 피해: 치명타 확률에 따라 용 훈련 중첩의 8%~14%. 무한의 대검으로 0%~1.8%가 추가됩니다.'],['Smolder gains Dragon Practice stacks when his abilities hit enemy champions or Q kills minions or monsters. His basic abilities deal additional magic damage based on stacks.','Q bonus magic damage: 25%–60% of stacks based on critical strike chance, plus 0%–10.5% with Infinity Edge.','W explosion bonus magic damage: 55% of stacks.','E bonus magic damage per attack: 8%–14% of stacks based on critical strike chance, plus 0%–1.8% with Infinity Edge.'])
rep('Syndra',[('20~215','20~199')],[('20 : 215','20 : 199')])
rep('Viego',[('(추가 공격 속도 100%당 5%)]','(추가 공격 속도 100%당 5%) + (추가 체력 500당 2%)]')],[('(+ 5% per 100% bonus attack speed) of','(+ 5% per 100% bonus attack speed) (+ 2% per 500 bonus health) of')])
rep('Xayah',[('30% / 40% / 50%','35% / 45% / 55%'),('(175% + 40%)의 피해','현재 치명타 피해 보정이 적용된 피해')],[('30% / 40% / 50%','35% / 45% / 55%'),('(175% + 40%) damage','damage using the current critical-strike modifier')])
rep('Zed',[('6% / 8% / 10%','5% / 7.5% / 10%'),('200%의 피해','75%의 피해'),('피해 상한은 300','에픽 몬스터 피해 상한은 175')],[('6% / 8% / 10%','5% / 7.5% / 10%'),('200% damage, capped at 300','75% damage, capped at 175 against epic monsters')])

# Materialize all preserved/updated rows.
for id in IDS:
 for a in RAW[id]:
  k=a['slot'];n=len(a['variants'])
  for v in a['variants']:
   for r in v['rows']:
    if r.get('_remove'):continue
    pre={'ko':LEX['variants'].get(v['name'],v['name'])+' · ' if n>1 else '', 'en':v['name']+' · ' if n>1 else ''}
    at={l:pre[l]+(LEX['labels'].get(r['attribute'],r['attribute']) if l=='ko' else r['attribute']) for l in ['ko','en']}
    val={l:' + '.join(fmtmod(m,l) for m in r['modifiers']) for l in ['ko','en']}
    OUT[id]['skills'][k]['rows'].append({'attribute':at,'value':val,'provenance':'derived' if r.get('_updated') else 'baseline','sources':sources(id,k) if r.get('_updated') else []})

# Additional properties absent from the archive's numeric rows.
ADD=[
('Akali','W','다시 은신하기까지','Restealth delay','마지막 공격/스킬 후 1 / 0.9 / 0.825 / 0.725 / 0.625초 (1 / 7 / 10 / 13 / 16레벨)','1 / 0.9 / 0.825 / 0.725 / 0.625s after last attack/ability at levels 1 / 7 / 10 / 13 / 16'),
('Brand','Q','불길 대상 기절','Ablaze stun','1.75초','1.75s'),
('Cassiopeia','E','기본 피해량','Base damage','50~120 (레벨 비례) + 20% AP','50–120 (based on level) + 20% AP'),
('Cassiopeia','E','독 대상 총 피해량','Total damage to poisoned target','50~120 (레벨 비례) + 20 / 45 / 70 / 95 / 120 + 65% AP','50–120 (based on level) + 20 / 45 / 70 / 95 / 120 + 65% AP'),
('DrMundo','E','최대 피해 조건','Maximum damage threshold','잃은 체력 70%','70% missing health'),
('DrMundo','E','몬스터 피해 배율','Monster damage modifier','140%','140%'),
('Gangplank','E','화약통 치명타','Keg critical strikes','별도 5% 추가 피해 삭제','Separate 5% bonus critical-strike damage removed'),
('Gangplank','E','화약통 시간','Keg timing','19레벨에서 0.25초로 감소하지 않음','Does not reduce to 0.25s at level 19'),
('Gwen','Q','미니언 피해 배율','Minion damage modifier','80%','80%'),
('Gwen','W','방어력 및 마법 저항력','Armor and magic resistance','22 / 24 / 26 / 28 / 30 + 7% AP','22 / 24 / 26 / 28 / 30 + 7% AP'),
('Gwen','E','재사용 대기시간 반환','Cooldown refund','25 / 35 / 45 / 55 / 65%','25 / 35 / 45 / 55 / 65%'),
('Gwen','R','첫 둔화','Initial slow','40 / 50 / 60%','40 / 50 / 60%'),
('Gwen','R','후속 둔화','Subsequent slow','15 / 20 / 25%','15 / 20 / 25%'),
('Irelia','W','피해 감소 주문력 계수','Damage-reduction AP scaling','AP 100당 8% (마법 피해에는 절반)','8% per 100 AP (halved for magic damage)'),
('Jayce','Q','두 형태의 몬스터 추가 피해','Bonus monster damage in both forms','10','10'),
('Jayce','R','캐논: 방어력/마법 저항력 감소','Cannon: armor/MR reduction','20 / 25 / 30 / 35%','20 / 25 / 30 / 35%'),
('Jayce','R','해머: 방어력 및 마법 저항력','Hammer: armor and magic resistance','5 / 12 / 19 / 26 + 추가 AD의 7.5%','5 / 12 / 19 / 26 + 7.5% bonus AD'),
('Lillia','R','수면 지속시간','Sleep duration','2.5 / 2.75 / 3초','2.5 / 2.75 / 3s'),
('Mel','Q','첫 폭발 피해','Initial explosion damage','60 / 85 / 110 / 135 / 160 + 55% AP','60 / 85 / 110 / 135 / 160 + 55% AP'),
('Mel','Q','후속 폭발 피해','Subsequent explosion damage','5 / 7 / 9 / 11 / 13 + 5% AP','5 / 7 / 9 / 11 / 13 + 5% AP'),
('Mel','Q','투사체 수','Number of bolts','6 / 7 / 8 / 9 / 10','6 / 7 / 8 / 9 / 10'),
('Mel','Q','미니언 피해 배율','Minion damage modifier','100%','100%'),
('Mel','Q','시전 시간','Cast time','0.35초','0.35s'),
('Mel','Q','투사체 속도','Missile speed','3800','3800'),
('Mel','Q','폭발 반경','Explosion radius','200','200'),
('Mel','Q','산포 범위','Area spread','25','25'),
('Mel','Q','정신 집중 시간','Channel time','0.5초','0.5s'),
('Mel','Q','피해 유형','Damage classification','광역 지속 피해','Area damage over time'),
('Mel','W','보호막','Shield','80 / 110 / 140 / 170 / 200 + 70% AP','80 / 110 / 140 / 170 / 200 + 70% AP'),
('Mel','W','추가 이동 속도','Bonus movement speed','40%, 0.75초 동안 감소','40%, decaying over 0.75s'),
('Mel','W','피해 면역','Damage immunity','제공하지 않음','No longer provided'),
('Mel','W','반사 물리 피해','Reflected physical damage','마법 피해로 변환 전 30% 감소','Reduced by 30% before conversion to magic damage'),
('Mel','W','개별 대상 지정 광역 투사체','Area attacks with per-target projectiles','멜을 향하지 않은 투사체는 반사 대신 파괴','Projectiles not targeting Mel are destroyed instead of reflected'),
('Mel','E','속박 투사체 반경','Root missile radius','70','70'),
('Mel','E','장판을 벗어난 뒤 약화 지속시간','Lingering debuff duration','0.5초','0.5s'),
('Mel','E','이동 종료 후 잔류','End-of-travel linger','0.25초','0.25s'),
('Mel','E','지속 피해 반경','Damage-over-time radius','230','230'),
('Mel','E','투사체 속도','Missile speed','1100','1100'),
('Mel','E','사거리','Cast range','1000','1000'),
('Neeko','W','재사용 대기시간 시작','Cooldown starts','분신이 사라질 때','On clone expiration'),
('Neeko','W','분신 감정 표현','Clone emotes','분신만 농담하는 기능 삭제; 농담·춤·귀환 명령은 가능','Clone-only joke command removed; joke/dance/recall commands remain available'),
('Olaf','Q','둔화','Slow','공식 문서: 30 / 40 / 45 / 50%, 거리 비례 1~3초 (전체 랭크 중 한 값 미표기)','Official notes: 30 / 40 / 45 / 50%, lasting 1–3s by distance (one of five rank values omitted)'),
('Olaf','E','자신이 받는 피해','Self damage','가한 피해의 40%','40% of damage dealt'),
('Olaf','W','재시전','Recast behavior','기존 효과 중 재시전해도 기본 공격 초기화 및 공격 속도 갱신','Recasting reapplies the attack reset and updates attack speed'),
('Riven','R','추가 공격력','Bonus attack damage','공격력의 20%','20% AD'),
('Senna','Q','둔화 주문력 계수','Slow AP scaling','AP 100당 7%','7% per 100 AP'),
('Senna','Q','재사용 대기시간 감소 조건','Cooldown refund trigger','적중 시에서 공격 시로 변경','On attack, rather than on hit'),
('Smolder','Q','기본 물리 피해','Base physical damage','60 / 70 / 80 / 90 / 100 + 추가 AD의 130%','60 / 70 / 80 / 90 / 100 + 130% bonus AD'),
('Smolder','Q','치명타 확률 비례 증가','Critical-strike scaling','최대 75% (+무한의 대검 22.5%)','Up to 75% (+22.5% with Infinity Edge)'),
('Syndra','W','강화 추가 고정 피해','Empowered bonus true damage','해당 마법 피해의 12% (+ AP 100당 2%)','12% (+2% per 100 AP) of the magic damage'),
('Teemo','E','적중 추가 공격력 계수','On-hit bonus AD scaling','추가 AD의 5%','5% bonus AD'),
('Teemo','E','독 피해 추가 공격력 계수','Poison bonus AD scaling','틱당 추가 AD의 10% (26.11 표기)','10% bonus AD per tick (26.11 wording)'),
('Teemo','E','몬스터 피해 배율','Monster damage modifier','160%','160%'),
('Teemo','R','덫 불투명도','Trap opacity','50%','50%'),
('TwistedFate','R','시야 확보','Reveal','대상 지정 불가 유닛도 드러냄','Also reveals untargetable units'),
('Vayne','W','몬스터 고정 피해','Fixed damage to monsters','140 / 155 / 170 / 185 / 200 (몬스터 체력 무관)','140 / 155 / 170 / 185 / 200, regardless of monster health'),
('Viego','Q','현재 체력 피해의 추가 치명타 피해 반영','Current-health on-hit bonus crit scaling','추가 치명타 피해의 70%','70% of bonus critical-strike damage'),
('Viego','Q','두 번째 타격 치명타 계수','Second-strike bonus crit scaling','추가 치명타 피해의 100%','100% of bonus critical-strike damage'),
('Viego','Q','사용 효과 치명타 계수','Active bonus crit scaling','추가 치명타 피해의 60%','60% of bonus critical-strike damage'),
('Viego','Q','표식 대상 회복 배율','Mark healing modifiers','미니언 100% / 몬스터 125% / 챔피언 150%','Minions 100% / monsters 125% / champions 150%'),
('Viego','Q','몬스터 고정 추가 피해','Flat bonus monster damage','0','0'),
('Viego','R','총 공격력 비례 기본 피해','Base AD damage','총 공격력의 120% · 치명타 확률과 추가 치명타 피해에 따라 아래 계수로 증가','120% total AD; increased by critical chance and bonus critical damage using the modifier below'),
('Viego','R','치명타 계수','Critical-strike scaling','추가 치명타 피해의 70%','70% of bonus critical-strike damage'),
('Xayah','E','치명타 계수','Critical-strike scaling','추가 치명타 피해의 최대 50%','Up to 50% of bonus critical-strike damage'),
('Zyra','W','충전 시간','Seed recharge','16 / 14.5 / 13 / 11.5 / 10초','16 / 14.5 / 13 / 11.5 / 10s')]
for x in ADD:
 add(*x)
 if x[:2]==('Viego','R') and x[3]=='Base AD damage':OUT[x[0]]['skills'][x[1]]['rows'][-1]['provenance']='derived'
# Reworked Shyvana values from official post-rework notes, no legacy values.
SHY={
'P':[('중첩당 방어력 및 마법 저항력','Armor and MR per stack','0.3','0.3')],
'Q':[('기본 지속 피해','Passive damage','대상 최대 체력의 1% (+ 추가 AD 100당 1.1%)','1% (+1.1% per 100 bonus AD) target maximum health'),('공격 적중 시 재사용 감소','On-hit cooldown reduction','0.5초','0.5s'),('광역 물리 피해','Area physical damage','10 / 15 / 20 / 25 / 30 + 총 AD의 110% + 30% AP','10 / 15 / 20 / 25 / 30 + 110% total AD + 30% AP'),('재사용 시작','Cooldown timing','연계를 끝내지 않아도 마지막 입력부터 진행','Starts from the last activated input even if the sequence is unfinished')],
'W':[('보호막','Shield','60 / 80 / 100 / 120 / 140 + 추가 체력의 12%','60 / 80 / 100 / 120 / 140 + 12% bonus health'),('피해량','Damage','80 / 100 / 120 / 140 / 160 + 65% AP','80 / 100 / 120 / 140 / 160 + 65% AP'),('용 형상 회복','Dragon-form heal','60~100 + 잃은 체력의 4~8% (레벨 비례)','60–100 +4–8% missing health (based on level)'),('이동 속도','Movement speed','보호막과 별도로 유지','Independent from the shield')],
'E':[('마법 피해','Magic damage','50 / 65 / 80 / 95 / 110 + 60 / 65 / 70 / 75 / 80% AP + 대상 최대 체력의 5%','50 / 65 / 80 / 95 / 110 + 60 / 65 / 70 / 75 / 80% AP +5% target maximum health'),('같은 대상 후속 폭발','Subsequent explosion on same target','40%','40%'),('둔화','Slow','30%','30%')],
'R':[('공포','Fear duration','0.75초','0.75s')]}
for k,rs in SHY.items():
 for r in rs:add('Shyvana',k,*r)
# New cooldowns/costs have full patch provenance and are also used by primary metadata.
for id in IDS:
 final={}
 for h in HIST[id]:
  for c in h['changes']:
   if c['slot'] not in 'QWER':continue
   name=c['text'].split(':')[0].strip().lower(); key='cooldown' if name in ['cooldown','q cooldown','w cooldown','e cooldown','r cooldown'] else 'mana' if name in ['mana cost','q mana cost','w mana cost','e mana cost','r mana cost'] else None
   if key and '⇒' in c['text']:final[(c['slot'],key)]=(h,c['text'].split('⇒',1)[1].strip())
 for (k,key),(h,val) in final.items():
  add(id,k,'재사용 대기시간' if key=='cooldown' else '마나 소모량','Cooldown' if key=='cooldown' else 'Mana cost',val.replace(' seconds','초').replace(' mana','').replace('seconds','초'),val,ss=[src(h)])
# Explicit unresolved source differences: never smooth them into made-up rank arrays.
note('Mel','Q','26.3·26.5 공식 문서의 총 피해 합계와 투사체 수가 완전히 일치하지 않아 합계는 표시하지 않습니다. 첫 타격·후속 타격의 최신 수치를 분리했습니다.','Totals and bolt counts in the 26.3/26.5 notes do not fully agree, so no total is asserted. Current initial and subsequent-hit damage are shown separately.')
note('Olaf','Q','26.6 공식 문서의 둔화 수치는 5개 스킬 랭크에 대해 4개 값만 표기합니다. 누락된 값을 추정하지 않았습니다.','The 26.6 notes list four slow values for five ranks. The missing value is not guessed.')
note('Teemo','E','26.9의 총 지속 피해 계수와 26.11의 틱당 계수 표기가 서로 맞지 않습니다. 최신 문서의 틱당 10% 추가 AD를 표시하며 총합은 확정하지 않습니다.','26.9 total-DoT and 26.11 per-tick coefficient wording disagree. The latest stated 10% bonus AD per tick is shown; its total is not asserted.')
OUT['Cassiopeia']['audit']['notes'].append('26.6 changes were announced but did not ship; 26.7 is the applied mana/E baseline. E rank4=95, not the withdrawn90.')
OUT['Zed']['audit']['notes'].append('26.3 February5 epic-monster cap175 is an inline General/A record belonging to P.')
for id in IDS:
 OUT[id]['audit']['historySha256']=hashlib.sha256(json.dumps([h for h in json.loads((DATA/'en'/(id+'.json')).read_text())['history'] if (25,15)<tuple(map(int,h['patch'].split('.')))<=(26,21) and not h.get('release')],ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest()
 OUT[id]['audit']['changeCount']=sum(len(h['changes']) for h in HIST[id])
 OUT[id]['audit']['notes'].append('Unchanged rows retain baseline provenance; official changes are merged, not a certification of all archive facts.')
(Path(__file__).parent/'group-3.json').write_text(json.dumps(OUT,ensure_ascii=False,indent=2)+'\n')
print('Wrote',len(OUT),'champions',sum(len(s['rows']) for c in OUT.values() for s in c['skills'].values()),'rows')
