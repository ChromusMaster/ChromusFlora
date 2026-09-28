package dev.chromus.flora.block;

import net.minecraft.world.level.block.DoorBlock;
import net.minecraft.world.level.block.state.BlockBehaviour;
import net.minecraft.world.level.block.state.properties.BlockSetType;

public final class FloraDoor extends DoorBlock {
    public FloraDoor(BlockBehaviour.Properties properties) {
        super(BlockSetType.OAK, properties);
    }
}
