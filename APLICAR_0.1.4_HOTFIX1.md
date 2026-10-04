# Chromus Flora 0.1.4 — Hotfix 1 de fontes

Patch incremental para a entrega completa 0.1.4 (três ZIPs). Não é um projeto completo e não muda a versão dos JARs.

## O que corrige

- Substitui `BlockEntityRendererRegistry` e `EntityRendererRegistry`, obsoletos, por `BlockEntityRenderers` e `EntityRenderers`. As duas APIs nativas são disponibilizadas pelos access wideners transitivos da Fabric API presente nas dependências 26.2 e 26.3.
- Permite alterações no arquivo local `.vscode/settings.json`. O verificador sinaliza esse arquivo como configuração editável e continua exigindo o hash exato de todos os demais arquivos do manifesto. A exceção é uma lista fixa, contendo apenas esse caminho.
- Remove do manifesto duas referências indevidas a caches Python em `tools/__pycache__`, permitindo que a limpeza os mova ao backup sem conflito com a lista de arquivos ativos.
- Não substitui suas configurações do VS Code. Não desativa `-Werror`, não suprime avisos e não altera baús, barcos, inventários ou a correção de chunks.

O primeiro PASS seguido de erro mostra que `.vscode/settings.json` mudou entre as duas verificações. O log não identifica o processo responsável. Essa mudança local não deve bloquear a verificação dos fontes Gradle.

## Aplicar

Extraia `ChromusFlora_0.1.4_Hotfix1_Fontes.zip` diretamente em `D:\Repository\ChromusFlora`, permitindo substituir os arquivos. Não extraia os ZIPs originais por cima depois deste patch.

```powershell
cd D:\Repository\ChromusFlora
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\tools\verify-source.ps1
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\tools\clean-project.ps1
.\gradlew.bat build --no-daemon --warning-mode=fail
```

**Se qualquer etapa falhar, pare nela.** A limpeza anterior foi interrompida antes de remover a receita obsoleta do barco; por isso é necessário executá-la novamente após aplicar o patch.

Saídas permanecem:

- `build\26.2\chromus-flora-0.1.4-26.2.jar`
- `build\26.3\chromus-flora-0.1.4-26.3.jar`

O aviso de daemon de uso único é informativo e não causou esta falha. Não é necessário apagar caches, alterar configurações do mundo ou criar outro mundo para corrigir estes erros de compilação/verificação.

## Validação e limites

Foram conferidos os métodos, as assinaturas, a ausência de depreciação nas novas classes/métodos e as regras de acesso transitivo dos artefatos reais de ambas as versões. A sintaxe Java foi analisada sem executar Java. Foram simulados o patch sobre a entrega 0.1.4, a alteração da configuração local e a detecção de corrupção em um fonte.

Nenhum Java, Gradle, PowerShell ou Minecraft foi executado nesta revisão. Compilação e teste em jogo continuam no ambiente do usuário. O relatório está em `verification/release-0.1.4/hotfix1-checks.json`.

Referência oficial: https://maven.fabricmc.net/docs/fabric-api-0.155.2%2B26.2/net/fabricmc/fabric/api/client/rendering/v1/BlockEntityRendererRegistry.html
