package dev.chromus.flora.compat;

import dev.chromus.flora.ChromusFlora;
import java.util.ArrayList;
import java.util.Collections;
import java.util.HashSet;
import java.util.List;
import java.util.Optional;
import net.fabricmc.fabric.api.biome.v1.BiomeModificationContext;
import net.fabricmc.fabric.api.biome.v1.BiomeModifications;
import net.fabricmc.fabric.api.biome.v1.BiomeSelectionContext;
import net.fabricmc.fabric.api.biome.v1.ModificationPhase;
import net.fabricmc.loader.api.FabricLoader;
import net.minecraft.core.Holder;
import net.minecraft.core.HolderSet;
import net.minecraft.core.registries.Registries;
import net.minecraft.resources.Identifier;
import net.minecraft.resources.ResourceKey;
import net.minecraft.world.level.levelgen.GenerationStep;
import net.minecraft.world.level.levelgen.placement.PlacedFeature;

/** Compatibility for the inspected 26.2 vegetation ordering, applied only at biome load. */
public final class VegetationOrderCompatibility {
    private static final Identifier BIOME = Identifier.parse("terrestria:rainbow_rainforest");
    private static final GenerationStep.Decoration STEP = GenerationStep.Decoration.VEGETAL_DECORATION;
    private static final ResourceKey<PlacedFeature> FLOWERS = feature("minecraft:flower_default");
    private static final ResourceKey<PlacedFeature> GRASS = feature("minecraft:patch_grass_jungle");

    private VegetationOrderCompatibility() {}

    private static ResourceKey<PlacedFeature> feature(String id) {
        return ResourceKey.create(Registries.PLACED_FEATURE, Identifier.parse(id));
    }

    private static boolean versionIs(String id, String version) {
        return FabricLoader.getInstance().getModContainer(id)
                .map(mod -> mod.getMetadata().getVersion().getFriendlyString().equals(version)).orElse(false);
    }

    public static void register() {
        if (!FabricLoader.getInstance().isModLoaded("terralith")
                || !FabricLoader.getInstance().isModLoaded("terrestria")) {
            return;
        }
        if (!versionIs("minecraft", "26.2") || !versionIs("terralith", "2.6.4")
                || !versionIs("terrestria", "8.1.0-beta.2")) {
            ChromusFlora.LOGGER.warn("Vegetation order compatibility not enabled: unreviewed Minecraft/Terralith/Terrestria versions");
            return;
        }
        BiomeModifications.create(ChromusFlora.id("terralith_terrestria_vegetation_order"))
                .add(ModificationPhase.POST_PROCESSING,
                        selection -> selection.getBiomeKey().identifier().equals(BIOME),
                        VegetationOrderCompatibility::repair);
    }

    private static void repair(BiomeSelectionContext selection, BiomeModificationContext context) {
        List<HolderSet<PlacedFeature>> stages = selection.getBiome().getGenerationSettings().features();
        if (stages.size() <= STEP.ordinal()) {
            return;
        }
        List<ResourceKey<PlacedFeature>> ordered = new ArrayList<>();
        for (Holder<PlacedFeature> holder : stages.get(STEP.ordinal())) {
            Optional<ResourceKey<PlacedFeature>> key = selection.getPlacedFeatureKey(holder.value());
            if (key.isEmpty()) {
                ChromusFlora.LOGGER.warn("Vegetation order compatibility skipped for {}: inline feature; preserving biome", BIOME);
                return;
            }
            ordered.add(key.orElseThrow());
        }
        int flowers = ordered.indexOf(FLOWERS);
        int grass = ordered.indexOf(GRASS);
        if (flowers < 0 || grass < 0 || grass < flowers) {
            return;
        }
        // Do not rearrange unknown datapack ordering or collapse duplicate entries.
        if (grass != flowers + 1 || new HashSet<>(ordered).size() != ordered.size()) {
            ChromusFlora.LOGGER.warn("Vegetation order compatibility skipped for {}: unexpected ordering or duplicates", BIOME);
            return;
        }
        Collections.swap(ordered, flowers, grass);
        BiomeModificationContext.GenerationSettingsContext generation = context.getGenerationSettings();
        // Fabric appends in call order and rebuilds its cached feature sets when it freezes the biome.
        // Snapshotting above preserves every registered addition made by other mods.
        for (ResourceKey<PlacedFeature> key : ordered) {
            generation.removeFeature(STEP, key);
        }
        for (ResourceKey<PlacedFeature> key : ordered) {
            generation.addFeature(STEP, key);
        }
        ChromusFlora.LOGGER.info("Applied vegetation order compatibility (Chromus Flora hotfix 4): {} grass before flowers; {} features preserved", BIOME, ordered.size());
    }
}
