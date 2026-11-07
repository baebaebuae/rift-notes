"""Reviewed reconciliation rules for group 4. Original rows remain labelled baseline.
Run from repository: python scripts/reconciled/build_group_4.py
"""
import copy,json,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]; D=ROOT/'dist/data'
IDS=['Akshan','Annie','Azir','Braum','Chogath','Draven','Fiddlesticks','Garen','Hecarim','Ivern','Jhin','Karma','Kayn','KogMaw','Lissandra','Malphite','Milio','Naafiri','Nidalee','Orianna','Qiyana','Rell','Rumble','Seraphine','Singed','Sona','TahmKench','Thresh','Twitch','Veigar','Viktor','Xerath','Yunara','Zeri']
G=json.loads((D/'localization-ko.json').read_text()); data={}; out={}; records={}; used={}; raw={}
def pk(v):return tuple(map(int,v.split('.')))
for id in IDS:
 en=json.loads((D/'en'/f'{id}.json').read_text());ko=json.loads((D/f'{id}.json').read_text());data[id]=(ko,en);used[id]=set();records[id]=[]
 for h in sorted(en['history'],key=lambda h:(pk(h['patch']),h['date'])):
  if not (25,15)<pk(h['patch'])<=(26,21) or h.get('release'):continue
  hs=[k for k in ko['history'] if k['patch']==h['patch'] and k.get('isHotfix')==h.get('isHotfix')]
  kh=next((k for k in hs if k['date']==h['date']),hs[0] if len(hs)==1 else None)
  for ci,ch in enumerate(h['changes']):
   kch=kh['changes'][ci] if kh and len(kh['changes'])==len(h['changes']) else None
   sl=ch['slot'];m=re.match(r'^([QWER])\b',ch['text']);sl=m[1] if sl=='A' and m else sl
   if sl=='A' and re.match(r'(?:Base |Attack Damage|Health|Armor|Magic Resist|Mana)',ch['text'],re.I):sl='S'
   records[id].append(dict(ch,slot=sl,ko=kch['text'] if kch else '',patch=h['patch'],date=h['date'],url=h['url'],koUrl=kh['url'] if kh else h['url'].replace('/en-us/','/ko-kr/'),idx=len(records[id])))
 raw[id]={s:[] for s in 'PQWER'};skills={}
 for a in en['formulas']:
  sl=a['slot']
  if sl not in raw[id]:continue
  for vi,v in enumerate(a['variants']):
   for ri,r in enumerate(v['rows']):raw[id][sl].append(dict(copy.deepcopy(r),_vi=vi,_ri=ri,_variant=v['name'] if len(a['variants'])>1 else '',_provenance='baseline',_sources=[]))
 for sl in 'PQWER':
  a=next((a for a in en['formulas'] if a['slot']==sl),None)
  effects={'ko':[],'en':[]}
  if sl=='P' and a:
   effects['en']=[x for v in a['variants'] for x in v['effects']]
   effects['ko']=[x for v in G['passives'].get(id,{}).get('variants',[]) for x in v['effects']]
  skills[sl]={'rows':[],'effects':effects,'status':'baseline','notes':{'ko':'','en':''},'sources':[]}
 out[id]={'skills':skills,'audit':{'reviewedPatches':list(dict.fromkeys(r['patch'] for r in records[id])),'notes':[]}}
def source(r):return {'patch':r['patch'],'date':r['date'],'url':r['url']}
def claim(id,slot,pattern):
 matches=[r for r in records[id] if (slot is None or r['slot']==slot) and re.search(pattern,r['text'],re.I)]
 if not matches:raise ValueError((id,slot,pattern))
 used[id].update(r['idx'] for r in matches)
 return list({(r['patch'],r['date'],r['url']):source(r) for r in matches}.values())
def row(id,sl,vi,ri):return next(r for r in raw[id][sl] if r['_vi']==vi and r['_ri']==ri)
def mark(id,sl,r,src,provenance='patch'):
 r['_sources']=src;r['_provenance']='derived' if provenance=='patch' and 'modifiers' in r else provenance
 out[id]['skills'][sl]['status']='reconciled'
 out[id]['skills'][sl]['sources']+=src
 return r
