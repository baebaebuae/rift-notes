from pathlib import Path
from urllib.request import urlopen
from concurrent.futures import ThreadPoolExecutor
import json
ROOT=Path(__file__).resolve().parents[1];idx=json.loads((ROOT/'dist/data/index.json').read_text());version=idx['meta']['version'];d=ROOT/'dist/assets/champions';d.mkdir(parents=True,exist_ok=True)
urls=[('https://ddragon.leagueoflegends.com/cdn/'+version+'/img/champion/'+c['id']+'.png',d/(c['id']+'.png'))for c in idx['champions']]
urls.append(('https://ddragon.leagueoflegends.com/cdn/img/champion/splash/Ahri_0.jpg',ROOT/'dist/assets/ahri-splash.jpg'))
def fetch(p):
 u,path=p
 if path.exists():return True
 try:path.write_bytes(urlopen(u,timeout=25).read());return True
 except Exception as e:print(path.name,str(e),flush=True);return False
with ThreadPoolExecutor(8) as pool:print('assets saved',sum(pool.map(fetch,urls)),'/',len(urls),flush=True)
