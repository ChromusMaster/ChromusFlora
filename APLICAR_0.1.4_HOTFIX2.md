# Chromus Flora 0.1.4 — Hotfix 2 de fontes

Patch cumulativo para a entrega completa 0.1.4, com ou sem o Hotfix 1. Mantém a versão dos JARs. Não é um projeto completo.

## Correções

- Introduz `FloraRenderSubmission` específico para cada alvo, selecionado pelo source set cliente de `versions/26.2` ou `versions/26.3`.
- Na 26.2, mantém as assinaturas de desenho com o parâmetro de quebra. Na 26.3, usa as novas assinaturas e desenha a sobreposição de quebra separadamente, na ordem usada pelo renderer nativo. A tampa continua animada e o barco mantém sua máscara de água.
- Mantém os registros nativos de renderers e a exceção exclusiva para `.vscode/settings.json` do Hotfix 1.
- Preserva integralmente o README enviado pelo usuário, incluindo o endereço do banner, e atualiza seu hash no manifesto.

## Aviso da JOML

O aviso de `Matrix4fc.class` vem da dependência JOML 1.10.9: ela contém anotações de tipo modernas em um classfile com versão antiga. O artefato foi conferido com o SHA-1 declarado pelo Minecraft e correspondente ao caminho do log; isso não indica corrupção do cache local.

Apenas em `:mc26_3:compileClientJava`, o lint passa a ser `-Xlint:all,-classfile`, mantendo `-Werror`. Isso desabilita a categoria de avisos sobre o conteúdo de classfiles externos nessa tarefa. Depreciação, tipos inseguros e os demais avisos continuam ativos e fatais. As demais tarefas mantêm `-Xlint:all`. Essa exceção abrange a categoria nessa tarefa, não exclusivamente uma classe JOML.

A versão da JOML usada pelo jogo não muda; nenhum JAR de dependência é reescrito ou incluído no patch. A exceção deve ser reavaliada quando a dependência for corrigida.

## Aplicar

1. Extraia `ChromusFlora_0.1.4_Hotfix2_Fontes.zip` diretamente em `D:\Repository\ChromusFlora`, permitindo substituir os arquivos.
2. Execute cada etapa abaixo separadamente. Se uma falhar, pare nela.

```powershell
cd D:\Repository\ChromusFlora
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\tools\verify-source.ps1
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\tools\clean-project.ps1
.\gradlew.bat build --no-daemon --warning-mode=fail
```

Não reaplique os ZIPs originais nem o Hotfix 1 sobre o Hotfix 2. A limpeza conserva suas configurações locais e guarda os arquivos obsoletos em backup.

Saídas:

- `build\26.2\chromus-flora-0.1.4-26.2.jar`
- `build\26.3\chromus-flora-0.1.4-26.3.jar`

Depois do build, a verificação opcional `python .\tools\verify-jars.py` também exige a presença do adaptador de renderização em ambos os JARs.

## Validação

Conferência direta dos descritores de cada chamada nos JARs respectivos do Minecraft, identidade dos artefatos, análise sintática Java, seleção dos source sets, integridade do patch e preservação dos arquivos de jogo. O teste estático distingue as assinaturas incompatíveis: não considera suficiente encontrar um método de mesmo nome.

Nenhum Java, Gradle, PowerShell ou Minecraft foi executado nesta revisão. Compilação e validação visual continuam pendentes no ambiente do usuário. Ao testar, confira também as rachaduras ao quebrar baús, suas tampas, os baús duplos e os barcos na água. Use uma cópia do mundo existente; não há migração de saves ou exigência de mundo novo.

Relatório: `verification/release-0.1.4/hotfix2-checks.json`.

Referências: https://docs.oracle.com/en/java/javase/25/docs/specs/man/javac.html e https://github.com/JOML-CI/JOML/issues/398 .