def mods(id,sl,vi,ri,changes,src,derived=False):
 r=row(id,sl,vi,ri)
 for mi,value in changes.items():
  if isinstance(value,tuple):vals,unit=value;r['modifiers'][mi]={'values':vals,'units':[unit]*len(vals)}
  else:r['modifiers'][mi]['values']=value
 return mark(id,sl,r,src,'derived' if derived else 'patch')
def val(id,sl,vi,ri,ko,en,src,derived=False):
 r=row(id,sl,vi,ri);r['_value']={'ko':ko,'en':en};return mark(id,sl,r,src,'derived' if derived else 'patch')
def add(id,sl,ko_label,en_label,ko,en,src,derived=False):
 r={'attribute':en_label,'_label':{'ko':ko_label,'en':en_label},'_value':{'ko':ko,'en':en},'_sources':src,'_provenance':'derived' if derived else 'patch','_vi':-1,'_ri':len(raw[id][sl]),'_variant':''}
 raw[id][sl].append(r);mark(id,sl,r,src,'derived' if derived else 'patch');return r
def note(id,sl,ko,en,partial=False):
 n=out[id]['skills'][sl]['notes'];n['ko']+=' '+ko;n['en']+=' '+en
 if partial:out[id]['skills'][sl]['status']='partial'
def effect(id,index,ko,en,src):
 s=out[id]['skills']['P'];s['effects']['ko'][index]=ko;s['effects']['en'][index]=en;s['sources']+=src;s['status']='reconciled'
def replace_effect(id,ko_pairs,en_pairs,src):
 s=out[id]['skills']['P']
 for lang,pairs in [('ko',ko_pairs),('en',en_pairs)]:
  for old,new in pairs:
   assert any(old in p for p in s['effects'][lang]),(id,lang,old)
   s['effects'][lang]=[p.replace(old,new) for p in s['effects'][lang]]
 s['sources']+=src;s['status']='reconciled'
