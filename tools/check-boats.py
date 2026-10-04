"""Check complete wood-boat resources for both versions without running Java."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RES = ROOT / 'flora/src/main/resources'


def read(path):
    return json.loads(path.read_text(encoding='utf-8'))


def verify():
    errors = []
    checks = 0
    def check(ok, label):
        nonlocal checks
        checks += 1
        if not ok:
            errors.append(label)
    species = [tree['id'] for tree in read(RES / 'chromusflora/catalog.json')['trees']]
    expected = {'chromusflora:' + name + '_boat' for name in species}
    shared = {p.relative_to(RES).as_posix(): p for p in RES.rglob('*') if p.is_file()}
    modern = ROOT / 'versions/26.3/src/main/resources'
    overlays = {p.relative_to(modern).as_posix(): p for p in modern.rglob('*') if p.is_file()}
    for version, files in [('26.2', shared), ('26.3', shared | overlays)]:
        for kind, tag in [('item', 'boats'), ('entity_type', 'boat')]:
            data = read(files[f'data/minecraft/tags/{kind}/{tag}.json'])
            check(data['replace'] is False and set(data['values']) == expected and len(data['values']) == len(species), version + ' additive boat tag ' + kind)
        check('data/chromusflora/recipe/boat.json' not in files, version + ' stale oak fallback')
        check('data/chromusflora/advancement/recipes/boat.json' not in files, version + ' stale fallback unlock')
        for name in species:
            item = 'chromusflora:' + name + '_boat'
            recipe = read(files[f'data/chromusflora/recipe/{name}_boat.json'])
            check(recipe == {'type': 'minecraft:crafting_shaped', 'category': 'misc', 'group': 'boat', 'pattern': ['# #', '###'], 'key': {'#': 'chromusflora:' + name + '_planks'}, 'result': {'id': item, 'count': 1}}, version + ' boat recipe ' + name)
            advancement = read(files[f'data/chromusflora/advancement/recipes/{name}_boat.json'])
            check(advancement['rewards']['recipes'] == [item], version + ' recipe reward ' + name)
            check(advancement['criteria']['has_the_recipe']['conditions'] == {('recipe' if version == '26.2' else 'recipes'): item}, version + ' unlock schema ' + name)
            definition = read(files[f'assets/chromusflora/items/{name}_boat.json'])
            check(definition['model'] == {'type': 'minecraft:model', 'model': 'chromusflora:item/' + name + '_boat'}, version + ' boat item ' + name)
            model = read(files[f'assets/chromusflora/models/item/{name}_boat.json'])
            check(model['textures']['wood'] == 'chromusflora:block/wood/' + name + '/planks', version + ' species texture ' + name)
            check(f'assets/chromusflora/textures/block/wood/{name}/planks.png' in files, version + ' missing wood texture ' + name)
            check(len(model['elements']) == 6, version + ' hull geometry ' + name)
            for element in model['elements']:
                check(all(0 <= a < b <= 16 for a, b in zip(element['from'], element['to'])), version + ' hull bounds ' + name)
                check(all(0 <= v <= 16 for face in element['faces'].values() for v in face['uv']), version + ' hull UV ' + name)
            for language in ['en_us', 'pt_br']:
                strings = read(files[f'assets/chromusflora/lang/{language}.json'])
                check(bool(strings.get('item.chromusflora.' + name + '_boat')) and bool(strings.get('entity.chromusflora.' + name + '_boat')), version + ' boat translation ' + name)
    metadata = read(RES / 'fabric.mod.json')
    check(metadata['entrypoints'].get('client') == ['dev.chromus.flora.client.FloraClient'], 'Missing client rendering entrypoint')
    return {'status': 'FAIL' if errors else 'PASS', 'assertions': checks, 'errors': errors, 'wood_boats': len(species), 'scope': 'Static resources only; no Java compilation or Minecraft execution.'}


if __name__ == '__main__':
    report = verify()
    out = ROOT / 'verification/release-0.1.4/boat-checks.json'
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(report, indent=2))
    raise SystemExit(0 if report['status'] == 'PASS' else 1)
