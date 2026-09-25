import ast
import collections
import gzip
import hashlib
import io
import json
import re
import struct
import sys
import tokenize
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RES = ROOT / 'flora/src/main/resources'
ERRORS = []
COUNTS = collections.Counter()


def check(condition, message):
    COUNTS['assertions'] += 1
    if not condition:
        ERRORS.append(message)


def pairs(rows):
    result = {}
    for key, value in rows:
        if key in result:
            raise ValueError('Duplicate JSON key: ' + key)
        result[key] = value
    return result


def read_json(path):
    return json.loads(path.read_text(encoding='utf-8'), object_pairs_hook=pairs)


def strings(value):
    if isinstance(value, str):
        yield value
    elif isinstance(value, dict):
        for child in value.values():
            yield from strings(child)
    elif isinstance(value, list):
        for child in value:
            yield from strings(child)


def walk(value):
    if isinstance(value, dict):
        yield value
        for child in value.values():
            yield from walk(child)
    elif isinstance(value, list):
        for child in value:
            yield from walk(child)


def nbt(path):
    stream = io.BytesIO(gzip.decompress(path.read_bytes()))

    def number(fmt):
        size = struct.calcsize(fmt)
        return struct.unpack(fmt, stream.read(size))[0]

    def string():
        return stream.read(number('>H')).decode('utf-8')

    def payload(kind):
        if kind in {1, 2, 3, 4, 5, 6}:
            return number({1:'>b', 2:'>h', 3:'>i', 4:'>q', 5:'>f', 6:'>d'}[kind])
        if kind == 8:
            return string()
        if kind == 9:
            child = number('>B')
            return [payload(child) for _ in range(number('>i'))]
        if kind == 10:
            result = {}
            while True:
                child = number('>B')
                if child == 0:
                    return result
                name = string()
                if name in result:
                    raise ValueError('Duplicate NBT tag ' + name)
                result[name] = payload(child)
        if kind in {7, 11, 12}:
            return [number({7:'>b', 11:'>i', 12:'>q'}[kind]) for _ in range(number('>i'))]
        raise ValueError('Unknown NBT kind ' + str(kind))

    if number('>B') != 10:
        raise ValueError('NBT root is not a compound')
    string()
    result = payload(10)
    if stream.read():
        raise ValueError('Trailing NBT bytes')
    return result


def acyclic(graph, label):
    incoming = collections.Counter({node:0 for node in graph})
    for children in graph.values():
        for child in children:
            incoming[child] += 1
    queue = collections.deque(node for node, count in incoming.items() if count == 0)
    visited = 0
    while queue:
        node = queue.popleft()
        visited += 1
        for child in graph.get(node, set()):
            incoming[child] -= 1
            if incoming[child] == 0:
                queue.append(child)
    check(visited == len(incoming), label + ' has a cycle')


