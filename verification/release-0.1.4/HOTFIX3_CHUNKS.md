# Auditoria de chunks — Hotfix 3

## Evidência da sessão de 04/10/2026

Foram examinados latest.log, stdout-logs.txt, stderr_stream.log, instance_audit.txt, modlist.txt, crash_assistant_app.log, a telemetria de carregamento/saída de mundos, minecraftinstance.json e o manifesto/conteúdo do modpack OFICIAL - Chromus Vanilla Plus 1.4.0. Informações de conta e telemetria pessoal não foram incluídas neste relatório.

O ambiente da sessão é Minecraft 26.2, Fabric Loader 0.19.5, Chromus Flora 0.1.4, Naturalist 2.0.6 e OTTYG 11.0.2. O manifesto do modpack lista 278 entradas externas; a lista da instância não deve ser tratada como prova de que todas foram carregadas. A identificação de versões efetivamente carregadas usa o cabeçalho do log.

Não foi encontrada a antiga exceção de acesso a chunk nesse log. Foram encontradas 19.992 mensagens de leitura insegura, todas em minecraft:spawn, distância 1 e raio de escrita -1. O stdout contém as mesmas 19.992 ocorrências em formato XML; elas não são uma segunda amostra independente.

## Correspondência com o Naturalist

O método `com.crispytwig.naturalist.world.entity.animal.hippo.Hippo.checkHippoSpawnRules` verifica o solo e a luminosidade e então procura água nos deslocamentos X/Z de -16 a +16 e Y de -1 a +1. Antes de getFluidState, consulta ServerLevelAccessor.hasChunk.

Na geração vanilla, a dependência de SPAWN para vizinhos é BIOMES. WorldGenRegion.hasChunk verifica a distância nas dependências; não garante terreno pronto. A presença do vizinho nessa região não torna segura a leitura de seus blocos/fluidos.

No chunk [7, -2], a busca com origem X=113, Z=-22 reproduz exatamente a ordem de todas as coordenadas registradas: oito repetições de 2.499 leituras externas. A correspondência é da sequência completa, não apenas da contagem. Isso fornece evidência forte e específica para a rotina do hipopótamo. O log original não contém a pilha dessas mensagens; não foi feita reprodução em jogo neste ambiente.

## Correção aplicada

Um mixin opcional redireciona exclusivamente a chamada hasChunk dentro desse método. Se o acesso usa WorldGenRegion, exige o chunk central antes de delegar ao hasChunk original; caso contrário, apenas delega ao original. Um resultado falso segue o desvio já existente no Naturalist e pula a consulta getFluidState. Não se substituem fluidos por valores fictícios.

A correção conserva a regra de água, solo e iluminação. No pior caso de busca seca, há até 768 consultas de fluido no chunk central, contra 3.267 antes; 2.499 acessos vizinhos são evitados por tentativa. O laço original continua percorrendo seus deslocamentos. Não se afirma uma redução medida de CPU/RAM ou TPS: nenhum perfil de execução foi coletado.

A mudança de comportamento é restrita ao nascimento durante geração: água apenas no vizinho não qualifica essa tentativa. Entidades existentes, nascimento comum no mundo ativo, IDs, saves e configurações de geração permanecem preservados.

## OTTYG

Foram inspecionadas as versões Fabric 11.0.2, 11.0.3, 12.0.1 e 12.0.2. O método de leitura já usa a tag aninhada e verifica os Optional antes de acessar seu conteúdo. As notas oficiais de 11.0.2/12.0.1 também anunciam a correção dos ticks. O remendo legado para 11.0.1/12.0.0 foi mantido sem alteração; ampliá-lo cegamente para as versões novas seria incorreto.

## Validação estática

- JARs oficiais de Minecraft comparados ao SHA-1 do manifesto de cada versão.
- Naturalist 2.0.6 de 26.2 e 26.3: método, descritor e bytecode idênticos; uma única chamada hasChunk redirecionável.
- Desvio falso validado: pula getFluidState e avança o laço.
- APIs públicas usadas conferidas diretamente em ambas as versões: WorldGenRegion.getCenter, ChunkPos.x()/z() e LevelAccessor.hasChunk herdado por ServerLevelAccessor. Os campos x/z de ChunkPos são privados; o código usa os acessores públicos.
- Sintaxe dos dois novos fontes Java validada com tree-sitter; isso não substitui javac.
- 1.024 casos geométricos: todas as 256 posições locais em quatro chunks positivos/negativos. Cada busca completa mantém apenas 16 × 3 × 16 posições para consultas de fluido.
- Configuração do mixin conferida com o gerador e verificador de JARs. Naturalist não virou dependência obrigatória.
- A validação do manifesto anterior confirmou 17.520 arquivos inalterados, incluindo 6.483 assets, 3.885 recursos de worldgen e todos os nove arquivos client cobertos pelo manifesto.
- Sem Java, Gradle, Minecraft, transformação real de mixins ou teste do modpack executados aqui.

## Critério de aceitação em jogo

Compilar as duas versões com -Werror preservado; testar a 26.2 com Naturalist 2.0.6 e o conjunto enviado; confirmar a linha de aplicação do hotfix; explorar terreno novo; sair/reabrir; analisar o log completo. A correção não pressupõe mundo novo nem autoriza remoção de chunks. A execução de 26.3 também requer confirmação própria antes de declarar essa combinação validada em jogo.

Versões futuras do Naturalist não são modificadas automaticamente. O guard é estritamente opcional e versionado; layout incompatível na versão revisada falha explicitamente em vez de aplicar um redirecionamento ambíguo.

## Referências consultadas

- Naturalist 2.0.6 Fabric 26.2: https://www.curseforge.com/minecraft/mc-mods/naturalist/files/9004422
- Metadados oficiais das versões Naturalist: https://api.modrinth.com/v2/project/naturalist/version
- Metadados oficiais OTTYG: https://api.modrinth.com/v2/project/g8NOG5OR/version
- Relato vanilla separado (sculk, não a causa atribuída à sessão): https://github.com/PaperMC/Paper/issues/13995

Os hashes dos artefatos e os resultados estruturados estão em hotfix3-checks.json. Não foram incluídos binários de terceiros no pacote.
