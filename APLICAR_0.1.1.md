# Aplicar Chromus Flora 0.1.1

Entrega completa em fontes para Fabric 26.2 e 26.3. Não contém JARs compilados. Os builds e os testes no jogo ainda precisam ser executados; os relatórios desta entrega são verificações estáticas.

## Atualizar a pasta do projeto

1. Feche builds e instâncias do jogo que usem esse projeto.
2. Extraia o conteúdo do ZIP diretamente sobre `D:\Repository\ChromusFlora`, substituindo os arquivos correspondentes. `build.gradle`, `flora`, `versions` e `tools` devem ficar na raiz, sem uma pasta extra.
3. No terminal PowerShell, inclusive o terminal integrado do VS Code, execute:

```powershell
cd D:\Repository\ChromusFlora
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\tools\verify-source.ps1
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\tools\clean-project.ps1
.\gradlew.bat build --no-daemon --warning-mode=fail
```

A limpeza move os caminhos obsoletos para um backup ao lado do projeto. Inclui os quatro arquivos Java deslocados para os adaptadores de versão. `.git`, `.github`, mundos, mods e configurações ficam preservados. O build também exclui cópias antigas desses Java da origem compartilhada, caso ainda estejam presentes.

`verify-source.ps1` verifica a integridade da entrega, não a compilação. Mudanças deliberadas nos arquivos após a extração poderão deixar os hashes diferentes.

## Saídas do mesmo comando

| Minecraft | JAR de uso no jogo |
|---|---|
| 26.2 | `build/26.2/chromus-flora-0.1.1-26.2.jar` |
| 26.3 | `build/26.3/chromus-flora-0.1.1-26.3.jar` |

Os JARs de fontes ficam em `build/<versão>/sources/`. Não os coloque na pasta `mods`. Para compilar somente uma versão, use `:mc26_2:build` ou `:mc26_3:build` no lugar de `build`.

Validação adicional dos artefatos, se Python estiver instalado:

```powershell
python .\tools\verify-jars.py
```

A mensagem de Gradle sobre `single-use Daemon` é informativa, mesmo com `--no-daemon`: a JVM temporária atende às configurações do build e encerra ao final. O resultado relevante é `BUILD SUCCESSFUL` ou o erro apresentado depois.

## Mundo já criado

Use o JAR **26.2** no modpack atual 26.2. Substitua o JAR anterior do Flora, deixando apenas uma versão instalada. Faça a primeira abertura em uma cópia do save e confirme blocos já colocados, inventário, receitas, geração de chunks e salvamento/reabertura.

Os IDs e as definições dos blocos antigos foram preservados. Não há apagamento de chunks, retrogen, troca do namespace `chromusflora` ou conversor de saves. As árvores existentes não são redesenhadas. Essa preservação é uma evidência estática; não equivale a um teste do save com todos os mods.

Não abra o mundo de produção em 26.3 como parte desta atualização. O alvo 26.3 exige versões correspondentes de todas as dependências e dos outros mods. O Terrestria e o Biolith anexados declaram dependência de Minecraft menor que 26.3.

## Crafting

- Mova um tronco para outro slot do inventário, faça tábuas e mova as tábuas: isso dispara o desbloqueio de receitas em um jogador que já existia.
- Portas, alçapões, cercas e portões usam **tábuas**, não troncos.
- Quatro troncos iguais em quadrado produzem três blocos de madeira com casca em todas as faces. Há a versão descascada equivalente.
- Barcos feitos com as tábuas do mod resultam no barco de carvalho vanilla. Baús e bancadas também resultam nas versões vanilla. As portas e os alçapões são próprios de cada família.

## GitHub Actions

O template atualizado está em `tools/ci/gradle.yml`. Substitua o conteúdo do workflow existente em `.github/workflows/` por esse template. Não mantenha o workflow antigo duplicado.

Há um único setup-gradle e um único build, que produz as duas versões. A etapa seguinte verifica o conteúdo dos dois JARs antes de publicá-los como artefatos do job. O template não executa dependency-submission, que exige permissões e configuração próprias. A entrega não sobrescreve automaticamente seus workflows.
