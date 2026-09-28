package dev.chromus.flora.world;

import com.mojang.serialization.MapCodec;
import dev.corgitaco.ohthetreesyoullgrow.world.level.levelgen.feature.configurations.TreeFromStructureNBTConfigV2;
import net.minecraft.core.BlockPos;
import net.minecraft.util.RandomSource;
import net.minecraft.world.level.WorldGenLevel;
import net.minecraft.world.level.chunk.ChunkGenerator;
import net.minecraft.world.level.levelgen.feature.Feature;

public record BoundedTreeFeature(TreeFromStructureNBTConfigV2 config) implements Feature {
    public static final MapCodec<BoundedTreeFeature> CODEC = TreeFromStructureNBTConfigV2.CODEC
            .xmap(BoundedTreeFeature::new, BoundedTreeFeature::config);

    @Override
    public MapCodec<BoundedTreeFeature> codec() {
        return CODEC;
    }

    @Override
    public boolean place(WorldGenLevel level, ChunkGenerator generator, RandomSource random, BlockPos origin) {
        return TreeFootprint.allows(level, origin, config) && config.place(level, generator, random, origin);
    }
}
