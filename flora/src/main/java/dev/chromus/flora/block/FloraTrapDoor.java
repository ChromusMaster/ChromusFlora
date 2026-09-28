package dev.chromus.flora.block;

import net.minecraft.world.level.block.TrapDoorBlock;
import net.minecraft.world.level.block.state.BlockBehaviour;
import net.minecraft.world.level.block.state.properties.BlockSetType;

public final class FloraTrapDoor extends TrapDoorBlock {
    public FloraTrapDoor(BlockBehaviour.Properties properties) {
        super(BlockSetType.OAK, properties);
    }
}
