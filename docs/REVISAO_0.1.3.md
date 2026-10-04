# Revisão técnica — Chromus Flora 0.1.3

## Defeito e escopo

Os 13 relatórios enviados apontam `NoSuchElementException` no handler `ohthetreesyoullgrow$readScheduledRandomTicks`, em mundos 26.2 com OTTYG 11.0.1. A mesma classe do serializador está presente, byte a byte, no OTTYG 12.0.0 usado pelo alvo 26.3.

O escritor coloca `scheduled_random_ticks` dentro do composto `ohthetreesyoullgrow`, em `structureData`. O leitor verifica a presença da chave no composto interno, mas chama `getList` no composto externo. O `Optional.orElseThrow` seguinte falha.

## Correção

Um mixin marcador no `SerializableChunkData` fornece um ponto `postApply`. O plugin identifica o handler pela anotação `MixinMerged` do serializador OTTYG e pelo sufixo do método, sem depender do prefixo aleatório gerado pelo Mixin. Verifica 23 instruções do início do método, descritores, constantes e unicidade da chamada antes de trocar o receptor `ALOAD` externo pelo interno.

Na classe original isso equivale a trocar o índice local 6 por 7 em um único operando. O plugin deriva os índices das instruções de armazenamento; não assume que os índices serão sempre 6 e 7. O tamanho do código, os tipos na pilha, os desvios, as variáveis locais, a iteração e o escritor permanecem intactos. Nenhuma exceção de dados malformados é suprimida.

A alteração ocorre uma vez, durante a transformação da classe; não cria uma busca, cópia NBT ou cache por chunk. Não foi realizado benchmark de CPU/RAM.

O plugin só é habilitado para **11.0.1 e 12.0.0**. Outras versões registram que esse ajuste específico não foi ativado. Um método já corrigido com a mesma estrutura é aceito sem alteração. Uma estrutura desconhecida nas versões revisadas interrompe a transformação com mensagem explícita, em vez de aplicar um ajuste presumido.

Referências do mecanismo:

- [IMixinConfigPlugin — SpongePowered](https://github.com/SpongePowered/Mixin/blob/master/src/main/java/org/spongepowered/asm/mixin/extensibility/IMixinConfigPlugin.java)
- [Ordem das fases do Mixin](https://github.com/SpongePowered/Mixin/blob/master/src/main/java/org/spongepowered/asm/mixin/transformer/MixinApplicatorStandard.java)
- [Origem MixinMerged](https://github.com/SpongePowered/Mixin/blob/master/src/main/java/org/spongepowered/asm/mixin/transformer/MixinTargetContext.java)

## Validação e limites

- Inspeção estática dos JARs reais das duas dependências e das APIs de Mixin/ASM/Fabric Loader.
- Interpretação em Python das instruções reais do leitor e escritor OTTYG, com modelos de NBT e scheduler. Reproduz a falha original e verifica o ajuste com zero, uma e quatro posições, incluindo coordenadas negativas e duplicatas, por três ciclos de regravação/reabertura. Confere ausência de tags, lista vazia, preservação de dados alheios e manutenção de erro para tag malformada.
- Comparação estática dos padrões do plugin Java com o bytecode real.
- Análise de sintaxe Java e verificações de recursos, receitas, registros e preservação da entrega 0.1.2.
- Verificação de CRC dos ZIPs e SHA-256 dos arquivos entregues.

**Não foram executados compilador Java, Gradle, plugin Mixin em uma JVM, Minecraft ou o mundo do usuário.** A simulação não substitui esses testes. Resultados detalhados: `verification/release-0.1.3/`. Relatórios antigos permanecem como histórico, não como certificação desta revisão.

Para reproduzir a simulação opcional, instale `jawa` em um ambiente Python e execute `tools/check-ottyg-bytecode.py --trees262 CAMINHO_DO_JAR_11.0.1 --trees263 CAMINHO_DO_JAR_12.0.0`. A ferramenta somente lê os JARs. Não é necessária para o build normal.

## Compatibilidade de mundos

Não há migração de save, mudança de namespace, registro, blockstate, NBT de árvores, receitas, texturas ou biomas nesta revisão. Os recursos de conteúdo são os mesmos da 0.1.2. A atualização foi projetada para ler os dados já salvos e manter o escritor original. O aceite no ambiente real exige salvar e reabrir uma cópia do mundo afetado. Um mundo novo não é solução padrão nem substitui esse aceite.
