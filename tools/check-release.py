import hashlib
import json
import runpy
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RES = ROOT / 'flora/src/main/resources'
REPORT = ROOT / 'verification/release-0.1.4'
BASELINE = ROOT / 'verification/release-0.1.1'
REPORT.mkdir(parents=True, exist_ok=True)


def read(path):
    return json.loads(path.read_text(encoding='utf-8'))


def verify():
    errors = []
    checks = 0
    def check(ok, message):
        nonlocal checks
        checks += 1
        if not ok:errors.append(message)
    catalog = read(RES / 'chromusflora/catalog.json')
    resources = {p.relative_to(RES).as_posix(): p for p in RES.rglob('*') if p.is_file()}
    modern = ROOT / 'versions/26.3/src/main/resources'
    overlays = {p.relative_to(modern).as_posix(): p for p in modern.rglob('*') if p.is_file()}
    targets = {'26.2': resources, '26.3': {k: v for k, v in resources.items() if '/worldgen/configured_feature/' not in k} | overlays}
    for version, files in targets.items():
        for tree in catalog['trees']:
            species = tree['id']
            for suffix in ['planks', 'slab', 'stairs', 'fence', 'fence_gate', 'door', 'trapdoor', 'wood', 'crafting_table', 'chest', 'boat']:
                name = species + '_' + suffix
                recipe = read(files['data/chromusflora/recipe/' + name + '.json'])
                advancement = read(files['data/chromusflora/advancement/recipes/' + name + '.json'])
                check(recipe['result']['id'] == 'chromusflora:' + name, version + ' wrong recipe ' + name)
                check(advancement['rewards']['recipes'] == ['chromusflora:' + name], version + ' missing recipe unlock ' + name)
                condition = advancement['criteria']['has_the_recipe']['conditions']
                check(condition == {('recipe' if version == '26.2' else 'recipes'): 'chromusflora:' + name}, version + ' unlock schema ' + name)
            logs = read(files[f'data/chromusflora/tags/item/{species}_logs.json'])['values']
            check(set(logs) == {'chromusflora:' + species + '_' + suffix for suffix in ['log', 'wood']} | {'chromusflora:stripped_' + species + '_' + suffix for suffix in ['log', 'wood']}, version + ' log tag ' + species)
            for suffix, count, pattern in [('door', 3, ['##', '##', '##']), ('trapdoor', 2, ['###', '###']), ('fence', 3, ['#S#', '#S#']), ('fence_gate', 1, ['S#S', 'S#S'])]:
                recipe = read(files[f'data/chromusflora/recipe/{species}_{suffix}.json'])
                check(recipe['result']['count'] == count and recipe['pattern'] == pattern, version + ' crafting pattern ' + species + '_' + suffix)
            door = read(files[f'assets/chromusflora/blockstates/{species}_door.json'])
            check(len(door['variants']) == 32, version + ' door state coverage ' + species)
            trapdoor = read(files[f'assets/chromusflora/blockstates/{species}_trapdoor.json'])
            check(len(trapdoor['variants']) == 16, version + ' trapdoor state coverage ' + species)
        for name, item in [('vanilla_chest', 'chest'), ('vanilla_crafting_table', 'crafting_table')]:
            check(read(files[f'data/chromusflora/recipe/{name}.json'])['result']['id'] == 'minecraft:' + item, version + ' fallback ' + name)
        features = {name for name in files if '/worldgen/' + ('configured_feature' if version == '26.2' else 'feature') + '/' in name}
        check(len(features) == 1752, version + ' feature resource count')
        for name in features:
            feature = read(files[name])
            check(('config' in feature) == (version == '26.2'), version + ' feature schema ' + name)
        if version == '26.3':
            for name, path in files.items():
                if '/loot_table/' in name:
                    text = path.read_text()
                    check(not any('"' + key + '"' in text for key in ['conditions', 'function', 'functions', 'block_state_property']), 'Old loot schema ' + name)
            check(not any('/configured_feature/' in name for name in files), '26.2 features leaked into 26.3')
    fingerprint = read(BASELINE / 'fix10-preserved-resources.json')
    palette_fixture = read(REPORT / 'hotfix7/preservation-fixture.json')
    approved = {name.removeprefix('flora/src/main/resources/'): digest
                for name, digest in palette_fixture['approved_wood_textures'].items()}
    revised = 0
    for name, digest in fingerprint['files'].items():
        if name in approved:
            check(hashlib.sha256(resources[name].read_bytes()).hexdigest() == approved[name],
                  'Unapproved wood palette: ' + name)
            revised += 1
            continue
        check(name in resources and hashlib.sha256(resources[name].read_bytes()).hexdigest() == digest, 'Changed saved-world definition: ' + name)
    graph = runpy.run_path(str(ROOT / 'tools/check-feature-order.py'))
    vanilla = read(ROOT / 'verification/fix8/vanilla-feature-order.json')['biomes']
    pack = read(BASELINE / 'pack-feature-fixture.json')['biomes']
    check(bool(graph['cycle'](vanilla | pack)), 'External cycle was not reproduced')
    new_native = read(ROOT / 'atelier/vanilla-biome-reference-26.3.json')
    new_graph = {'minecraft:' + key: value['features'] for key, value in new_native.items()}
    new_graph.update({'chromusflora:' + p.stem: read(p)['features'] for p in (modern / 'data/chromusflora/worldgen/biome').glob('*.json')})
    check(not graph['cycle'](new_graph), '26.3 Flora/vanilla feature cycle')
    compatibility = runpy.run_path(str(ROOT / 'tools/check-vegetation-compatibility.py'))
    compatibility['main']()
    check(read(REPORT / 'hotfix4/feature-order-checks.json')['status'] == 'PASS',
          'Terralith/Terrestria vegetation compatibility regression')
    furniture = runpy.run_path(str(ROOT / 'tools/check-furniture-rendering.py'))['verify']()
    (REPORT / 'hotfix6/furniture-checks.json').write_text(json.dumps(furniture, indent=2) + '\n')
    check(furniture['status'] == 'PASS', 'Furniture geometry/occlusion and loader output regression: '
          + '; '.join(furniture['errors']))
    for script, filename in [('check-palette-preservation.py', 'palette-checks.json'),
                             ('check-crafting-completion.py', 'crafting-checks.json')]:
        result = runpy.run_path(str(ROOT / 'tools' / script))['verify']()
        (REPORT / 'hotfix7' / filename).write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
        check(result['status'] == 'PASS', script + ': ' + '; '.join(result['errors']))
    woodworks = runpy.run_path(str(ROOT / 'tools/check-woodworks.py'))['verify']()
    (REPORT / 'hotfix8/woodworks-checks.json').write_text(json.dumps(woodworks, indent=2) + '\n', encoding='utf-8')
    check(woodworks['status'] == 'PASS', 'Woodworks regression: ' + '; '.join(woodworks['errors']))
    public = runpy.run_path(str(ROOT / 'tools/check-public-release.py'))['verify']()
    (ROOT / 'verification/release-1.0.0/release-checks.json').write_text(json.dumps(public, indent=2) + '\n')
    check(public['status'] == 'PASS', 'Public release regression: ' + '; '.join(public['errors']))
    return {'status': 'PASS' if not errors else 'FAIL', 'assertions': checks, 'errors': errors,
            'old_definitions_preserved': len(fingerprint['files']) - revised,
            'approved_visual_overrides': revised,
            'recipes_per_target': {target: len([n for n in files if n.startswith('data/chromusflora/recipe/') and n.endswith('.json')])
                                   for target, files in targets.items()},
            'scope': 'Static file and graph checks only; no Java, Gradle or Minecraft execution'}


if __name__ == '__main__':
    report = verify()
    (REPORT / 'checks.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(report, indent=2))
    raise SystemExit(0 if report['status'] == 'PASS' else 1)
