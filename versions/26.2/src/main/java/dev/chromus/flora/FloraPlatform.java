package dev.chromus.flora;

import dev.chromus.flora.world.BoundedTreeFeature;
import net.minecraft.core.Registry;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.core.registries.Registries;
import net.minecraft.resources.ResourceKey;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.grower.TreeGrower;
import net.minecraft.world.level.ItemLike;
import net.minecraft.world.level.WorldGenLevel;
import net.minecraft.world.level.levelgen.structure.templatesystem.StructureTemplateManager;

import java.util.Optional;
import net.fabricmc.fabric.api.registry.CompostableRegistry;
import net.fabricmc.fabric.api.registry.StrippableBlockRegistry;
import net.minecraft.world.level.levelgen.feature.ConfiguredFeature;

public final class FloraPlatform {
    private FloraPlatform() {}

    public static StructureTemplateManager structureTemplates(WorldGenLevel level) {
        return level.getLevel().getStructureManager();
    }

    public static void registerFeature() {
        Registry.register(BuiltInRegistries.FEATURE, ChromusFlora.id("bounded_tree"), new BoundedTreeFeature());
    }

    public static TreeGrower grower(String id) {
        ResourceKey<ConfiguredFeature<?, ?>> key = ResourceKey.create(Registries.CONFIGURED_FEATURE, ChromusFlora.id("trees/" + id));
        return new TreeGrower(ChromusFlora.ID + ":" + id, Optional.empty(), Optional.of(key), Optional.empty());
    }

    public static void compost(ItemLike item, float chance) {
        CompostableRegistry.INSTANCE.add(item, chance);
    }

    public static void strip(Block block, Block stripped) {
        StrippableBlockRegistry.register(block, stripped);
    }
}
