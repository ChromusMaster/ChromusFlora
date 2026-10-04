import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RES = ROOT / 'flora/src/main/resources'
ASSETS = RES / 'assets/chromusflora'
DATA = RES / 'data/chromusflora'


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')


def tag(kind, name, values, namespace='minecraft'):
    path = RES / f'data/{namespace}/tags/{kind}/{name}.json'
    old = json.loads(path.read_text())['values'] if path.exists() else []
    write(path, {'replace': False, 'values': sorted(set(old + values))})


def shaped(name, pattern, keys, result, count=1, group=None):
    write(DATA / f'recipe/{name}.json', {'type': 'minecraft:crafting_shaped', 'category': 'building',
          'pattern': pattern, 'key': keys, 'result': {'id': result, 'count': count},
          **({'group': group, 'category': 'misc'} if group else {})})


def generate():
    trees = json.loads((RES / 'chromusflora/catalog.json').read_text())['trees']
    for tree in trees:
        species = tree['id']
        plank = 'chromusflora:block/wood/' + species + '/planks'
        names = [species + '_wood', 'stripped_' + species + '_wood']
        for name, texture in zip(names, ['bark', 'stripped']):
            material = 'chromusflora:block/wood/' + species + '/' + texture
            write(ASSETS / f'models/block/{name}.json', {'parent': 'minecraft:block/cube_column', 'textures': {'side': material, 'end': material}})
            write(ASSETS / f'blockstates/{name}.json', {'variants': {
                'axis=y': {'model': 'chromusflora:block/' + name},
                'axis=x': {'model': 'chromusflora:block/' + name, 'x': 90, 'y': 90},
                'axis=z': {'model': 'chromusflora:block/' + name, 'x': 90}}})
            log = name.removesuffix('_wood') + '_log'
            shaped(name, ['##', '##'], {'#': 'chromusflora:' + log}, 'chromusflora:' + name, 3)
        door = species + '_door'
        variants = {}
        for facing, angle in [('east', 0), ('south', 90), ('west', 180), ('north', 270)]:
            for half, section in [('lower', 'bottom'), ('upper', 'top')]:
                for hinge in ['left', 'right']:
                    for opened in [False, True]:
                        suffix = section + '_' + hinge + ('_open' if opened else '')
                        rotation = (angle + ((90 if hinge == 'left' else 270) if opened else 0)) % 360
                        variants[f'facing={facing},half={half},hinge={hinge},open={str(opened).lower()}'] = {'model': 'chromusflora:block/' + door + '_' + suffix, 'y': rotation}
                        write(ASSETS / f'models/block/{door}_{suffix}.json', {'parent': 'minecraft:block/door_' + suffix, 'textures': {'bottom': 'chromusflora:block/door/' + species + '/bottom', 'top': 'chromusflora:block/door/' + species + '/top'}})
        write(ASSETS / f'blockstates/{door}.json', {'variants': variants})
        trapdoor = species + '_trapdoor'
        for suffix in ['bottom', 'top', 'open']:
            write(ASSETS / f'models/block/{trapdoor}_{suffix}.json', {'parent': 'minecraft:block/template_orientable_trapdoor_' + suffix, 'textures': {'texture': 'chromusflora:block/trapdoor/' + species + '/main'}})
        variants = {}
        for facing, angle in [('north', 0), ('east', 90), ('south', 180), ('west', 270)]:
            for half in ['bottom', 'top']:
                for opened in [False, True]:
                    value = {'model': 'chromusflora:block/' + trapdoor + '_' + ('open' if opened else half), 'y': angle}
                    if opened and half == 'top':
                        value['x'] = 180
                        value['y'] = (angle + 180) % 360
                    variants[f'facing={facing},half={half},open={str(opened).lower()}'] = value
        write(ASSETS / f'blockstates/{trapdoor}.json', {'variants': variants})
        shaped(door, ['##', '##', '##'], {'#': 'chromusflora:' + species + '_planks'}, 'chromusflora:' + door, 3)
        shaped(trapdoor, ['###', '###'], {'#': 'chromusflora:' + species + '_planks'}, 'chromusflora:' + trapdoor, 2)
        furniture = [species + '_crafting_table', species + '_chest']
        for kind, pattern in [('crafting_table', ['##', '##']), ('chest', ['###', '# #', '###'])]:
            shaped(species + '_' + kind, pattern, {'#': 'chromusflora:' + species + '_planks'},
                   'chromusflora:' + species + '_' + kind, group=kind)
        for name in names + [door, trapdoor] + furniture:
            target = name + ('_bottom_left' if name == door else '_bottom' if name == trapdoor else '')
            write(ASSETS / f'items/{name}.json', {'model': {'type': 'minecraft:model', 'model': 'chromusflora:block/' + target}})
            conditions = [{'condition': 'minecraft:survives_explosion'}]
            if name == door:
                conditions.append({'condition': 'minecraft:block_state_property', 'block': 'chromusflora:' + door, 'properties': {'half': 'lower'}})
            write(DATA / f'loot_table/blocks/{name}.json', {'type': 'minecraft:block', 'pools': [{'rolls': 1, 'conditions': conditions, 'entries': [{'type': 'minecraft:item', 'name': 'chromusflora:' + name}]}]})
        for kind in ['item', 'block']:
            tag(kind, 'logs', ['chromusflora:' + n for n in names])
            tag(kind, species + '_logs', ['chromusflora:' + species + '_log', 'chromusflora:stripped_' + species + '_log'] + ['chromusflora:' + n for n in names], 'chromusflora')
            if tree['dimension'] != 'nether':tag(kind, 'logs_that_burn', ['chromusflora:' + n for n in names])
            for suffix in ['door', 'trapdoor']:tag(kind, 'wooden_' + suffix + 's', ['chromusflora:' + species + '_' + suffix])
        tag('block', 'mineable/axe', ['chromusflora:' + n for n in names + [door, trapdoor] + furniture])
    tag('item', 'planks', ['chromusflora:' + t['id'] + '_planks' for t in trees], 'chromusflora')
    shaped('boat', ['# #', '###'], {'#': '#chromusflora:planks'}, 'minecraft:oak_boat')
    for kind, pattern in [('crafting_table', ['##', '##']), ('chest', ['###', '# #', '###'])]:
        for folder in ['recipe', 'advancement/recipes']:
            (DATA / f'{folder}/{kind}.json').unlink(missing_ok=True)
        write(RES / f'data/minecraft/recipe/{kind}.json', {
            'type': 'minecraft:crafting_shaped', 'category': 'misc', 'group': kind,
            'pattern': pattern, 'key': {'#': {'fabric:type': 'fabric:difference',
            'base': '#minecraft:planks', 'subtracted': '#chromusflora:planks'}},
            'result': {'id': 'minecraft:' + kind, 'count': 1}})
        tag('item', kind + 's', ['chromusflora:' + tree['id'] + '_' + kind for tree in trees], 'chromusflora')
        write(DATA / f'recipe/vanilla_{kind}.json', {
            'type': 'minecraft:crafting_shapeless', 'category': 'misc', 'group': kind,
            'ingredients': ['#chromusflora:' + kind + 's'], 'result': {'id': 'minecraft:' + kind, 'count': 1}})
    for path in (DATA / 'recipe').glob('*.json'):
        recipe = json.loads(path.read_text())
        ingredient = recipe.get('ingredients', [recipe.get('key', {}).get('#')])[0]
        name = path.stem
        write(DATA / f'advancement/recipes/{name}.json', {
            'parent': 'minecraft:recipes/root',
            'criteria': {'has_material': {'trigger': 'minecraft:inventory_changed', 'conditions': {'items': [{'items': ingredient}]}},
                         'has_the_recipe': {'trigger': 'minecraft:recipe_unlocked', 'conditions': {'recipe': 'chromusflora:' + name}}},
            'requirements': [['has_material', 'has_the_recipe']], 'rewards': {'recipes': ['chromusflora:' + name]}})
    for language in ['en_us', 'pt_br']:
        path = ASSETS / f'lang/{language}.json'
        strings = json.loads(path.read_text())
        for tree in trees:
            species = tree['id']
            name = strings['block.chromusflora.' + species + '_planks']
            name = name.removesuffix(' Planks') if language == 'en_us' else name.removeprefix('Tábuas de ')
            for suffix, en, pt in [('wood', 'Wood', 'Madeira de'), ('door', 'Door', 'Porta de'), ('trapdoor', 'Trapdoor', 'Alçapão de'), ('crafting_table', 'Crafting Table', 'Bancada de Trabalho de'), ('chest', 'Chest', 'Baú de')]:
                strings['block.chromusflora.' + species + '_' + suffix] = name + ' ' + en if language == 'en_us' else pt + ' ' + name
            strings['block.chromusflora.stripped_' + species + '_wood'] = 'Stripped ' + name + ' Wood' if language == 'en_us' else 'Madeira Descascada de ' + name
        write(path, strings)
    import joinery
    joinery.generate()
    import runpy
    runpy.run_path(str(ROOT / "tools/generate-door-trapdoor-art.py"), run_name="__main__")


if __name__ == '__main__':
    generate()