# Akshan: 26.1 changes are absolute final formulas; old R extraction was malformed.
s=claim('Akshan','Q',r'^Damage');mods('Akshan','Q',0,0,{0:[45,75,105,135,165],1:([70]*5,'% bonus AD')},s);mods('Akshan','Q',0,1,{0:[90,150,210,270,330],1:([140]*5,'% bonus AD')},s,True)
s=claim('Akshan','E',r'^Damage');val('Akshan','E',0,0,'(8 / 16 / 24 / 32 / 40 + 총 공격력의 25%) × (1 + 추가 공격 속도 100%당 0.3)','(8 / 16 / 24 / 32 / 40 + 25% total AD) × (1 + 0.3 per 100% bonus attack speed)',s,True)
s=claim('Akshan','P',r'second shot crit damage');effect('Akshan',1,'추가 탄환에는 적중 시 효과와 공격 시 효과가 적용되며, 치명타 시 추가 치명타 피해의 100%를 적용합니다. 26.1 원문 예시는 2배 / 2.3배입니다.','The additional shot applies on-hit and on-attack effects. Critical strikes apply 100% of bonus critical strike damage; the 26.1 examples are 2× / 2.3×.',s)
raw['Akshan']['R']=[r for r in raw['Akshan']['R'] if r['_ri']<2]
note('Akshan','R','보관본의 탄환 피해 계산식은 괄호와 변수가 훼손되어 제외했습니다. 치명타 보정은 26.1 공식 수치를 사용합니다.','Archived bullet damage formulas contain broken variables and brackets and are omitted. Critical scaling follows the official 26.1 update.',True)
# Annie
s=claim('Annie','Q',r'^Base Damage');mods('Annie','Q',0,0,{0:[80,125,170,215,260]},s)
s=claim('Annie','W',r'^Base Damage');mods('Annie','W',0,0,{0:[70,110,150,190,230]},s)
s=claim('Annie','R',r'^Magic Penetration');mods('Annie','R',0,0,{0:[10,15,20]},s)
# Azir: malformed published level increment deliberately exposed instead of guessed.
s=claim('Azir','Q',r'^Damage');mods('Azir','Q',0,0,{0:[75,95,115,135,155],1:[35,40,45,50,55]},s)
s=claim('Azir',None,r'^(?:W )?(?:Damage )?AP Ratio|^Damage\s*:')
s=[x for x in s if x['patch']!='25.20']+s[:0] if False else s
val('Azir','W',0,0,'50 / 65 / 80 / 95 / 110 + 레벨 비례 추가 피해 0~72 + 주문력의 35 / 42.5 / 50 / 57.5 / 65%','50 / 65 / 80 / 95 / 110 + 0–72 level-based bonus damage + 35 / 42.5 / 50 / 57.5 / 65% AP',s,True)
note('Azir','W','26.6 원문은 레벨 비례 피해를 0~72라고 하면서 10레벨부터 레벨당 7이라고도 적어 산술적으로 일치하지 않습니다. 범위는 원문대로 표시하고 레벨별 중간값은 계산하지 않습니다.','The 26.6 notes give both 0–72 and 7 per level starting at level 10, which do not agree arithmetically. The published range is retained; intermediate levels are not inferred.',True)
s=claim('Azir','E',r'^Damage');mods('Azir','E',0,1,{0:[70,110,150,190,230],1:[60]*5},s)
# Braum
s=claim('Braum','P',r'Damage On Follow');replace_effect('Braum',[('20%','40%'),('5.2~39.2','10.4~78.4')],[('20%','40%'),('5.2 : 39.2','10.4 : 78.4')],s)
s=claim('Braum','Q',r'^Damage');mods('Braum','Q',0,0,{0:[75,120,165,210,255]},s)
s=claim('Braum','R',r'^Base Damage');mods('Braum','R',0,0,{0:[150,250,350]},s)
# Cho'Gath
s=claim('Chogath','E',r'^Base Damage');mods('Chogath','E',0,0,{0:[30,50,70,90,110]},s);mods('Chogath','E',0,1,{0:[90,150,210,270,330]},s,True)
s=claim('Chogath','E',r'^Monster Damage');add('Chogath','E','몬스터 대상 피해량','Monster damage','100 / 150 / 200 / 250 / 300 + 주문력의 30%','100 / 150 / 200 / 250 / 300 + 30% AP',s)
# Draven
s=claim('Draven','W',r'^Attack Speed');mods('Draven','W',0,0,{0:[20,25,30,35,40]},s)
s=claim('Draven','R',r'^Damage\s*:');mods('Draven','R',0,0,{0:[200,300,400]},s);mods('Draven','R',0,1,{0:[400,600,800]},s,True)
s+=claim('Draven','R',r'^Damage Reduction');mods('Draven','R',0,2,{0:[100,150,200],1:[55,65,75]},s,True);mods('Draven','R',0,3,{0:[200,300,400],1:[110,130,150]},s,True)
add('Draven','R','관통 시 피해 감소','Damage falloff','적 적중마다 피해량이 곱연산으로 5% 감소, 최소 50% (14회 적중)','Damage decreases multiplicatively by 5% per enemy hit, to a minimum of 50% (14 hits)',s)
# Garen
s=claim('Garen','Q',r'^Move speed duration');mods('Garen','Q',0,0,{0:[1.4,1.95,2.5,3.05,3.6]},s)
s=claim('Garen','E',r'^AD Ratio|^Damage per spin');mods('Garen','E',0,0,{1:[40,43,46,49,52]},s);mods('Garen','E',0,1,{1:[50,53.75,57.5,61.25,65]},s,True)
s=claim('Garen','R',r'^True Damage');mods('Garen','R',0,0,{0:[125,200,275]},s)
# Hecarim
s=claim('Hecarim','Q',r'^Damage per hit');mods('Hecarim','Q',0,0,{0:[60,90,120,150,180]},s);mods('Hecarim','Q',0,1,{0:[36,54,72,90,108]},s,True)
# Jhin
s=claim('Jhin','P',r'^Move Speed');replace_effect('Jhin',[('1%당 0.4%','1%당 0.44%')],[('0.4% per 1%','0.44% per 1%')],s)
s=claim('Jhin','S',r'Multiplicative Crit Damage');add('Jhin','P','치명타 피해 보정','Critical damage modifier','총 치명타 피해의 75% (기본 치명타는 총 공격력의 150%)','75% of total critical strike damage (base critical strike: 150% total AD)',s)
s=claim('Jhin','W',r'^Damage');mods('Jhin','W',0,0,{0:[70,105,140,175,210]},s);mods('Jhin','W',0,1,{0:[52.5,78.75,105,131.25,157.5]},s,True)
# Karma: Mantra E lives under E despite patch heading R.
s=claim('Karma','R',r'Empowered E');mods('Karma','E',1,0,{0:[45,85,125,165]},s);mods('Karma','E',1,1,{1:[45,85,125,165]},s,True);mods('Karma','E',1,2,{0:[45,85,125,165]},s)
# Kayn
s=claim('Kayn','P',r'^Bonus Post');replace_effect('Kayn',[('25%~45%','20%~40%')],[('25% : 45%','20% : 40%')],s)
s=claim('Kayn','Q',r'^Damage');mods('Kayn','Q',0,0,{0:[75,105,135,165,195]},s);mods('Kayn','Q',0,1,{0:[150,210,270,330,390]},s,True);mods('Kayn','Q',0,2,{0:[115,145,175,205,235]},s,True);mods('Kayn','Q',0,3,{0:[230,290,350,410,470]},s,True)
# Kog'Maw
s=claim('KogMaw','Q',r'^Damage');mods('KogMaw','Q',0,1,{1:[90]*5},s)
s=claim('KogMaw','Q',r'^Passive Attack');mods('KogMaw','Q',0,0,{0:[5,10,15,20,25]},s)
s=claim('KogMaw','W',r'^Damage On');mods('KogMaw','W',0,1,{1:[1.5]*5},s)
s=claim('KogMaw','R',r'^Minimum Damage|^Maximum damage');mods('KogMaw','R',0,0,{2:[35,40,45]},s);mods('KogMaw','R',0,1,{2:[70,80,90]},s,True)
# Malphite
s=claim('Malphite','E',r'^(?:Base )?Damage');mods('Malphite','E',0,0,{0:[60,95,130,165,200]},s)
s=claim('Malphite','W',r'^Monster');add('Malphite','W','몬스터 대상 피해 배율','Monster damage modifier','180%','180%',s)
# Naafiri
s=claim('Naafiri','P',r'^Packmate Monster');add('Naafiri','P','무리 동료의 몬스터 대상 피해','Packmate monster damage','155%','155%',s)
out['Naafiri']['skills']['P']['effects']['ko'].append('무리 동료는 몬스터에게 피해량의 155%를 입힙니다.');out['Naafiri']['skills']['P']['effects']['en'].append('Packmates deal 155% damage to monsters.')
s=claim('Naafiri','Q',r'^(?:Minimum|Maximum) Bonus');mods('Naafiri','Q',0,4,{0:[30,42.5,55,67.5,80]},s);mods('Naafiri','Q',0,5,{0:[60,85,110,135,160]},s);mods('Naafiri','Q',0,6,{0:[100,142.5,185,227.5,270]},s,True);mods('Naafiri','Q',0,7,{0:[130,185,240,295,350]},s,True)
s=claim('Naafiri','R',r'^(?:Physical Damage|Damage)');mods('Naafiri','R',0,0,{0:[125,200,275],1:[100]*3},s);mods('Naafiri','R',0,1,{0:[12.5,20,27.5],1:[10]*3},s)
# Nidalee: retain unchanged extreme, show changed distance transition explicitly.
s=claim('Nidalee','Q',r'^Bonus Damage Beyond');add('Nidalee','Q','창 투척 · 525 거리 이후 추가 피해','Javelin Toss · additional damage beyond 525 range','0~125%; 525보다 짧은 거리의 피해는 변경 없음','0–125%; damage below 525 range is unchanged',s)
s=claim('Nidalee','W',r'^Damage');val('Nidalee','W',1,1,'50 / 80 / 110 / 140 / 170 + 추가 공격력의 50% + 주문력의 30%','50 / 80 / 110 / 140 / 170 + 50% bonus AD + 30% AP',s)
note('Nidalee','W','26.21 공식 문서는 쿠거 W 피해를 5개 값으로 제시합니다. 기존 자료의 4랭크와 배열 길이가 달라 원문의 5개 값을 그대로 표시합니다.','The 26.21 notes list five cougar W damage values, unlike the archive\'s four-rank array. The five published values are preserved.',True)
s=claim('Nidalee','E',r'^Attack Speed');mods('Nidalee','E',0,0,{0:[20,30,40,50,60]},s)
# Orianna
s=claim('Orianna','P',r'^Damage Increase');replace_effect('Orianna',[('피해가 20%','피해가 15%'),('2~10','1.5~7.5'),('주문력의 3%','주문력의 2.25%'),('14~70','13~65'),('주문력의 21%','주문력의 19.5%')],[('20%','15%'),('2 : 10','1.5 : 7.5'),('(+ 3% AP)','(+ 2.25% AP)'),('14 : 70','13 : 65'),('(+ 21% AP)','(+ 19.5% AP)')],s)
s=claim('Orianna','Q',r'^Damage');mods('Orianna','Q',0,0,{1:[60]*5},s);mods('Orianna','Q',0,1,{1:[42]*5},s,True)
s=claim('Orianna','W',r'^Damage');mods('Orianna','W',0,0,{0:[70,110,150,190,230],1:[85]*5},s)
s=claim('Orianna','R',r'^Damage');mods('Orianna','R',0,0,{0:[225,350,475],1:[110]*3},s)
# Qiyana
s=claim('Qiyana','P',r'^Bonus Damage');replace_effect('Qiyana',[('추가 공격력의 30%','추가 공격력의 25%')],[('30% bonus AD','25% bonus AD')],s)
s=claim('Qiyana','Q',r'^(?:Base )?Damage');
for vi in [0,1]:
 mods('Qiyana','Q',vi,0,{0:[70,100,130,160,190],1:[90]*5},s);mods('Qiyana','Q',vi,1,{0:[52.5,75,97.5,120,142.5],1:[67.5]*5},s,True)
