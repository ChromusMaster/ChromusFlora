package dev.chromus.flora;

import net.minecraft.world.item.Item;
import net.minecraft.world.level.block.Block;
import net.minecraft.core.Direction;
import net.minecraft.world.item.StandingAndWallBlockItem;
import net.minecraft.world.level.storage.loot.providers.number.ints.ContextIntProviders;

public final class FloraWoodworksPlatform {
    private FloraWoodworksPlatform() {}

    public static void fuel(Item item, String kind) {}

    public static void finish() {}

    public static Item sign(Block sign, Block wall, Item.Properties properties) {
        return new StandingAndWallBlockItem(sign, wall, Direction.DOWN, properties.signText());
    }

    public static Item.Properties properties(Item.Properties properties, String kind) {
        return properties.cookingFuel(switch (kind) {
            case "button" -> ContextIntProviders.COOKING_TIME_WOOD_ITEMS_SMALL;
            case "pressure_plate" -> ContextIntProviders.COOKING_TIME_WOOD_BLOCKS;
            default -> ContextIntProviders.COOKING_TIME_WOOD_ITEMS_LARGE;
        });
    }
}
