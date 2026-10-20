"""Build the English snapshot from version-matched official Riot sources.

The Korean snapshot supplies unchanged numeric formulas/stat provenance. Display
text and patch history come from English Data Dragon and official English notes;
unavailable patch pages are reported rather than replaced with Korean text.
Run: python -m pip install beautifulsoup4 && python scripts/collect_english.py
"""
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen
from bs4 import BeautifulSoup
import hashlib
import json
import os
import re
import time

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'dist/data'
OUT = DATA / 'en'
CACHE = Path(os.environ.get('RIFT_CACHE', '/workspace/scratch/rift-cache'))
OUT.mkdir(parents=True, exist_ok=True)
CACHE.mkdir(parents=True, exist_ok=True)
KO_INDEX = json.loads((DATA / 'index.json').read_text())
VERSION = KO_INDEX['meta']['version']
BASE = 'https://ddragon.leagueoflegends.com/cdn/' + VERSION


def fetch(url):
    path = CACHE / (hashlib.sha256(url.encode()).hexdigest() + '.cache')
    if path.exists():
        return path.read_bytes()
    error = path.with_suffix('.missing')
    if error.exists() and time.time() - error.stat().st_mtime < 86400:
        raise RuntimeError('Recent collection failure: ' + error.read_text())
    for attempt in range(2):
        try:
            request = Request(url, headers={'User-Agent': 'RiftNotes/1.0 (personal research)'})
            with urlopen(request, timeout=25) as response:
                content = response.read()
            path.write_bytes(content)
            return content
        except HTTPError as exc:
            if exc.code in (403, 404):
                error.write_text(str(exc))
                raise
            if attempt:
                raise
        except Exception:
            if attempt:
                raise
    raise RuntimeError('Unable to collect ' + url)


def write(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, separators=(',', ':')))


def normalized(value):
    return re.sub(r'[^\w]', '', value).lower()


def patch_key(value):
    return tuple(map(int, value.split('.')))


NAMES = {}
for champion in KO_INDEX['champions']:
    for name in (champion['id'], champion['englishName']):
        NAMES[normalized(name)] = champion['id']
NAMES.update({'wukong': 'MonkeyKing', 'nunu': 'Nunu', 'nunuandwillump': 'Nunu', 'renataglasc': 'Renata'})


def slot(label):
    label = re.sub(r'^\s*(?:new|updated)\s+', '', label, flags=re.I).lstrip('> ')
    label = re.sub(r'^(?:human|spider|cougar)\s+', '', label, flags=re.I)
    match = re.match(r'([QWER])(?=[QWER]?(?:\d|\s|\(|\+|[-–—:]))', label, re.I)
    if match:
        return match[1].upper()
    if re.search(r'\bpassive\b|^P\s*[-–—:]', label, re.I):
        return 'P'
    if re.search(r'base stat|^stats$', label, re.I):
        return 'S'
    return 'A'


def kind(text):
    if not re.search('⇒|→', text):
        return 'fix' if re.search(r'\bbug|\bfix', text, re.I) else 'adjust'
    before, after = re.split('⇒|→', text, maxsplit=1)
    numbers = lambda value: [float(n) for n in re.findall(r'(?<!\d)-?\d+(?:\.\d+)?', value)]
    left, right = numbers(before.split(':')[-1]), numbers(after)
    if not left or len(left) != len(right):
        return 'adjust'
    directions = {1 if b > a else -1 for a, b in zip(left, right) if a != b}
    if len(directions) != 1:
        return 'adjust'
    direction = next(iter(directions))
    if re.search(r'cooldown|cost|recharge time', before, re.I):
        direction *= -1
    return 'buff' if direction > 0 else 'nerf'