mods('Qiyana','Q',1,2,{0:[112,160,208,256,304],1:[144]*5},s,True)
mods('Qiyana','Q',1,3,{0:[94.5,135,175.5,216,256.5],1:[121.5]*5},s,True)
s=claim('Qiyana','Q',r'^Monster');add('Qiyana','Q','몬스터 대상 피해 배율','Monster damage modifier','160%','160%',s)
s=claim('Qiyana','W',r'^Bonus Attack Speed');mods('Qiyana','W',0,0,{0:[15,20,25,30,35]},s)
# Rell
s=claim('Rell','W',r'^Shield');mods('Rell','W',0,1,{1:[11]*5},s)
s=claim('Rell','E',r'^Move Speed');add('Rell','E','추가 이동 속도','Bonus movement speed','3초 동안 15%; 강화된 아군 또는 시야에 들어온 적 챔피언을 향하면 30%','15% for 3 seconds; 30% toward the empowered ally or a visible enemy champion',s)
s=claim('Rell','R',r'^Damage');mods('Rell','R',0,1,{0:[150,200,350]},s);mods('Rell','R',0,0,{0:[18.75,25,43.75]},s,True)
# Rumble: recompute all dependent totals/ticks from the current three-second formula.
s=claim('Rumble','Q',r'^Damage(?: over| Over|\s*:)')
b=[50,75,100,125,150];hp=[6,6.5,7,7.5,8]
for ri,factor in enumerate([1,1/12,.7,.7/12,1.5,1.5/12,1.05,1.05/12]):
 mods('Rumble','Q',0,ri,{0:[v*factor for v in b],1:[105*factor]*5,2:[v*factor for v in hp]},s,ri!=0)
