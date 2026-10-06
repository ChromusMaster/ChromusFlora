# Hotfix 5 — revisão dos móveis

## Evidência e correções

No vídeo de 23,416867 s, 1280×720 a 60 fps, a faixa sob a crafting table expõe regiões que deveriam estar cobertas pelo terreno. O modelo recuado e o uso de propriedades de `Blocks.CRAFTING_TABLE` sem `noOcclusion()` confirmam a configuração incompatível: o bloco ocultava faces vizinhas como um cubo inteiro. Corrigido no construtor, sem alterar colisão ou menu.

O gerador anterior sobrepunha o gabinete aos quatro pés e a haste à cabeça dos emblemas metálicos. As peças foram particionadas mantendo seu contorno. O tampo decorado agora termina em y=16, em vez de avançar até 16,1. Todas as coordenadas UV permanecem dentro de [0,16]. São 21 caixas/126 faces por modelo de bancada, antes 19/114. O custo adicional é de geometria estática, sem novos callbacks por tick. Não foi realizado benchmark.

O `ChestModel` nativo, nas duas versões, define corpo y=0..10 e tampa y=9..14. A aplicação de duas texturas opacas diferentes em superfícies laterais coincidentes cria uma faixa suscetível a z-fighting. O renderer Flora agora escala somente o corpo para y=0..9, salvando a pose inicial para que `setupAnim` não desfaça a correção. A tampa, a fechadura, os modelos esquerdo/direito e a lógica nativa de abertura continuam em uso. O modelo de inventário foi alinhado à mesma junção. As texturas PNG não foram editadas.

A evidência estática confirma os defeitos corrigidos; somente a reprodução local no jogo pode confirmar que todos os sintomas do vídeo desapareceram.

## Build e verificadores

`layout.buildDirectory` de cada alvo agora aponta para `build/<versão>/Fabric`, não apenas o destino do JAR. O verificador de JARs e o modelo de CI foram atualizados. Nenhum loader adicional foi implementado. A compilação continua em JDK 25, com `-Werror`, e mantém a exceção de lint de classfile já existente somente no cliente 26.3.

O verificador geral tinha regras obsoletas que rejeitavam comentários explicativos e procuravam uma expressão literal antiga das opções do compilador. Foram corrigidas, mantendo a análise sintática Python, os testes de integridade de recursos, a detecção de cópias binárias de assets antigos e a obrigatoriedade de `-Werror`.

## Preservação e testes

Consulte `preservation-checks.json`, `native-api-checks.json`, `native-chest-geometry.json`, `furniture-checks.json` e `validation-summary.json`. A suíte de geometria rejeita os casos antigos de sobreposição e verifica as três variantes de baú nas duas versões, incluindo uma varredura analítica de abertura de 0° a 90°. Isso não é uma renderização executada no Minecraft.

Foram preservados byte a byte os arquivos protegidos identificados no relatório, incluindo registros, inventários, receitas, geração de mundo, correções anteriores de chunks, barcos e README com banner. O Hotfix 5 não requer criação de mundo novo nem migração de dados.

Fontes técnicas consultadas: `https://wiki.fabricmc.net/tutorial:blockappearance`, `https://wikis.khronos.org/opengl/Depth_Buffer_Precision` e os JARs oficiais Minecraft 26.2/26.3, cujos hashes e assinaturas constam no relatório. A inspeção dos JARs foi feita como dados, sem executar Java.