def section_date(section, article_date):
    match = re.search(r'\b(\d{1,2})/(\d{1,2})/(20\d{2})\b', section)
    if match:
        month, day, year = map(int, match.groups())
        return f'{year:04d}-{month:02d}-{day:02d}'
    match = re.search(r'\b(20\d{2})-(\d{1,2})-(\d{1,2})\b', section)
    if match:
        year, month, day = map(int, match.groups())
        return f'{year:04d}-{month:02d}-{day:02d}'
    months = 'January February March April May June July August September October November December'.split()
    match = re.search(r'\b(' + '|'.join(months) + r')\s+(\d{1,2})(?:st|nd|rd|th)?(?:,?\s+(20\d{2}))?', section, re.I)
    if match:
        year = int(match[3] or article_date[:4])
        month = next(i for i, value in enumerate(months, 1) if value.lower() == match[1].lower())
        return f'{year:04d}-{month:02d}-{int(match[2]):02d}'
    # Some older notes write "6/9 Mid-Patch Update" and omit the year.
    match = re.search(r'\b(\d{1,2})/(\d{1,2})\b', section)
    if match and article_date:
        return f'{article_date[:4]}-{int(match[1]):02d}-{int(match[2]):02d}'
    return article_date


def collect_patch(entry):
    patch = entry['patch']
    url = entry['url'].replace('/ko-kr/', '/en-us/')
    try:
        soup = BeautifulSoup(fetch(url), 'html.parser')
    except Exception as exc:
        return {'patch': patch, 'url': url, 'error': str(exc)}
    for element in soup(['script', 'style', 'nav', 'footer']):
        element.decompose()
    published = soup.find('time')
    date = published.get('datetime', '')[:10] if published else ''
    events = []
    for heading in soup.find_all('h3'):
        heading_text = re.sub(r'^\s*(?:new|updated)\s+', '', heading.get_text(' ', strip=True), flags=re.I)
        # Reused article anchors are not reliable champion identifiers: Riot has
        # used champion anchors for unrelated item and April Fools headings.
        champion = NAMES.get(normalized(heading_text))
        if not champion:
            continue
        previous = heading.find_previous('h2')
        section = previous.get_text(' ', strip=True) if previous else ''
        if re.search(r'arena|aram|classic|swarm|urf|swiftplay|quickplay|nexus blitz|ultimate spellbook|doom bots|hexakill|one for all|april fool', section, re.I):
            continue
        if re.search(r'mid.patch|hotfix', section, re.I):
            # Riot sometimes nests dated hotfix headings as h4 under a generic h2.
            for nearby in heading.find_all_previous(['h2', 'h3', 'h4']):
                if nearby is previous:
                    break
                text = nearby.get_text(' ', strip=True)
                if re.search(r'\b\d{1,2}/\d{1,2}/20\d{2}\b|\b(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2}', text, re.I):
                    section = text if re.search(r'mid.patch|hotfix', text, re.I) else section + ' · ' + text
                    break
        block = heading.find_parent(class_='patch-change-block') or heading.parent
        changes = []
        title = 'General'
        started = False
        for node in block.select('h2, h3, h4, li, div.attribute-change'):
            if node is heading:
                started = True
                continue
            if not started:
                continue
            if node.name in ('h2', 'h3'):
                break
            if node.name == 'h4':
                title = node.get_text(' ', strip=True)
                if re.search(r'arena|aram|classic|swarm|urf|swiftplay|quickplay|clash schedule|known issues', title, re.I):
                    break
                if re.search(r'mid.patch|hotfix', section, re.I) and re.fullmatch(r'bugfixes|bug fixes', title, re.I):
                    break
                if re.search(r'\b\d{1,2}/\d{1,2}/20\d{2}\b', title):
                    break
                if champion != 'Ornn' and any('/img/item/' in image.get('src', '') for image in node.find_all('img')):
                    break
                continue
            if node.find_parent('li'):
                continue
            if node.name == 'div':
                attribute = node.select_one('.attribute')
                before = node.select_one('.attribute-before')
                after = node.select_one('.attribute-after')
                text = (attribute.get_text(' ', strip=True) + ': ' if attribute else '')
                text += (before.get_text(' ', strip=True) + ' ⇒ ' if before else '')
                text += after.get_text(' ', strip=True) if after else node.get_text(' ', strip=True)
            else:
                text = node.get_text(' ', strip=True)
            text = ' '.join(text.split())
            if text:
                changes.append({'slot': slot(title), 'title': title, 'text': text, 'kind': kind(text)})
        if changes:
            events.append({'champion': champion, 'patch': patch,
                           'date': section_date(section, date), 'articleDate': date,
                           'url': url + '#' + heading.get('id', 'patch-champions'),
                           'changes': changes, 'section': section,
                           'isHotfix': bool(re.search(r'mid.patch|hotfix', section, re.I))})
    return {'patch': patch, 'date': date, 'url': url, 'events': events}


