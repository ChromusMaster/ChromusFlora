package dev.chromus.flora.block;

import net.minecraft.world.level.block.PressurePlateBlock;
import net.minecraft.world.level.block.state.BlockBehaviour;
import net.minecraft.world.level.block.state.properties.BlockSetType;

public final class FloraPressurePlate extends PressurePlateBlock {
    public FloraPressurePlate(BlockBehaviour.Properties properties) {
        super(BlockSetType.OAK, properties);
    }
}
