package dev.chromus.flora.block;

import net.minecraft.core.BlockPos;
import net.minecraft.world.MenuProvider;
import net.minecraft.world.SimpleMenuProvider;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.inventory.ContainerLevelAccess;
import net.minecraft.world.inventory.CraftingMenu;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.phys.BlockHitResult;
import net.minecraft.stats.Stats;
import net.minecraft.world.level.block.state.BlockBehaviour;
import net.minecraft.world.level.block.state.BlockState;

public final class FloraCraftingTable extends Block {
    public FloraCraftingTable(BlockBehaviour.Properties properties) {
        // The inset cabinet leaves visible gaps between its corner posts.
        // A full-cube occluder would hide the ground and adjacent block faces.
        // Keep the existing collision shape and menu behaviour.
        super(properties.noOcclusion());
    }

    @Override
    protected InteractionResult useWithoutItem(BlockState state, Level level, BlockPos pos,
                                               Player player, BlockHitResult hit) {
        if (!level.isClientSide()) {
            player.openMenu(getMenuProvider(state, level, pos));
            player.awardStat(Stats.INTERACT_WITH_CRAFTING_TABLE);
        }
        return InteractionResult.SUCCESS;
    }

    @Override
    protected MenuProvider getMenuProvider(BlockState state, Level level, BlockPos pos) {
        ContainerLevelAccess access = ContainerLevelAccess.create(level, pos);
        return new SimpleMenuProvider((id, inventory, player) -> new CraftingMenu(id, inventory, access) {
            @Override
            public boolean stillValid(Player viewer) {
                return stillValid(access, viewer, FloraCraftingTable.this);
            }
        }, getName());
    }
}
