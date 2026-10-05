import json
import struct
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VERSION = next(line.split('=', 1)[1] for line in (ROOT / 'gradle.properties').read_text().splitlines() if line.startswith('mod_version='))
for target in ['26.2', '26.3']:
    path = ROOT / f'build/{target}/chromus-flora-{VERSION}-{target}.jar'
    if not path.is_file():raise SystemExit('Missing artifact: ' + str(path))
    with zipfile.ZipFile(path) as jar:
        if jar.testzip() is not None:raise SystemExit('Corrupt JAR: ' + str(path))
        names = set(jar.namelist())
        metadata = json.loads(jar.read('fabric.mod.json'))
        if metadata['id'] != 'chromusflora' or metadata['version'] != VERSION + '-' + target or metadata['depends']['minecraft'] != target:
            raise SystemExit('Wrong artifact metadata: ' + str(path))
        for entries in metadata['entrypoints'].values():
            for entrypoint in entries:
                if entrypoint.replace('.', '/') + '.class' not in names:raise SystemExit('Missing entrypoint: ' + entrypoint)
        classes = [n for n in names if n.startswith('dev/chromus/') and n.endswith('.class')]
        config_name = 'chromusflora.chunk-read.mixins.json'
        safety_config_name = 'chromusflora.chunk-safety.mixins.json'
        if metadata.get('mixins') != [config_name, safety_config_name]:raise SystemExit('Missing chunk mixin registration')
        config = json.loads(jar.read(config_name))
        if config.get('required') is not True or config.get('plugin') != 'dev.chromus.flora.compat.ChunkReadMixinPlugin':
            raise SystemExit('Invalid chunk-read mixin configuration')
        for class_name in ['compat/ChunkReadMixinPlugin', 'mixin/ChunkReadCompatibility']:
            if 'dev/chromus/flora/' + class_name + '.class' not in names:raise SystemExit('Missing chunk repair class: ' + class_name)
        safety_config = json.loads(jar.read(safety_config_name))
        if (safety_config.get('required') is not True
                or safety_config.get('plugin') != 'dev.chromus.flora.compat.NaturalistChunkMixinPlugin'
                or safety_config.get('mixins') != ['NaturalistHippoCompatibility']
                or safety_config.get('injectors', {}).get('defaultRequire') != 1):
            raise SystemExit('Invalid Naturalist chunk-safety mixin configuration')
        for class_name in ['compat/NaturalistChunkMixinPlugin', 'mixin/NaturalistHippoCompatibility']:
            if 'dev/chromus/flora/' + class_name + '.class' not in names:raise SystemExit('Missing chunk safety class: ' + class_name)
        if not classes:raise SystemExit('No compiled Chromus Flora classes')
        for name in classes:
            if struct.unpack('>IHH', jar.read(name)[:8]) != (0xCAFEBABE, 0, 69):raise SystemExit('Unexpected Java bytecode version: ' + name)
        folder = 'configured_feature' if target == '26.2' else 'feature'
        wrong = 'feature' if target == '26.2' else 'configured_feature'
        if len([n for n in names if n.startswith('data/chromusflora/worldgen/' + folder + '/') and n.endswith('.json')]) != 1752:
            raise SystemExit('Incomplete tree features: ' + str(path))
        if any(n.startswith('data/chromusflora/worldgen/' + wrong + '/') and n.endswith('.json') for n in names):raise SystemExit('Mixed game resource schemas')
        for name in names:
            if name.endswith('.json'):
                text = jar.read(name).decode('utf-8')
                json.loads(text)
                if '${version}' in text or '${minecraft}' in text:raise SystemExit('Unexpanded resource: ' + name)
        for class_name in ['client/FloraRenderSubmission', 'FloraBoats', 'client/FloraClient', 'client/FloraBoatRenderer', 'client/FloraChestRenderer', 'FloraFurniture', 'block/FloraChest', 'block/FloraChestEntity', 'block/FloraCraftingTable']:
            if 'dev/chromus/flora/' + class_name + '.class' not in names:raise SystemExit('Missing furniture class: ' + class_name)
        catalog = json.loads(jar.read('chromusflora/catalog.json'))
        expected_boats = {'chromusflora:' + tree['id'] + '_boat' for tree in catalog['trees']}
        for kind, tag in [('item', 'boats'), ('entity_type', 'boat')]:
            data = json.loads(jar.read(f'data/minecraft/tags/{kind}/{tag}.json'))
            if data.get('replace') is not False or set(data['values']) != expected_boats:raise SystemExit('Incomplete boat tag: ' + kind)
        if metadata['entrypoints'].get('client') != ['dev.chromus.flora.client.FloraClient']:raise SystemExit('Missing furniture/boat client entrypoint')
        if 'data/chromusflora/recipe/boat.json' in names:raise SystemExit('Stale generic boat recipe')
        for tree in catalog['trees']:
            species = tree['id']
            for suffix in ['crafting_table', 'chest', 'boat']:
                if f'data/chromusflora/recipe/{species}_{suffix}.json' not in names:raise SystemExit('Missing furniture recipe: ' + species)
            for suffix in ['chest', 'boat']:
                if f'assets/chromusflora/models/item/{species}_{suffix}.json' not in names:raise SystemExit('Missing item model: ' + species + '_' + suffix)
            for kind in ['single', 'left', 'right']:
                model = json.loads(jar.read(f'assets/chromusflora/models/block/{species}_chest_{kind}.json'))
                if model.get('elements') != []:raise SystemExit('Static/animated chest overlap: ' + species)
            sprite = jar.read(f'assets/chromusflora/textures/item/door/{species}.png')
            if struct.unpack('>II', sprite[16:24]) != (64,128):raise SystemExit('Invalid door sprite: ' + species)
        for kind in ['chest', 'crafting_table']:
            if f'data/chromusflora/recipe/{kind}.json' in names:raise SystemExit('Stale duplicate recipe: ' + kind)
            recipe = json.loads(jar.read(f'data/minecraft/recipe/{kind}.json'))
            if recipe.get('group') != kind or recipe['key']['#'].get('fabric:type') != 'fabric:difference':raise SystemExit('Missing recipe partition: ' + kind)
        if len([n for n in names if n.startswith('data/chromusflora/recipe/') and n.endswith('.json')]) != 998:raise SystemExit('Missing recipes')
    print('PASS:', path.relative_to(ROOT))
