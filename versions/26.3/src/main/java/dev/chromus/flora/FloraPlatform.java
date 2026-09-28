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

import net.fabricmc.fabric.api.item.v1.BlockTransformerHelper;
import net.fabricmc.fabric.api.item.v1.DefaultItemComponentEvents;
import net.minecraft.core.component.DataComponents;
import net.minecraft.util.random.WeightedList;
import net.minecraft.world.item.component.Compostable;
import net.minecraft.world.level.levelgen.feature.Feature;
import net.minecraft.world.level.storage.loot.providers.number.ints.ContextIntProviders;

public final class FloraPlatform {
    private FloraPlatform() {}

    public static StructureTemplateManager structureTemplates(WorldGenLevel level) {
        return level.getLevel().getStructureTemplateManager();
    }

    public static void registerFeature() {
        Registry.register(BuiltInRegistries.FEATURE_TYPE, ChromusFlora.id("bounded_tree"), BoundedTreeFeature.CODEC);
    }

    public static TreeGrower grower(String id) {
        ResourceKey<Feature> key = ResourceKey.create(Registries.FEATURE, ChromusFlora.id("trees/" + id));
        return new TreeGrower(ChromusFlora.ID + ":" + id, WeightedList.of(key), WeightedList.of(), WeightedList.of(), key);
    }

    public static void compost(ItemLike item, float chance) {
        var provider = chance == 0.3F ? ContextIntProviders.COMPOSTABLE_LOW : ContextIntProviders.COMPOSTABLE_MEDIUM;
        DefaultItemComponentEvents.MODIFY.register(context -> context.modify(item.asItem(),
                builder -> builder.set(DataComponents.COMPOSTABLE, new Compostable(provider))));
    }

    public static void strip(Block block, Block stripped) {
        BlockTransformerHelper.registerStripping(block, stripped);
    }
}
