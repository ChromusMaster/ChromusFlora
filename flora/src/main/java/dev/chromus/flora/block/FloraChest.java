package dev.chromus.flora.block;

import dev.chromus.flora.FloraFurniture;
import net.minecraft.core.BlockPos;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.world.level.block.ChestBlock;
import net.minecraft.world.level.block.entity.BlockEntity;
import net.minecraft.world.level.block.state.BlockBehaviour;
import net.minecraft.world.level.block.state.BlockState;

public final class FloraChest extends ChestBlock {
    public FloraChest(BlockBehaviour.Properties properties) {
        super(FloraFurniture::chestType, SoundEvents.CHEST_OPEN, SoundEvents.CHEST_CLOSE, properties);
    }

    @Override
    public BlockEntity newBlockEntity(BlockPos pos, BlockState state) {
        return new FloraChestEntity(pos, state);
    }
}
