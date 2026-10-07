
import copy
import graphlib
import itertools
import json
import runpy
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / 'verification/release-0.1.4/hotfix4'
FLOWERS = 'minecraft:flower_default'
GRASS = 'minecraft:patch_grass_jungle'


def cycle(biomes):
    graph = {}
    for stages in biomes.values():
        nodes = [(step, feature) for step, row in enumerate(stages) for feature in row]
        for node in nodes:
            graph.setdefault(node, set())
        for before, after in zip(nodes, nodes[1:]):
            graph[after].add(before)
    try:
        list(graphlib.TopologicalSorter(graph).static_order())
        return []
    except graphlib.CycleError as error:
        return error.args[1]


def repair(row):
    result = list(row)
    if any(not isinstance(x, str) for x in row) or len(set(row)) != len(row):
        return result
    if FLOWERS in row and GRASS in row and row.index(GRASS) == row.index(FLOWERS) + 1:
        i = row.index(FLOWERS)
        result[i:i + 2] = [GRASS, FLOWERS]
    return result


def read(path):
    return json.loads(path.read_text(encoding='utf-8'))


def main():
    fixture = read(FIXTURES / 'feature-order-fixture-26.2.json')
    flora = {'chromusflora:' + p.stem: read(p)['features'] for p in
             (ROOT / 'flora/src/main/resources/data/chromusflora/worldgen/biome').glob('*.json')}
    fixture['flora'] = flora
    baseline = cycle(fixture['vanilla'] | fixture['flora'] | fixture['terralith'] | fixture['terrestria'])
    assert baseline, 'Regression fixture must reproduce the original conflict'
    assert cycle(fixture['vanilla'] | fixture['terralith'] | fixture['terrestria'])
    scenarios = []
    for use_flora, use_terralith, use_terrestria in itertools.product([False, True], repeat=3):
        biomes = copy.deepcopy(fixture['vanilla'])
        for name, enabled in [('flora', use_flora), ('terralith', use_terralith), ('terrestria', use_terrestria)]:
            if enabled:
                biomes.update(copy.deepcopy(fixture[name]))
        if use_terralith and use_terrestria:
            stages = biomes['terrestria:rainbow_rainforest']
            stages[9] = repair(stages[9])
        found = cycle(biomes)
        assert not found, (use_flora, use_terralith, use_terrestria, found)
        scenarios.append({'flora': use_flora, 'terralith': use_terralith, 'terrestria': use_terrestria,
                          'biomes': len(biomes), 'acyclic': True})
    old = runpy.run_path(str(ROOT / 'tools/check-feature-order.py'))
    jaiz_fixture = read(ROOT / 'verification/fix8/jaiz-feature-order.json')
    native = fixture['vanilla'] | {'jaizmod:' + k: v for k, v in jaiz_fixture['biomes'].items()}
    native = {key: old['additions'](value, [r for r in jaiz_fixture['additions'] if r['biome'] == key], True)
              for key, value in native.items()}
    catalog = read(ROOT / 'flora/src/main/resources/chromusflora/catalog.json')['biomes']
    templates = {'chromusflora:' + b['id']: b['vanilla'] for b in catalog}
    rules = read(ROOT / 'flora/src/main/resources/chromusflora/jaiz-compatibility.json')['features']
    for enabled in [False, True]:
        cf = {key: old['additions'](value, [r for r in rules if r['biome'] == templates[key]], True)
              if enabled else value for key, value in flora.items()}
        biomes = copy.deepcopy(native | cf | fixture['terralith'] | fixture['terrestria'])
        biomes['terrestria:rainbow_rainforest'][9] = repair(biomes['terrestria:rainbow_rainforest'][9])
        assert not cycle(biomes), ('Jaiz regression', enabled, cycle(biomes))
        scenarios.append({'jaiz_features': enabled, 'biomes': len(biomes), 'acyclic': True})
    original = fixture['terrestria']['terrestria:rainbow_rainforest'][9]
    fixed = repair(original)
    assert sorted(fixed) == sorted(original) and repair(fixed) == fixed
    for row in [[], [FLOWERS], [GRASS], [GRASS, FLOWERS], [FLOWERS, 'other:between', GRASS],
                [FLOWERS, GRASS, FLOWERS], [FLOWERS, GRASS, {}]]:
        assert repair(row) == row
    assert repair(original + ['other:custom_vegetation']) == fixed + ['other:custom_vegetation']
    v263 = read(FIXTURES / 'feature-order-fixture-26.3.json')
    cf263 = {'chromusflora:' + p.stem: read(p)['features'] for p in
             (ROOT / 'versions/26.3/src/main/resources/data/chromusflora/worldgen/biome').glob('*.json')}
    assert not cycle(v263['vanilla'] | cf263 | v263['terralith'])
    report = {'status': 'PASS', 'original_cycle': baseline, 'scenarios_26_2': scenarios,
              'biomes_26_3_checked': len(v263['vanilla'] | cf263 | v263['terralith']),
              'preserves_membership_and_additions': True, 'idempotent': True,
              'limits': ['Static graph and algorithm model, not Java compilation or a Minecraft runtime test',
                         'Jaiz fixture models previously audited additions, not every installed runtime modifier',
                         'No Terrestria 26.3 release was available in the consulted version listing; not patched or claimed tested',
                         'Scenarios without Flora model a hypothetical upstream repair, not execution of an absent mod',
                         'Other mods and user datapacks can introduce further relationships']}
    (FIXTURES / 'feature-order-checks.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
