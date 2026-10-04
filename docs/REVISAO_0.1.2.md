# Revisão 0.1.2 — 03/10/2026

## O que mudou

As seis imagens enviadas foram adaptadas para as 83 espécies existentes. Há 83 portas diferentes e 83 alçapões correspondentes, com painéis, grades, entalhes, flores, escamas, cristais e ferragens conforme as referências. Os desenhos são adaptações ao formato do jogo, não recortes diretos das fotografias das pranchas. Nenhuma textura de outro mod foi incorporada.

A segunda referência contém 12 desenhos e a última contém um desenho extra sem espécie. A associação completa e as adaptações estão em `atelier/joinery/species.json`. Fungal Imparius recebeu uma variante de cogumelos na cor ciano das suas tábuas; Giant Pink Allium recebeu a variação floral correspondente. A porta dupla ilustrada de Mahogany foi adaptada para uma folha do Minecraft. O desenho marrom extra da última referência ficou fora das 83 espécies. Os prompts e sete arquivos de arte-fonte estão em `atelier/joinery/`; não entram no JAR do jogo.

Cada face de bloco tem 64×64 pixels. A imagem completa da porta é redimensionada antes de ser dividida, e o ícone 64×128 usa a mesma imagem. Isso evita o desalinhamento produzido por recortes independentes. Foram mantidos os modelos vanilla de abertura/dobradiça, os 32 estados da porta e os 16 estados do alçapão. Os ícones frontais corrigidos no Fix3.2 foram preservados. As janelas são ilustradas em textura opaca; arcos, cristais e entalhes não acrescentam geometria nem emissão de luz.

Há 83 bancadas e 83 baús próprios, usando as texturas de madeira já existentes. Os baús herdam o inventário do baú nativo e usam um tipo de block entity próprio, `chromusflora:wood_chest`. O modelo cobre baú simples e as duas metades do baú duplo. A bancada abre o menu nativo de crafting 3×3 e valida a distância em relação ao seu próprio bloco.

## Livro de receitas

Os grupos `crafting_table` e `chest` reúnem as variantes no livro nativo. Com o filtro **somente fabricáveis**, o livro usa os materiais disponíveis; com várias madeiras disponíveis, alterna as opções do mesmo grupo. Sem esse filtro, também pode mostrar variantes não fabricáveis. Não foi criado um ícone de inventário que muda dinamicamente nem um único item que troca de madeira depois de fabricado.

Cada variante requer tábuas de uma espécie só. As receitas vanilla de bancada/baú excluem apenas as tábuas Flora, por meio do ingrediente de diferença da Fabric API; as outras tábuas continuam elegíveis. Isso evita que a receita vanilla concorra com a saída da madeira correspondente. As antigas receitas Flora redundantes que davam bancada/baú vanilla foram removidas, inclusive no overlay de 26.3. Há conversão de um móvel Flora para o equivalente vanilla, usando o item sozinho na grade, para receitas de outros mods que exijam o item vanilla exato.

Esses dois arquivos de receita vanilla podem ser substituídos por datapacks ou outros mods com o mesmo identificador. A revisão estática não executa o resolvedor de receitas do modpack. Não foi alterado o inventário criativo para esconder variantes, nem a interface de EMI/REI/JEI.

## Limites dos móveis

- O novo baú tem **tampa visual estática**, embora o menu de armazenamento use o comportamento nativo. Não há renderer animado nem ticker de animação por baú.
- A nova bancada não persiste ingredientes ao fechar e não reproduz a exibição de itens do Visual Workbench. O fallback vanilla permite continuar usando as integrações desse mod.
- Baús duplos usam a mesma espécie. Não foi implementada mistura de espécies nas duas metades ou mistura de tábuas na receita.
- Baús e bancadas vanilla já colocados não são convertidos. Os barcos continuam sendo barcos de carvalho vanilla.

## Preservação e validação

Não foram renomeados IDs antigos, alteradas estruturas NBT de árvores, densidades de geração, definições de biomas ou as 332 texturas de madeira. A correção dos acessores de estruturas separados para 26.2/26.3 foi mantida. Não há retrogen, conversão automática de saves ou migração de entidades antigas.

| Verificação estática | Resultado |
|---|---|
| Varredura de fontes e recursos | PASS; 175.479 asserções |
| Recursos e esquemas dos dois alvos | PASS; 15.208 asserções; 918 receitas por alvo incluindo 2 vanilla |
| Preservação em relação ao Fix10 | 4.223 definições idênticas |
| Comparação adicional com Fix3.2 | 4.556 verificações sem alteração dos recursos protegidos |
| Marcenaria e separação de receitas | PASS; 2.512 asserções; 83 imagens completas distintas |
| Galeria de portas | PASS; 420 verificações |
| Estruturas e limites de geração | PASS; 21.190 asserções; 1.119 formas; 3.747.840 rotações de voxels verificadas |
| Regeneração completa de recursos em cópia isolada | 12.666 recursos compartilhados + 4.180 do overlay 26.3 reproduzidos byte a byte |
| APIs 26.2 e 26.3 | Imports e assinaturas inspecionados; parser Java sem erros sintáticos |

As contagens refletem o que os scripts verificam; não representam execuções do jogo. Não foram executados compilador Java, Gradle, JDT, servidor, cliente Minecraft ou a instância com 277 mods. A análise de API não substitui a checagem de tipos Java, de avisos do editor ou de compatibilidade em execução. Não é possível afirmar redução medida dos picos sem perfil de CPU/alocação do seu ambiente.

Os relatórios desta revisão ficam em `verification/release-0.1.2/`. `verification/global-scan.json` e `verification/visual-resources.json` incluem os detalhes da varredura. `docs/DESEMPENHO_0.1.2.md` descreve as mudanças e o teste necessário.

## Referências consultadas

- Macaw's Doors: https://github.com/sketchmacaw/MacawsDoors
- Macaw's Trapdoors: https://modrinth.com/mod/macaws-trapdoors
- More Crafting Tables: https://github.com/LieOnLion/More-Crafting-Tables
- More Chest Variants: https://github.com/LieOnLion/More-Chest-Variants
- Fabric custom ingredients: https://github.com/FabricMC/fabric
- Visual Workbench: https://github.com/Fuzss/visual-workbench/tree/26.2.x
- Nether Chested: https://github.com/Fuzss/nether-chested/tree/26.2.x

As referências de mods serviram para estudar organização, agrupamento de receitas e APIs. A arte final parte das imagens enviadas pelo usuário e de geração de imagens para o projeto; arquivos de outros mods não integram esta entrega.
