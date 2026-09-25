package dev.chromus.flora.compat;

import dev.chromus.flora.ChromusFlora;
import dev.chromus.flora.FloraCatalog;
import dev.chromus.flora.FloraConfig;
import java.util.List;
import net.fabricmc.fabric.api.biome.v1.BiomeModifications;
import net.fabricmc.fabric.api.biome.v1.ModificationPhase;
import net.fabricmc.loader.api.FabricLoader;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.core.registries.Registries;
import net.minecraft.resources.Identifier;
import net.minecraft.resources.ResourceKey;
import net.minecraft.world.entity.MobCategory;
import net.minecraft.world.level.biome.MobSpawnSettings;
import net.minecraft.world.level.levelgen.GenerationStep;

public final class JaizCompatibility {
    public record Spawn(String biome, String entity, String category, int weight, int min, int max) {}
    public record Feature(String biome, String feature, String step) {}
    public record Rules(List<Spawn> spawns, List<Feature> features) {}

    private JaizCompatibility() {}

    public static void register() {
        if (!FabricLoader.getInstance().isModLoaded("jaizmod")) {
            return;
        }
        Rules rules = FloraCatalog.read("/chromusflora/jaiz-compatibility.json", Rules.class);
        FloraConfig.Settings settings = FloraConfig.get();
        BiomeModifications.create(ChromusFlora.id("jaiz_compatibility")).add(ModificationPhase.ADDITIONS,
                selection -> selection.getBiomeKey().identifier().getNamespace().equals(ChromusFlora.ID),
                (selection, context) -> {
                    FloraCatalog.Biome biome = FloraCatalog.biome(selection.getBiomeKey().identifier().getPath());
                    if (biome == null) {
                        return;
                    }
                    if (settings.jaizSpawns()) {
                        for (Spawn spawn : rules.spawns()) {
                            if (spawn.biome().equals(biome.vanilla())) {
                                BuiltInRegistries.ENTITY_TYPE.getOptional(Identifier.parse(spawn.entity())).ifPresent(entity ->
                                        context.getMobSpawnSettings().addSpawn(MobCategory.valueOf(spawn.category()),
                                                new MobSpawnSettings.SpawnerData(entity, spawn.min(), spawn.max()), spawn.weight()));
                            }
                        }
                    }
                    if (settings.jaizFeatures()) {
                        for (Feature feature : rules.features()) {
                            if (feature.biome().equals(biome.vanilla())) {
                                context.getGenerationSettings().addFeature(GenerationStep.Decoration.valueOf(feature.step()),
                                        ResourceKey.create(Registries.PLACED_FEATURE, Identifier.parse(feature.feature())));
                            }
                        }
                    }
                });
    }
}
