"""Validate the translated passive archive before including it in the UI glossary.

Translations retain the archived source version. A source fingerprint prevents a
data refresh from silently pairing changed English effects with old Korean text.
"""
from collections import Counter
from hashlib import sha256
import json
from pathlib import Path
import re


def passive_source(champion):
    variants = [v for f in champion['formulas'] if f['slot'] == 'P' for v in f['variants']]
    return {'version': champion['formulaVersion'], 'variants': [
        {'name': v['name'], 'effects': v.get('effects', [])} for v in variants
    ]}


def fingerprint(source):
    return sha256(json.dumps(source, ensure_ascii=False, sort_keys=True,
                             separators=(',', ':')).encode()).hexdigest()


def numbers(text):
    return Counter(re.findall(r'\d+(?:\.\d+)?', text))


def build_passives(root):
    root = Path(root)
    data = root / 'dist/data'
    locales = root / 'scripts/locales'
    translations = {}
    for path in sorted(locales.glob('passives-ko-*.json')):
        part = json.loads(path.read_text())
        assert not translations.keys() & part.keys(), f'Duplicate passive translations: {path}'
        translations.update(part)
    locks = json.loads((locales / 'passives-source.json').read_text())
    result = {}
    paragraphs = 0
    for item in json.loads((data / 'index.json').read_text())['champions']:
        champion = json.loads((data / (item['id'] + '.json')).read_text())
        source = passive_source(champion)
        if not source['variants']:
            continue
        id_ = champion['id']
        assert locks.get(id_) == fingerprint(source), f'Passive source changed; review translation: {id_}'
        translated = translations[id_]
        assert len(translated) == len(source['variants']), f'Passive variant count: {id_}'
        for original, target in zip(source['variants'], translated):
            assert target['name'].strip(), f'Empty passive name: {id_}'
            assert len(target['effects']) == len(original['effects']), f'Passive paragraph count: {id_}'
            for n, (english, korean) in enumerate(zip(original['effects'], target['effects'])):
                assert korean.strip(), f'Empty passive description: {id_} {n}'
                assert numbers(english) == numbers(korean), f'Passive numeric mismatch: {id_} {n}'
                allowed = r'(?<![A-Za-z])(?:AP|AD|H-28G|H-28Q|CH-2|CH-3X)(?![A-Za-z])'
                assert not re.search(r'[A-Za-z]{2,}', re.sub(allowed, '', korean)), f'Untranslated passive: {id_} {n}'
                paragraphs += 1
        result[id_] = {'version': source['version'], 'variants': translated}
    assert set(result) == set(translations) == set(locks), 'Unused or missing passive translations'
    print(f'Passive archive: {len(result)} champions, {paragraphs} Korean paragraphs; source and numbers checked')
    return result
