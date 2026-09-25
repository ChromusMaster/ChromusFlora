# English

Global static scan: **PASS**. Date: 2026-09-25.

| Checked content | Count |
|---|---:|
| Biomes | 92 |
| Tree/fungus families | 83 |
| Named configurations, including selectors | 458 |
| Blocks / items | 830 / 748 |
| Resource JSON files | 6,377 |
| Original NBT structures | 1,121 |
| Configured small/normal/giant forms | 1,119 |
| Java source files | 12 |

`global-scan.json` records the executable offline scan and its limits.
`java-static-review.json` records Java syntax parsing, source hashes, 67 imports
matched against release class files and the selected API signatures inspected.
`inspected-artifacts.json` records hashes of external artifacts inspected;
those jars are not included in this source package.

The scan found no missing checked resource references, duplicate JSON keys,
invalid NBT bounds or markers, unsupported canopy leaves, feature dependency
cycles, biome catalogue omissions, tree registry omissions, height ceiling
violations, unknown checked Jaiz identifiers or byte-identical legacy Java,
PNG, NBT or OGG resources in the active source tree. New Java/Python files have
no internal comments. Java syntax parsing reported no syntax errors.

During review, Nether climate registration, the End biome tag, wooden stair
tags, structural fungus coverage, tree family aliases and giant height bounds
were corrected. Texture tiles were visually inspected. The final ZIP is
checked for integrity and prohibited compiled artifacts, then extracted and
scanned again before delivery.

**No Gradle build, Java compilation, game launch, server launch or multiplayer
test was performed.** A static PASS is not proof of zero compiler warnings,
zero runtime bugs or confirmed compatibility. Minecraft's codecs and registries
must still load successfully during the user's local game checks. This is why
the package remains an alpha source candidate.

Repeat the scan with `py -3 tools\scan.py`. Build locally with JDK 25 using
`.\gradlew.bat clean build --warning-mode=fail`. See the README for installation
and the client/server verification sequence.

# Português do Brasil

Scan global estático: **APROVADO**. Data: 25/09/2026.

Foram conferidos 92 biomas, 83 famílias de árvores/fungos, 458 configurações
nomeadas, 830 blocos, 748 itens, 6.377 JSONs, 1.121 estruturas NBT, 1.119 formas
pequenas/normais/gigantes e 12 arquivos Java.

`global-scan.json` registra o resultado do scanner e suas limitações.
`java-static-review.json` registra a análise sintática, hashes dos fontes,
67 imports encontrados nos artefatos oficiais e assinaturas selecionadas das
APIs. `inspected-artifacts.json` identifica os artefatos consultados por hash;
seus jars não integram a entrega.

Não foram encontradas referências ausentes dentre as verificadas, chaves JSON
duplicadas, limites/marcadores NBT inválidos, folhas sem sustentação, ciclos nas
features, omissões dos catálogos de biomas/registros de árvores, alturas acima
do limite, identificadores Jaiz desconhecidos dentre os conferidos ou recursos
Java/PNG/NBT/OGG idênticos aos antigos no código ativo. Os novos arquivos Java
e Python não contêm comentários internos. A análise sintática Java passou.

A revisão corrigiu o registro climático do Nether, tag do End, tags das
escadas, cobertura de fungos estruturais, associações de famílias e limites
das árvores gigantes. As texturas foram inspecionadas visualmente. Antes da
entrega, o ZIP final tem sua integridade e ausência de compilados verificadas;
em seguida é extraído e submetido novamente ao scan.

**Não houve build Gradle, compilação Java, abertura do jogo, inicialização do
servidor nem teste multiplayer.** Aprovação estática não comprova ausência de
warnings de compilação, bugs em execução ou compatibilidade confirmada.
Codecs e registros precisam ser carregados nos testes locais do usuário.
O pacote permanece um candidato alfa em código-fonte por esse motivo.

Repita o scan com `py -3 tools\scan.py`. Compile com JDK 25 usando
`.\gradlew.bat clean build --warning-mode=fail`. O README detalha instalação
e verificações de cliente/servidor.