def main():
    data = {}
    for path in sorted(RES.rglob('*.json')):
        try:
            data[path.relative_to(RES).as_posix()] = read_json(path)
        except (ValueError, OSError) as error:
            ERRORS.append(str(path) + ': ' + str(error))
    COUNTS['json_resources'] = len(data)
    spec = read_json(ROOT/'atelier/catalogue-spec.json')
    index = read_json(ROOT/'verification/reference-index.json')
    trees = {t['id']:t for t in spec['trees']}
    families = set(trees)
    check(len(families) == len(spec['trees']), 'Duplicate tree family')
    check(len({b['id'] for b in spec['biomes']}) == len(spec['biomes']), 'Duplicate biome')
    check(len({v['id'] for v in spec['variants']}) == len(spec['variants']), 'Duplicate variant')
    check({b['id'] for b in spec['biomes']} == set(index['merged_biome_ids']), 'Biome union mismatch')
    check(set(index['tree_registry_ids']) <= {v['id'] for v in spec['variants']}, 'Tree registry coverage incomplete')
    check({b['id'] for b in spec['biomes']} == {p.stem for p in (RES/'data/chromusflora/worldgen/biome').glob('*.json')}, 'Biome resources differ from catalogue')
    COUNTS.update(biomes=len(spec['biomes']), tree_families=len(families), variants=len(spec['variants']))
    block_ids = {n.removeprefix('assets/chromusflora/blockstates/').removesuffix('.json') for n in data if n.startswith('assets/chromusflora/blockstates/')}
    item_ids = {n.removeprefix('assets/chromusflora/items/').removesuffix('.json') for n in data if n.startswith('assets/chromusflora/items/')}
    expected_blocks = {t+'_'+suffix for t in families for suffix in ['log','leaves','planks','slab','stairs','fence','fence_gate','sapling']}
    expected_blocks |= {'stripped_'+t+'_log' for t in families} | {'potted_'+t+'_sapling' for t in families}
    check(block_ids == expected_blocks, 'Block registry/model mismatch')
    check(item_ids == {n for n in block_ids if not n.startswith('potted_')} | {'grove_fruit'}, 'Item registry/model mismatch')
    COUNTS.update(blocks=len(block_ids), items=len(item_ids))
    for id in block_ids:
        check('data/chromusflora/loot_table/blocks/'+id+'.json' in data, 'Missing loot: '+id)
        for lang in ['en_us','pt_br']:
            check('block.chromusflora.'+id in data['assets/chromusflora/lang/'+lang+'.json'], 'Missing translation: '+lang+'/'+id)
    all_files = {p.relative_to(RES).as_posix() for p in RES.rglob('*') if p.is_file()}
    vanilla_files = set(index['vanilla_resources'])

    def resource(kind, id, extension='.json', asset=False):
        if ':' not in id:
            id = 'minecraft:'+id
        namespace, name = id.split(':', 1)
        path = ('assets/' if asset else 'data/')+namespace+'/'+kind+'/'+name+extension
        check(path in (all_files if namespace == 'chromusflora' else vanilla_files), 'Missing reference: '+path)

    graph = collections.defaultdict(set)
    stage_graph = collections.defaultdict(set)
    for path, obj in data.items():
        for value in strings(obj):
            check(not value.startswith(('byg:', 'biomeswevegone:')), 'Legacy resource reference: '+path+'/'+value)
        if '/models/' in path:
            if 'parent' in obj:
                resource('models', obj['parent'], asset=True)
            for texture in obj.get('textures', {}).values():
                if not texture.startswith('#'):
                    resource('textures', texture, '.png', True)
        if '/blockstates/' in path or '/items/' in path:
            for node in walk(obj):
                if isinstance(node.get('model'), str):
                    resource('models', node['model'], asset=True)
        if '/tags/' in path:
            kind = path.split('/tags/')[1].rsplit('/',1)[0]
            if kind.startswith('block/'):
                kind = 'block'
            for ref in obj['values']:
                ref = ref if isinstance(ref, str) else ref['id']
                if ref.startswith('#'):
                    continue
                if ref.startswith('chromusflora:'):
                    if kind == 'block':
                        check(ref.split(':')[1] in block_ids, 'Unknown block tag member '+ref)
                    if kind == 'item':
                        check(ref.split(':')[1] in item_ids, 'Unknown item tag member '+ref)
        if '/loot_table/' in path:
            for node in walk(obj):
                if node.get('type') == 'minecraft:item' and node['name'].startswith('chromusflora:'):
                    check(node['name'].split(':')[1] in item_ids, 'Unknown loot item '+node['name'])
        if '/recipe/' in path:
            check(obj['result']['id'].split(':')[1] in item_ids, 'Unknown recipe result '+path)
            for ref in strings(obj.get('key', obj.get('ingredients', []))):
                if ref.startswith('chromusflora:'):
                    check(ref.split(':')[1] in item_ids, 'Unknown recipe ingredient '+ref)
                if ref.startswith('#chromusflora:'):
                    resource('tags/item', ref[1:])
        if '/configured_feature/' in path:
            id = 'chromusflora:'+path.split('/configured_feature/')[1].removesuffix('.json')
            graph[id]
            for node in walk(obj):
                if isinstance(node.get('feature'), str):
                    ref = node['feature']
                    resource('worldgen/configured_feature', ref)
                    graph[id].add(ref)
        if '/placed_feature/' in path:
            resource('worldgen/configured_feature', obj['feature'])
        if '/worldgen/biome/' in path and '/tags/' not in path:
            for carver in ([obj['carvers']] if isinstance(obj['carvers'], str) else obj['carvers']):
                resource('worldgen/configured_carver', carver)
            for stage, features in enumerate(obj['features']):
                for ref in features:
                    resource('worldgen/placed_feature', ref)
                for before, after in zip(features, features[1:]):
                    stage_graph[(stage,before)].add((stage,after))
            check(len(obj['features']) == 11, 'Wrong decoration stage count: '+path)
            check(all(0 <= x['minCount'] <= x['maxCount'] and x['weight'] > 0 for rows in obj['spawners'].values() for x in rows), 'Invalid spawner: '+path)
    for biome in index['vanilla_biome_feature_order']:
        for stage, features in enumerate(biome):
            for before, after in zip(features, features[1:]):
                stage_graph[(stage,before)].add((stage,after))
    acyclic(graph, 'Configured features')
    acyclic(stage_graph, 'Vanilla/custom decoration order')
    used = {t for b in spec['biomes'] if b['density'] > 0 for t in b['trees']}
    check(used == families, 'A tree family has no natural biome placement')
    nbt_data = {}
    for path in sorted((RES/'data/chromusflora/structure').rglob('*.nbt')):
        try:
            obj = nbt(path)
            nbt_data['chromusflora:'+path.relative_to(RES/'data/chromusflora/structure').as_posix().removesuffix('.nbt')] = obj
            palette = obj['palette']
            cells = {tuple(row['pos']):row['state'] for row in obj['blocks']}
            check(len(cells) == len(obj['blocks']), 'Overlapping NBT cells: '+str(path))
            check(obj['DataVersion'] == 4903 and not obj['entities'], 'Wrong NBT version/entities: '+str(path))
            check(all(0 <= state < len(palette) and all(0 <= p[i] < obj['size'][i] for i in range(3)) for p,state in cells.items()), 'Invalid NBT bounds/palette: '+str(path))
            check(sum(palette[s]['Name']=='minecraft:white_wool' for s in cells.values()) == 1, 'Wrong center marker count: '+str(path))
            check(any(palette[s]['Name']=='minecraft:red_wool' for s in cells.values()), 'Missing trunk markers: '+str(path))
        except (ValueError, OSError, struct.error, KeyError) as error:
            ERRORS.append(str(path)+': '+str(error))
    COUNTS['nbt_structures'] = len(nbt_data)
    height_rows = []
    for path,obj in data.items():
        if obj.get('type') != 'chromusflora:bounded_tree':
            continue
        config = obj['config']
        check(config['base_location'] in nbt_data and config['canopy_location'] in nbt_data, 'Missing tree template: '+path)
        canopy = nbt_data[config['canopy_location']]
        palette = canopy['palette']
        base = nbt_data[config['base_location']]
        family = config['log_provider']['state']['Name'].split(':')[1].removesuffix('_log')
        cells = {tuple(row['pos']):palette[row['state']]['Name'] for row in canopy['blocks']}
        log_y = max(p[1] for p,s in cells.items() if s in ['minecraft:oak_log','minecraft:red_wool'])
        provider = config['height']
        low,high = (provider,provider) if isinstance(provider,int) else (provider['min_inclusive'],provider['max_inclusive'])
        check(0 < low <= high, 'Invalid height provider '+path)
        check(config['max_log_depth'] == 1 and config['tree_filter_behavior'] == 'BLOCK', 'Unsafe tree filters '+path)
        check(config['leaves_target'] == ['minecraft:oak_leaves'] and len(config['leaves_provider']) == 1, 'Leaves palette mismatch '+path)
        check(high+log_y+1 <= trees[family]['maxHeight'], 'Height ceiling exceeded '+path)
        logs = {p for p,s in cells.items() if s in ['minecraft:oak_log','minecraft:red_wool']}
        leaves = {p for p,s in cells.items() if s == 'minecraft:oak_leaves'}
        distances = {p:0 for p in logs}
        queue = collections.deque(logs)
        while queue:
            p = queue.popleft()
            if distances[p] == 6:
                continue
            for d in [(1,0,0),(-1,0,0),(0,1,0),(0,-1,0),(0,0,1),(0,0,-1)]:
                q = tuple(p[i]+d[i] for i in range(3))
                if q in leaves and q not in distances:
                    distances[q] = distances[p]+1
                    queue.append(q)
        check(bool(leaves) and leaves <= distances.keys(), 'Unsupported or missing leaves '+path)
        if path.endswith('/small.json'):
            base_red = sum(base['palette'][row['state']]['Name']=='minecraft:red_wool' for row in base['blocks'])
            check(low == high == 2 and log_y == 0 and len(logs) == 1 and base_red == 1, 'Small form does not have exactly three log blocks '+path)
        height_rows.append({'family':family,'form':config['canopy_location'],'min_trunk_height':low+log_y+1,'max_trunk_height':high+log_y+1})
    COUNTS['tree_forms'] = len(height_rows)
    java_files = list((ROOT/'flora/src').rglob('*.java'))
    for path in java_files:
        source = path.read_text(encoding='utf-8')
        without_strings = re.sub(r'"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\'', '""', source)
        check('//' not in without_strings and '/*' not in without_strings, 'Java comment: '+str(path))
    for path in (ROOT/'tools').glob('*.py'):
        source = path.read_text(encoding='utf-8')
        ast.parse(source, filename=str(path))
        check(not any(token.type == tokenize.COMMENT for token in tokenize.generate_tokens(io.StringIO(source).readline)), 'Python comment: '+str(path))
    COUNTS['java_sources'] = len(java_files)
    forbidden_hashes = set(index['source_asset_sha256'])
    for path in (ROOT/'flora').rglob('*'):
        if path.is_file():
            check(path.suffix not in ['.class','.jar','.exe'], 'Compiled artifact in source set: '+str(path))
            if path.suffix in ['.png','.nbt','.ogg','.java']:
                check(hashlib.sha256(path.read_bytes()).hexdigest() not in forbidden_hashes, 'Byte-identical legacy asset/code: '+str(path))
    for path in (RES/'assets/chromusflora').rglob('*.png'):
        raw = path.read_bytes()
        check(raw[:8] == b'\x89PNG\r\n\x1a\n', 'Invalid PNG '+str(path))
        w,h = struct.unpack('>II',raw[16:24])
        check((w,h) == ((256,256) if path.name=='icon.png' else (64,64)), 'Wrong texture dimensions '+str(path))
    build = (ROOT/'build.gradle').read_text()
    check("'-Xlint:all', '-Werror'" in build, 'Compiler warnings not fatal')
    check('org.gradle.warning.mode=fail' in (ROOT/'gradle.properties').read_text(), 'Gradle warnings not fatal')
    rules = data['chromusflora/jaiz-compatibility.json']
    for row in rules['spawns']:
        check(row['entity'] in index['jaiz_entity_ids'], 'Unknown Jaiz entity '+row['entity'])
    for row in rules['features']:
        check(row['feature'] in index['jaiz_placed_feature_ids'], 'Unknown Jaiz feature '+row['feature'])
    check('English' in (ROOT/'README.md').read_text() and (ROOT/'README.md').read_text().index('English') < (ROOT/'README.md').read_text().index('Português'), 'README language order')
    report = {'scope':'offline static source/resource scan; no Java compilation or game execution',
              'status':'PASS' if not ERRORS else 'FAIL','counts':dict(COUNTS),'errors':ERRORS,
              'limitations':['No Java type checking or compiler warning result','No registry/datapack loading in the game','No world generation, server, multiplayer or optional-mod runtime tests'],
              'tree_height_results':height_rows}
    (ROOT/'verification/global-scan.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in report.items() if k not in ['tree_height_results']},indent=2))
    return 1 if ERRORS else 0


if __name__ == '__main__':
    sys.exit(main())
