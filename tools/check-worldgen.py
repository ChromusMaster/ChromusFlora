import collections
import json
import runpy
from pathlib import Path
from scan import nbt, read_json


ROOT = Path(__file__).resolve().parents[1]
RES = ROOT / 'flora/src/main/resources'
NEIGHBORS = ((1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1))


def template_bounds(obj):
    size = obj['size']
    if len(size) != 3 or any(n <= 0 for n in size):
        raise ValueError('Empty or invalid template size')
    if 'palettes' in obj:
        raise ValueError('Bundled trees must use a single palette')
    palette = obj['palette']
    positions = [tuple(row['pos']) for row in obj['blocks']]
    if len(positions) != len(set(positions)):
        raise ValueError('Duplicate block positions')
    if any(not 0 <= p[i] < size[i] for p in positions for i in range(3)):
        raise ValueError('Block outside declared template size')
    anchors = [tuple(row['pos']) for row in obj['blocks']
               if palette[row['state']]['Name'] == 'minecraft:white_wool']
    if len(anchors) != 1:
        raise ValueError('Expected exactly one white-wool anchor')
    anchor = anchors[0]
    radius = max(max(abs(p[0] - anchor[0]), abs(p[2] - anchor[2])) for p in positions)
    return radius, anchor


def chunk_range(x, z, radius):
    return {(cx, cz) for cx in range((x - radius) // 16, (x + radius) // 16 + 1)
            for cz in range((z - radius) // 16, (z + radius) // 16 + 1)}


def permitted(x, z, radius, read_chunks, write_chunks):
    return (chunk_range(x, z, radius + 1) <= read_chunks
            and chunk_range(x, z, radius) <= write_chunks)


def verify():
    errors = []
    checks = collections.Counter()

    def check(condition, message):
        checks['assertions'] += 1
        if not condition:
            errors.append(message)

    catalog = read_json(RES / 'chromusflora/catalog.json')
    trees = catalog['trees']
    biomes = catalog['biomes']
    tree_ids = {t['id'] for t in trees}
    check(len(tree_ids) == len(trees), 'Duplicate tree registry IDs')
    check(len({b['id'] for b in biomes}) == len(biomes), 'Duplicate biome registry IDs')
    for biome in biomes:
        check(biome['dimension'] in ('overworld', 'nether', 'end'), 'Invalid dimension: ' + biome['id'])
        check(set(biome['trees']) <= tree_ids, 'Unknown tree in biome: ' + biome['id'])
        check(0 <= biome['density'] <= 6, 'Tree density budget exceeded: ' + biome['id'])

    rules = read_json(RES / 'chromusflora/jaiz-compatibility.json')
    for name in ('features', 'spawns'):
        rows = [json.dumps(row, sort_keys=True) for row in rules[name]]
        check(len(rows) == len(set(rows)), 'Duplicate compatibility rows: ' + name)
    feature_order = runpy.run_path(str(ROOT / 'tools/check-feature-order.py'))['verify']()
    check(feature_order['status'] == 'PASS', 'Feature order fixture failed')
    for path in (RES / 'data/chromusflora/worldgen/biome').glob('*.json'):
        stages = read_json(path)['features']
        check(len(stages) == 11, 'Unexpected generation step count: ' + path.name)
        flat = [entry for stage in stages for entry in stage]
        check(len(flat) == len(set(flat)), 'Duplicate feature or feature used in multiple steps: ' + path.name)

    templates = {}
    rows = []
    for path in sorted((RES / 'data/chromusflora/worldgen/configured_feature/forms').rglob('*.json')):
        label = path.relative_to(RES).as_posix()
        try:
            definition = read_json(path)
            check(definition['type'] == 'chromusflora:bounded_tree', 'Unbounded tree: ' + label)
            config = definition['config']
            check(config['orientation'] == 'STANDARD' and not config['decorators'],
                  'Unsupported orientation or decorator footprint: ' + label)
            check(not config['replace_from_nbt'], 'Unreviewed NBT replacement provider: ' + label)
            check(config['max_log_depth'] == 1 and config['tree_filter_behavior'] == 'BLOCK',
                  'Changed root or log collision contract: ' + label)
            check(config['can_grow_on_filter'] == {'type': 'minecraft:matching_block_tag',
                                                  'tag': 'chromusflora:tree_soils'},
                  'Unreviewed ground predicate: ' + label)
            for key in ('can_logs_place_filter', 'can_leaves_place_filter'):
                check(config[key] == {'type': 'minecraft:replaceable'}, 'Unreviewed predicate offset: ' + label)
            for key in ('base_location', 'canopy_location'):
                identifier = config[key]
                if identifier not in templates:
                    namespace, name = identifier.split(':', 1)
                    obj = nbt(RES / f'data/{namespace}/structure/{name}.nbt')
                    templates[identifier] = obj, template_bounds(obj)
            base, (base_radius, base_anchor) = templates[config['base_location']]
            canopy, (canopy_radius, anchor) = templates[config['canopy_location']]
            check(not base['entities'] and not canopy['entities'], 'Entities in tree template: ' + label)
            check(all(base['palette'][b['state']]['Name'] != 'minecraft:yellow_wool'
                      for b in base['blocks']), 'Unreviewed alternate canopy origin: ' + label)
            height = config['height']
            low, high = (height, height) if isinstance(height, int) else (height['min_inclusive'], height['max_inclusive'])
            check(0 < low <= high <= 64, 'Invalid or oversized height interval: ' + label)
            radius = base_radius + canopy_radius
            check(radius <= 15, 'Tree exceeds the reviewed horizontal budget: ' + label)
            check(len(canopy['blocks']) <= 4096 and len(base['blocks']) <= 32,
                  'Tree template exceeds the reviewed block budget: ' + label)
            positions = [(row['pos'][0] - anchor[0], row['pos'][1] + high, row['pos'][2] - anchor[2])
                         for row in canopy['blocks']]
            positions += [(row['pos'][0] - base_anchor[0], row['pos'][1], row['pos'][2] - base_anchor[2])
                          for row in base['blocks']]
            rotations_fit = True
            halo_fits = True
            for x, y, z in positions:
                for rx, rz in ((x, z), (-z, x), (-x, -z), (z, -x)):
                    rotations_fit &= abs(rx) <= radius and abs(rz) <= radius
                    halo_fits &= all(abs(rx + d[0]) <= radius + 1 and abs(rz + d[2]) <= radius + 1
                                     for d in NEIGHBORS)
                    checks['voxel_rotations'] += 1
            check(rotations_fit, 'Rotation outside preflight footprint: ' + label)
            check(halo_fits, 'Leaf-neighbor read outside preflight halo: ' + label)
            check(all(-config['max_log_depth'] <= y < high + base['size'][1] + canopy['size'][1]
                      for x, y, z in positions), 'Vertical preflight does not cover geometry: ' + label)
            red_base = sum(base['palette'][b['state']]['Name'] == 'minecraft:red_wool' for b in base['blocks'])
            red_canopy = sum(canopy['palette'][b['state']]['Name'] == 'minecraft:red_wool' for b in canopy['blocks'])
            candidates = len(base['blocks']) + len(canopy['blocks']) + red_base * high + red_canopy * (high + 1)
            check(candidates <= 8192, 'Candidate block budget exceeded: ' + label)
            rows.append({'form': label, 'write_radius': radius, 'read_radius': radius + 1,
                         'canopy_blocks': len(canopy['blocks']), 'candidate_block_upper_bound': candidates})
        except (ValueError, KeyError, IndexError, OSError) as error:
            errors.append(label + ': ' + str(error))

    read_chunks = {(x, z) for x in range(-8, 9) for z in range(-8, 9)}
    write_chunks = {(x, z) for x in range(-1, 2) for z in range(-1, 2)}
    check(chunk_range(31, 31, 29) <= read_chunks,
          'Boundary regression setup must pass the old read-only preflight')
    check(not permitted(31, 31, 15, read_chunks, write_chunks), 'Cross-chunk write was accepted')
    check(not permitted(-17, -17, 15, read_chunks, write_chunks), 'Negative-coordinate write was accepted')
    check(permitted(0, 0, 15, read_chunks, write_chunks), 'Valid central placement was rejected')
    check(not permitted(0, 0, 15, {(0, 0)}, write_chunks), 'Missing read halo was accepted')
    for radius in sorted({row['write_radius'] for row in rows}):
        for x in range(16):
            for z in range(16):
                check(permitted(x, z, radius, read_chunks, write_chunks),
                      f'Valid central-chunk placement rejected: {x},{z},r={radius}')
    checks['forms'] = len(rows)
    checks['templates'] = len(templates)
    return {'status': 'PASS' if not errors else 'FAIL',
            'scope': 'Static resource contracts and independent voxel/chunk geometry model; no Java execution',
            'counts': dict(checks), 'errors': errors, 'feature_order': feature_order['scenarios'],
            'max_write_radius': max((r['write_radius'] for r in rows), default=0),
            'max_canopy_blocks': max((r['canopy_blocks'] for r in rows), default=0),
            'max_candidate_blocks': max((r['candidate_block_upper_bound'] for r in rows), default=0),
            'forms': rows,
            'limitations': ['Does not execute the Java preflight, Minecraft or C2ME.',
                            'Graph fixture covers supplied vanilla and Jaiz data, not all installed mods.',
                            'Block budgets are structural limits, not measured timings or memory usage.',
                            'Arbitrary datapack decorators, providers, predicates and orientations require a new footprint review.']}


if __name__ == '__main__':
    report = verify()
    destination = ROOT / 'verification/release-0.1.3/worldgen-checks.json'
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({key: value for key, value in report.items() if key != 'forms'}, indent=2))
    raise SystemExit(0 if report['status'] == 'PASS' else 1)
