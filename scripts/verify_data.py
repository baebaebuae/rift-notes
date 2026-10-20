import json
from pathlib import Path
root=Path(__file__).resolve().parents[1]/'dist';idx=json.loads((root/'data/index.json').read_text());byid={c['id'] for c in idx['champions']}
assert len(byid)==len(idx['champions'])==173
count=0
for k in byid:
 c=json.loads((root/'data'/f'{k}.json').read_text())
 assert c['version']==idx['meta']['version']
 assert (root/'assets/champions'/f'{k}.png').exists()
 assert len(c['spells'])==4
 versions=[tuple(map(int,h['patch'].split('.')))for h in c['history']]
 assert versions==sorted(versions,reverse=True)
 for h in c['history']:
  assert h['changes'] and h['url'].startswith('https://www.leagueoflegends.com/')
  assert not any(x in h.get('section','').lower()for x in ['아레나','총력전','신속 대전','arena','aram','swiftplay'])
 count+=len(c['history'])
assert count==idx['meta']['historyCount']
ahri=json.loads((root/'data/Ahri.json').read_text());assert ahri['attackDamageGrowth']['value']==3
ashe=json.loads((root/'data/Ashe.json').read_text());assert ashe['attackDamageGrowth']['value']==3
assert any('3.5 ⇒ 3' in c['text'] for h in ashe['history'] if h['patch']=='26.20' for c in h['changes'])
yasuo=json.loads((root/'data/Yasuo.json').read_text());assert any(c['kind']=='buff' for h in yasuo['history'] if h['patch']=='26.17'for c in h['changes'])
lux=json.loads((root/'data/Lux.json').read_text());assert any(h['date']=='2025-12-16' for h in lux['history']if h['patch']=='25.24')
v=json.loads((root/'data/verified.json').read_text());assert v['Ahri']['skills']['Q'][0]['modifiers'][0]['values']==[35,60,85,110,135]
assert v['Ahri']['skills']['R'][0]['modifiers'][0]['values']==[75,125,175]
for locale,hotfix in [('', '2026-01-12'),('en/', '2026-01-09')]:
 folder=root/'data'/locale; localidx=json.loads((folder/'index.json').read_text()); total=0
 for champion in localidx['champions']:
  c=json.loads((folder/(champion['id']+'.json')).read_text());total+=len(c['history'])
  ordered=[(tuple(map(int,h['patch'].split('.'))),h['date']) for h in c['history']]
  assert ordered==sorted(ordered,reverse=True)
 assert total==localidx['meta']['historyCount']
 swain=json.loads((folder/'Swain.json').read_text());assert not any(h['patch']=='26.7' for h in swain['history'])
 xayah=json.loads((folder/'Xayah.json').read_text());assert not any(h['patch']=='11.23' for h in xayah['history'])
 zed=json.loads((folder/'Zed.json').read_text());assert all(len(h['changes'])==1 for h in zed['history'] if h['patch']=='25.5')
 tryn=json.loads((folder/'Tryndamere.json').read_text());h=next(h for h in tryn['history'] if h['patch']=='26.1' and h['isHotfix']);assert h['date']==hotfix and len(h['changes'])==2
print(f'PASS: {len(byid)} champions, {count} history entries, source URLs, ordering, game-mode separation, missing-growth correction, signed change classification, hotfix date, verified damage values.')