s=claim('Rumble','P',r'^Overheated Damage|^Overheat Attack Speed|^Monster Cap');replace_effect('Rumble',[('50%~130%','30%~100%'),('대상 최대 체력의 5%','대상 최대 체력의 4%'),('65~150','90~175')],[('50% : 130%','30% : 100%'),("5% of the target's maximum health","4% of the target's maximum health"),('65 : 150','90 : 175')],s)
s=claim('Rumble','R',r'^Tick Rate|^Maximum Damage');mods('Rumble','R',0,2,{0:[600,1000,1400]},s)
# Tick duration changed; 5 seconds *4 ticks/sec from official max/per-tick relation.
mods('Rumble','R',0,0,{0:[30,50,70],1:[8.75]*3},s,True)
# Minimum-duration formula is not established by the patch note; omit the old two-tick assumption.
raw['Rumble']['R']=[r for r in raw['Rumble']['R'] if r['_ri']!=1]
note('Rumble','R','0.25초 주기 피해는 최대 피해를 20회로 나누어 계산했습니다. 보관본의 최소 피해량은 변경된 주기와의 관계가 불명확해 제외했습니다.','Quarter-second tick damage is derived as maximum damage divided by 20 ticks. The archived minimum-damage assumption is omitted because its relation to the new tick timing is unclear.',True)
# Seraphine
s=claim('Seraphine','Q',r'^Ability Power');mods('Seraphine','Q',0,0,{1:[40]*5},s);mods('Seraphine','Q',0,1,{1:[70]*5},s,True)
s=claim('Seraphine','W',r'^Healing');val('Seraphine','W',0,1,'대상 잃은 체력의 8 / 10 / 12 / 14 / 16% (범위 내 아군 수에 무관)','8 / 10 / 12 / 14 / 16% target missing health, regardless of allies in the area',s);row('Seraphine','W',0,1)['_label']={'ko':'체력 회복','en':'Healing'}
# Singed
s=claim('Singed','R',r'^Bonus Stats');mods('Singed','R',0,0,{0:[25,55,85]},s);mods('Singed','R',0,1,{0:[2.5,5.5,8.5]},s,True);mods('Singed','R',0,2,{0:[125,275,425]},s,True)
note('Singed','R','보관본의 총 회복량 행은 지속시간 전체 합계이며 5초당 재생량이 아닙니다.','The archived total-regeneration row represents the full duration, not regeneration per five seconds.')
row('Singed','R',0,2)['_label']={'ko':'지속시간 전체 추가 체력/마나 재생','en':'Total bonus health/mana regeneration over full duration'}
# Tahm Kench
s=claim('TahmKench','P',r'^Damage');replace_effect('TahmKench',[('6~48(레벨에 따라)','5~60(1~12레벨에 따라)'),('AP의 1.5%','AP의 1.25%')],[('6 : 48 (based on level)','5 : 60 (based on levels 1–12)'),('1.5% AP per 100','1.25% AP per 100')],s)
val('TahmKench','Q',0,0,'75 / 120 / 165 / 210 / 255 + 주문력의 100% + 절대 미각 추가 피해 [5~60 (1~12레벨) + 추가 체력 100당 주문력의 1.25% + 추가 체력의 4%]','75 / 120 / 165 / 210 / 255 + 100% AP + An Acquired Taste bonus damage [5–60 (levels 1–12) + 1.25% AP per 100 bonus health + 4% bonus health]',s,True)
s=claim('TahmKench','Q',r'^Base Healing');mods('TahmKench','Q',0,1,{0:[10,20,30,40,50]},s)
# Thresh
s=claim('Thresh','E',r'^Active Damage');mods('Thresh','E',0,2,{0:[65,110,155,200,245],1:[60]*5},s)
# Twitch
s=claim('Twitch','Q',r'^Bonus Attack Speed');mods('Twitch','Q',0,1,{0:[40,45,50,55,60]},s)
# Veigar
s=claim('Veigar','W',r'^AP Ratio');mods('Veigar','W',0,0,{1:[70,80,90,100,110]},s)
# Viktor
s=claim('Viktor','Q',r'^Shield');add('Viktor','Q','보호막 흡수량','Shield strength','30~130 (레벨에 따라) + 주문력의 20%','30–130 (based on level) + 20% AP',s)
# Xerath
s=claim('Xerath','Q',r'^Damage');mods('Xerath','Q',0,1,{0:[70,110,150,190,230]},s)
# Yunara: empowered W is reported under R in26.1; keep both UI slots consistent.
s=claim('Yunara','Q',r'^(?:Passive|Active) On Hit Damage');
for ri,factor in [(0,1),(2,1),(3,2),(4,2.5),(5,5)]:mods('Yunara','Q',0,ri,{0:[v*factor for v in [3,8,13,18,23]]},s,ri not in [0,2])
s=claim('Yunara','Q',r'^Attack Speed');mods('Yunara','Q',0,1,{0:[20,30,40,50,60]},s)
s=claim('Yunara','W',r'^Initial Damage');mods('Yunara','W',0,0,{0:[55,95,135,175,215],1:([85]*5,'% bonus AD')},s)
s=claim('Yunara','W',r'^Damage per second');mods('Yunara','W',0,1,{0:[8.25,14.25,20.25,26.25,32.25],1:([12.75]*5,'% bonus AD')},s,True);mods('Yunara','W',0,2,{0:[33,57,81,105,129],1:([51]*5,'% bonus AD')},s)
s=claim('Yunara',None,r'^Damage\s*:');mods('Yunara','R',0,0,{0:[160,320,480]},s)
add('Yunara','W','파멸의 호 · 강화 시 피해','Arc of Ruin · empowered damage','160 / 320 / 480 + 추가 공격력의 120% + 주문력의 75% (궁극기 랭크 기준)','160 / 320 / 480 + 120% bonus AD + 75% AP (ultimate rank)',s,True)
# same full formula inR avoidsbase-onlyrow misleading
val('Yunara','R',0,0,'160 / 320 / 480 + 추가 공격력의 120% + 주문력의 75%','160 / 320 / 480 + 120% bonus AD + 75% AP',s,True)
s=claim('Yunara','E',r'^(?:Bonus )?Movement Speed(?: Duration| toward|\s*:)')
mods('Yunara','E',0,0,{0:[30,35,40,45,50]},s);mods('Yunara','E',0,1,{0:[45,52.5,60,67.5,75]},s);val('Yunara','E',0,2,'1.5초 후 이동 속도 감소 시작','Movement speed starts decaying after 1.5 seconds',s)
# Zeri
s=claim('Zeri','P',r'^Execute threshold');replace_effect('Zeri',[('60~150','70~160'),('주문력의 18%','주문력의 20%')],[('60 : 150','70 : 160'),('18% AP','20% AP')],s)
s=claim('Zeri','Q',r'^(?:Base )?Damage');mods('Zeri','Q',0,0,{0:[22,26,30,34,38],1:[102,104,106,108,110]},s);mods('Zeri','Q',0,1,{0:[v/7 for v in [22,26,30,34,38]],1:[v/7 for v in [102,104,106,108,110]]},s,True)
s=claim('Zeri','Q',r'^Excess');add('Zeri','Q','초과 공격 속도의 공격력 전환','Excess attack speed to AD conversion','60%','60%',s)
s=claim('Zeri','W',r'^Damage\s*:|^AP Ratio');mods('Zeri','W',0,0,{1:[100]*5,2:[50]*5},s)
s=claim('Zeri','W',r'^Through-Wall|^Wall Crit|^Wall Damage|^Critical Strike');add('Zeri','W','벽 통과 피해량','Wall-enhanced damage','45 / 105 / 165 / 225 / 285 + 총 공격력의 150% + 주문력의 75%','45 / 105 / 165 / 225 / 285 + 150% total AD + 75% AP',s,True);add('Zeri','W','벽 통과 치명타 배율','Wall critical multiplier','150% (무한의 대검 적용 시 15% 추가)','150% (+15% with Infinity Edge)',s)
s=claim('Zeri','E',r'^Damage\s*:|^Bonus Magic Damage');mods('Zeri','E',0,0,{0:[22,24,26,28,30],1:([0]*5,'% bonus AD')},s)
# Remove the now-deleted bonus AD term instead of presenting 0% as a live scaling.
row('Zeri','E',0,0)['modifiers'].pop(1)
s=claim('Zeri','R',r'^Active Damage|^Burst AD ratio');mods('Zeri','R',0,0,{0:[150,250,350],1:[60]*3},s)
s=claim('Zeri','R',r'^(?:Move Speed|MS) per Stack');add('Zeri','R','중첩당 이동 속도','Movement speed per stack','1.5%','1.5%',s)
# Consistency fixes for labels/notes known to be source-limited.
for sl in 'PQWER':
 if any('[' in str(r.get('modifiers')) and '] × [' in str(r.get('modifiers')) for r in raw['Akshan'][sl]):note('Akshan',sl,'원본 계산식의 누락된 변수가 있어 검증이 필요합니다.','The source has unresolved calculation variables.',True)
