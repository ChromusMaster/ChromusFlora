import copy
import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'flora/src/main/resources'
TARGET = ROOT / 'versions/26.3/src/main/resources'


def transform(value):
    if isinstance(value, list):
        return [transform(v) for v in value]
    if not isinstance(value, dict):
        return value
    if value.get('type') == 'minecraft:simple_state_provider':
        return transform(value['state'])
    if 'Name' in value:
        return {'id': value['Name'], **({'properties': value['Properties']} if 'Properties' in value else {})}
    result = {k: transform(v) for k, v in value.items()}
    if 'config' in result and 'type' in result:
        result = {'type': result['type'], **result['config']}
    return result


def loot(value):
    if isinstance(value, list):
        return [loot(v) for v in value]
    if not isinstance(value, dict):
        return value
    if value.get('condition') == 'minecraft:match_tool':
        predicate = value.get('predicate', {})
        if predicate.get('items') == 'minecraft:shears':return 'minecraft:tool/can_shear'
        if 'minecraft:enchantments' in predicate.get('predicates', {}):return 'minecraft:tool/can_silk_touch'
    result = {k: loot(v) for k, v in value.items()}
    if 'conditions' in result:
        terms = result.pop('conditions')
        if terms:result['condition'] = terms[0] if len(terms) == 1 else {'type': 'minecraft:all_of', 'terms': terms}
    if 'condition' in result and isinstance(result['condition'], str):
        result['type'] = result.pop('condition')
    if 'function' in result:result['type'] = result.pop('function')
    if 'functions' in result:result['modifier'] = result.pop('functions')
    if result.get('type') == 'minecraft:block_state_property':
        result['type'] = 'minecraft:match_block'
        result['blocks'] = result.pop('block')
        result['state'] = result.pop('properties')
    return result


def generate():
    if TARGET.exists():shutil.rmtree(TARGET)
    native = json.loads((ROOT / 'atelier/vanilla-biome-reference-26.3.json').read_text())
    catalog = json.loads((SOURCE / 'chromusflora/catalog.json').read_text())
    biomes = {b['id']: b for b in catalog['biomes']}
    for path in SOURCE.rglob('*.json'):
        relative = path.relative_to(SOURCE).as_posix()
        data = json.loads(path.read_text())
        if '/worldgen/configured_feature/' in relative:
            relative = relative.replace('/configured_feature/', '/feature/')
            data = transform(data)
        elif '/worldgen/placed_feature/' in relative:
            data = transform(data)
        elif '/worldgen/biome/' in relative and relative.startswith('data/chromusflora/'):
            base = copy.deepcopy(native[biomes[path.stem]['vanilla'].split(':')[1]])
            base['attributes'] = {k: v for k, v in base.get('attributes', {}).items() if not k.startswith('minecraft:audio/')}
            base['attributes'].update(data['attributes'])
            base['effects'].update(data['effects'])
            for stage in base['features']:
                stage[:] = [f for f in stage if not any(word in f for word in ['tree', 'fungi', 'huge_mushroom', 'bamboo_vegetation', 'bamboo_light', 'mangrove'])]
            while len(base['features']) < 11:base['features'].append([])
            base['features'][9].append('chromusflora:biomes/' + path.stem)
            data = base
        elif '/loot_table/' in relative:
            data = loot(data)
        elif '/advancement/' in relative:
            for criterion in data.get('criteria', {}).values():
                if criterion.get('trigger') == 'minecraft:recipe_unlocked':
                    criterion['conditions']['recipes'] = criterion['conditions'].pop('recipe')
        else:
            continue
        target = TARGET / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(data, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')


if __name__ == '__main__':
    generate()
