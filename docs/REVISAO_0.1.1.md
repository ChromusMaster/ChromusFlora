# Revisão Chromus Flora 0.1.1 — 28/09/2026

## Situação da entrega

Pacote completo em fontes para Fabric 26.2 e 26.3. Verificações estáticas aprovadas. **Não foram executados Gradle, compilador Java, JDT, Minecraft ou o modpack nesta revisão.** Portanto, esta entrega ainda não tem um resultado de compilação ou de execução que permita garantir estabilidade no jogo.

O comando de build está configurado para produzir `build/26.2/chromus-flora-0.1.1-26.2.jar` e `build/26.3/chromus-flora-0.1.1-26.3.jar`. A versão 26.3 tem adaptadores e recursos próprios; não é uma renomeação do JAR de 26.2.

## Alterações de conteúdo

| Solicitação | Implementação |
|---|---|
| Reconhecimento das árvores no crafting | 750 receitas com seus desbloqueios no livro, por alvo. Em jogadores existentes, adquirir ou mover os materiais dispara os critérios. |
| Tábuas e madeiras | Tábuas a partir de troncos e madeiras da família; novas madeiras com casca em todas as faces e versões descascadas. |
| Portas | 83 variantes, receitas de três portas, estados de abertura/dobradiça, item de colocação de duas alturas e loot somente da metade inferior. |
| Alçapões | 83 variantes, receitas de dois alçapões, estados de abertura e orientação. |
| Cercas e portões | As receitas já existiam no Fix10 e foram preservadas. Agora também têm desbloqueios próprios. |
| Barcos | Nova receita com tábuas do Flora produz barco de carvalho vanilla. Sem novas entidades ou renderizadores. |
| Baús e bancadas | Fallback vanilla explícito, fabricável com as tábuas do Flora. Não foram adicionadas entidades de bloco personalizadas. |
| Nomes de artefatos | `chromus-flora-0.1.1-26.2.jar` e `chromus-flora-0.1.1-26.3.jar`. |
| Limpeza | Backup dos caminhos obsoletos, exclusão das antigas cópias dos adaptadores no build e preservação de Git, workflows, mundos e configurações. |

Total atual: 83 famílias, 92 biomas, 1.162 blocos e 1.080 itens. A entrega anterior tinha 830 blocos e 748 itens; todos os IDs antigos continuam presentes. Os 332 blocos adicionais são madeira, madeira descascada, porta e alçapão de cada família.

As novas portas e alçapões usam as texturas de tábuas autorais já existentes e modelos-base vanilla. Nenhuma textura ou geometria foi copiada dos mods de origem. As árvores e texturas do Fix10 não foram regeneradas.

## Compatibilidade com o mundo atual

A comparação binária confirmou preservação de **4.223 arquivos antigos**:

- 830 blockstates;
- 336 texturas;
- 1.121 estruturas NBT;
- 1.936 arquivos de geração de mundo de 26.2.

Os IDs do mod, dos biomas e dos blocos existentes permanecem. Não há retrogen, remoção de chunks, alteração dos blocos já colocados ou exigência programada de criar um mundo novo. O novo limite de posicionamento pode recusar uma árvore futura se a região disponível não comportar sua leitura/escrita; ele não percorre nem modifica árvores existentes.

Esses fatos reduzem o risco de quebra de referências no save. Não substituem abrir, salvar e reabrir uma cópia do mundo com a lista real de mods. Para o modpack anexado, use **26.2**. Os JARs anexados de Terrestria 8.1.0-beta.2 e Biolith 3.7.0-beta.1 declaram Minecraft `>=26.2 <26.3`.

## Evidências dos logs do modpack

O log registra um ciclo de features com Terralith, Terrestria e um bioma do Flora. O Biolith detectou o problema e removeu uma aresta de ordenação para continuar. Isso é diferente de um log sem conflitos.

A reconstrução dos biomas JSON dos releases oficiais Terralith 2.6.4 e Terrestria 8.1.0-beta.2, junto aos vanilla, reproduz o seguinte ciclo **mesmo sem Flora**:

`patch_grass_jungle → patch_bush → flower_default → patch_grass_jungle`

A última aresta aparece em `terrestria:rainbow_rainforest`. A fixture cobre 153 biomas desses dois mods, além dos vanilla; não representa todas as injeções de código e todos os 277 mods. Não foi aplicada uma reordenação global nem alterado o conteúdo desses outros mods. O conflito externo permanece para acompanhamento; o funcionamento observado dependeu da recuperação oferecida pelo Biolith.

Há ainda 19.992 mensagens de leitura insegura na etapa `minecraft:spawn`, associadas ao chunk `[-30, 18]`. Os registros analisados não estabelecem uma chamada do Flora como origem. A proteção das árvores não deve ser apresentada como correção comprovada dessas mensagens.

O log termina com salvamento das dimensões. Também há três avisos de atraso do servidor. Não foi realizado benchmark, e os dados não permitem atribuir esses atrasos isoladamente ao Flora.

## Prioridades de estabilidade

