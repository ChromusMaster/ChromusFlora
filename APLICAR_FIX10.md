# Fix 10 — aplicação

Pacote completo: extraia diretamente na raiz do repositório, substituindo arquivos.
Siga README.md, seção Português do Brasil. Com Minecraft e IDE fechados:

```powershell
Set-Location D:\Repository\ChromusFlora
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\tools\verify-source.ps1
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\tools\clean-project.ps1 -WhatIf
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\tools\clean-project.ps1
.\gradlew.bat build --no-daemon --warning-mode=fail
```

Pare se qualquer etapa falhar. A limpeza preserva os arquivos removidos em um backup
irmão do repositório. Após BUILD SUCCESSFUL, use somente o novo JAR fix10, sem -sources.
Não há necessidade de executar clean ou compilar novamente no VS Code.

Texturas: efeito nos blocos existentes após reiniciar. Galhos: somente árvores novas,
geradas ou crescidas de mudas. Teste as mudas em espaço aberto, longe de construções.
Não há reconstrução automática de árvores já existentes.
