package dev.chromus.flora.block;

import net.minecraft.world.level.block.ButtonBlock;
import net.minecraft.world.level.block.state.BlockBehaviour;
import net.minecraft.world.level.block.state.properties.BlockSetType;

public final class FloraButton extends ButtonBlock {
    public FloraButton(BlockBehaviour.Properties properties) {
        super(BlockSetType.OAK, 30, properties);
    }
}
