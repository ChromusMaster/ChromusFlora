# Revisão 0.1.4

## Baús

A versão anterior desativava o ticker do baú no cliente e desenhava um modelo estático de bloco. Isso impedia a animação e usava geometria própria na junção de baús duplos.

Esta revisão restaura o ticker herdado de `ChestBlock` e registra um renderer para o tipo existente `chromusflora:wood_chest`. Usa os modelos nativos simples, esquerdo e direito, com corpo, tampa e fecho separados. A interpolação de abertura, a combinação de metades e a iluminação vêm do renderer nativo. Os modelos estáticos no mundo ficam sem elementos para evitar sobreposição; o inventário usa um modelo fechado separado.

O corpo usa a textura de tábuas da espécie, a tampa usa sua madeira descascada e o fecho usa ferro vanilla. Nenhuma textura PNG existente foi alterada. Os modelos são preparados ao carregar os renderers; o desenho não gera texturas nem relê arquivos a cada quadro.

`FloraChestEntity`, `FloraFurniture`, o ID da entidade de bloco, os IDs de blocos e seus estados permanecem inalterados. Não há migração de inventários, substituição de baús colocados ou reconstrução de chunks.

## Barcos

Cada uma das 83 famílias recebe um item e um tipo de entidade `chromusflora:<especie>_boat`. Usam a implementação nativa de barco, incluindo navegação, remos, passageiros, persistência e drop do item correspondente. Há registro de dispensadores, tags aditivas, tradução e receita desbloqueada pelas tábuas da espécie.

O renderer usa a geometria nativa do barco e a textura existente das tábuas. O ícone de inventário tem um casco em modelo JSON. As receitas usam cinco tábuas da mesma espécie e compartilham o grupo `boat`. A antiga receita genérica de barco de carvalho foi retirada; o ID vanilla e barcos antigos não são alterados.

Os renderers e suas dependências ficam exclusivamente no source set cliente. O código comum registra apenas itens, entidades e comportamentos de jogo. Não foram adicionados eventos globais de tick ou novas rotinas de geração de terreno.

## Preservação e validação

A correção de chunks da 0.1.3, já testada pelo usuário, permanece byte a byte. Também foram preservados os arquivos de geração de mundo, estruturas, definições de biomas, inventários de baús e texturas existentes. Os registros novos de barcos são aditivos.

Foram inspecionadas as assinaturas e instruções relevantes dos artefatos das duas versões do jogo e da Fabric API, sem executar Java. Os relatórios de sintaxe, recursos, receitas, preservação e APIs estão em `verification/release-0.1.4/`.

**Não houve compilação Java/Gradle nem execução do jogo nesta entrega.** A inspeção estática não substitui o teste visual, a interação com baús e barcos, ou o teste com os 277 mods. Não há medição nova de FPS, CPU ou RAM. O roteiro de teste está em `APLICAR_0.1.4.md`.

O README foi refeito em inglês e português brasileiro, limitado à apresentação, finalidade, público e conteúdo do mod.