| Prioridade | Resultado desta revisão | Limite da evidência |
|---|---|---|
| P0 — Ordem de features | Fixtures Flora/vanilla/Jaiz sem ciclo; ciclo externo Terralith/Terrestria reproduzido sem Flora. | Grafo completo das modificações em execução ainda pendente. |
| P0 — RNG e estado global | Nenhum RNG global novo; o contexto fornece a aleatoriedade. Listas de catálogo e regras copiadas para coleções imutáveis. | OTTYG contém cache mutável de palettes e lista de modificadores de terceiros; concorrência real ainda requer teste. C2ME não apareceu no log anexado. |
| P0 — Limites entre chunks | Pré-checagem da base, copa, altura, área gravável e halo de leitura antes de delegar a colocação. Sem forçar carga de chunks. | O modelo Python de geometria não executa a implementação Java. |
| P1 — TerraBlender | Região e superfície de 26.2 mantidas; API de material rules adaptada em 26.3. | Transições de superfície, End e Nether precisam de verificação visual em execução. |
| P1 — Reload e registros | Sem cache próprio de templates; consulta ao gerenciador da dimensão. Registro continua nas entradas do ciclo de inicialização. | Reloads e múltiplas entradas em mundos ainda não exercitados nesta versão. |
| P1 — Idempotência | Catálogo, regras e features conferidos contra duplicações; sem registro por tick ou por chunk. | Não há promessa de suportar a chamada manual repetida de um inicializador de mod. |
| P2 — Save | IDs antigos mantidos; 4.223 definições antigas idênticas. | Carregamento real do save pendente. |
| P2 — Árvores extremas | 1.119 formas conferidas; máximo de 2.620 blocos na copa e limite de 3.071 candidatos no modelo. | Sem medidas de TPS, memória ou tempo de geração. |

## Nulidade e avisos do editor

Os pacotes receberam contratos JSpecify `@NullMarked`. Retornos e estados realmente opcionais receberam `@Nullable`, incluindo busca de bioma, configuração do próximo lançamento, tela anterior e âncora temporária. Foram removidas verificações redundantes da âncora após validar os limites da estrutura. Os contratos das sobrescritas de Jade e Sapling passam a seguir a declaração dos respectivos pacotes.

Isso trata a causa de vários diagnósticos do JDT, sem desativar a análise de nulidade. **Não foi executado JDT para confirmar zero avisos.** O build continua com `-Xlint:all`, `-Werror` e avisos de Gradle fatais. Avisos do JDT e avisos do javac são análises diferentes.

## Separação 26.2 / 26.3

Em 26.3, foram adaptados registro e codec de features, TreeGrower, retirada do codec de SaplingBlock, material rules do TerraBlender, composição de spawns, stripping e compostagem. Nos recursos, há conversão dos campos de features, provedores de estado, loot e critérios de desbloqueio de receita, além da base vanilla de biomas correspondente.

Fontes primárias consultadas:

- [Fabric para Minecraft 26.3](https://fabricmc.net/2026/09/15/263.html)
- [Notas oficiais de Minecraft 26.3](https://www.minecraft.net/en-us/article/minecraft-java-edition-26-3)
- Metadados oficiais de Mojang e Fabric e artefatos publicados pelos projetos no Modrinth, inspecionados sem execução.

Dependências diretas por alvo:

| Dependência | 26.2 | 26.3 |
|---|---|---|
| Java / Fabric Loader | 25 / 0.19.5 | 25 / 0.19.5 |
| Fabric API | 0.161.0+26.2 | 0.161.0+26.3 |
| TerraBlender | 26.2.0.0.2 | 26.3.0.0.7, release beta |
| Oh The Trees You'll Grow | 11.0.1 | 12.0.0 |
| Jade, opcional | Pin anterior `ue8CO97w` | 26.3.1+fabric |
| Mod Menu, opcional | Pin anterior `iRo7AZXf` | 21.0.0 |

TerraBlender é resolvido pelo ID exato da publicação oficial no Modrinth. O artefato 26.2 desse canal é byte a byte igual ao utilizado na revisão anterior. O alvo 26.3 depende de um release beta do TerraBlender e tem validação de execução pendente; não deve ser tratado como certificado para produção.

## Verificações entregues

- `verification/global-scan.json`: 142.235 verificações estáticas, resultado PASS.
- `verification/release-0.1.1/checks.json`: 14.046 verificações de receitas, separação de esquemas e preservação do Fix10, resultado PASS.
- `verification/release-0.1.1/worldgen-checks.json`: 21.190 verificações; 3.747.840 rotações de voxels no modelo geométrico.
- `verification/release-0.1.1/api-inspection.json`: sintaxe Java e existência de imports/membros selecionados nos artefatos de ambas as versões. Não valida resolução completa de tipos.
- `verification/release-0.1.1/modpack-analysis.json`: diagnóstico e limites do ciclo externo.
- `verification/release-0.1.1/packaging.json`: resultado da simulação de extração sobre Fix10 e limpeza.
- `tools/ci/gradle.yml`: template de CI que compila ambos os alvos e valida seus JARs antes de disponibilizar os artefatos.

A sequência de aplicação e compilação está em `APLICAR_0.1.1.md`. A primeira confirmação de execução deve ser feita em uma cópia do save: conferir receitas, itens antigos, portas/alçapões, stripping, chunks novos, salvamento e reabertura. Para investigar as leituras inseguras restantes, é necessária uma reprodução com stack trace ou perfil que identifique o responsável; não há motivo demonstrado para apagar o mundo.
