"""Rebuild the static champion index from versioned Riot data and official patch notes.
Run: python -m pip install beautifulsoup4 && python scripts/collect_data.py
Never silently promote archived Meraki formulas to the current patch.
"""
from urllib.request import urlopen, Request
from urllib.error import HTTPError
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from bs4 import BeautifulSoup
from datetime import datetime, timezone
import json, re, os, hashlib, time
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'dist/data'; OUT.mkdir(parents=True,exist_ok=True)
CACHE=Path(os.environ.get('RIFT_CACHE','/workspace/scratch/rift-cache')); CACHE.mkdir(parents=True,exist_ok=True)
FAIL=[]
def fetch(url):
 p=CACHE/(hashlib.sha256(url.encode()).hexdigest()+'.cache')
 if p.exists(): return p.read_bytes()
 err=p.with_suffix('.missing')
 if err.exists() and time.time()-err.stat().st_mtime<86400:raise RuntimeError('최근 수집 실패: '+err.read_text())
 for attempt in range(2):
  try:
   with urlopen(Request(url,headers={'User-Agent':'RiftNotes/1.0 (personal research)'}),timeout=22) as r: d=r.read()
   p.write_bytes(d); return d
  except HTTPError as e:
   if e.code in (404,403):
    err.write_text(str(e));raise
  except Exception:
   if attempt:raise
 raise RuntimeError(url)
def write(p,obj):p.write_text(json.dumps(obj,ensure_ascii=False,separators=(',',':')))
version=json.loads(fetch('https://ddragon.leagueoflegends.com/api/versions.json'))[0]
base='https://ddragon.leagueoflegends.com/cdn/'+version
index=json.loads(fetch(base+'/data/ko_KR/champion.json'))['data']
try: archive=json.loads(fetch('https://cdn.merakianalytics.com/riot/lol/resources/latest/en-US/champions.json'))
except Exception:archive={}
names={}
for k,c in index.items():
 for n in [k,c['name'],archive.get(k,{}).get('name','')]:
  if n:names[re.sub(r'[^\w]','',n).lower()]=k
aliases={'wukong':'MonkeyKing','nunu':'Nunu','nunuandwillump':'Nunu','renataglasc':'Renata','누누':'Nunu'}
names.update(aliases)
def canon(name): return names.get(re.sub(r'[^\w]','',name).lower())
def slot(label):
 m=re.match(r'\s*([QWER])\s*[-–—:]?',label,re.I)
 if m:return m[1].upper()
 if re.search('기본 지속|패시브|passive',label,re.I):return 'P'
 if re.search('기본 능력|능력치|base stat',label,re.I):return 'S'
 return 'A'
def kind(txt):
 if '⇒' not in txt and '→' not in txt:
  return 'fix' if re.search('버그|수정|bug|fix',txt,re.I) else 'adjust'
 a,b=re.split('⇒|→',txt,maxsplit=1)
 aa=[float(x) for x in re.findall(r'(?<!\d)-?\d+(?:\.\d+)?',a.split(':')[-1])]
 bb=[float(x) for x in re.findall(r'(?<!\d)-?\d+(?:\.\d+)?',b)]
 if not aa or len(aa)!=len(bb):return 'adjust'
 dirs={1 if y>x else -1 for x,y in zip(aa,bb) if x!=y}
 if len(dirs)!=1:return 'adjust'
 direction=next(iter(dirs))
 if re.search('재사용|소모|cooldown|cost|충전 시간',a,re.I):direction*=-1
 return 'buff' if direction>0 else 'nerf'
