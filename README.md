# English

Chromus Flora — Minecraft 26.2 / Fabric — 0.1.0-alpha.1.fix10+26.2.
Complete source distribution. No compiled mod or dependency binaries included.

## Build on Windows

Install JDK 25; set JAVA_HOME to the JDK directory and add its bin directory to PATH.
Close the game and IDE before replacing files. Extract this ZIP directly over
D:\Repository\ChromusFlora (build.gradle must be directly in that directory).
Open a separate PowerShell there and run:

```powershell
java -version
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\tools\verify-source.ps1
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\tools\clean-project.ps1 -WhatIf
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\tools\clean-project.ps1
.\gradlew.bat build --no-daemon --warning-mode=fail
```

The Windows launcher downloads Gradle 9.5.1 with SHA-256 verification. Internet
access is required for dependencies. No global Gradle installation is needed.
Do not add clean: the cleanup script already moves the previous build directory.
It preserves obsolete files in a sibling backup directory, including legacy modules,
old reports and redundant textures. The explicit list is verification/cleanup-paths.json.
It does not remove .git, game worlds, mods, configuration or Gradle caches.
Review the backup before deleting it yourself. No PowerShell script was executed
in the delivery environment; only static checks and an overlay simulation were performed.

After BUILD SUCCESSFUL, replace the previous mod JAR in the instance with
build\libs\chromus-flora-0.1.0-alpha.1.fix10+26.2.jar (not the -sources JAR).
Keep just one Chromus Flora JAR. Runtime: Minecraft 26.2, Fabric Loader 0.19.5,
Fabric API 0.161.0+26.2, TerraBlender 26.2-26.2.0.0.2, and Oh The Trees You'll Grow
(version pinned by Modrinth ID 2frKVds1). Optional integrations: JaizMod 2.3.11,
ModMenu, Jade and AppleSkin. Exact build pins remain in gradle.properties.

Linux/macOS: install JDK 25 and Gradle 9.5.1, then use sh ./gradlew build
--no-daemon --warning-mode=fail. The source-only shell launcher does not require
a bundled gradle-wrapper.jar. Windows uses its existing PowerShell bootstrap.

## Content and maintenance

83 wood families now have 4 individual 64x64 textures each: bark, end grain,
stripped wood and planks. Slabs, stairs, fences, gates and sapling stems use the
matching family. Six original generated atlases and the exact crop coordinates
are retained in atelier/wood. docs/WOOD_GALLERY.html previews all families locally.
Palettes interpret the names artistically; they are not botanical color measurements.
No original mod texture was supplied as a reference for the new wood artwork.

Java sources, identifiers, biome definitions and the Fix 8 Jaiz integration are unchanged.
Normal and giant NBT tree structures now have connected, oriented branches and broader,
asymmetric crowns. Small tree geometry is unchanged. Trees keep species shape profiles:
conifer tiers, spreading forks, hanging foliage, palm fronds and fungal caps.
Existing worlds show the new textures after restart. New branches only appear on newly
generated or newly grown trees; existing trees are not rebuilt. No new save is required
for textures or sapling tests. Runtime remains to be tested.

For resource maintenance only (not required to compile): install Python 3 and Pillow
(python -m pip install Pillow), then run python tools/generate.py and python tools/scan.py.
python tools/check-visual-resources.py checks periodic texture edges, connected branches
and leaf support; scan.py includes these checks.
python tools/check-feature-order.py checks the stored static generation-order model.
After intentional edits, the delivery checksum manifest will report changes; it describes
the delivered snapshot and is not a build requirement. Never regenerate it merely to
hide unexpected changes. New resources are already included in this ZIP.

The project license and asset provenance remain in LICENSE.txt and ASSET_PROVENANCE.md.
Validation scope and limitations: verification/FIX10.json. No Gradle build or game execution
was performed for this delivery.

# Português do Brasil

Entrega completa em fontes da Fix 10, com 83 famílias de madeira e 332 texturas
individuais de 64×64. Cada família possui casca, topo cortado, tronco descascado
e tábuas. Escadas, lajes, cercas, portões e caules das mudas usam a mesma madeira.
As cores são interpretações artísticas dos nomes, sem copiar texturas dos mods de origem.
A galeria docs/WOOD_GALLERY.html permite conferir todas as famílias.

## Aplicação e compilação no Windows

1. Instale JDK 25 e configure JAVA_HOME e PATH. Confira java -version.
2. Feche Minecraft e VS Code. Extraia o ZIP por cima de D:\Repository\ChromusFlora.
   Não crie outra pasta ChromusFlora dentro dela. Substitua os arquivos existentes.
3. Execute os quatro comandos PowerShell do bloco acima, após java -version:
   verificação, simulação da limpeza, limpeza e build.
4. A limpeza move arquivos antigos e a pasta build para um backup ao lado do projeto.
   Confira verification/cleanup-paths.json para a lista exata. Não apaga .git,
   mundos, mods, configurações ou caches. Apague o backup somente após validá-lo.
5. Depois de BUILD SUCCESSFUL, substitua o JAR antigo pelo
   chromus-flora-0.1.0-alpha.1.fix10+26.2.jar de build\libs, sem -sources.
6. Reinicie o jogo e confira troncos, troncos descascados, tábuas e derivados.
   As texturas atualizam os blocos existentes. Os galhos aparecem apenas em árvores
   novas: cresça mudas ou explore terreno ainda não gerado. Não é preciso apagar seu mundo.

Não é preciso recompilar no VS Code. O inicializador baixa o Gradle correto e
valida seu hash. Internet é necessária para dependências. Não acrescente clean.
A versão do JAR agora identifica a Fix 10 explicitamente.

A limpeza inclui Common/Fabric/Forge antigos, saídas binárias, relatórios substituídos
e as 12 texturas genéricas de madeira. Os fontes Java ativos e a correção da Fix 8
foram preservados. Árvores normais e gigantes passam a ter ramificações orientadas,
conectadas e copas assimétricas. Árvores pequenas mantêm a geometria anterior. O ZIP já está limpo; o script retira sobras de extrações anteriores.
Licenças, geradores, atlas originais e referências necessárias às verificações permanecem.

Os recursos já estão gerados. Python e Pillow só são necessários para regenerá-los,
não para compilar o mod. O manifesto verifica o pacote entregue; alterações intencionais
nos fontes passam a divergir dele. Ele não participa do build.

Validação desta entrega: inspeção estática e simulação da sobreposição. Não compilei,
não executei PowerShell nem iniciei Minecraft. O visual e o build precisam ser
confirmados no seu ambiente. Relatório: verification/FIX10.json.

## Fix 10 — validação visual

As 332 texturas passam por recorte interno sem bordas e compatibilização determinística
das extremidades em tools/texture_tiles.py. A correspondência exata dos pixels opostos
é validada; shaders, iluminação, mipmaps e percepção de repetição ainda precisam ser
conferidos no jogo. docs/TEXTURE_TILING_PREVIEW.png mostra repetição dos PNGs entregues.

As novas copas incluem galhos em alturas distintas e bifurcações, com eixo x/y/z nos
troncos. A altura da seção reta foi reduzida para acomodar a copa ramificada. Os limites
por família permanecem respeitados para a altura de madeira. Folhas e marcador técnico
são considerados pela proteção de altura do recurso no jogo.
A prévia docs/TREE_STRUCTURE_PREVIEW.png é uma projeção dos voxels NBT, com cores
esquemáticas e base exemplificada de 18 blocos; não é uma captura do Minecraft.
A galeria docs/WOOD_GALLERY.html mostra os arquivos de textura utilizados.