note('Ivern','P','보관본의 정글 캠프 체력·마나 소모 수치가 비정상적으로 낮은 끝값을 포함합니다. 이후 패치로 확인되지 않아 현재 수치로 보장하지 않습니다.','The archive\'s camp health/mana costs have suspiciously low endpoint values. Later notes do not verify these costs; they are not guaranteed current.',True)
# Any remaining published change is retained as a current condition/parameter.
# Exact same labelled parameter is replaced chronologically, never stacked as old values.
for id in IDS:
 residual={}
 for r in records[id]:
  if r['idx'] in used[id]:continue
  if r['slot'] not in 'PQWER':
   used[id].add(r['idx']);continue
  text=r['text']; label=text.split(':',1)[0].strip() if ':' in text else text
  key=(r['slot'],re.sub(r'[^a-z0-9]','',label.lower()))
  residual[key]=r
 for r in residual.values():
  text=r['text'];kt=r['ko'];sl=r['slot']
  # Same semantic cosmetic changes stay in history; no numeric ability content lost.
  if re.match(r'^(?:Bugfix|Fixed|Clarified|Tooltip now|Damage now cosmetically|Step Right)',text,re.I):continue
  enlabel=text.split(':',1)[0].strip() if ':' in text else 'Current behavior'
  envalue=re.split('[⇒→]',text)[-1].strip() if re.search('[⇒→]',text) else text.split(':',1)[-1].strip()
  if not kt:raise ValueError(('Unpaired remaining translation',id,text))
  kolabel=kt.split(':',1)[0].strip() if ':' in kt else '현재 동작'
  kovalue=re.split('[⇒→]',kt)[-1].strip() if re.search('[⇒→]',kt) else kt.split(':',1)[-1].strip()
  if id=='Zeri' and sl=='R' and 'Overcharged duration' in enlabel:
   kolabel='공격 시 궁극기 지속시간 증가';enlabel='Ultimate extension per attack';kovalue='2.5초';envalue='2.5s'
  add(id,sl,kolabel,enlabel,kovalue,envalue,[source(r)])
