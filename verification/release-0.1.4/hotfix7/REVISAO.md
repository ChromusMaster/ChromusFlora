# Chromus Flora 0.1.4 — Hotfix 7

Atualização de recursos sobre o Hotfix 6 aprovado. Nenhum código Java, ID de
registro, blockstate, estrutura de árvore, geração de mundo ou arquivo Gradle foi
alterado em relação ao H6. A entrega mantém Fabric 26.2 e 26.3, JDK 25 e os destinos
`build/26.2/Fabric` e `build/26.3/Fabric`.

## Aparência

| Espécie | Madeira interna, descascada e tábuas | Folhas |
|---|---|---|
| Blue Spruce | Cinza claro com azulado sutil, pouco saturado | Azul acinzentado |
| Giant White Allium | Marfim predominante, veio menta discreto | Branco marfim |
| White Cherry | Creme muito claro com veios quentes | Salmão claro |
| White Sakura | Branco perolado com rosa discreto | Branco perolado rosado |

São 12 PNGs de madeira atualizados, 16 novas texturas de folhas e 38 modelos de
folhas com a referência de textura revista. As 83 espécies foram conferidas;
45 conservaram a associação de folhas anterior. O mapa completo está em
`atelier/palette-hotfix7/appearance.json`. Cascas, outras 79 famílias de madeira,
portas e alçapões permanecem byte a byte iguais ao H6. As novas tábuas são usadas
pelos derivados existentes, inclusive móveis e barcos, através das referências
que já existiam. Todos os novos tiles têm 64 × 64 pixels, são opacos e possuem
bordas opostas idênticas. Os dois atlas e seus prompts estão incluídos para
permitir regeneração futura, sem copiar arte dos mods originais.

## Receitas e livro

Cercas, portões, escadas e lajes já possuíam receitas válidas por espécie. Foram
mantidas. Três receitas novas aceitam as tábuas Chromus Flora: placa de sinalização
(6 tábuas + 1 graveto → 3 placas), botão (1 tábua → 1 botão) e placa de pressão
(2 tábuas → 1). Esses três resultados são de carvalho vanilla, sem variantes de
cor próprias. As receitas não substituem as receitas nativas de outras madeiras.

Espadas e lanças de madeira continuam sendo os itens vanilla. As receitas nativas
de 26.2 e 26.3 aceitam `minecraft:wooden_tool_materials`, que já inclui tábuas.
A associação explícita e aditiva das tábuas do mod foi acrescentada a essa tag,
com `replace: false`. Não foi necessário criar receitas duplicadas de armas.
Os ingredientes são somente tábuas e gravetos. Os JSONs nativos usados na auditoria
estão registrados em `vanilla-wood-crafting.json`, com os hashes dos JARs oficiais.

Há 83 novos desbloqueios de família em cada versão, além dos desbloqueios das
três alternativas vanilla e dos equipamentos de madeira. Ao obter/movimentar as
tábuas no inventário, o evento de inventário disponibiliza as receitas correspondentes.
Os novos caminhos de advancement funcionam também em mundos existentes; não
exigem limpar os advancements anteriores. Livro desbloqueado não dispensa os
ingredientes: o filtro “fabricáveis” só mostra o que pode ser feito com o inventário.

## Preservação e verificações

- 17.351 arquivos de execução/configuração comparados com os hashes da entrega H6.
- 17.668 verificações de paletas, preservação, referências, opacidade e bordas: PASS.
- 7.982 verificações de receitas, ingredientes, resultados e desbloqueios: PASS.
- 7.685 verificações estáticas dos móveis herdadas do H6: PASS.
- 15.708 verificações da entrega e compatibilidade de recursos: PASS.
- Varredura geral: 177.645 verificações, PASS.
- Regeneração completa em cópia isolada: 17.539 recursos equivalentes; 17.536
  idênticos em bytes e 3 JSONs equivalentes com ordem de chaves diferente.
- Testes negativos detectaram folha Blue Spruce incorreta, ingrediente de placa
  incorreto e esquema de advancement 26.3 incorreto.

A referência histórica Fix 10 não foi reescrita. O verificador permite exatamente
os 12 novos PNGs autorizados, com hashes fixados; preserva os outros 4.211 arquivos
dessa referência. O verificador de JAR agora compara o conjunto e conteúdo das
receitas, dos assets e dos desbloqueios com os fontes, em vez de depender apenas
de uma contagem antiga. Há 1.001 receitas no namespace do mod por versão.

Esses resultados são estáticos. Não foram executados Java, Gradle, Minecraft,
modpacks ou testes de renderização em jogo nesta revisão. A geometria e os
renderizadores que corrigiram o flickering permanecem exatamente os do H6, mas
isso não substitui a conferência visual em jogo. Não há migração nem necessidade
prevista de criar outro mundo: IDs e dados salvos foram preservados.
