package dev.chromus.flora.block;

import dev.chromus.flora.FloraFurniture;
import net.minecraft.core.BlockPos;
import net.minecraft.network.chat.Component;
import net.minecraft.world.level.block.entity.ChestBlockEntity;
import net.minecraft.world.level.block.state.BlockState;

public final class FloraChestEntity extends ChestBlockEntity {
    public FloraChestEntity(BlockPos pos, BlockState state) {
        super(FloraFurniture.chestType(), pos, state);
    }

    @Override
    protected Component getDefaultName() {
        return getBlockState().getBlock().getName();
    }
}
