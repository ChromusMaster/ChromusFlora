# Chromus Flora — English

Original biome and tree recreation for Minecraft Java **26.2 / Fabric / Java 25**.
Version: **0.1.0-alpha.1+26.2**. Dependency review: **2026-09-25**.

This source release contains 92 biome definitions: 72 Overworld, 12 Nether and
8 End biomes. It registers 83 tree/fungus families, 830 blocks and 748 items.
The merged catalogue contains 458 named tree configurations, including
selectors and independently generated replacements for structural fungi.
Selectors are not counted as separate tree species.

All new tree templates, block geometry, textures and icons were created for
this project. No ARR BYG/BWG implementation or visual asset is included.
Read `ASSET_PROVENANCE.md` for provenance and scope.

## Compilation correction — Fix 2

Adds `com.google.errorprone:error_prone_annotations:2.50.0` to both main and
client compile-only classpaths. Gson 2.14.0 references `InlineMe`; without its
annotation definitions, javac emits classfile warnings and `-Werror` correctly
stops the build. The missing annotation class and its `replacement`, `imports`
and `staticImports` members were checked in the published stable artifact.

`-Xlint:all`, `-Werror` and `org.gradle.warning.mode=fail` remain enabled. No
warning suppression, annotation processor, Gson override or additional runtime
mod is introduced. The dependency is resolved from Maven Central at build time
and is not bundled in the mod. The Fix 1 bootstrap correction is retained.

Extract this complete source package over the repository root and run:

```powershell
.\gradlew.bat clean build --warning-mode=fail
```

The user-reported compilation failed before this fix. No compilation or game
execution was performed by the assistant for Fix 2. Static validation and
package verification are recorded in `verification/DEPENDENCY_FIX2.md`.

## Delivery correction — Fix 1

This delivery replaces the incomplete Alpha 1 ZIP and fixes the PowerShell
bootstrap. SHA-256 checking now uses .NET directly; extraction uses .NET
ZipFile. Neither `Get-FileHash` nor `Expand-Archive` is required. A corrupt cached
Gradle archive is discarded and downloaded again. Extraction is staged; a
completion marker is written only after the archive is verified and extracted.