# Materialize localized rows.
def n(v):return str(round(v,4)).rstrip('0').rstrip('.') if isinstance(v,float) and not v.is_integer() else str(int(v)) if isinstance(v,(int,float)) else str(v)
def fmt(m,lang):
 vals=m.get('values',[]);units=m.get('units',[])
 unit=lambda u: G['units'].get(u,u) if lang=='ko' else u
 if not vals:return '—'
 if len(set(map(str,vals)))==1 and len(set(units))<=1:return n(vals[0])+unit(units[0] if units else '')
 if len(set(units))<=1:return ' / '.join(map(n,vals))+unit(units[0] if units else '')
 return ' / '.join(n(v)+unit(units[i] if i<len(units) else '') for i,v in enumerate(vals))
for id in IDS:
 for sl in 'PQWER':
  s=out[id]['skills'][sl]
  for r in raw[id][sl]:
   en=r['attribute']; ko=G['labels'].get(en,en)
   if r['_variant']:
    en=r['_variant']+' · '+en;ko=G['variants'].get(r['_variant'],r['_variant'])+' · '+ko
   values=r.get('_value') or {lang:' + '.join(fmt(m,lang) for m in r.get('modifiers',[])) for lang in ['ko','en']}
   if id=='TahmKench' and values['en']=='60 - 100% (Level 1 - 18)':values['ko']='60~100% (1~18레벨)'
   s['rows'].append({'attribute':r.get('_label',{'ko':ko,'en':en}),'value':values,'provenance':r['_provenance'],'sources':r['_sources']})
  s['sources']=list({(x['patch'],x['date'],x['url']):x for x in s['sources']}.values())
  s['notes']={k:v.strip() for k,v in s['notes'].items()}
  # Empty R formula slots can still have a valid official summary; flag incomplete details.
  if not s['rows'] and not any(s['effects'].values()) and s['status']=='baseline':s['status']='partial'
 out[id]['audit']['changeCount']=len(records[id]);out[id]['audit']['notes'].append('All post-25.15 champion-section changes reviewed. Unchanged values retain baseline provenance; stats handled by main collector. Cosmetic-only fixes remain in patch history.')
 # Preserve source identity for change-review traceability.
 out[id]['audit']['sourceFingerprint']=__import__('hashlib').sha256(json.dumps([(r['patch'],r['date'],r['text']) for r in records[id]],ensure_ascii=False,separators=(',',':')).encode()).hexdigest()
path=ROOT/'scripts/reconciled/group-4.json';path.write_text(json.dumps(out,ensure_ascii=False,indent=2))
print(len(out),'champions',sum(len(c['skills']) for c in out.values()),'skills',sum(len(s['rows']) for c in out.values() for s in c['skills'].values()),'rows')
