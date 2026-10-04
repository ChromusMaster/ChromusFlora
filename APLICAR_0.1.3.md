# Chromus Flora 0.1.3 — correção de carregamento de chunks

Esta entrega contém somente fontes, recursos e ferramentas. Não foi compilada nem executada em Java/Minecraft. A correção foi preparada para mundos existentes; criar outro mundo não é requisito.

## Aplicar e compilar no Windows

1. Feche o Minecraft e guarde uma cópia completa do mundo fora da instância. Preserve também o JAR anterior para reverter na cópia de segurança, se necessário.
2. Extraia os **três ZIPs** na mesma pasta `D:\Repository\ChromusFlora`. São ZIPs independentes que se complementam. Não crie uma subpasta por parte. Permita substituir os fontes anteriores. Eles não devem ser extraídos na pasta do mundo.
3. Depois de extrair os três arquivos, execute:

```powershell
cd D:\Repository\ChromusFlora
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\tools\verify-source.ps1
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\tools\clean-project.ps1
.\gradlew.bat build --no-daemon --warning-mode=fail
```

A limpeza preserva os caminhos protegidos e move somente os arquivos obsoletos previstos para um backup. Não é uma ferramenta para limpar mundos.

Saídas:

- `build\26.2\chromus-flora-0.1.3-26.2.jar`
- `build\26.3\chromus-flora-0.1.3-26.3.jar`

Opcional, após compilar:

```powershell
python .\tools\verify-jars.py
```

Use **somente o JAR 26.2** na instância atual 26.2. Substitua o ChromusFlora anterior, sem deixar dois JARs do mod. Mantenha Oh The Trees You'll Grow 11.0.1 nessa instância. A saída 26.3 utiliza OTTYG 12.0.0 e destina-se a uma instância 26.3 compatível; não migre seu modpack inteiro como parte deste teste.

## Teste obrigatório no mundo existente

Faça o teste em uma **cópia do mundo afetado**, com os mesmos mods. Um mundo novo sozinho não demonstra que a leitura dos dados antigos foi corrigida.

1. Abra a cópia e confira no `logs\latest.log` a mensagem:

```text
Applied OTTYG scheduled tick chunk-read repair (nested tag receiver)
```

A alternativa `OTTYG scheduled tick chunk reader already uses the nested tag; no change needed` significa que outro ajuste já havia corrigido o receptor e o plugin não o modificou novamente.

2. Visite chunks que falharam: `[18, -38]` (centro X=296, Z=-600), `[7, -39]` (X=120, Z=-616), `[-51, -20]` (X=-808, Z=-312) e `[-53, -8]` (X=-840, Z=-120). Escolha uma altura segura no criativo. Confira terreno, construções e inventários conhecidos.
3. Salve, feche o jogo completamente, reabra essa mesma cópia e retorne aos locais. Repita o ciclo mais uma vez. Verifique se não surgiram novos `Failed to load chunk`, `Chunk load failure` ou relatórios de chunks nesses testes.
4. Confira também baús já colocados e seu conteúdo. A atualização não altera seus registros.

Se aparecer `cannot safely apply the OTTYG chunk-read repair`, uma verificação identificou uma estrutura incompatível do método. Preserve o log completo; não remova a verificação nem apague os chunks para contornar o problema.

## Limites

A correção recupera a lista do local em que a dependência já a grava. Não apaga ticks, não modifica arquivos de região e não altera IDs, biomas ou estruturas. Dados realmente malformados continuam gerando erro, pois escondê-lo descartaria informações.

Ela não reconstrói conteúdo que já tenha sido perdido antes da atualização e não certifica o estado atual do seu save. A compatibilidade prática com os demais mods precisa ser confirmada pelo teste acima. Criação de mundo novo fica apenas como teste complementar.