Download the complete replacement ZIP and extract it over the project root,
replacing all matching files, including `verification/reference-index.json`.
Do not continue from an extraction that reports archive errors. You do not
need to delete your global Gradle cache or reinstall Java for this correction.
Immediately after extraction, verify the delivered files in PowerShell:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\tools\verify-source.ps1
.\gradlew.bat clean build --warning-mode=fail
```

The source verifier compares against the delivery manifest; intentional source
edits will also be reported as changes. It is an optional delivery check, not
a mandatory build gate. See `verification/BOOTSTRAP_FIX1.md` for verification
scope and the archive failure found during this correction.

## Validation status

**Source candidate: Java compilation and in-game execution have not been
performed.** The offline global scan checks the complete active resource tree,
catalogue coverage, JSON syntax and duplicate keys, NBT geometry and markers,
tree height bounds, leaf support, feature dependency cycles, vanilla feature
order, models/textures, recipes/loot/tags, compatibility identifiers and
byte-identical legacy code/image/NBT contamination. Its exact results are in
`verification/global-scan.json` and `verification/SCAN.md`.

Java syntax and selected public API signatures were inspected separately.
Static inspection cannot certify zero compiler warnings, correct registry
loading, world generation or multiplayer compatibility. The build treats Java
warnings and Gradle deprecation warnings as errors. Complete the local checks
below before using this alpha in a persistent world.

## Pinned toolchain and dependencies

| Component | Version | Requirement |
|---|---|---|
| Minecraft | 26.2 | Required |
| Java JDK | 25 | Build and game |
| Gradle | 9.5.1 | Downloaded by the source launcher |
| Fabric Loom | 1.17.21 | Stable 1.17 series |
| Fabric Loader | 0.19.5 | Latest stable at review |
| Fabric API | 0.161.0+26.2 | Required stable release |
| Error Prone annotations | 2.50.0 | Compile only; stable release |
| TerraBlender Fabric | 26.2.0.0.2 | Required; **beta explicitly accepted** |
| Oh The Trees You'll Grow | 11.0.1 | Required stable release |
| ModMenu | 20.0.3 | Optional client integration |
| Jade | 26.2.11+fabric | Optional client integration |
| AppleSkin | 3.0.10+mc26.2 | Optional client integration |
| JaizMod | Supplied 2.3.11 / 26.2 source | Optional compatibility target |

TerraBlender's Maven version is `26.2-26.2.0.0.2`. It is the only authorized
prerelease dependency. Modrinth dependencies use immutable version IDs listed
in `gradle.properties`; there are no dynamic `latest` selectors. Libraries are
downloaded during your build and are not included in this archive.

## Apply the source overlay

1. Keep a backup or commit of the original ChromusFlora checkout.
2. Extract this ZIP **into that checkout's root**, replacing matching files.
   The ZIP has `build.gradle` directly at its root.
3. Use the new root build. Its active sources are exclusively `flora/src/`.
   Older `Common/`, `Fabric/`, `Forge/`, `NeoForge/`, Kotlin build scripts and
   old assets can remain on disk; the new settings do not include those projects.
4. Do not copy the new resources into an old source set. You can also extract
   this source package into an empty directory and build it independently.

There is no automatic migration from `byg:` or `biomeswevegone:` blocks or
biomes to `chromusflora:`. Removing an old worldgen mod from an existing save
can remove its registered content. Use a new test world for this recreation.

## Compile on Windows 10

Install a **64-bit JDK 25**, set `JAVA_HOME` to its installation directory and
open PowerShell in the project root. The first build needs Internet access.

```powershell
java -version
.\gradlew.bat clean build --warning-mode=fail
```

`gradlew.bat` is a source-only launcher. It downloads Gradle 9.5.1 from the
official distribution service, verifies its pinned SHA-256, and caches it in
`.gradle-bootstrap/`. It does not require a shipped Gradle wrapper jar or a
global Gradle installation. The build fails if the selected Java version is
not 25. A successful build writes the mod jar and sources jar to `build/libs/`.
Install the normal mod jar, **not** the `-sources.jar`, in your game's `mods/`
folder alongside Fabric API, TerraBlender and Oh The Trees You'll Grow for 26.2.

On another operating system, install Gradle 9.5.1 and JDK 25 and run:

```sh
gradle clean build --warning-mode=fail
```

An offline source scan can be repeated with Python 3.11 or later:

```powershell
py -3 tools\scan.py
```

Python is optional for the normal Gradle build. The Gradle `check` task also
performs JSON and catalogue-presence checks. To rebuild generated resources,
install Pillow and run `py -3 tools\generate.py`, followed by the global scan.
The generator **replaces `flora/src/main/resources/` completely**. Edit the
catalogue or generator first; manual changes in generated resources will be lost.

## Local game checks after compilation

```powershell
.\gradlew.bat runClient -PwithOptionalMods=true --warning-mode=fail
.\gradlew.bat runServer --warning-mode=fail
```

Run these separately. The dedicated server requires the normal Minecraft EULA
acceptance. JaizMod is not downloaded by these commands: build your supplied
26.2 JaizMod separately and add its jar to the development `run/mods/` folder
when checking that integration.

Create a new creative test world. Check `/locate biome chromusflora:orchard`,
Overworld/Nether/End terrain, saplings with bone meal, giant trees, log stripping,
recipes and drops. Check Jade's sapling tooltip and the ModMenu settings screen.
Eat a Grove Fruit to check AppleSkin. Repeat with JaizMod enabled, including
a dedicated server and a connected client. Save the complete build and game
logs if any error or warning occurs.

## Generation and compatibility

TerraBlender's `terrablender` entrypoint implements
`TerraBlenderApi.onTerraBlenderInitialized`. Overworld and Nether regions use
separate climate mappings; End biomes use the End registry. Biome surface rules
include bedrock and dimension-specific top/underlying blocks.

Every tree family has an original NBT canopy with small, normal and giant forms.
Generation delegates to Oh The Trees You'll Grow's V2 template feature through
a bounds-checking wrapper. Small forms contain **exactly three log blocks**.
Giant forms have a 3×3 base and maximum central wooden height of 48 blocks, or
64 for ancient, baobab, mahogany, redwood and skyris. Terrain height, flat ground,
collisions and available chunks can prevent a placement.

Selection probabilities per attempt are 25% small, 70% normal and 5% giant.
They are not promises about the proportion of successful trees in a world.
Normal and giant heights vary uniformly within their configured intervals.

JaizMod compatibility uses optional registry lookups and biome modifications
for the supplied source's creatures and vegetation. It maps these rules to
each new biome's vanilla habitat analogue. Missing entity IDs are skipped;
feature IDs are checked against the supplied snapshot. JaizMod's code, assets
and own biomes are not copied or changed. Future JaizMod changes need a new
compatibility review; this is not a claim of compatibility with every version.

Jade shows the possible trunk height on saplings. ModMenu edits region weight
and the JaizMod switches. Settings are stored in `config/chromusflora.json` and
apply only after a complete game/server restart. Server settings govern server
world generation. AppleSkin reads the Grove Fruit's standard food component;
it needs no custom API bridge.

VS Code configuration selects Gradle 9.5.1, enables Java project import, hides
JetBrains project files and excludes legacy source projects. Actual Java and
Gradle diagnostics remain visible. No warning category is blanket-suppressed.

## Catalogue and assets

`docs/*-inventory.json` records both original catalogues and JaizMod.
`docs/merge-candidates.json` records exact-ID overlap without filtering by
Minecraft version. There are 37 shared biomes, 37 ChromusFlora-only biomes and
18 BWG-only biomes. Renamed IDs remain separate. All 362 tree-registry IDs are
represented, alongside structural fungi and supplementary original families.
The initial 103 sapling IDs included 51 potted variants: **52 were actual
source sapling varieties**. The 83 families include additional structural and
vanilla-derived families needed by the union.

Shared IDs use the successor BWG catalogue for classification, with original
replacement code and assets. This is not proof of per-file chronology. The
35 excluded candidates are non-tree plants or terrain decorations, listed
explicitly in `docs/content-coverage.json`. Biomes use new compositions based
on vanilla habitats; special legacy geology, flowers, sounds and structures
are not cloned. The scope is the merged biome/tree catalogue, not all blocks
and features from either original mod.

The internal icon is `flora/src/main/resources/assets/chromusflora/icon.png`.
The official distribution icon is `branding/chromus-flora-official.png`.
The original texture atlas and editable catalogue are under `atelier/`.

# Chromus Flora — Português do Brasil

Recriação de biomas e árvores para **Minecraft Java 26.2 / Fabric / Java 25**.
Versão: **0.1.0-alpha.1+26.2**. Dependências conferidas em **25/09/2026**.

O pacote-fonte contém 92 definições de bioma: 72 no Overworld, 12 no Nether e
8 no End. Registra 83 famílias de árvores/fungos, 830 blocos e 748 itens.
O catálogo mesclado reúne 458 configurações nomeadas, incluindo seletores e
substituições originais de fungos estruturais. Seletores não são espécies extras.

Estruturas, geometria, texturas e ícones novos foram criados para este projeto.
Nenhuma implementação ou imagem ARR de BYG/BWG foi incluída no mod ativo.
Consulte `ASSET_PROVENANCE.md` para origem e escopo dos recursos.

## Correção de compilação — Fix 2

Adiciona `com.google.errorprone:error_prone_annotations:2.50.0` aos classpaths
somente de compilação do código comum e do cliente. O Gson 2.14.0 referencia
`InlineMe`; sem as definições da anotação, javac gera warnings de classfile e
`-Werror` interrompe corretamente o build. A classe e os membros `replacement`,
`imports` e `staticImports` foram conferidos no artefato estável publicado.

`-Xlint:all`, `-Werror` e `org.gradle.warning.mode=fail` permanecem ativos.
Não há supressão de warnings, processador de anotações, substituição do Gson
ou novo mod exigido em execução. A dependência é baixada do Maven Central
para compilar e não é embutida no mod. A correção do inicializador da Fix 1
continua incluída.

Extraia o pacote completo por cima da raiz do repositório e execute:

```powershell
.\gradlew.bat clean build --warning-mode=fail
```

A compilação informada pelo usuário falhou antes desta correção. Não compilei
nem executei o mod na Fix 2. A validação estática e as verificações da entrega
estão registradas em `verification/DEPENDENCY_FIX2.md`.

## Correção da entrega — Fix 1

Esta entrega substitui o ZIP incompleto da Alpha 1 e corrige o inicializador
PowerShell. O SHA-256 é calculado diretamente pelo .NET; a extração usa ZipFile
do .NET. `Get-FileHash` e `Expand-Archive` não são necessários. Um ZIP Gradle
inválido no cache é descartado e baixado novamente. A extração usa uma pasta
temporária; a conclusão só é marcada após verificação e extração completas.

Baixe o pacote completo atualizado e extraia por cima da raiz do projeto,
substituindo todos os arquivos correspondentes, inclusive
`verification/reference-index.json`. Não prossiga se a extração informar erros.
Não é necessário apagar o cache global do Gradle nem reinstalar Java para
esta correção. Logo após extrair, confira os arquivos pelo PowerShell:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\tools\verify-source.ps1
.\gradlew.bat clean build --warning-mode=fail
```

O verificador compara os arquivos com o manifesto da entrega; modificações
intencionais também serão informadas. A verificação é opcional e não impede
edições posteriores nem participa obrigatoriamente do build.
`verification/BOOTSTRAP_FIX1.md` registra o escopo de validação e a falha do ZIP.

## Situação da validação

**Candidato em código-fonte: não houve compilação Java nem execução do jogo.**
O scan global estático verifica todos os recursos ativos, cobertura do catálogo,
JSON e chaves duplicadas, NBTs e marcadores, alturas e sustentação das folhas,
ciclos de dependência, ordem das decorações vanilla, modelos, texturas, receitas,
loot, tags, identificadores de compatibilidade e cópias idênticas de código ou
assets antigos. Resultados: `verification/global-scan.json` e `verification/SCAN.md`.

A sintaxe Java e assinaturas públicas selecionadas foram inspecionadas à parte.
Isso não comprova ausência de erros/warnings de compilação, carregamento dos
registros, geração correta ou compatibilidade multiplayer. O build trata
warnings Java e deprecações Gradle como erros. Faça os testes locais antes de
usar esta versão alfa em um mundo permanente.

## Versões e instalação dos fontes

As versões fixadas são: JDK 25, Gradle 9.5.1, Loom 1.17.21, Fabric Loader 0.19.5,
Fabric API 0.161.0+26.2, TerraBlender Fabric 26.2.0.0.2 e Oh The Trees You'll
Grow 11.0.1. Integrações opcionais: ModMenu 20.0.3, Jade 26.2.11+fabric,
AppleSkin 3.0.10+mc26.2 e o JaizMod 2.3.11 fornecido para 26.2.

TerraBlender é a **única dependência beta autorizada**. As demais versões
selecionadas são estáveis. Os IDs fixos do Modrinth estão em `gradle.properties`;
as bibliotecas são baixadas durante seu build e não acompanham o ZIP.

1. Faça backup ou commit do checkout original do ChromusFlora.
2. Extraia o ZIP **na raiz desse checkout**, substituindo arquivos correspondentes.
   `build.gradle` fica diretamente na raiz do ZIP.
3. Compile pelo novo build da raiz. Apenas `flora/src/` participa dele.
   Pastas antigas `Common/`, `Fabric/`, `Forge/`, `NeoForge/`, scripts Kotlin e
   assets antigos podem permanecer; não são incluídos pelo novo projeto.
4. Também é possível extrair este pacote em uma pasta vazia e compilar isoladamente.

Não existe conversão automática de conteúdo `byg:` ou `biomeswevegone:` para
`chromusflora:`. Retirar um mod antigo de um save pode remover seu conteúdo.
Crie um mundo de teste novo para esta recriação.

## Compilar no Windows 10

Instale um **JDK 25 de 64 bits**, configure `JAVA_HOME` com a pasta de instalação
e abra PowerShell na raiz do projeto. A primeira compilação requer Internet.

```powershell
java -version
.\gradlew.bat clean build --warning-mode=fail
```

O inicializador em código-fonte baixa o Gradle 9.5.1 do serviço oficial,
confere seu SHA-256 e o mantém em `.gradle-bootstrap/`. Não é preciso instalar
Gradle globalmente. O script exige Java 25. Após sucesso, os jars ficam em
`build/libs/`. Instale o jar normal, **não** o `-sources.jar`, junto com
Fabric API, TerraBlender e Oh The Trees You'll Grow para 26.2.

Em outro sistema operacional, instale JDK 25 e Gradle 9.5.1 e execute
`gradle clean build --warning-mode=fail`.

Para repetir o scan sem compilar, use Python 3.11 ou superior:

```powershell
py -3 tools\scan.py
```

Python não é necessário para o build Gradle normal, que também confere JSONs
e presença dos recursos do catálogo. Para regenerar recursos, instale Pillow
e execute `py -3 tools\generate.py`, depois repita o scan.
**A regeneração substitui integralmente `flora/src/main/resources/`.**
Edite primeiro o catálogo ou gerador; alterações manuais nos recursos gerados
serão perdidas.

## Testes locais após compilar

```powershell
.\gradlew.bat runClient -PwithOptionalMods=true --warning-mode=fail
.\gradlew.bat runServer --warning-mode=fail
```

Execute separadamente. O servidor requer a aceitação normal da EULA do jogo.
JaizMod não é baixado por esses comandos: compile seu projeto 26.2 separadamente
e coloque o jar em `run/mods/` para verificar essa integração.

Crie um mundo criativo novo. Confira `/locate biome chromusflora:orchard`,
terreno nas três dimensões, mudas com farinha de osso, árvores gigantes,
descascamento de troncos, receitas e drops. Confira Jade nas mudas e a tela
do ModMenu. Consuma a Fruta do Bosque para verificar AppleSkin. Repita com
JaizMod, incluindo servidor dedicado e cliente conectado. Guarde logs completos
de compilação e do jogo caso apareçam erros ou warnings.

## Geração e compatibilidade

O entrypoint `terrablender` implementa
`TerraBlenderApi.onTerraBlenderInitialized`. Overworld e Nether têm mapeamentos
climáticos separados; o End usa seu registro específico. As regras de superfície
incluem bedrock e blocos adequados a cada dimensão.

Cada família possui copas NBT originais em formas pequena, normal e gigante.
A geração usa o recurso V2 da biblioteca Oh The Trees You'll Grow, com uma
verificação prévia dos limites do mundo e dos chunks disponíveis.
As formas pequenas contêm **exatamente três blocos de madeira no tronco**.
Gigantes têm base 3×3 e altura máxima central de madeira de 48 blocos, ou 64
para ancient, baobab, mahogany, redwood e skyris. Terreno irregular, colisões,
limites de altura e chunks indisponíveis podem impedir uma tentativa.

Cada tentativa seleciona 25% de pequenas, 70% de normais e 5% de gigantes.
A proporção de árvores que efetivamente conseguem nascer pode diferir.
As alturas normais e gigantes variam aleatoriamente em intervalos próprios.

A integração opcional com JaizMod consulta registros de criaturas e aplica
suas regras de vegetação aos novos biomas conforme o habitat vanilla de referência.
Entidades ausentes são ignoradas; os identificadores de features foram conferidos
contra o código fornecido. Código, recursos e biomas do JaizMod permanecem
inalterados e não acompanham o pacote. Mudanças futuras desse mod exigem nova
revisão; não se afirma compatibilidade com toda versão existente.

Jade informa a faixa de altura das mudas. ModMenu permite configurar peso das
regiões e ativar/desativar integrações JaizMod. `config/chromusflora.json`
armazena as opções, aplicadas somente após reiniciar completamente jogo/servidor.
Em multiplayer, o servidor determina a geração. AppleSkin usa o componente
alimentar padrão da Fruta do Bosque, sem ponte de API especial.

O VS Code recebe configuração para Gradle 9.5.1, importação Java, ocultação de
arquivos JetBrains e exclusão dos projetos antigos. Diagnósticos reais Java e
Gradle continuam visíveis; nenhuma categoria de warning foi suprimida globalmente.

## Catálogo e ícones

`docs/*-inventory.json` contém os inventários de origem e JaizMod.
`docs/merge-candidates.json` registra a comparação por ID, sem filtrar versão
do Minecraft: 37 biomas comuns, 37 exclusivos do ChromusFlora e 18 exclusivos
do BWG. IDs renomeados permanecem distintos. Os 362 IDs do registro de árvores
estão representados, além de fungos estruturais e famílias originais complementares.
Dos 103 IDs de mudas inicialmente encontrados, 51 eram versões em vasos:
**52 correspondiam a variedades de mudas reais dos pacotes**.

IDs compartilhados adotam a classificação do catálogo sucessor BWG, com código
e recursos recriados. Isso não comprova a cronologia individual dos arquivos.
Os 35 candidatos excluídos são plantas pequenas ou decorações de terreno,
listados em `docs/content-coverage.json`. Os biomas usam novas composições baseadas
em habitats vanilla; geologia especial, flores, sons e estruturas antigas não
foram clonados. O escopo reúne o catálogo de árvores/biomas, não todos os blocos
e recursos dos mods originais.

Ícone interno: `flora/src/main/resources/assets/chromusflora/icon.png`.
Ícone oficial: `branding/chromus-flora-official.png`.
Atlas original e catálogo editável: pasta `atelier/`.