def get_patch(pair):
 major,minor=pair;patch=f'{major}.{minor}'
 slug=f'league-of-legends-patch-{major}-{minor}-notes' if major>=26 and minor>=4 else f'patch-{major}-{minor}-notes'
 if major==25 and minor<10:slug=f'patch-25-{minor:02d}-notes'
 if major==25 and minor<3:slug=f'patch-25-s1-{minor}-notes'
 if major==25 and minor==3:slug='patch-2025-s1-3-notes'
 url='https://www.leagueoflegends.com/ko-kr/news/game-updates/'+slug+'/'
 try:html=fetch(url)
 except Exception as e:return {'patch':patch,'error':str(e),'url':url}
 s=BeautifulSoup(html,'html.parser')
 for script in s(['script','style','nav','footer']):script.decompose()
 t=s.find('time');date=t.get('datetime','')[:10] if t else ''
 events=[]
 for h in s.find_all('h3'):
  heading=re.sub(r'^\s*(?:신규|업데이트된|업데이트|new|updated)\s+','',h.get_text(' ',strip=True),flags=re.I)
  heading=re.sub(r'\s+업데이트$','',heading)
  c=canon(heading)
  # Riot sometimes reuses champion anchors for items or event promotions.
  # Match the actual heading, never infer a champion from an unrelated anchor.
  if not c:continue
  section=h.find_previous('h2');sectiontxt=section.get_text(' ',strip=True) if section else ''
  if re.search('아레나|총력전|무작위|클래식|격전|돌격|신속|만우절|arena|aram|classic|swarm|urf|swiftplay',sectiontxt,re.I):continue
  hotfix=bool(re.search('추가 패치|긴급|mid.patch',sectiontxt,re.I))
  if hotfix:
   for near in h.find_all_previous(['h2','h3','h4']):
    if near is section:break
    dated=near.get_text(' ',strip=True)
    if re.search(r'20\d{2}년\s*\d{1,2}월\s*\d{1,2}일',dated):sectiontxt=dated;break
  block=h.find_parent(class_='patch-change-block') or h.parent
  changes=[]; current='일반'; started=False
  for node in block.select('h2, h3, h4, li, div.attribute-change'):
   if node is h:started=True;continue
   if not started:continue
   if node.name in ('h2','h3'):break
   if node.name=='h4':
    current=node.get_text(' ',strip=True)
    if re.search('아레나|총력전|아수라장|클래식|격전 일정|확인된 문제|신속 모드|신속 대전|arena|aram|classic|swiftplay',current,re.I):break
    if hotfix and re.fullmatch('버그 수정|버그 수정 및 편의성 개선',current):break
    if re.search(r'20\d{2}년\s*\d{1,2}월\s*\d{1,2}일',current):break
    if c!='Ornn' and any('/img/item/' in im.get('src','') for im in node.find_all('img')):break
    continue
   if node.find_parent('li'):continue
   if node.name=='div':
    attr=node.select_one('.attribute');before=node.select_one('.attribute-before');after=node.select_one('.attribute-after')
    txt=(attr.get_text(' ',strip=True)+': ' if attr else '')+(before.get_text(' ',strip=True)+' ⇒ ' if before else '')+(after.get_text(' ',strip=True) if after else node.get_text(' ',strip=True))
   else:txt=node.get_text(' ',strip=True)
   txt=' '.join(txt.split())
   if txt:changes.append({'slot':slot(current),'title':current,'text':txt,'kind':kind(txt)})
  if not changes:continue
  eventdate=date
  dm=re.search(r'(20\d{2})년\s*(\d{1,2})월\s*(\d{1,2})일',sectiontxt)
  if dm:eventdate=f'{int(dm[1]):04d}-{int(dm[2]):02d}-{int(dm[3]):02d}'
  events.append({'champion':c,'patch':patch,'date':eventdate,'articleDate':date,'url':url+'#'+h.get('id','patch-champions'),'changes':changes,'section':sectiontxt,'isHotfix':hotfix})
 return {'patch':patch,'date':date,'url':url,'events':events}
current_major,current_minor=map(int,version.split('.')[:2]);current_public=current_major+10 if current_major>=15 else current_major
pairs=[(y,n) for y in range(9,15) for n in range(1,25)]+[(y,n) for y in range(25,current_public+1) for n in range(1,(current_minor if y==current_public else 24)+1)]
# Optional limit is useful during parser development, never enabled in production.
if os.environ.get('RIFT_RECENT_ONLY'):pairs=[p for p in pairs if p[0]>=25]
patches=[]
with ThreadPoolExecutor(max_workers=8) as pool:
 fs={pool.submit(get_patch,p):p for p in pairs}
 for i,f in enumerate(as_completed(fs),1):
  r=f.result();patches.append(r)
  if i%20==0:print('patches',i,'/',len(pairs),flush=True)
patches.sort(key=lambda p:tuple(map(int,p['patch'].split('.'))),reverse=True)
bychamp={k:[] for k in index}
for p in patches:
 for e in p.get('events',[]):bychamp[e.pop('champion')].append(e)
