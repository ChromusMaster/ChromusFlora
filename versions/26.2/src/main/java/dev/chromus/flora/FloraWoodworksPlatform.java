package dev.chromus.flora;

import net.minecraft.world.item.Item;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.item.SignItem;
import java.util.LinkedHashMap;
import java.util.Map;
import net.fabricmc.fabric.api.registry.FuelValueEvents;

public final class FloraWoodworksPlatform {
    private static final Map<Item, Integer> FUELS = new LinkedHashMap<>();

    private FloraWoodworksPlatform() {}

    public static void fuel(Item item, String kind) {
        FUELS.put(item, kind.equals("button") ? 100 : kind.equals("pressure_plate") ? 300 : 200);
    }

    public static void finish() {
        FuelValueEvents.BUILD.register((builder, context) -> FUELS.forEach((item, ticks) -> builder.add(item, context.baseSmeltTime() * ticks / 200)));
    }

    public static Item sign(Block sign, Block wall, Item.Properties properties) {
        return new SignItem(sign, wall, properties);
    }

    public static Item.Properties properties(Item.Properties properties, String kind) {
        return properties;
    }
}
