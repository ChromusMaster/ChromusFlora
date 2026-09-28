package dev.chromus.flora.block;

import dev.chromus.flora.ChromusFlora;
import net.minecraft.core.BlockPos;
import net.minecraft.core.registries.Registries;
import net.minecraft.tags.TagKey;
import net.minecraft.world.level.BlockGetter;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.SaplingBlock;
import net.minecraft.world.level.block.grower.TreeGrower;
import net.minecraft.world.level.block.state.BlockBehaviour;
import net.minecraft.world.level.block.state.BlockState;

public final class FloraSapling extends SaplingBlock {
    public static final TagKey<Block> SOILS = TagKey.create(Registries.BLOCK, ChromusFlora.id("tree_soils"));
    public FloraSapling(TreeGrower grower, BlockBehaviour.Properties properties) {
        super(grower, properties);
    }

    @Override
    protected boolean mayPlaceOn(BlockState state, BlockGetter level, BlockPos pos) {
        return state.is(SOILS);
    }
}
