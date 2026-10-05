# Chromus Flora 0.1.4 — Hotfix 3: leitura de chunks do Naturalist

Este pacote é uma atualização de fontes para o projeto completo 0.1.4. Inclui os Hotfixes 1 e 2 e repõe `APLICAR_0.1.4.md` e `ASSET_PROVENANCE.md`. Não é um projeto completo independente nem contém um JAR pré-compilado.

## Diagnóstico

O `latest.log` enviado contém 19.992 mensagens `Detected unsafe terrain read during worldgen`, todas às 15:13:20, na etapa `minecraft:spawn`, no chunk [7, -2]. A ordem completa das coordenadas corresponde a oito buscas de água do método `Hippo.checkHippoSpawnRules` do Naturalist 2.0.6, com origem X=113, Z=-22.

Cada busca percorre 33 × 3 × 33 posições. O teste original `hasChunk` aceita chunks vizinhos disponíveis, mas durante essa etapa eles não têm terreno garantidamente pronto para leitura. Cada busca seca produz 2.499 leituras vizinhas; oito buscas produzem os 19.992 avisos encontrados.

O OTTYG 11.0.2 já corrige nativamente o antigo problema dos ticks. A mensagem de que o remendo antigo não foi ativado é esperada nessa versão. Não é necessário fazer downgrade do OTTYG.

## Aplicação

1. Feche o jogo e faça uma cópia de segurança do projeto e do mundo que vai testar.
2. Extraia todo este ZIP diretamente em `D:\Repository\ChromusFlora`, permitindo substituir os arquivos correspondentes. Não crie uma segunda pasta ChromusFlora dentro do projeto.
3. Execute:

```powershell
cd D:\Repository\ChromusFlora
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\tools\verify-source.ps1
.\gradlew.bat build --no-daemon --warning-mode=fail
```

Não é necessário executar `clean-project.ps1` para aplicar este hotfix. O script continua disponível e a verificação continua rigorosa. Não remova arquivos apontados no manifesto para contornar falhas.

4. Depois de `BUILD SUCCESSFUL`, use o JAR correspondente à versão da instância:

- Minecraft 26.2: `build\26.2\chromus-flora-0.1.4-26.2.jar`.
- Minecraft 26.3: `build\26.3\chromus-flora-0.1.4-26.3.jar`.

O nome do JAR permanece o mesmo. Substitua a cópia anterior na pasta `mods`; não mantenha duas cópias do Chromus Flora. Não é necessário substituir ou remover Naturalist 2.0.6.

Se Python já estiver instalado, a verificação adicional dos dois JARs pode ser executada com `python .\tools\verify-jars.py`.

## Teste no mundo existente

Não crie outro mundo para aplicar a correção. Teste primeiro uma cópia do mundo existente, mantendo o mesmo conjunto de mods.

- Confirme no `logs/latest.log` a linha:
  `Applied Naturalist 2.0.6 hippo worldgen read guard (Chromus Flora hotfix 3)`.
- Explore terreno novo, especialmente biomas em que hipopótamos podem nascer. Só ficar em chunks já gerados não testa este caminho de código.
- Saia, reabra o mesmo mundo e volte a percorrer áreas já visitadas, para também conferir a leitura dos chunks salvos.
- Ao terminar a sessão, execute a verificação do log. Para a instância enviada:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\tools\check-chunk-log.ps1 -LogPath 'E:\CurseForge\Instances\OFICIAL - Chromus Vanilla Plus\logs\latest.log'
```

O verificador só lê o arquivo. `PASS` significa que a ativação foi encontrada e os padrões de erro verificados não aparecem nessa sessão. `FAIL` identifica erros remanescentes. `INCONCLUSIVE` significa que a ativação não foi confirmada. Guarde o log completo antes de abrir outra sessão, que pode substituí-lo.

## Escopo e efeito

- Compatibilidade opcional, aplicada apenas ao Naturalist 2.0.6 revisado para 26.2 e 26.3. Sem Naturalist, o mixin não é aplicado; versões diferentes produzem aviso de compatibilidade não revisada.
- Na geração, a busca do hipopótamo pula chunks vizinhos antes de consultar o fluido. Se a única água estiver fora do chunk central, essa tentativa de nascimento é recusada. Isso pode reduzir nascimentos iniciais perto de bordas, mas mantém a exigência de água.
- Fora de `WorldGenRegion`, o teste original é preservado. Hipopótamos existentes não são alterados ou removidos.
- Não há filtro de logs, aumento artificial da área segura, carregamento forçado de chunks, exclusão de regiões ou migração de NBT.
- Nenhuma textura, modelo, receita, ID, inventário ou recurso de geração de biomas/árvores foi alterado por este hotfix. O README com banner permanece igual ao do Hotfix 2.

## Validação desta entrega

Foram conferidos os métodos nos JARs exatos de Minecraft e Naturalist para ambas as versões, a sintaxe Java, os pontos de aplicação dos mixins, a integridade dos fontes e 1.024 casos de limites de chunks, incluindo coordenadas negativas. O modelo elimina todas as leituras vizinhas da busca identificada.

Java, Gradle e Minecraft não foram executados nesta entrega. A compilação e a confirmação em jogo ainda precisam do seu teste. A correção trata a causa identificada neste log; não seria correto prometer ausência de qualquer erro de chunk causado por outros mods ou versões futuras.

Detalhes: `verification/release-0.1.4/HOTFIX3_CHUNKS.md` e `hotfix3-checks.json`.
