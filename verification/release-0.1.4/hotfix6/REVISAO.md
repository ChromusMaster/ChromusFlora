# Chromus Flora 0.1.4 — Hotfix 6

## Escopo

Corrige a geometria do baú animado e acrescenta a superfície interna escura para as 83 madeiras, nas variantes simples, esquerda e direita. Mantém a tampa/fechadura e a animação nativas. A superfície interna usa o sprite vanilla `minecraft:block/black_concrete`; pacotes de recursos podem alterar esse sprite.

O corpo agora nasce com altura 9, terminando na dobradiça da tampa. A face superior integral de madeira foi removida e substituída por quatro bordas (três em cada metade do baú duplo) e uma superfície interna escura. As bordas e o interior não compartilham área; o encontro das duas metades não recebe parede nem borda intermediária.

## Por que o Hotfix 5 não resolveu

A correção anterior alterava `ModelPart.yScale` e chamava `setInitialPose(storePose())`. A leitura dos clientes oficiais 26.2 e 26.3 confirmou que `storePose()` captura posição e rotação, mas não escala. `ChestModel.setupAnim()` chama o reset do modelo, e `loadPose()` restaura também as escalas. O corpo voltava a ter altura 10, sobrepondo a tampa entre y=9 e y=10.

O teste anterior considerava a escala escrita no código, sem modelar a escala restaurada pela animação. Seu resultado PASS era insuficiente. O relatório do Hotfix 5 é histórico e não deve ser usado como comprovação da correção visual. Este hotfix elimina a dependência de escala e acrescenta testes que rejeitam o corpo de altura 10, a face de madeira sobre o interior e superfícies superiores duplicadas.

## Preservação

Nenhuma alteração nos registros, block entities, inventários, receitas, arquivos de mundo, geração de árvores, barcos ou compatibilidade com outros mods. Mesas de trabalho e seus modelos mantêm a correção anterior de oclusão. As saídas permanecem em `build/26.2/Fabric` e `build/26.3/Fabric`. Não há migração nem exigência de mundo novo.

Os modelos são construídos uma vez por instância de renderer e reutilizados. Há uma submissão adicional para o interior por metade de baú renderizada. Não são adicionados tickers, consultas a chunks ou texturas próprias. Não foi realizado benchmark de GPU.

README e configuração local do VS Code são editáveis. O verificador aceita a remoção dos seis documentos históricos apontados pelo usuário e de `APLICAR_0.1.4.md`. Os demais arquivos continuam verificados, inclusive `ASSET_PROVENANCE.md`, necessário ao pacote. O teste da galeria não exige mais o índice Markdown opcional.

## Evidência e limites

- `native-api-checks.json`: assinaturas públicas em ambos os clientes oficiais, causa do reset, faces planas UP e presença do sprite escuro; leitura de bytecode sem execução da JVM.
- `furniture-checks.json`: modelos das 83 madeiras, cobertura das superfícies e varredura analítica da tampa entre 0 e 90 graus.
- `mutation-checks.json`: defeitos inseridos deliberadamente são rejeitados pelo teste.
- `preservation-checks.json`: comparação de arquivos com a entrega Hotfix 5.
- `validation-summary.json`: resultados desta entrega.

Java, Gradle e Minecraft não foram executados. As verificações estáticas não garantem ausência de flickering com todos os renderizadores e pacotes de recursos. Compilação e inspeção visual no jogo ainda precisam ser realizadas pelo usuário.
