import collections
import copy
import gzip
import hashlib
import json
import math
import random
import shutil
import struct
from pathlib import Path
import tree_shapes
from texture_tiles import periodic_tile

ROOT = Path(__file__).resolve().parents[1]
RES = ROOT / 'flora/src/main/resources'
ASSETS = RES / 'assets/chromusflora'
DATA = RES / 'data/chromusflora'
SPEC = json.loads((ROOT / 'atelier/catalogue-spec.json').read_text(encoding='utf-8'))
TREES = {tree['id']: tree for tree in SPEC['trees']}


def write(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def string(value):
    raw = value.encode('utf-8')
    return struct.pack('>H', len(raw)) + raw


def compound(fields):
    return b''.join(bytes([kind]) + string(key) + value for key, kind, value in fields) + b'\0'


def integer(value):
    return struct.pack('>i', value)


def sequence(kind, rows):
    return bytes([kind]) + integer(len(rows)) + b''.join(rows)


def nbt(path, cells):
    palettes = [
        {'Name': 'minecraft:white_wool'},
        {'Name': 'minecraft:red_wool'},
        {'Name': 'minecraft:oak_log', 'Properties': {'axis': 'y'}},
        {'Name': 'minecraft:oak_leaves', 'Properties': {'distance': '1', 'persistent': 'false', 'waterlogged': 'false'}},
        {'Name': 'minecraft:oak_log', 'Properties': {'axis': 'x'}},
        {'Name': 'minecraft:oak_log', 'Properties': {'axis': 'z'}}]
    encoded = []
    for palette in palettes:
        fields = [('Name', 8, string(palette['Name']))]
        if 'Properties' in palette:
            fields.append(('Properties', 10, compound([(k, 8, string(v)) for k, v in palette['Properties'].items()])))
        encoded.append(compound(fields))
    size = [max(p[axis] for p in cells) + 1 for axis in range(3)]
    blocks = [compound([('pos', 9, sequence(3, [integer(v) for v in pos])), ('state', 3, integer(state))])
              for pos, state in sorted(cells.items())]
    raw = bytes([10]) + string('') + compound([
        ('DataVersion', 3, integer(4903)), ('size', 9, sequence(3, [integer(v) for v in size])),
        ('palette', 9, sequence(10, encoded)), ('blocks', 9, sequence(10, blocks)), ('entities', 9, sequence(10, []))])
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(gzip.compress(raw, compresslevel=9, mtime=0))
    return size


def canopy(tree, variant, tier):
    if tier != 'small':
        return tree_shapes.canopy(tree, variant, tier)
    seed = int(hashlib.sha256((variant + tier).encode()).hexdigest()[:16], 16)
    rng = random.Random(seed)
    radius = 2 if tier == 'small' else 3 if tier == 'normal' else 5
    shape = tree['shape']
    height = 2 if tier == 'small' else 6 if shape == 'conifer' else 4
    center = radius + 1
    cells = {}
    thick = 1 if tier == 'giant' else 0
    for x in range(-thick, thick + 1):
        for z in range(-thick, thick + 1):
            cells[(center+x, 0, center+z)] = 1
    if tier != 'small':
        for y in range(1, height):
            cells[(center, y, center)] = 2
        for dx,dz in [(1,0),(-1,0),(0,1),(0,-1)]:
            for distance in range(1, radius):
                y = 2
                cells[(center+dx*distance, y, center+dz*distance)] = 2
    for y in range(height + 1):
        for x in range(-radius, radius + 1):
            for z in range(-radius, radius + 1):
                distance = x*x + z*z
                if tier == 'small':
                    inside = y <= 1 and distance <= (2.2 if y == 0 else 1.8)**2
                elif shape == 'conifer':
                    layer = max(0.8, radius * (1-y/(height+1)))
                    inside = distance <= layer*layer and (y % 2 == 0 or distance <= (layer-0.4)**2)
                elif shape == 'palm':
                    inside = y <= 2 and (abs(x) <= 1 or abs(z) <= 1 or abs(abs(x)-abs(z)) <= 0.3) and distance <= radius*radius
                elif shape == 'fungus':
                    inside = y >= 2 and distance <= (radius * (1-0.13*abs(y-3)))**2
                elif shape == 'weeping':
                    inside = (y >= 2 and distance <= radius*radius) or (y < 2 and radius-1 <= math.sqrt(distance) <= radius and rng.random() < 0.75)
                elif shape == 'candelabra':
                    inside = y >= 1 and min((x-radius+1)**2+z*z, (x+radius-1)**2+z*z, x*x+(z-radius+1)**2, x*x+(z+radius-1)**2) <= 2.8
                else:
                    inside = distance/(radius*radius) + ((y-2)/2.4)**2 <= 1.15
                pos = (center+x, y, center+z)
                if inside and pos not in cells and (rng.random() > 0.07 or abs(x)+abs(z) <= 2):
                    cells[pos] = 3
    support = {pos for pos,state in cells.items() if state in (1,2)}
    distances = {pos: 0 for pos in support}
    queue = collections.deque(support)
    while queue:
        pos = queue.popleft()
        if distances[pos] >= 6:
            continue
        for offset in [(1,0,0),(-1,0,0),(0,1,0),(0,-1,0),(0,0,1),(0,0,-1)]:
            nxt = tuple(pos[i]+offset[i] for i in range(3))
            if nxt in cells and cells[nxt] == 3 and nxt not in distances:
                distances[nxt] = distances[pos] + 1
                queue.append(nxt)
    cells = {p:s for p,s in cells.items() if s != 3 or p in distances}
    cells[(center, height+2, center)] = 0
    return cells


def provider(name, properties=None):
    state = {'Name': name}
    if properties:
        state['Properties'] = properties
    return {'type':'minecraft:simple_state_provider','state':state}


def placed_inline(id):
    return {'feature':'chromusflora:'+id, 'placement':[]}


def selector(id, refs):
    write(DATA / ('worldgen/configured_feature/' + id + '.json'),
          {'type':'minecraft:simple_random_selector','config':{'features':[placed_inline(ref) for ref in refs]}})


def tree_resources():
    nbt(DATA/'structure/trees/base.nbt', {(0,0,0):1,(0,1,0):0})
    base = {(x,0,z):1 for x in range(3) for z in range(3)}
    base[(1,1,1)] = 0
    nbt(DATA/'structure/trees/base_giant.nbt', base)
    families = collections.defaultdict(list)
    measurements = []
    for variant in SPEC['variants']:
        if variant['aggregate']:
            continue
        id, tree = variant['id'], TREES[variant['tree']]
        families[tree['id']].append('variants/'+id)
        for tier in ['small','normal','giant']:
            cells = canopy(tree,id,tier)
            path = 'trees/'+id+'/'+tier
            size = nbt(DATA/('structure/'+path+'.nbt'),cells)
            crown_log_height = max(p[1] for p,s in cells.items() if s in tree_shapes.LOGS) + 1
            stem = 2 if tier=='small' else {'type':'minecraft:uniform','min_inclusive':4 if tier=='normal' else 12,
                    'max_inclusive':10 if tier=='normal' else tree['maxHeight']-crown_log_height}
            config = {'base_location':'chromusflora:trees/base_giant' if tier=='giant' else 'chromusflora:trees/base',
                      'canopy_location':'chromusflora:'+path, 'height':stem,
                      'log_provider':provider('chromusflora:'+tree['id']+'_log',{'axis':'y'}),
                      'leaves_provider':[provider('chromusflora:'+tree['id']+'_leaves',{'distance':'1','persistent':'false','waterlogged':'false'})],
                      'log_target':['minecraft:oak_log'], 'leaves_target':['minecraft:oak_leaves'],
                      'can_grow_on_filter':{'type':'minecraft:matching_block_tag','tag':'chromusflora:tree_soils'},
                      'can_leaves_place_filter':{'type':'minecraft:replaceable'},
                      'can_logs_place_filter':{'type':'minecraft:replaceable'},
                      'tree_filter_behavior':'BLOCK','max_log_depth':1,'decorators':[],
                      'replace_from_nbt':{},'random_rotation':True,'orientation':'STANDARD'}
            write(DATA/('worldgen/configured_feature/forms/'+id+'/'+tier+'.json'),{'type':'chromusflora:bounded_tree','config':config})
            measurements.append({'variant':id,'family':tree['id'],'tier':tier,'canopy_size':size,
                                 'leaf_blocks':sum(s==3 for s in cells.values()),'canopy_logs':sum(s in (2,4,5) for s in cells.values()),
                                 'base_trunk_columns':9 if tier=='giant' else 1,'height_provider':stem})
        write(DATA/('worldgen/configured_feature/variants/'+id+'.json'),
              {'type':'minecraft:random_selector','config':{
                  'features':[{'chance':0.25,'feature':placed_inline('forms/'+id+'/small')},
                              {'chance':1/15,'feature':placed_inline('forms/'+id+'/giant')}],
                  'default':placed_inline('forms/'+id+'/normal')}})
    for family, refs in families.items():
        selector('trees/'+family, refs)
    for variant in SPEC['variants']:
        if variant['aggregate']:
            selector('variants/'+variant['id'],['trees/'+variant['tree']])
    write(ROOT/'verification/tree-measurements.json',measurements)


def model(id, data):
    write(ASSETS/('models/block/'+id+'.json'),data)


def blockstate(id, variants):
    write(ASSETS/('blockstates/'+id+'.json'),{'variants':variants})


def item_model(id, target=None):
    write(ASSETS/('items/'+id+'.json'),{'model':{'type':'minecraft:model','model':'chromusflora:block/'+(target or id)}})


def cuboid(start,end,texture):
    return {'from':start,'to':end,'faces':{side:{'texture':texture} for side in ['down','up','north','south','west','east']}}


def drop(id, count=1):
    entry={'type':'minecraft:item','name':'chromusflora:'+id}
    if count>1:entry['functions']=[{'function':'minecraft:set_count','count':count}]
    return {'type':'minecraft:block','pools':[{'rolls':1,'conditions':[{'condition':'minecraft:survives_explosion'}],'entries':[entry]}]}


def loot(id,obj):
    write(DATA/('loot_table/blocks/'+id+'.json'),obj)


def block_resources():
    tags = collections.defaultdict(list)
    for tree in SPEC['trees']:
        id,palette=tree['id'],tree['palette']
        bark='chromusflora:block/wood/'+id+'/bark'
        end='chromusflora:block/wood/'+id+'/end'
        plank='chromusflora:block/wood/'+id+'/planks'
        stripped='chromusflora:block/wood/'+id+'/stripped'
        leaf='chromusflora:block/leaves_'+str(palette)
        for name,texture in [(id+'_log',bark),('stripped_'+id+'_log',stripped)]:
            model(name,{'parent':'minecraft:block/cube_column','textures':{'side':texture,'end':end}})
            blockstate(name,{'axis=y':{'model':'chromusflora:block/'+name},
                             'axis=x':{'model':'chromusflora:block/'+name,'x':90,'y':90},
                             'axis=z':{'model':'chromusflora:block/'+name,'x':90}})
            tags['logs'].append(name);tags['mineable/axe'].append(name)
            if tree['dimension']!='nether':tags['logs_that_burn'].append(name)
        for suffix,texture in [('planks',plank),('leaves',leaf)]:
            name=id+'_'+suffix
            model(name,{'parent':'minecraft:block/cube_all','textures':{'all':texture}})
            blockstate(name,{'':{'model':'chromusflora:block/'+name}})
            tags[suffix].append(name)
        tags['mineable/hoe'].append(id+'_leaves')
        tags['mineable/axe'].append(id+'_planks')
        name=id+'_sapling'
        sapling={'textures':{'bark':bark,'leaf':leaf,'particle':leaf},'elements':[
            cuboid([7,0,7],[9,7,9],'#bark'),cuboid([3,5,3],[13,10,13],'#leaf'),cuboid([5,10,5],[11,13,11],'#leaf')]}
        model(name,sapling)
        blockstate(name,{'':{'model':'chromusflora:block/'+name}})
        tags['saplings'].append(name)
        pot='potted_'+name
        model(pot,{'textures':{'pot':plank,'bark':bark,'leaf':leaf,'particle':plank},'elements':[
            cuboid([5,0,5],[11,5,11],'#pot'),cuboid([7,5,7],[9,9,9],'#bark'),cuboid([4,8,4],[12,12,12],'#leaf')]})
        blockstate(pot,{'':{'model':'chromusflora:block/'+pot}})
        tags['flower_pots'].append(pot)
        loot(pot,{'type':'minecraft:block','pools':[
            {'rolls':1,'entries':[{'type':'minecraft:item','name':'minecraft:flower_pot'}]},
            {'rolls':1,'entries':[{'type':'minecraft:item','name':'chromusflora:'+name}]}]})
        name=id+'_slab'
        for suffix,parent in [('', 'slab'),('_top','slab_top')]:
            model(name+suffix,{'parent':'minecraft:block/'+parent,'textures':{'top':plank,'bottom':plank,'side':plank}})
        blockstate(name,{'type=bottom':{'model':'chromusflora:block/'+name},'type=top':{'model':'chromusflora:block/'+name+'_top'},'type=double':{'model':'chromusflora:block/'+id+'_planks'}})
        slabloot=drop(name)
        slabloot['pools'][0]['entries'][0]['functions']=[{'function':'minecraft:set_count','count':2,'conditions':[{'condition':'minecraft:block_state_property','block':'chromusflora:'+name,'properties':{'type':'double'}}]}]
        loot(name,slabloot)
        name=id+'_stairs'
        for suffix,parent in [('', 'stairs'),('_inner','inner_stairs'),('_outer','outer_stairs')]:
            model(name+suffix,{'parent':'minecraft:block/'+parent,'textures':{'top':plank,'bottom':plank,'side':plank}})
        variants={}
        for facing,angle in [('east',0),('south',90),('west',180),('north',270)]:
            for half in ['bottom','top']:
                for shape in ['straight','inner_left','inner_right','outer_left','outer_right']:
                    suffix='' if shape=='straight' else '_'+shape.split('_')[0]
                    rotation=angle
                    if shape.endswith('left'):rotation-=90
                    if half=='top' and shape!='straight':rotation+=90
                    value={'model':'chromusflora:block/'+name+suffix,'uvlock':True,'y':rotation%360}
                    if half=='top':value['x']=180
                    variants['facing='+facing+',half='+half+',shape='+shape]=value
        blockstate(name,variants)
        name=id+'_fence'
        for suffix,parent in [('_post','fence_post'),('_side','fence_side'),('_inventory','fence_inventory')]:
            model(name+suffix,{'parent':'minecraft:block/'+parent,'textures':{'texture':plank}})
        multipart=[{'apply':{'model':'chromusflora:block/'+name+'_post'}}]
        for direction,rotation in [('north',0),('east',90),('south',180),('west',270)]:
            multipart.append({'when':{direction:'true'},'apply':{'model':'chromusflora:block/'+name+'_side','y':rotation,'uvlock':True}})
        write(ASSETS/('blockstates/'+name+'.json'),{'multipart':multipart})
        name=id+'_fence_gate'
        for suffix,parent in [('', 'template_fence_gate'),('_open','template_fence_gate_open'),('_wall','template_fence_gate_wall'),('_wall_open','template_fence_gate_wall_open')]:
            model(name+suffix,{'parent':'minecraft:block/'+parent,'textures':{'texture':plank}})
        variants={}
        for facing,angle in [('south',0),('west',90),('north',180),('east',270)]:
            for wall in [False,True]:
                for opened in [False,True]:
                    suffix=('_wall' if wall else '')+('_open' if opened else '')
                    variants[f'facing={facing},in_wall={str(wall).lower()},open={str(opened).lower()}']={'model':'chromusflora:block/'+name+suffix,'y':angle,'uvlock':True}
        blockstate(name,variants)
        for suffix in ['slab','stairs','fence','fence_gate']:
            tags[{'slab':'wooden_slabs','stairs':'wooden_stairs','fence':'wooden_fences','fence_gate':'fence_gates'}[suffix]].append(id+'_'+suffix)
            tags['mineable/axe'].append(id+'_'+suffix)
        for suffix in ['log','leaves','sapling','planks','slab','stairs','fence','fence_gate']:
            name=id+'_'+suffix
            item_model(name,name+'_inventory' if suffix=='fence' else None)
            if suffix not in ['leaves','slab']:loot(name,drop(name))
        item_model('stripped_'+id+'_log');loot('stripped_'+id+'_log',drop('stripped_'+id+'_log'))
        silk={'condition':'minecraft:match_tool','predicate':{'predicates':{'minecraft:enchantments':[{'enchantments':'minecraft:silk_touch','levels':{'min':1}}]}}}
        shears={'condition':'minecraft:match_tool','predicate':{'items':'minecraft:shears'}}
        special={'condition':'minecraft:any_of','terms':[silk,shears]}
        leafloot={'type':'minecraft:block','pools':[{'rolls':1,'entries':[{'type':'minecraft:alternatives','children':[
            {'type':'minecraft:item','name':'chromusflora:'+id+'_leaves','conditions':[special]},
            {'type':'minecraft:item','name':'chromusflora:'+id+'_sapling','conditions':[{'condition':'minecraft:survives_explosion'},
             {'condition':'minecraft:table_bonus','enchantment':'minecraft:fortune','chances':[0.06,0.08,0.1,0.13]}]}]}]}]}
        if id=='orchard':
            leafloot['pools'].append({'rolls':1,'conditions':[{'condition':'minecraft:inverted','term':special}],
                'entries':[{'type':'minecraft:item','name':'chromusflora:grove_fruit','conditions':[{'condition':'minecraft:random_chance','chance':0.08},{'condition':'minecraft:survives_explosion'}]}]})
        loot(id+'_leaves',leafloot)
        write(DATA/('tags/item/'+id+'_logs.json'),{'replace':False,'values':['chromusflora:'+id+'_log','chromusflora:stripped_'+id+'_log']})
        write(DATA/('recipe/'+id+'_planks.json'),{'type':'minecraft:crafting_shapeless','category':'building','group':'planks','ingredients':['#chromusflora:'+id+'_logs'],'result':{'id':'chromusflora:'+id+'_planks','count':4}})
        for suffix,pattern,count in [('slab',['###'],6),('stairs',['#  ','## ','###'],4),('fence',['#S#','#S#'],3),('fence_gate',['S#S','S#S'],1)]:
            keys={'#':'chromusflora:'+id+'_planks'}
            if 'S' in ''.join(pattern):keys['S']='minecraft:stick'
            write(DATA/('recipe/'+id+'_'+suffix+'.json'),{'type':'minecraft:crafting_shaped','category':'building','pattern':pattern,'key':keys,'result':{'id':'chromusflora:'+id+'_'+suffix,'count':count}})
    for tag,values in tags.items():
        write(RES/('data/minecraft/tags/block/'+tag+'.json'),{'replace':False,'values':['chromusflora:'+x for x in sorted(set(values))]})
        if tag not in ['flower_pots','mineable/axe','mineable/hoe']:
            write(RES/('data/minecraft/tags/item/'+tag+'.json'),{'replace':False,'values':['chromusflora:'+x for x in sorted(set(values))]})
    model('grove_fruit',{'textures':{'fruit':'chromusflora:block/leaves_2','stem':'chromusflora:block/wood/orchard/bark','particle':'chromusflora:block/leaves_2'},
                        'elements':[cuboid([4,3,4],[12,11,12],'#fruit'),cuboid([7,11,7],[9,14,9],'#stem')]})
    item_model('grove_fruit')
    write(DATA/'tags/block/tree_soils.json',{'replace':False,'values':['#minecraft:dirt','minecraft:grass_block','minecraft:mycelium','minecraft:podzol','minecraft:mud','minecraft:moss_block','minecraft:sand','minecraft:red_sand','minecraft:snow_block','minecraft:stone','minecraft:calcite','minecraft:basalt','minecraft:netherrack','minecraft:soul_soil','minecraft:crimson_nylium','minecraft:warped_nylium','minecraft:end_stone']})


def biome_resources():
    reference=json.loads((ROOT/'atelier/vanilla-biome-reference.json').read_text(encoding='utf-8'))
    tags=collections.defaultdict(list)
    for index,biome in enumerate(SPEC['biomes']):
        id=biome['id'];dim=biome['dimension']
        source=reference[biome['vanilla'].split(':')[1]]
        obj=copy.deepcopy(source)
        obj['attributes']={k:v for k,v in obj.get('attributes',{}).items() if not k.startswith('minecraft:audio/')}
        if dim=='overworld':obj['attributes']['minecraft:visual/sky_color']=['#82b2d5','#8fa7d1','#b5acc8','#89bcb8'][index%4]
        obj['effects']['water_color']=['#426c82','#4c7a78','#517f91','#496d78'][index%4]
        obj['effects']['foliage_color']=['#428b85','#698d67','#b08f46','#816b91'][index%4]
        obj['effects']['grass_color']=['#69896b','#839163','#6c927f','#88946b'][index%4]
        for stage in obj['features']:
            stage[:]=[name for name in stage if not any(word in name for word in ['tree','fungi','huge_mushroom','bamboo_vegetation','bamboo_light','mangrove'])]
        selector('biomes/'+id,['trees/'+name for name in biome['trees']])
        if dim=='nether':
            placement=[{'type':'minecraft:count_on_every_layer','count':biome['density']},{'type':'minecraft:biome'}]
        else:
            placement=[{'type':'minecraft:count','count':biome['density']},{'type':'minecraft:in_square'},
                       {'type':'minecraft:surface_water_depth_filter','max_water_depth':0},
                       {'type':'minecraft:heightmap','heightmap':'OCEAN_FLOOR'},
                       {'type':'minecraft:block_predicate_filter','predicate':{'type':'minecraft:matching_block_tag','tag':'chromusflora:tree_soils','offset':[0,-1,0]}},
                       {'type':'minecraft:biome'}]
        write(DATA/('worldgen/placed_feature/biomes/'+id+'.json'),{'feature':'chromusflora:biomes/'+id,'placement':placement})
        while len(obj['features'])<11:obj['features'].append([])
        obj['features'][9].append('chromusflora:biomes/'+id)
        write(DATA/('worldgen/biome/'+id+'.json'),obj)
        tags['is_'+dim].append(id)
        vanilla=biome['vanilla'].split(':')[1]
        for name,needles in [('is_forest',['forest','grove']),('is_taiga',['taiga']),('is_jungle',['jungle']),('is_savanna',['savanna']),('is_badlands',['badlands']),('is_beach',['beach','shore']),('is_ocean',['ocean']),('is_mountain',['peaks','windswept'])]:
            if any(n in vanilla for n in needles):tags[name].append(id)
        if dim=='overworld':
            for name in ['has_structure/mineshaft','has_structure/stronghold']:tags[name].append(id)
    for tag,values in tags.items():write(RES/('data/minecraft/tags/worldgen/biome/'+tag+'.json'),{'replace':False,'values':['chromusflora:'+id for id in values]})


def localization():
    en={'itemGroup.chromusflora':'Chromus Flora','item.chromusflora.grove_fruit':'Grove Fruit',
        'screen.chromusflora.title':'Chromus Flora Settings','screen.chromusflora.weight':'Biome region weight: %s',
        'screen.chromusflora.spawns':'JaizMod creature integration: %s','screen.chromusflora.features':'JaizMod vegetation integration: %s',
        'screen.chromusflora.restart':'Changes apply after a full game/server restart.',
        'screen.chromusflora.saved':'Saved. Restart before generating new terrain.',
        'screen.chromusflora.save_failed':'Could not save. Check the game log.',
        'screen.chromusflora.save':'Save','tooltip.chromusflora.height':'Trunk height: %s–%s blocks',
        'config.jade.plugin_chromusflora.tree_height':'Tree height'}
    pt={'itemGroup.chromusflora':'Chromus Flora','item.chromusflora.grove_fruit':'Fruta do Bosque',
        'screen.chromusflora.title':'Configurações do Chromus Flora','screen.chromusflora.weight':'Peso das regiões de biomas: %s',
        'screen.chromusflora.spawns':'Integração de criaturas JaizMod: %s','screen.chromusflora.features':'Integração de vegetação JaizMod: %s',
        'screen.chromusflora.restart':'Alterações exigem reiniciar o jogo/servidor.',
        'screen.chromusflora.saved':'Salvo. Reinicie antes de gerar novos terrenos.',
        'screen.chromusflora.save_failed':'Não foi possível salvar. Consulte o log.',
        'screen.chromusflora.save':'Salvar','tooltip.chromusflora.height':'Altura do tronco: %s–%s blocos',
        'config.jade.plugin_chromusflora.tree_height':'Altura das árvores'}
    translations={'araucaria':'Araucária','aspen':'Álamo','baobab':'Baobá','cypress':'Cipreste','ebony':'Ébano','fir':'Abeto','holly':'Azevinho','ironwood':'Pau-ferro','jacaranda':'Jacarandá','joshua':'Josué','mahogany':'Mogno','maple':'Bordo','orchard':'Pomar','palm':'Palmeira','pine':'Pinheiro','redwood':'Sequoia','willow':'Salgueiro','witch_hazel':'Hamamélis','oak':'Carvalho','birch':'Bétula','spruce':'Pinheiro-nórdico'}
    for tree in SPEC['trees']:
        id=tree['id'];name=id.replace('_',' ').title();local=translations.get(id,name)
        for suffix,en_suffix,pt_suffix in [('log','Log','Tronco de'),('leaves','Leaves','Folhas de'),('sapling','Sapling','Muda de'),('planks','Planks','Tábuas de'),('slab','Slab','Laje de'),('stairs','Stairs','Escadas de'),('fence','Fence','Cerca de'),('fence_gate','Fence Gate','Portão de')]:
            key='block.chromusflora.'+id+'_'+suffix;en[key]=name+' '+en_suffix;pt[key]=pt_suffix+' '+local
        en['block.chromusflora.stripped_'+id+'_log']='Stripped '+name+' Log';pt['block.chromusflora.stripped_'+id+'_log']='Tronco Descascado de '+local
        en['block.chromusflora.potted_'+id+'_sapling']='Potted '+name+' Sapling';pt['block.chromusflora.potted_'+id+'_sapling']='Vaso com Muda de '+local
    for biome in SPEC['biomes']:
        key='biome.chromusflora.'+biome['id'];name=biome['id'].replace('_',' ').title();en[key]=name;pt[key]=name
    write(ASSETS/'lang/en_us.json',en);write(ASSETS/'lang/pt_br.json',pt)


def textures():
    from PIL import Image
    atlas=Image.open(ROOT/'atelier/original-texture-atlas.png').convert('RGBA')
    xs=[0,313,627,940,1254];ys=[0,314,627,907,1254]
    folder=ASSETS/'textures/block';folder.mkdir(parents=True,exist_ok=True)
    for column in range(4):
        tile=atlas.crop((xs[column]+2,ys[3]+2,xs[column+1]-2,ys[4]-2))
        tile.resize((64,64),Image.Resampling.NEAREST).save(folder/('leaves_'+str(column)+'.png'))
    wood=json.loads((ROOT/'atelier/wood/species.json').read_text(encoding='utf-8'))
    sheets={number:Image.open(ROOT/('atelier/wood/sheet_'+str(number)+'.png')).convert('RGBA')
            for number in sorted({entry['sheet'] for entry in wood['species']})}
    for entry in wood['species']:
        sheet=sheets[entry['sheet']]
        target=folder/'wood'/entry['id'];target.mkdir(parents=True,exist_ok=True)
        for offset,kind in enumerate(wood['kinds']):
            column=entry['column'];row=entry['first_row']+offset
            grid=wood['sheets'][str(entry['sheet'])]
            inset=grid['inset']
            box=(grid['x'][column]+inset,grid['y'][row]+inset,
                 grid['x'][column+1]-inset,grid['y'][row+1]-inset)
            tile=sheet.crop(box).resize((wood['tile_size'],wood['tile_size']),Image.Resampling.NEAREST)
            periodic_tile(tile,wood['edge_blend_pixels']).save(target/(kind+'.png'))
    icon=Image.open(ROOT/'branding/chromus-flora-official.png')
    icon.resize((256,256),Image.Resampling.LANCZOS).save(ASSETS/'icon.png')


def main():
    if RES.exists():
        shutil.rmtree(RES)
    RES.mkdir(parents=True,exist_ok=True)
    write(RES/'chromusflora/catalog.json',{'trees':SPEC['trees'],'biomes':SPEC['biomes']})
    write(RES/'chromusflora/jaiz-compatibility.json',json.loads((ROOT/'atelier/jaiz-compatibility.json').read_text()))
    tree_resources();block_resources();biome_resources();localization();textures()
    from palette_overrides import apply as apply_palette_overrides
    apply_palette_overrides()
    from wood_recipes import generate as wood_recipes
    from resources_263 import generate as resources_263
    wood_recipes()
    import runpy
    runpy.run_path(str(ROOT / "tools/generate-door-test-gallery.py"), run_name="__main__")
    resources_263()
    write(RES/'chromusflora.chunk-read.mixins.json',{'required': True, 'minVersion': '0.8', 'package': 'dev.chromus.flora.mixin', 'plugin': 'dev.chromus.flora.compat.ChunkReadMixinPlugin', 'compatibilityLevel': 'JAVA_25', 'priority': 100, 'mixins': ['ChunkReadCompatibility']})
    write(RES/'chromusflora.chunk-safety.mixins.json',{'required': True, 'minVersion': '0.8', 'package': 'dev.chromus.flora.mixin', 'plugin': 'dev.chromus.flora.compat.NaturalistChunkMixinPlugin', 'compatibilityLevel': 'JAVA_25', 'mixins': ['NaturalistHippoCompatibility'], 'injectors': {'defaultRequire': 1}})
    write(RES/'fabric.mod.json',{'schemaVersion':1,'id':'chromusflora','version':'${version}',
        'name':'Chromus Flora','description':'Original forests and biomes across the Overworld, Nether and End.',
        'authors':['Chromus Master'],'license':'MIT','icon':'assets/chromusflora/icon.png','environment':'*',
        'mixins':['chromusflora.chunk-read.mixins.json','chromusflora.chunk-safety.mixins.json'],
        'entrypoints':{'client':['dev.chromus.flora.client.FloraClient'],'main':['dev.chromus.flora.ChromusFlora'],'terrablender':['dev.chromus.flora.world.FloraTerraBlender'],
                      'modmenu':['dev.chromus.flora.client.FloraModMenu'],'jade':['dev.chromus.flora.client.FloraJade']},
        'depends':{'fabricloader':'>=0.19.5','minecraft':'${minecraft}','java':'>=25','fabric-api':'>=0.161.0',
                   'terrablender':'${terrablender}','ohthetreesyoullgrow':'${trees}'},
        'suggests':{'jaizmod':'>=2.3.11','appleskin':'*','jade':'*','modmenu':'*'},
        'breaks':{'jaizmod':'<2.3.11'},'custom':{'modmenu':{'badges':[]},
        'chromusflora:build':{'internal_version':'${internal_version}','source_revision':'${source_revision}'}}})
    write(ROOT/'docs/content-coverage.json',{'biomes':SPEC['biomes'],'trees':SPEC['trees'],'variants':SPEC['variants'],
            'excluded_non_tree_candidates':SPEC['excluded_candidates'],'arr_assets_copied':0,'arr_code_copied':0})
    print(json.dumps({'biomes':len(SPEC['biomes']),'families':len(TREES),'variants':len(SPEC['variants']),
          'resources':sum(p.is_file() for p in RES.rglob('*'))}))


if __name__=='__main__':
    main()
