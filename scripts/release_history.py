"""Riot sometimes gives a new kit its own section outside the champion list."""
import re

RELEASES = {
    ('26.6', 'patch-shyvana-update'): 'Shyvana',
    ('26.13', 'patch-locke'): 'Locke',
}


def release_events(soup, patch, date, url):
    events = []
    for heading in soup.find_all('h2', id=True):
        champion = RELEASES.get((patch, heading['id']))
        if not champion:
            continue
        title = slot = None
        changes = []
        for node in heading.find_all_next(['h2', 'h4', 'li']):
            if node.name == 'h2':
                break
            if node.name == 'h4':
                title = node.get_text(' ', strip=True)
                match = re.match(r'(Passive|기본 지속 효과|[QWER])\s*[-–]', title, re.I)
                slot = (match[1] if match[1] in 'QWER' else 'P') if match else None
            elif slot and not node.find('a', href=True):
                # Nested list items contain separate stack rules.
                text = ' '.join(s.strip() for s in node.find_all(string=True)
                                if s.find_parent('li') is node and s.strip())
                if text:
                    changes.append({'slot': slot, 'title': title, 'text': text, 'kind': 'adjust'})
        if {c['slot'] for c in changes} != set('PQWER'):
            raise ValueError(f'Incomplete {patch} release section for {champion}')
        events.append({'champion': champion, 'patch': patch, 'date': date, 'articleDate': date,
                       'url': url + '#' + heading['id'], 'isHotfix': False, 'release': True,
                       'section': heading.get_text(' ', strip=True), 'changes': changes})
    return events


def normalize_26_22(champion, changes, classify):
    """Riot joins some adjustments with <br>, and splits Zaahen's arrow across two items."""
    continuation = {
        'Corki': ('Big One Damage', '거대한 미사일 피해량'),
        'Locke': ('Maximum Stack Damage', '최대 중첩 피해량'),
        'Rumble': ('Maximum Damage Ability Power Ratio', '최대 피해량 주문력 계수'),
    }
    result = []
    for change in changes:
        line = change['text'].strip()
        if champion == 'Zaahen' and line.startswith(('⇒', '→')) and result:
            result[-1]['text'] += ' ' + line
            result[-1]['kind'] = classify(result[-1]['text'])
            continue
        parts = [line]
        for label in continuation.get(champion, ()):
            start = line.lower().find(label.lower())
            if start > 0:
                parts = [line[:start].strip(), line[start:]]
                break
        for text in parts:
            kind = classify(text)
            if champion in ('AurelionSol', 'Rumble') and change['slot'] in ('E', 'R'):
                kind = 'buff'
            if champion == 'Mel' and change['slot'] == 'P' and ('minion' in text.lower() or '미니언' in text):
                kind = 'buff'
            result.append({**change, 'text': text, 'kind': kind})
    return result