for history in bychamp.values():history.sort(key=lambda h:(tuple(map(int,h['patch'].split('.'))),h['date']),reverse=True)
write(OUT/'patches.json',{'patches':[{k:v for k,v in p.items() if k!='events'} for p in patches]})
print('patch fetch complete',sum('events' in x for x in patches),'successes',flush=True)
def champion(k):
 try:
  d=json.loads(fetch(base+'/data/ko_KR/champion/'+k+'.json'))['data'][k]
  a=archive.get(k);formula=[]
  if a:
   for key,abilities in a['abilities'].items():
    variants=[]
    for ability in abilities:
     rows=[l for e in ability['effects'] for l in e.get('leveling',[])]
     variants.append({'name':ability['name'],'rows':rows,'damageType':ability.get('damageType'),'effects':[e['description'] for e in ability['effects'] if not e.get('leveling')]})
    formula.append({'slot':key,'variants':variants})
  ad=re.search(r'/cdn/([^/]+)/',a.get('icon','')) if a else None
  archiveversion=ad[1] if ad else None
  # Keep current official information and archived formulas explicitly separate.
  obj={k2:d[k2] for k2 in ['id','key','name','title','tags','partype','stats','passive','spells','info','image']}
  obj.update({'version':version,'formulas':formula,'formulaVersion':archiveversion,'history':bychamp[k],
    'archiveLastChanged':a.get('patchLastChanged') if a else None,'englishName':a.get('name',k) if a else k,
    'positions':a.get('positions',[]) if a else [],'source':base+'/data/ko_KR/champion/'+k+'.json',
    'formulaSource':'https://cdn.merakianalytics.com/riot/lol/resources/latest/en-US/champions.json'})
  # Data Dragon 16.20 returns zero for every attackdamageperlevel field.
  # Reconstruct this field from a labelled baseline plus subsequent numeric official changes.
  adgrowth=a.get('stats',{}).get('attackDamage',{}).get('perLevel') if a else None
  growthSource=obj['formulaSource'];growthPatch=archiveversion
  baseline=(int(archiveversion.split('.')[0])+10,int(archiveversion.split('.')[1])) if archiveversion else (0,0)
  for h in reversed(bychamp[k]):
   if tuple(map(int,h['patch'].split('.')))<=baseline:continue
   for ch in h['changes']:
    if ch['slot']=='S' and re.search(r'공격력.*증가량|레벨당 공격력|성장 공격력|attack damage growth',ch['text'],re.I) and ('⇒' in ch['text'] or '→' in ch['text']):
     after=re.split('⇒|→',ch['text'])[-1];match=re.search(r'\d+(?:\.\d+)?',after)
     if match:adgrowth=float(match[0]);growthSource=h['url'];growthPatch=h['patch']
  obj['attackDamageGrowth']={'value':adgrowth,'source':growthSource,'sourcePatch':growthPatch,'method':'보관본 및 이후 공식 능력치 변경 반영'}
  write(OUT/(k+'.json'),obj)
  return {'id':k,'name':d['name'],'title':d['title'],'tags':d['tags'],'englishName':obj['englishName'],'positions':obj['positions'],'patchCount':len(bychamp[k]),'latestPatch':bychamp[k][0]['patch'] if bychamp[k] else None}
 except Exception as e:FAIL.append({'champion':k,'error':str(e)});return None
summaries=[]
with ThreadPoolExecutor(max_workers=8) as pool:
 for i,c in enumerate(pool.map(champion,index),1):
  if c:summaries.append(c)
  if i%35==0:print('champions',i,'/',len(index),flush=True)
valid=[p for p in patches if p.get('events')]
meta={'version':version,'patch':str(int(version.split('.')[0])+10)+'.'+version.split('.')[1],
 'collectedAt':datetime.now(timezone.utc).isoformat(),'championCount':len(summaries),'patchCount':len(valid),
 'historyCount':sum(len(v) for v in bychamp.values()),'earliestPatch':valid[-1]['patch'] if valid else None,
 'latestPatch':valid[0]['patch'] if valid else None,'coverage':'소환사의 협곡 챔피언 조정. 원문 내 챔피언 항목 기준이며, 별도 버그 수정·게임 모드 및 누락 문서는 포함되지 않을 수 있습니다.',
 'missingPatches':[p['patch'] for p in patches if not p.get('events')],'failures':FAIL}
write(OUT/'index.json',{'meta':meta,'champions':summaries})
print(json.dumps(meta,ensure_ascii=False),flush=True)
