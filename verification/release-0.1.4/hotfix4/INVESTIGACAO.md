# Investigação — 05/10/2026

O ciclo também existe no grafo vanilla + Terralith + Terrestria, sem Chromus Flora. A relação patch_bush → flower_default é vanilla; Terralith sakura_grove/sakura_valley impõem patch_grass_jungle → patch_bush, e Terrestria rainbow_rainforest impõe flower_default → patch_grass_jungle. Chromus Flora herda a relação vanilla e participa, mas não é necessário para o conflito existir.

Foram inspecionados os artefatos das versões efetivamente carregadas, os 66 biomas vanilla, 92 Chromus Flora, 95 Terralith e 20 Terrestria, e os repositórios relacionados. A troca adjacente de grama e flores no Terrestria torna o grafo de 273 biomas acíclico. O Biolith atualmente recupera o ciclo descartando uma relação; isso permite continuar, mas não torna os dados originais compatíveis.

A API de modificação de biomas do Fabric fornece a lista após modificadores anteriores. Remoção e reinserção conservam a ordem solicitada; o freeze reconstrói caches derivados. O código preserva todos os membros, rejeita formas inesperadas e executa apenas no carregamento, sem custo por chunk/tick. Nenhum arquivo do Terrestria é sobrescrito. IDs, assets, formas de árvore, baús/barcos, correções antigas e README/banner permanecem inalterados.

## Referências examinadas

- https://github.com/TerraformersMC/Terrestria/tree/04d17f3ab87c5ed402d0ee135dee0c274dee1fd2 — src/main/java/com/terraformersmc/terrestria/biome/RainbowRainforestBiomes.java, createGenerationSettings.
- https://github.com/Stardust-Labs-MC/Terralith/tree/13ec712b2415944ff1b028d2162b39cdcae1b5c2 — comparação com os JSONs sakura_grove/sakura_valley do JAR 2.6.4, que são a evidência da versão carregada.
- https://github.com/TerraformersMC/Biolith/tree/52c09a7201c484b84484b2cd863d7db254e695fd — ResilientPlacedFeatureIndexer e MixinFeatureSorter.
- https://github.com/FabricMC/fabric/tree/26.2/fabric-biome-api-v1/src/main/java/net/fabricmc/fabric — BiomeSelectionContext, ModificationPhase e BiomeModificationContextImpl. Assinaturas conferidas nos artefatos Fabric API 0.161.0+26.2 e +26.3.

Uma branch pública atual não é automaticamente a versão instalada. Fixtures e hashes registram a origem dos grafos. Cenários sem Flora modelam uma correção hipotética upstream; não representam execução de um mod ausente. A integração Jaiz é modelada pelos fixtures anteriormente auditados, sem prometer cobertura de todo modificador instalado.

## Limites

Sem execução Java/Gradle/Minecraft. Compatibilidade de saves foi protegida por estabilidade de IDs/recursos e ausência de escrita de chunks, não por teste de carregamento de um save real. Mudanças futuras de versões ou datapacks exigem nova revisão. Os 356 erros durante geração da vila sueca continuam sendo um caso separado, documentado para o autor de Towns and Towers.
