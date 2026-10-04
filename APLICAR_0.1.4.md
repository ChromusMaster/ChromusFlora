# Chromus Flora 0.1.4 — baús e barcos

Entrega completa de fontes e recursos para Minecraft 26.2 e 26.3. **Não compilada nem executada em Java/Minecraft nesta revisão.** As verificações fornecidas são estáticas. Detalhes em `docs/REVISAO_0.1.4.md`.

## Aplicar

1. Feche o jogo. Guarde uma cópia do mundo e o JAR 0.1.3 que funcionou para poder testar e reverter com segurança.
2. Extraia os **três ZIPs na mesma pasta do projeto**, por exemplo `D:\Repository\ChromusFlora`, permitindo substituir arquivos. São partes complementares, sem subpasta adicional. Não extraia na pasta do mundo.
3. Execute:

```powershell
cd D:\Repository\ChromusFlora
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\tools\verify-source.ps1
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\tools\clean-project.ps1
.\gradlew.bat build --no-daemon --warning-mode=fail
```

A limpeza move arquivos obsoletos para um backup externo ao projeto. Ela também remove a receita antiga que convertia qualquer madeira Flora em barco de carvalho.

Saídas esperadas:

- `build\26.2\chromus-flora-0.1.4-26.2.jar`
- `build\26.3\chromus-flora-0.1.4-26.3.jar`

Após compilar, `python .\tools\verify-jars.py` confere os dois artefatos. Na instância 26.2, substitua apenas o JAR do Chromus Flora pela saída 26.2. Não mantenha duas versões do mod. As dependências permanecem as da 0.1.3.

## Conferir no mundo existente

Use uma cópia do mundo com o mesmo modpack. **Não é necessário criar um mundo novo.**

1. Confira os itens de baús já colocados. Teste baús simples e duplos nas quatro orientações, abrindo por ambas as metades. Observe tampa, fecho, junção central, sons e bloqueio por um bloco acima.
2. Teste transferência com funis, baús submersos e quebra de uma metade de um baú duplo. Salve, feche e reabra para conferir conteúdo e aparência. Recarregue os recursos com F3+T e confira novamente.
3. Fabrique barcos com cinco tábuas da mesma espécie, no formato nativo. Confira ícone, madeira no mundo, remos, embarque, desembarque, dispensadores e o item recebido ao destruir o barco. Salve e reabra com barcos de espécies diferentes colocados.
4. Visite os chunks que antes falhavam e confira o log. A correção de leitura de chunks da 0.1.3 foi preservada byte a byte.

Barcos de carvalho fabricados anteriormente continuam barcos de carvalho. Esta versão adiciona barcos comuns; não adiciona barcos com baú. Depois de salvar barcos novos no mundo, não volte à 0.1.3 nesse mesmo save; para reverter, use a cópia anterior.

## Ferramentas

Requisitos de compilação: JDK 25 e Gradle 9.5.1. O bootstrap Windows baixa e verifica o Gradle; não é necessário regenerar recursos com Python. Em Linux/macOS, instale essas versões e use `sh ./gradlew build --no-daemon --warning-mode=fail`.

Para repetir as verificações estáticas:

```powershell
python -m pip install -r tools/requirements.txt
python tools/scan.py
python tools/check-release.py
python tools/check-joinery.py
python tools/check-boats.py
python tools/check-door-gallery.py
```

O modelo de CI em `tools/ci/gradle.yml` contém as verificações e a compilação dos dois alvos. Os recursos finais já estão no pacote. O histórico de verificações antigas serve como referência, não como resultado de compilação desta versão.
