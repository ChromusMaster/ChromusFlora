# Chromus Flora 0.1.3

## English

Source-only Fabric mod for Minecraft **26.2 and 26.3**. JDK 25, Gradle 9.5.1 and Loom 1.17.21 remain pinned. Shared content is in `flora/`; game API adapters are in `versions/`.

This patch corrects the nested scheduled-tick NBT reader in OTTYG 11.0.1 (26.2) and 12.0.0 (26.3), in memory at class transformation time. It preserves the save schema and existing content.

The previous update combines the previous Fix3.2 corrections with 83 reference-based doors and matching trapdoors, 83 crafting tables and 83 chests. Door inventory icons remain front-facing 2D sprites. Tree structures, old registry names, existing wood textures and biome definitions are preserved. No retrogen or automatic save migration is introduced.

Build both targets from the repository root:

```powershell
.\gradlew.bat build --no-daemon --warning-mode=fail
```

Runtime artifacts:

- `build/26.2/chromus-flora-0.1.3-26.2.jar`
- `build/26.3/chromus-flora-0.1.3-26.3.jar`

Independent builds: `:mc26_2:build` and `:mc26_3:build`. Development clients: `:mc26_2:runClient` and `:mc26_3:runClient`. Optional Jade/Mod Menu runtime: `-PwithOptionalMods=true`. Consult each target's `build.gradle` for matching runtime dependencies.

Windows bootstrap downloads and checks the Gradle distribution. This source-only package intentionally has no wrapper JAR. Linux/macOS: install the pinned JDK and Gradle, then run `sh ./gradlew build --no-daemon --warning-mode=fail`. The CI template `tools/ci/gradle.yml` installs these tools and builds both targets once.

Install the static-check dependency with `python -m pip install -r tools/requirements.txt`, then run `python tools/scan.py`, `python tools/check-release.py`, `python tools/check-joinery.py` and `python tools/check-door-gallery.py`. After building, run `python tools/verify-jars.py`.

Checked-in resources are complete; Python and artwork regeneration are unnecessary for a normal Gradle build. `python tools/generate.py` regenerates content from the supplied atelier sources, including final door artwork. `python tools/preview-joinery.py` refreshes the self-contained visual catalog.

Validation supplied here is **static only**: no Java compiler, Gradle, JDT, Minecraft or 277-mod runtime was executed. Current reports are in `verification/release-0.1.3/`, `verification/global-scan.json` and `verification/visual-resources.json`. Earlier fixtures remain as preservation baselines.

## Português

Comece por **`APLICAR_0.1.3.md`**. Alterações e limitações estão em `docs/REVISAO_0.1.3.md`; o catálogo visual pesquisável está em `docs/Marcenaria_0.1.2.html`.

Extraia este ZIP sobre a pasta do projeto, confirme a integridade e execute a limpeza com backup antes de compilar. Não copie o conteúdo sobre a pasta do mundo. O mundo atual permanece no Minecraft **26.2**, com o JAR 26.2 e as dependências correspondentes.

As bancadas e os baús usam receitas por espécie, reunidas nos grupos nativos `crafting_table` e `chest`. Ative **somente fabricáveis** no livro para filtrar pelas tábuas disponíveis. Com várias espécies fabricáveis, o grupo alterna as opções. Use tábuas de uma mesma espécie em cada receita. Um baú ou bancada Flora também pode ser convertido no item vanilla colocando-o sozinho na grade.

Os baús novos usam inventário nativo, mas têm tampa visual estática. As bancadas novas abrem a grade 3×3 nativa, sem guardar ingredientes depois de fechar. Não implementam automaticamente os recursos de Visual Workbench. Os itens vanilla existentes continuam vanilla. Barcos continuam usando o fallback de barco de carvalho.

A revisão preserva as definições existentes; não certifica compatibilidade com todos os mods nem transforma um modpack 26.2 em 26.3. A validação em cópia do mundo e o perfil de desempenho ainda precisam ser feitos no seu ambiente.
