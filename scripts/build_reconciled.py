"""Package reviewed ability data into the existing, locale-specific requests.

Run the five reviewed group generators before this script. --record-review is
only for a completed manual review; ordinary rebuilds reject changed inputs.
"""
from pathlib import Path
import argparse
import hashlib
import json
from reconcile_stats import reconcile_stats

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'dist/data'
REVIEWS = ROOT / 'scripts/reconciled'
VERSION, PATCH, REVIEW_DATE = '16.22.1', '26.22', '2026-11-07'


def read(path):
    return json.loads(path.read_text())


def write(path, obj):
    path.write_text(json.dumps(obj, ensure_ascii=False, separators=(',', ':')))


def digest(obj):
    return hashlib.sha256(json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def inputs():
    result = {}
    for c in read(DATA / 'index.json')['champions']:
        for lang, prefix in [('ko', ''), ('en', 'en/')]:
            d = read(DATA / (prefix + c['id'] + '.json'))
            recent = [h for h in d['history'] if tuple(map(int, h['patch'].split('.'))) > (25, 15)]
            result[lang + '/' + c['id']] = digest({k: d[k] for k in ['version', 'stats', 'spells', 'passive', 'formulas']} | {'history': recent})
    return result


def load_profiles():
    profiles = {}
    for number in range(1, 6):
        group = read(REVIEWS / f'group-{number}.json')
        assert not (profiles.keys() & group.keys()), 'Duplicate champion in review groups'
        profiles.update(group)
    return profiles


def apply_review(profiles):
    """Layer newly reviewed rows over the five original through-26.21 profiles."""
    updates = read(REVIEWS / 'updates-26.22.json')
    for champion, slots in updates.items():
        for slot, update in slots.items():
            skill = profiles[champion]['skills'][slot]
            rows = skill['rows']
            labels = {r['attribute']['en'] for r in rows}
            drop = set(update['drop'])
            if not drop <= labels:
                raise ValueError((champion, slot, 'Missing replaced rows', drop - labels))
            if 'minionLabel' in update:
                # The archive gives the normal and minion DoT the same English label.
                hits = [r for r in rows if r['attribute']['en'] == 'Field Magic Damage per Second']
                if len(hits) != 2 or not hits[1]['value']['en'].startswith('8 / 14'):
                    raise ValueError('Mel E minion damage row changed')
                hits[1]['attribute'] = update['minionLabel']
            kept = [r for r in rows if r['attribute']['en'] not in drop]
            existing = {r['attribute']['en'] for r in kept}
            for row in update['rows']:
                if row['attribute']['en'] in existing:
                    raise ValueError((champion, slot, 'Duplicate reviewed row', row['attribute']))
                existing.add(row['attribute']['en'])
            skill['rows'] = update['rows'] + kept
            for field in ('notes', 'effects', 'status'):
                if field in update:
                    skill[field] = update[field]
            references = [ref for r in update['rows'] for ref in r['sources']]
            if update.get('tooltipSource'):
                references.append({'patch': PATCH, 'date': REVIEW_DATE,
                                   'url': read(DATA / 'en' / (champion + '.json'))['source']})
            skill['sources'] = list({s['url']: s for s in skill['sources'] + references}.values())

    for champion in ('Shyvana', 'Locke'):
        history = read(DATA / 'en' / (champion + '.json'))['history']
        release = next(h for h in history if h.get('release'))
        source = {k: release[k] for k in ('patch', 'date', 'url')}
        for skill in profiles[champion]['skills'].values():
            if source not in skill['sources']:
                skill['sources'].append(source)


def apply_card_text(profiles):
    """Use gameplay wording for cards while retaining the original reviews and history."""
    for champion, slots in read(REVIEWS / 'card-text.json').items():
        for slot, edits in slots.items():
            skill = profiles[champion]['skills'][slot]
            effects = edits.get('effects', {})
            if effects:
                rewritten = {'ko': [], 'en': []}
                pairs = zip(skill['effects']['ko'], skill['effects']['en'], strict=True)
                for ko, en in pairs:
                    copy = effects.get(en, {'ko': ko, 'en': en})
                    if copy is not None:
                        for lang in rewritten:
                            rewritten[lang].append(copy[lang])
                skill['effects'] = rewritten
            rows = []
            for row in skill['rows']:
                key = row['attribute']['en'] + ' | ' + row['value']['en']
                copy = edits.get('rows', {}).get(key, {})
                if copy is not None:
                    rows.append({**row, **copy})
            skill['rows'] = rows


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--record-review', action='store_true')
    args = parser.parse_args()
    index = read(DATA / 'index.json')
    assert index['meta']['version'] == VERSION and index['meta']['patch'] == PATCH
    profiles = load_profiles()
    assert set(profiles) == {c['id'] for c in index['champions']}
    apply_review(profiles)
    apply_card_text(profiles)
    distances = read(REVIEWS / 'spell-distances.json')
    if distances['patch'] != PATCH:
        raise ValueError('Review spell distances for the new patch before publishing')
    for champion, slots in distances['skills'].items():
        for key in slots:
            if key not in profiles[champion]['skills'] or key == 'P':
                raise ValueError((champion, key, 'Invalid distance review'))
    revisions = inputs()
    lock = REVIEWS / 'source-revisions.json'
    if not args.record_review and (not lock.exists() or read(lock) != revisions):
        raise RuntimeError('Official input changed: review the affected abilities before refreshing the review lock.')
    counts = {'champions': len(profiles), 'abilities': 0, 'rows': 0, 'patchRows': 0, 'derivedRows': 0, 'baselineRows': 0, 'partialAbilities': 0, 'statFields': 0, 'statConflicts': 0}
    for champion, profile in profiles.items():
        assert set(profile['skills']) == set('PQWER'), champion
        en = read(DATA / 'en' / (champion + '.json'))
        stats = reconcile_stats(en)
        counts['statFields'] += len(stats['sources'])
        counts['statConflicts'] += len(stats['conflicts'])
        for skill in profile['skills'].values():
            counts['abilities'] += 1
            counts['partialAbilities'] += skill['status'] == 'partial'
            for row in skill['rows']:
                assert row['provenance'] in ('patch', 'derived', 'baseline'), champion
                assert all(isinstance(row[k][lang], str) and row[k][lang] for k in ('attribute', 'value') for lang in ('ko', 'en')), champion
                assert row['provenance'] == 'baseline' or row['sources'], (champion, row)
                counts['rows'] += 1
                counts[row['provenance'] + 'Rows'] += 1
        for lang, prefix in [('ko', ''), ('en', 'en/')]:
            path = DATA / (prefix + champion + '.json')
            d = read(path)
            skills = {}
            current_note = next((h['url'] for h in d['history'] if h['patch'] == PATCH), None)
            def local_sources(sources):
                # Use the matching article in the display language. Leave historical
                # source-language corrections (such as Elise Q in Korean) intact.
                return [{**source, 'url': current_note}
                        if current_note and source['patch'] == PATCH and '/news/game-updates/' in source['url']
                        else {**source, 'url': d['source']} if source['url'].endswith('/champion/' + champion + '.json')
                        else source for source in sources]

            for key, skill in profile['skills'].items():
                skills[key] = {'status': skill['status'], 'notes': skill['notes'][lang], 'sources': local_sources(skill['sources']),
                               'effects': skill['effects'][lang],
                               'rows': [{**row, 'sources': local_sources(row['sources']), 'attribute': row['attribute'][lang], 'value': row['value'][lang]} for row in skill['rows']]}
                distance = distances['skills'].get(champion, {}).get(key)
                if distance is not None:
                    # An empty list explicitly suppresses a raw cast parameter for this ability.
                    skills[key]['distance'] = {
                        'source': distance['source'],
                        'rows': [
                            {'label': row[lang],
                             'value': row['value'][lang] if isinstance(row['value'], dict) else row['value']}
                            for row in distance['rows']
                        ]
                    }
            d['details'] = {'version': VERSION, 'patch': PATCH, 'reviewedAt': REVIEW_DATE, 'skills': skills}
            d['effectiveStats'] = stats['stats']
            d['statConflicts'] = [{k: c[k] for k in ['field', 'value', 'dataDragon', 'patch', 'date', 'url']} for c in stats['conflicts']]
            growth = stats['sources'].get('attackdamageperlevel')
            if growth:
                d['attackDamageGrowth'].update(value=growth['value'], source=growth['url'], sourcePatch=growth['patch'])
            write(path, d)
    for prefix in ['', 'en/']:
        path = DATA / (prefix + 'index.json')
        d = read(path)
        d['meta']['reconciliation'] = {'fromPatch': '25.16', 'throughPatch': PATCH, 'reviewedAt': REVIEW_DATE, **counts}
        write(path, d)
    if args.record_review:
        write(lock, revisions)
    print(json.dumps(counts))


if __name__ == '__main__':
    main()
