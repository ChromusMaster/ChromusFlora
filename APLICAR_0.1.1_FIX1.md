# Chromus Flora 0.1.1 — correção 1 de compilação

Corrige o erro `cannot find symbol: getStructureManager()` em `:mc26_3:compileJava`.

O código compartilhado usava o nome da API 26.2 em ambas as versões. Agora ele chama `FloraPlatform.structureTemplates(level)`, cuja implementação usa `getStructureManager()` em 26.2 e `getStructureTemplateManager()` em 26.3. As assinaturas, o retorno e o acesso público foram conferidos nos artefatos correspondentes do Minecraft. A inspeção anterior não cobriu essa chamada e deixou o erro passar.

## Aplicação sobre a pasta atual

1. Extraia este ZIP diretamente sobre `D:\Repository\ChromusFlora`, substituindo os arquivos correspondentes. O ZIP de correção exige o pacote completo 0.1.1 já instalado; o pacote completo atualizado pode ser usado sozinho.
2. Execute no PowerShell:

```powershell
cd D:\Repository\ChromusFlora
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\tools\verify-source.ps1
.\gradlew.bat build --no-daemon --warning-mode=fail
```

Não é necessário executar a limpeza novamente: não há arquivos removidos nem deslocados nesta correção. O manifesto completo foi atualizado para reconhecer os fontes corrigidos.

A versão do mod continua 0.1.1. Saídas esperadas:

- `build/26.2/chromus-flora-0.1.1-26.2.jar`
- `build/26.3/chromus-flora-0.1.1-26.3.jar`

A mensagem sobre `single-use Daemon` não é a causa do erro. A falha foi uma chamada Java incompatível com 26.3.

## Alcance e validação

Foram alterados três arquivos Java: o ponto de acesso compartilhado e os dois adaptadores de versão. Receitas, texturas, estruturas, IDs e definições de mundo permanecem byte a byte iguais aos do pacote 0.1.1 anterior. Não há migração de save ou alteração de mundo nesta correção.

A sintaxe dos fontes e as assinaturas dos métodos foram inspecionadas estaticamente. **Não foram executados Gradle, compilação Java ou Minecraft.** O relatório está em `verification/release-0.1.1/template-access-fix1.json`.