def main():
    official_index = json.loads(fetch(BASE + '/data/en_US/champion.json'))['data']
    expected = {champion['id'] for champion in KO_INDEX['champions']}
    if set(official_index) != expected:
        raise RuntimeError('English champion index does not match the existing snapshot')
    for key, champion in official_index.items():
        NAMES[normalized(champion['name'])] = key

    patches = []
    source_patches = json.loads((DATA / 'patches.json').read_text())['patches']
    with ThreadPoolExecutor(max_workers=8) as pool:
        futures = [pool.submit(collect_patch, entry) for entry in source_patches]
        for count, future in enumerate(as_completed(futures), 1):
            patches.append(future.result())
            if count % 20 == 0:
                print(f'English patches {count}/{len(source_patches)}', flush=True)
    patches.sort(key=lambda entry: patch_key(entry['patch']), reverse=True)
    histories = {key: [] for key in expected}
    for patch in patches:
        for event in patch.get('events', []):
            champion = event.pop('champion')
            histories[champion].append(event)
    for history in histories.values():
        history.sort(key=lambda entry: (patch_key(entry['patch']), entry['date']), reverse=True)
    write(OUT / 'patches.json', {'patches': [{key: value for key, value in patch.items() if key != 'events'} for patch in patches]})

    name_map = {}
    summaries = []
    def collect_champion(key):
        url = BASE + '/data/en_US/champion/' + key + '.json'
        english = json.loads(fetch(url))['data'][key]
        korean = json.loads((DATA / (key + '.json')).read_text())
        result = dict(korean)
        for field in ('name', 'title', 'tags', 'partype', 'passive', 'spells', 'info', 'image'):
            result[field] = english[field]
        result['englishName'] = english['name']
        result['source'] = url
        result['history'] = histories[key]
        result['attackDamageGrowth'] = {**korean['attackDamageGrowth'], 'method': 'Archived baseline with subsequent official stat changes applied'}
        # All output is localized; numeric archived formulas are intentionally unchanged.
        if re.search('[가-힣]', json.dumps(result, ensure_ascii=False)):
            raise RuntimeError('Unexpected Korean text remains in English champion ' + key)
        write(OUT / (key + '.json'), result)
        mapping = [{'slot': 'P', 'en': english['passive']['name'], 'ko': korean['passive']['name']}]
        mapping.extend({'slot': slot, 'en': a['name'], 'ko': b['name']} for slot, a, b in zip('QWER', english['spells'], korean['spells']))
        summary = {'id': key, 'name': english['name'], 'title': english['title'],
                   'tags': english['tags'], 'englishName': english['name'],
                   'positions': korean['positions'], 'patchCount': len(histories[key]),
                   'latestPatch': histories[key][0]['patch'] if histories[key] else None}
        return summary, mapping
    with ThreadPoolExecutor(max_workers=8) as pool:
        futures = {pool.submit(collect_champion, key): key for key in official_index}
        for count, future in enumerate(as_completed(futures), 1):
            summary, mapping = future.result()
            summaries.append(summary)
            name_map[summary['id']] = mapping
            if count % 35 == 0:
                print(f'English champions {count}/{len(official_index)}', flush=True)
    summaries.sort(key=lambda champion: champion['name'].casefold())
    valid = [patch for patch in patches if patch.get('events')]
    meta = {'version': VERSION, 'patch': KO_INDEX['meta']['patch'], 'locale': 'en_US',
            'collectedAt': datetime.now(timezone.utc).isoformat(),
            'championCount': len(summaries), 'patchCount': len(valid),
            'historyCount': sum(map(len, histories.values())),
            'earliestPatch': valid[-1]['patch'] if valid else None,
            'latestPatch': valid[0]['patch'] if valid else None,
            'coverage': "Summoner's Rift champion adjustments in official English patch-note champion sections. Separate bug-fix sections, other game modes and unavailable documents may not be included. English and Korean source coverage can differ.",
            'missingPatches': [patch['patch'] for patch in patches if not patch.get('events')],
            'failures': []}
    write(OUT / 'index.json', {'meta': meta, 'champions': summaries})
    write(Path('/workspace/scratch/rift-en-ko-skill-names.json'), name_map)
    print(json.dumps(meta, ensure_ascii=False), flush=True)


if __name__ == '__main__':
    main()
