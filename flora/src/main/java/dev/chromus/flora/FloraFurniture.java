package dev.chromus.flora;

import dev.chromus.flora.block.FloraChest;
import dev.chromus.flora.block.FloraChestEntity;
import java.util.Objects;
import java.util.Set;
import java.util.stream.Collectors;
import net.minecraft.core.Registry;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.entity.BlockEntityType;
import org.jspecify.annotations.Nullable;

public final class FloraFurniture {
    private static @Nullable BlockEntityType<FloraChestEntity> chestType;

    private FloraFurniture() {}

    public static BlockEntityType<FloraChestEntity> chestType() {
        return Objects.requireNonNull(chestType, "Flora furniture is not registered");
    }

    public static void register() {
        Set<Block> chests = FloraContent.blocks().values().stream().filter(FloraChest.class::isInstance)
                .collect(Collectors.toUnmodifiableSet());
        chestType = Registry.register(BuiltInRegistries.BLOCK_ENTITY_TYPE, ChromusFlora.id("wood_chest"),
                new BlockEntityType<>(FloraChestEntity::new, chests));
    }
}
