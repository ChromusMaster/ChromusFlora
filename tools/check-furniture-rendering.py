
import itertools
import json
import math
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RES = ROOT / 'flora/src/main/resources'
ASSETS = RES / 'assets/chromusflora'
REPORT = ROOT / 'verification/release-0.1.4/hotfix6'
EPS = 1e-7
AXES = {'west': (0, 0), 'east': (0, 1), 'down': (1, 0),
        'up': (1, 1), 'north': (2, 0), 'south': (2, 1)}


def read(path):
    return json.loads(path.read_text(encoding='utf-8'))


def intersections(elements):

    volumes, faces = [], []
    for (i, a), (j, b) in itertools.combinations(enumerate(elements), 2):
        overlap = [min(a['to'][k], b['to'][k]) - max(a['from'][k], b['from'][k])
                   for k in range(3)]
        if all(size > EPS for size in overlap):
            volumes.append([i, j])
        for side in a['faces'].keys() & b['faces'].keys():
            axis, end = AXES[side]
            bound = 'to' if end else 'from'
            if (abs(a[bound][axis] - b[bound][axis]) < EPS
                    and all(overlap[k] > EPS for k in range(3) if k != axis)):
                faces.append([i, j, side])
    return volumes, faces


def verify():
    checks, errors = 0, []

    def check(ok, message):
        nonlocal checks
        checks += 1
        if not ok:
            errors.append(message)

    families = [t['id'] for t in read(RES / 'chromusflora/catalog.json')['trees']]
    max_quads = 0
    for name in families:
        for kind, folder in [('crafting_table', 'block'), ('chest', 'item')]:
            model = read(ASSETS / f'models/{folder}/{name}_{kind}.json')
            elements = model['elements']
            volumes, faces = intersections(elements)
            check(not volumes, f'{name}_{kind}: intersecting boxes {volumes}')
            check(not faces, f'{name}_{kind}: duplicate coplanar faces {faces}')
            for element in elements:
                check(all(0 <= element['from'][k] < element['to'][k] <= 16 for k in range(3)),
                      f'{name}_{kind}: geometry outside the block')
                check(all(all(0 <= n <= 16 for n in face['uv'])
                          for face in element['faces'].values()), f'{name}_{kind}: UV outside the sprite')
            if kind == 'crafting_table':
                max_quads = max(max_quads, sum(len(e['faces']) for e in elements))

                point = (8, 0.5, 0.5)
                check(not any(all(e['from'][k] <= point[k] <= e['to'][k] for k in range(3))
                              for e in elements), name + ': cabinet gap was filled to hide the bug')
        for kind in ['single', 'left', 'right']:
            check(read(ASSETS / f'models/block/{name}_chest_{kind}.json')['elements'] == [],
                  name + ': static chest duplicates the animated model')
    check(max_quads <= 126, 'Crafting-table static mesh exceeds the reviewed budget')

    table_source = (ROOT / 'flora/src/main/java/dev/chromus/flora/block/FloraCraftingTable.java').read_text()
    check('super(properties.noOcclusion());' in table_source, 'Inset table must not occlude a full cube')
    renderer = (ROOT / 'flora/src/client/java/dev/chromus/flora/client/FloraChestRenderer.java').read_text()
    model = (ROOT / 'flora/src/client/java/dev/chromus/flora/client/FloraChestModel.java').read_text()
    check('yScale' not in model + renderer and 'storePose' not in model + renderer,
          'Correction must be mesh geometry, not a scale discarded by setupAnim')
    check('black_concrete' in renderer and 'interiors.select(state.type)' in renderer,
          'Dark interior must be submitted')
    check('sides.remove(Direction.UP);' in model, 'Wooden body roof would cover the dark interior')
    check('if (type == ChestType.LEFT) sides.remove(Direction.WEST);' in model
          and 'if (type == ChestType.RIGHT) sides.remove(Direction.EAST);' in model,
          'Double chest must omit the joining wall')
    check('LayerDefinition.create(mesh, 64, 64).bakeRoot()' in model,
          'Use permanent cubes in independent baked model roots')
    check('root.addOrReplaceChild("lid", CubeListBuilder.create(), PartPose.ZERO)' in model
          and 'root.addOrReplaceChild("lock", CubeListBuilder.create(), PartPose.ZERO)' in model,
          'Stationary meshes must not duplicate the native moving parts')
    check('bodies = stationaryParts(false);' in renderer and 'interiors = stationaryParts(true);' in renderer,
          'Body and interior variants must be built once per renderer')


    def arithmetic(expr, values):
        import ast
        node = ast.parse(re.sub(r'(\d(?:[\d.]*))F', r'\1', expr.strip()), mode='eval').body
        def evaluate(n):
            if isinstance(n, ast.Constant) and isinstance(n.value, (int, float)): return n.value
            if isinstance(n, ast.Name): return values[n.id]
            if isinstance(n, ast.BinOp) and isinstance(n.op, ast.Sub): return evaluate(n.left) - evaluate(n.right)
            raise ValueError('Unsupported geometry expression: ' + expr)
        return evaluate(node)

    native = read(ROOT / 'verification/release-0.1.4/hotfix5/native-chest-geometry.json')
    top_args = re.search(r'cubes.addBox\((x, .*?Set.of\(Direction.UP\))\);', model)[1].split(', ')[:6]
    body_args = re.search(r'cubes.addBox\((minX, .*?), sides\);', model)[1].split(', ')
    old_overlap, body_tops = [], []
    for kind in ['single', 'left', 'right']:
        values = {}
        for name, target, yes, no in re.findall(r'float (\w+) = type == ChestType.(\w+) \? ([\d.]+)F : ([\d.]+)F;', model):
            values[name] = float(yes if kind.upper() == target else no)
        body = [arithmetic(e, values) for e in body_args]
        body_top = body[1] + body[4]
        body_tops.append(body_top)
        tops = []
        for line in model.splitlines():
            call = re.search(r'top\(cubes, (.*?)\);', line)
            if not call: continue
            cond = re.search(r'if \(type != ChestType.(\w+)\)', line)
            if cond and kind.upper() == cond[1]: continue
            args = [arithmetic(e, values) for e in call[1].split(', ')]
            env = dict(zip(['x', 'z', 'width', 'depth'], args))
            box = [arithmetic(e, env) for e in top_args]
            tops.append({'from': box[:3], 'to': [box[k]+box[k+3] for k in range(3)],
                         'faces': {'up': {}}})
        _, overlap = intersections(tops)
        check(not overlap, kind + ': dark cap and wooden rim overlap')
        check(all(e['from'][1] == body_top and e['to'][1] == body_top for e in tops),
              kind + ': top surfaces detached from body')


        for xi in range(int(body[0]*2), int((body[0]+body[3])*2)):
            for zi in range(2, 30):
                x, z = xi/2 + .25, zi/2 + .25
                count = sum(e['from'][0] < x < e['to'][0] and e['from'][2] < z < e['to'][2] for e in tops)
                check(count == 1, f'{kind}: roof coverage {count} at {x},{z}')
        for version, variants in native['targets'].items():
            shape = variants[kind]
            hinge = shape['lid_hinge_y']
            old_overlap.append(shape['body_height'] - hinge)
            check(body_top == hinge, version + '/' + kind + ': closed chest gap/overlap')
            for degree in range(91):
                angle = math.radians(degree)
                lowest = min(hinge + y*math.cos(angle) + z*math.sin(angle)
                             for y in [0, shape['lid_height']] for z in [0, shape['depth']])
                check(lowest >= body_top - EPS, f'{version}/{kind}: overlap at {degree} degrees')
    check(all(value == 1 for value in old_overlap), 'Native overlap regression fixture is inconsistent')


    def cube(a, b):
        return {'from': a, 'to': b, 'faces': {face: {} for face in AXES}}
    original = [cube([1, 0, 1], [15, 15, 15]), cube([0, 0, 0], [2, 15, 2]),
                cube([0, 8, 5], [.15, 12, 6]), cube([0, 11, 3.5], [.15, 12, 7.5])]
    volumes, faces = intersections(original)
    check(bool(volumes) and bool(faces), 'Original broken geometry was not rejected')

    gradle = (ROOT / 'gradle/mod.gradle').read_text()
    check('rootProject.layout.buildDirectory.dir("${targetMinecraft}/Fabric")' in gradle,
          'All target outputs must be scoped to Fabric')
    verifier = (ROOT / 'tools/verify-jars.py').read_text()
    check("build/{target}/Fabric/chromus-flora-" in verifier, 'JAR verifier still uses the old path')
    ci = (ROOT / 'tools/ci/gradle.yml').read_text()
    for version in ['26.2', '26.3']:
        check(f'build/{version}/Fabric/chromus-flora-*-{version}.jar' in ci, 'CI artifact path ' + version)
    return {'status': 'PASS' if not errors else 'FAIL', 'assertions': checks, 'errors': errors,
            'wood_families': len(families), 'table_quads_max': max_quads,
            'native_overlap_before_units': old_overlap, 'body_top_after_units': body_tops,
            'scope': 'Static models, analytic lid sweep, source contracts and output paths. No runtime validation.'}


if __name__ == '__main__':
    result = verify()
    REPORT.mkdir(parents=True, exist_ok=True)
    (REPORT / 'furniture-checks.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))
    raise SystemExit(0 if result['status'] == 'PASS' else 1)
