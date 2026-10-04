# CPU e memória — revisão 0.1.2

A revisão examinou fontes compartilhados, adaptadores das duas versões, integração Jade/Jaiz/TerraBlender, geração de árvores, receitas, modelos e texturas. Foram aplicadas mudanças de custo previsível, sem alterar formas, densidades, alturas ou orçamento de colocação das árvores. Não há benchmark do modpack nesta entrega.

## Alterações implementadas

| Área | Alteração | Limite da conclusão |
|---|---|---|
| Limites das árvores | Cache por paleta da estrutura, com referências fracas e limite de 2.048 entradas; guarda apenas dimensões, contagem e raio | Evita repetir a varredura dos blocos quando a paleta já foi validada; não mede o custo da colocação feita por OTTYG |
| Concorrência da cache | Sincronização apenas nas consultas e alterações do mapa; cálculo fora do bloqueio | Duas threads podem calcular a mesma entrada inicialmente; não seguram o bloqueio durante a varredura |
| Recarga | A chave é a paleta; a recarga vanilla substitui as paletas. Dimensões e contagem também são conferidas | Um mod que mutar a mesma paleta in-place, preservando dimensões e contagem, exigirá integração específica |
| Alocações de posição | Dois `MutableBlockPos` por avaliação, reutilizados na checagem dos chunks | Mantém `hasChunk`, halo de leitura, zona de escrita e limites verticais |
| Jade | Busca por ID em mapa, mantendo a melhoria do Fix3.2 | Evita percorrer 83 espécies a cada tooltip; não reduz o trabalho de outros providers |
| Catálogo de blocos | Uma view imutável reutilizada | Evita criar wrappers em acessos repetidos; o registro continua ocorrendo na inicialização |
| Portas e alçapões | Modelos vanilla simples; detalhes nas texturas | Não há entidades, animações por frame, shaders próprios ou emissão de luz adicional |
| Móveis | Bancada sem block entity; um tipo de block entity compartilhado pelos baús, sem ticker de animação | Baús têm tampa estática; os custos normais de inventário, comparadores e abertura continuam |

No Fix3.2 já existia cache por estrutura. Esta versão troca sua retenção por uma cache limitada por paleta e reutiliza as posições; não apresenta a cache como ganho inteiramente novo em relação àquela revisão.

As 669 imagens PNG do runtime continuam somando **12.566.528 bytes de pixels RGBA**, calculados por largura × altura × 4: o mesmo orçamento de pixels do Fix3.2. Os móveis reutilizam texturas existentes. Essa conta não inclui mipmaps, padding dos atlas, buffers, objetos Java ou memória de GPU; não é uma medição de RAM do jogo. As sete imagens-fonte maiores ficam fora dos source sets de recursos do JAR.

A densidade máxima declarada continua 6; as árvores mantêm raio horizontal revisado de até 15 blocos e as mesmas formas. Os limites estáticos medidos nos recursos continuam 2.620 blocos máximos de copa e 3.071 candidatos máximos por árvore. Os testes geométricos não executam a feature Java nem demonstram segurança de qualquer datapack que acrescente decorators ou providers próprios.

Configurações e catálogos são lidos na inicialização, sem novo acesso a arquivos por tick. Os loops de registros e das regras de terreno continuam no bootstrap. Não foram introduzidas threads, tarefas periódicas globais, caches de mundos/chunks ou geração retroativa.

## O que os logs permitem concluir

Os logs fornecidos contêm pausas e avisos de geração, mas não trazem amostragem suficiente para atribuir os picos a ChromusFlora. Um ciclo de features Terralith/Terrestria também foi reproduzido no fixture sem Flora. Nenhum desses mods foi alterado silenciosamente. Não se afirma que essa revisão resolveu picos causados pelo restante do modpack.

## Capturar o pico no Windows com spark

O modpack informado já inclui spark. Faça a comparação com a mesma distância de renderização/simulação, JVM, shaders e conjunto de mods. Separe um trecho em chunks já existentes de um trecho em chunks novos, usando cópias equivalentes do mundo para comparar versões.

Para CPU, no mundo local com permissão de comandos:

```text
/spark profiler start --thread *
```

Reproduza o pico por cerca de dois minutos, então salve o perfil local:

```text
/spark profiler stop --save-to-file
```

Para relacionar pausas à coleta de lixo, ative `/spark gcmonitor`, reproduza o episódio e desative-o com o mesmo comando. O `latest.log` desse período ajuda a correlacionar os horários. Para investigar o cliente/renderização, faça uma coleta separada com `/sparkc profiler start --thread *` e `/sparkc profiler stop --save-to-file`.

Se o mecanismo de profiling disponível no seu sistema aceitar alocações, faça uma coleta separada com `/spark profiler start --alloc` e finalize com `/spark profiler stop --save-to-file`. Caso esse modo não seja suportado no Windows, o perfil de CPU e o log do GC ainda são úteis; inclua a mensagem retornada pelo spark.

Envie o arquivo local produzido, o `latest.log` correspondente e informe se o trecho percorria chunks novos ou existentes. Esses dados permitem distinguir geração de terreno, renderização, leitura de disco, coleta de lixo e custo dos demais mods. Um aumento de uso de heap seguido de coleta não basta, sozinho, para provar vazamento.

Documentação do profiler: https://spark.lucko.me/docs/Command-Usage

Investigação de picos: https://spark.lucko.me/docs/guides/Finding-lag-spikes
