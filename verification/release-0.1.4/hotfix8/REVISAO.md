# Chromus Flora 0.1.4 — Hotfix 8

## Entrega

83 espécies × 5 itens = **415 novos itens**: placa, botão, placa de pressão,
espada e lança por madeira. São 332 blocos novos: placa de chão, placa de parede,
botão e placa de pressão. Há um único item de placa para as duas posições.
Placas suspensas não fazem parte desta revisão.

As placas usam colocação, edição de texto, tinta, brilho, cera e entidade de bloco
nativos. Os botões usam o comportamento de madeira vanilla (30 ticks), incluindo
ativação por projéteis; as placas de pressão usam BlockSetType.OAK. Essas funções
são herdadas, não reimplementadas. O uso de OAK aqui define comportamento e som;
a aparência vem da textura da espécie nos modelos.

Espadas e lanças usam ToolMaterial.WOOD e os mesmos argumentos usados pelos itens
vanilla em cada versão. Durabilidade, combate, encantabilidade e reparo ficam
sob o comportamento nativo. As tags swords/spears são aditivas e alcançam as tags
de encantamento correspondentes. Todas as espécies têm o mesmo equilíbrio de
combate; não foi inventada vantagem por cor ou bioma. A queima usa FuelValueEvents
na 26.2 e cookingFuel na 26.3.

## Compatibilidade entre versões

A auditoria dos JARs oficiais detectou que SignItem existe em 26.2 e não existe
em 26.3. O adaptador 26.2 usa SignItem; o 26.3 usa StandingAndWallBlockItem com
Direction.DOWN e o componente signText, seguindo o registro nativo de oak_sign.
StandingSignBlock e WallSignBlock são adicionados aos blocos válidos da entidade
SIGN usando a extensão Fabric. A injeção de interface para compilação foi
confirmada nos arquivos classtweaker das dependências exatas do projeto.

Os modelos de placa são JSON com pais nativos nas duas versões; não foi usado
o antigo mecanismo de uma textura de entidade por WoodType. Nenhum renderizador
novo foi registrado, evitando duplicar a malha da placa com a renderização do texto.
Os modelos dos móveis continuam exatamente os do Hotfix 6 aprovado.

## Receitas

Todas exigem tábuas da espécie do resultado. Gravetos continuam vanilla:

| Item | Ingredientes | Resultado |
|---|---|---|
| Placa | 6 tábuas da mesma espécie + 1 graveto | 3 placas |
| Botão | 1 tábua | 1 botão |
| Placa de pressão | 2 tábuas da mesma espécie | 1 placa de pressão |
| Espada | 2 tábuas da mesma espécie + 1 graveto | 1 espada |
| Lança | 1 tábua + 2 gravetos, diagonal | 1 lança |

As três receitas de fallback H7 ficam desativadas por fabric:false, assim como
seus desbloqueios. Os arquivos permanecem como tombstones de atualização: um ZIP
sobreposto não pode deixar a versão antiga ativa no diretório. Não os apague
isoladamente. As receitas minecraft:wooden_sword e minecraft:wooden_spear mantêm
seus IDs e resultados, mas usam o ingrediente Fabric difference para excluir as
tábuas Chromus Flora. Isso elimina a disputa com as receitas por espécie e mantém
as madeiras externas no ingrediente nativo. Modpacks que substituam esses mesmos
dois JSONs precisam mesclar essa exclusão; não há teste de todo modpack possível.
Misturar tábuas de espécies distintas não é uma receita de arma/placa desta entrega.

São 415 novos desbloqueios por versão, agrupados por categoria de item no livro.
Obter ou movimentar a tábua no inventário aciona o desbloqueio correspondente.
O filtro de itens fabricáveis continua exigindo todos os ingredientes disponíveis.

## Mundos existentes e preservação

Nenhum ID antigo foi renomeado, removido ou convertido. Os registros novos são
acrescentados após os itens antigos. Itens/placas/botões de carvalho que já foram
produzidos continuam vanilla: não há informação que permita recuperar a espécie
da tábua consumida para convertê-los corretamente.

17.578 arquivos de execução do H7 permanecem idênticos em bytes e estão protegidos
por hashes. As alterações existentes são limitadas ao ponto de registro de
conteúdo, traduções, tag de machado e desativação dos fallbacks H7. Todas as
texturas PNG, modelos antigos, estruturas, configurações de worldgen, renderizadores
de baús/barcos e código de compatibilidade de chunks foram preservados.
README/banner, configurações locais do editor, JDK 25 e layout de build por versão
/Fabric permanecem iguais. Não há rotina nova de geração de chunks nem migração
de mundo. O custo adicional é o registro/carregamento de modelos e receitas, além
das entidades de placa nativas quando o jogador as coloca.

## Verificações realizadas

- 45.815 verificações H8: receitas, ingredientes errados, exclusão vanilla,
  desbloqueios, tags de armas/encantamentos, modelos, 16 rotações de placa, quatro
  faces de placa de parede, 24 estados de botão, dois estados de placa de pressão,
  loot por espécie e preservação H7: PASS.
- APIs dos clientes oficiais 26.2/26.3 e Fabric API 0.161.0 de cada versão: PASS.
- Parser de sintaxe Java: 55 arquivos, PASS. Isso não é compilação nem type checking.
- Varredura geral: 214.295 verificações, PASS.
- Verificação integrada: 16.041 verificações, PASS, incluindo os testes de móveis H6.
- Regeneração completa: 21.534 recursos equivalentes, 21.531 idênticos em bytes;
  três JSONs diferem apenas na ordem de chaves.
- Testes negativos detectam receita vanilla concorrente, drop de placa errado
  e reativação indevida do fallback.

Os relatórios JSON estão nesta pasta. **Não foram executados Java, Gradle,
Minecraft ou um modpack nesta revisão.** A compilação local e testes reais de
colocação, texto, redstone, combate e renderização continuam necessários.

Referências oficiais consultadas:

- https://maven.fabricmc.net/docs/fabric-api-0.155.2+26.2/net/fabricmc/fabric/api/object/builder/v1/block/entity/FabricBlockEntityType.html
- https://github.com/FabricMC/fabric-api
- Clientes oficiais identificados pelos SHA-1 nos arquivos api-checks.json e native-contracts.json.
