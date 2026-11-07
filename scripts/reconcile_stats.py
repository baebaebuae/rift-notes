"""Resolve ordinary champion stats from Data Dragon and chronological patch notes.

Only exact stat labels are accepted: an ability's damage is never a base stat.
The raw Data Dragon stats remain intact for source comparisons.
"""
import copy
import re

BASE = {
    'health': 'hp', 'hp': 'hp', 'mana': 'mp', 'armor': 'armor', 'ar': 'armor',
    'magic resistance': 'spellblock', 'magic resist': 'spellblock',
    'attack damage': 'attackdamage', 'ad': 'attackdamage',
    'attack speed': 'attackspeed', 'as': 'attackspeed',
    'move speed': 'movespeed', 'movement speed': 'movespeed',
    'health regeneration': 'hpregen', 'health regen': 'hpregen',
    'health per 5': 'hpregen', 'mana regeneration': 'mpregen',
    'mana regen': 'mpregen', 'attack speed ratio': 'attackspeedratio',
}


def reconcile_stats(champion):
    result = copy.deepcopy(champion['stats'])
    growth = champion.get('attackDamageGrowth', {}).get('value')
    result['attackdamageperlevel'] = growth
    evidence = {}
    for event in reversed(champion['history']):
        if tuple(map(int, event['patch'].split('.'))) <= (25, 15):
            continue
        for change in event['changes']:
            if change['slot'] not in ('S', 'A') or ':' not in change['text']:
                continue
            attribute, value = change['text'].split(':', 1)
            if not re.search('⇒|→', value):
                continue
            attribute = re.sub(r'^(?:base|starting)\s+', '', attribute.lower().strip())
            growing = bool(re.search(r'\s+(?:growth|per level)$', attribute))
            attribute = re.sub(r'\s+(?:growth|per level)$', '', attribute)
            field = BASE.get(attribute)
            if not field:
                continue
            after = re.split('⇒|→', value)[-1].strip()
            numbers = re.findall(r'\d+(?:\.\d+)?|(?<!\d)\.\d+', after)
            updates = {}
            if len(numbers) == 2 and '+' in after and re.search(r'/\s*level', after, re.I):
                updates[field] = float(numbers[0])
                updates[('attackspeed' if field == 'attackspeedratio' else field) + 'perlevel'] = float(numbers[1])
            elif len(numbers) == 1 and re.fullmatch(r'[+]?([\d.]+)\s*%?\s*(?:/\s*level|per level)?', after, re.I):
                per_level = growing or bool(re.search(r'/\s*level|per level', after, re.I))
                updates[field + ('perlevel' if per_level else '')] = float(numbers[0])
            for key, number in updates.items():
                result[key] = number
                evidence[key] = {'value': number, 'patch': event['patch'], 'date': event['date'], 'url': event['url'], 'text': change['text']}
    conflicts = [{**source, 'field': field, 'dataDragon': champion['stats'].get(field)}
                 for field, source in evidence.items()
                 if field != 'attackdamageperlevel' and field in champion['stats']
                 and source['value'] != champion['stats'][field]]
    # A historical change is not evidence that the newer official snapshot is
    # wrong. Preserve current Data Dragon values on an unresolved conflict;
    # only the separately diagnosed all-zero AD-growth field is reconstructed.
    for conflict in conflicts:
        result[conflict['field']] = conflict['dataDragon']
        conflict['resolution'] = 'current-data-dragon'
    return {'stats': result, 'sources': evidence, 'conflicts': conflicts}
