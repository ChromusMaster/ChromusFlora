import copy
import graphlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RES = ROOT / 'flora/src/main/resources'
STEPS = ['RAW_GENERATION', 'LAKES', 'LOCAL_MODIFICATIONS', 'UNDERGROUND_STRUCTURES',
         'SURFACE_STRUCTURES', 'STRONGHOLDS', 'UNDERGROUND_ORES', 'UNDERGROUND_DECORATION',
         'FLUID_SPRINGS', 'VEGETAL_DECORATION', 'TOP_LAYER_MODIFICATION']


def read(path):
    return json.loads(path.read_text(encoding='utf-8'))


def identifier_order(row):
    namespace, path = row['feature'].split(':', 1)
    return path, namespace


def additions(features, rows, ordered):
    result = copy.deepcopy(features)
    for row in sorted(rows, key=identifier_order) if ordered else rows:
        stage = result[STEPS.index(row['step'])]
        if row['feature'] not in stage:
            stage.append(row['feature'])
    return result


def cycle(biomes):
    predecessors = {}
    for features in biomes.values():
        nodes = [(step, feature) for step, entries in enumerate(features) for feature in entries]
        for node in nodes:
            predecessors.setdefault(node, set())
        for before, after in zip(nodes, nodes[1:]):
            predecessors[after].add(before)
    try:
        list(graphlib.TopologicalSorter(predecessors).static_order())
        return []
    except graphlib.CycleError as error:
        return [list(node) for node in error.args[1]]


def verify():
    fixture = read(ROOT / 'verification/fix8/jaiz-feature-order.json')
    vanilla = read(ROOT / 'verification/fix8/vanilla-feature-order.json')['biomes']
    jaiz = {'jaizmod:' + key: value for key, value in fixture['biomes'].items()}
    native = {key: additions(value, [r for r in fixture['additions'] if r['biome'] == key], True)
              for key, value in (vanilla | jaiz).items()}
    flora = {'chromusflora:' + p.stem: read(p)['features']
             for p in (RES / 'data/chromusflora/worldgen/biome').glob('*.json')}
    catalog = read(RES / 'chromusflora/catalog.json')['biomes']
    rules = read(RES / 'chromusflora/jaiz-compatibility.json')['features']
    templates = {'chromusflora:' + b['id']: b['vanilla'] for b in catalog}
    old = {key: additions(value, [r for r in rules if r['biome'] == templates[key]], False)
           for key, value in flora.items()}
    fixed = {key: additions(value, [r for r in rules if r['biome'] == templates[key]], True)
             for key, value in flora.items()}
    pair = {'chromusflora:zelkova_forest': old['chromusflora:zelkova_forest'],
            'jaizmod:mahogany_forest': native['jaizmod:mahogany_forest']}
    old_cycle = cycle(pair)
    scenarios = {'jaiz_without_flora': native, 'flora_without_jaiz': vanilla | flora,
                 'both_jaiz_features_disabled': native | flora,
                 'both_jaiz_features_enabled': native | fixed}
    results = {name: {'biomes': len(biomes), 'cycle': cycle(biomes)}
               for name, biomes in scenarios.items()}
    checks = {
        'reproduces_reported_pair_before_fix': bool(old_cycle),
        'all_scenarios_acyclic': all(not result['cycle'] for result in results.values()),
        'feature_membership_preserved': all(
            [set(stage) for stage in old[key]] == [set(stage) for stage in fixed[key]] for key in flora),
        'no_duplicate_compatibility_rules': len(rules) == len({(r['biome'], r['step'], r['feature']) for r in rules})
    }
    return {'status': 'PASS' if all(checks.values()) else 'FAIL',
            'scope': 'Static graph model of vanilla, Chromus Flora and supplied Jaiz source; no Java or game execution',
            'checks': checks, 'old_pair_cycle': old_cycle, 'scenarios': results,
            'limitations': ['Does not load the installed Jaiz JAR or the other mods in the instance',
                            'Does not validate Java types, runtime registries or actual world generation']}


if __name__ == '__main__':
    report = verify()
    (ROOT / 'verification/fix8/feature-order-result.json').write_text(
        json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(report, indent=2))
    raise SystemExit(0 if report['status'] == 'PASS' else 1)
