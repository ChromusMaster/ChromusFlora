import json
from pathlib import Path
from joinery import box

ROOT = Path(__file__).resolve().parents[1]
RES = ROOT / 'flora/src/main/resources'
ASSETS = RES / 'assets/chromusflora'
DATA = RES / 'data/chromusflora'


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')


def generate():
    trees = json.loads((RES / 'chromusflora/catalog.json').read_text())['trees']
    ids = []
    for tree in trees:
        species = tree['id']
        name = species + '_boat'
        item = 'chromusflora:' + name
        ids.append(item)
        planks = 'chromusflora:' + species + '_planks'
        write(DATA / f'recipe/{name}.json', {'type': 'minecraft:crafting_shaped', 'category': 'misc', 'group': 'boat',
              'pattern': ['# #', '###'], 'key': {'#': planks}, 'result': {'id': item, 'count': 1}})
        write(DATA / f'advancement/recipes/{name}.json', {
            'parent': 'minecraft:recipes/root',
            'criteria': {'has_material': {'trigger': 'minecraft:inventory_changed', 'conditions': {'items': [{'items': planks}]}},
                         'has_the_recipe': {'trigger': 'minecraft:recipe_unlocked', 'conditions': {'recipe': item}}},
            'requirements': [['has_material', 'has_the_recipe']], 'rewards': {'recipes': [item]}})
        elements = [box((0,0,2),(16,2,14)), box((0,2,2),(16,6,4)), box((0,2,12),(16,6,14)),
                    box((0,2,4),(2,6,12)), box((14,2,4),(16,6,12)), box((6,2,4),(8,3,12))]
        write(ASSETS / f'models/item/{name}.json', {'parent': 'minecraft:block/block',
              'textures': {'wood': 'chromusflora:block/wood/' + species + '/planks', 'particle': 'chromusflora:block/wood/' + species + '/planks'},
              'elements': elements, 'display': {'gui': {'rotation': [30,225,0], 'translation': [0,2,0], 'scale': [0.9,0.9,0.9]},
              'ground': {'rotation': [0,0,0], 'translation': [0,3,0], 'scale': [0.5,0.5,0.5]}}})
        write(ASSETS / f'items/{name}.json', {'model': {'type': 'minecraft:model', 'model': 'chromusflora:item/' + name}})
    for kind, name in [('item','boats'),('entity_type','boat')]:
        write(RES / f'data/minecraft/tags/{kind}/{name}.json', {'replace': False, 'values': ids})
    for language in ['en_us', 'pt_br']:
        path = ASSETS / f'lang/{language}.json'
        strings = json.loads(path.read_text())
        for tree in trees:
            species = tree['id']
            label = strings['block.chromusflora.' + species + '_planks']
            label = label.removesuffix(' Planks') if language == 'en_us' else label.removeprefix('Tábuas de ')
            value = label + ' Boat' if language == 'en_us' else 'Barco de ' + label
            strings['item.chromusflora.' + species + '_boat'] = value
            strings['entity.chromusflora.' + species + '_boat'] = value
        write(path, strings)
    for folder in ['recipe', 'advancement/recipes']:
        (DATA / f'{folder}/boat.json').unlink(missing_ok=True)
        (ROOT / f'versions/26.3/src/main/resources/data/chromusflora/{folder}/boat.json').unlink(missing_ok=True)
    return len(trees)


if __name__ == '__main__':
    print('Boat families:', generate())
