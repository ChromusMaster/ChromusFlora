# Chromus Flora 0.1.1

Source revision: build fix 1. See `APLICAR_0.1.1_FIX1.md` for the corrected 26.3 template-manager accessor.

## English

Source-only Fabric mod for Minecraft 26.2 and 26.3. JDK 25, Gradle 9.5.1, Loom 1.17.21. Shared content and separate game API adapters live in `flora/` and `versions/`.

Build both targets from the repository root:

```powershell
.\gradlew.bat build --no-daemon --warning-mode=fail
```

Expected runtime artifacts:

- `build/26.2/chromus-flora-0.1.1-26.2.jar`
- `build/26.3/chromus-flora-0.1.1-26.3.jar`

Linux/macOS: install the pinned Gradle and JDK, then run `sh ./gradlew build --no-daemon --warning-mode=fail`. This source-only distribution intentionally contains no Gradle wrapper JAR. Windows bootstrap downloads and verifies Gradle; Linux CI installs it through setup-gradle.

Independent builds: `:mc26_2:build` or `:mc26_3:build`. Development clients: `:mc26_2:runClient` or `:mc26_3:runClient`. Optional Jade/Mod Menu runtime: `-PwithOptionalMods=true`. Runtime dependencies must match the game version; consult each `versions/<game>/build.gradle`.

83 wood families now have recipe unlocks, bark-sided wood, stripped wood, doors and trapdoors. Existing plank, slab, stair, fence and fence-gate recipes remain. Mod planks also craft vanilla oak boats, chests and crafting tables. There are no custom boat entities or chest/crafting-table block entities in this release.

Old block IDs, blockstate definitions, textures, tree NBT and 26.2 worldgen JSON are preserved against the delivered Fix10. No retrogen or save migration is included. This does not certify compatibility with every mod or permit moving a complete 26.2 modpack to 26.3.

Validation performed for this delivery is **static only**. Gradle, Java compilation, JDT, Minecraft and the 277-mod instance were not executed. The provided CI template builds and validates both artifacts when installed in the repository. The observed Terralith/Terrestria feature cycle also reproduces without Flora; this package does not silently alter those mods.

Offline checks require Python 3.12+ and `python -m pip install -r tools/requirements.txt`, followed by `python tools/scan.py` and `python tools/check-release.py`. After building, `python tools/verify-jars.py` checks both runtime artifacts. Regenerating assets is optional and requires the same Python dependency; normal Gradle builds use checked-in resources.

## Português

Veja `APLICAR_0.1.1.md` para atualizar por cima da pasta atual e `docs/REVISAO_0.1.1.md` para alterações, evidências e limitações.

A entrega contém somente fontes e recursos. Os dois JARs são gerados na sua máquina ou pelo GitHub Actions. Os avisos do editor receberam contratos JSpecify explícitos; a ausência de novos avisos ainda precisa ser confirmada pelo JDT e pelo build.

O mundo atual deve continuar na versão **26.2**, com o JAR correspondente. Preserve uma cópia desse mundo para validar a atualização. O alvo 26.3 é um port separado; a atualização do mod não migra automaticamente os outros 277 mods.

As receitas do livro são desbloqueadas ao adquirir/movimentar o material no inventário. Em saves existentes, mova um tronco e uma pilha de tábuas para disparar a verificação. Primeiro transforme troncos em tábuas; portas, cercas, portões, alçapões e barcos usam tábuas.

Os documentos e fixtures em `verification/fix8`, `verification/fix10` e arquivos anteriores são evidências históricas. Os resultados atuais estão em `verification/release-0.1.1/` e `verification/global-scan.json`.
