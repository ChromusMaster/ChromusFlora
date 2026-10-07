package dev.chromus.flora;

import dev.chromus.flora.block.FloraButton;
import dev.chromus.flora.block.FloraPressurePlate;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.function.Function;
import net.minecraft.core.Registry;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.core.registries.Registries;
import net.minecraft.resources.ResourceKey;
import net.minecraft.world.item.BlockItem;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ToolMaterial;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.StandingSignBlock;
import net.minecraft.world.level.block.WallSignBlock;
import net.minecraft.world.level.block.entity.BlockEntityTypes;
import net.minecraft.world.level.block.state.BlockBehaviour;
import net.minecraft.world.level.block.state.properties.WoodType;

public final class FloraWoodworks {
    private FloraWoodworks() {}

    public static void register(Map<String, Block> blocks, List<Item> items) {
        for (FloraCatalog.Tree tree : FloraCatalog.get().trees()) {
            String id = tree.id();
            Block sign = block(blocks, id + "_sign", p -> new StandingSignBlock(WoodType.OAK, p), Blocks.OAK_SIGN);
            Block wall = block(blocks, id + "_wall_sign", p -> new WallSignBlock(WoodType.OAK, p), Blocks.OAK_WALL_SIGN);
            BlockEntityTypes.SIGN.addValidBlock(sign);
            BlockEntityTypes.SIGN.addValidBlock(wall);
            item(items, id + "_sign", p -> FloraWoodworksPlatform.sign(sign, wall, p),
                    new Item.Properties().stacksTo(16).useBlockDescriptionPrefix(), "sign");
            Block button = block(blocks, id + "_button", FloraButton::new, Blocks.OAK_BUTTON);
            item(items, id + "_button", p -> new BlockItem(button, p),
                    new Item.Properties().useBlockDescriptionPrefix(), "button");
            Block plate = block(blocks, id + "_pressure_plate", FloraPressurePlate::new, Blocks.OAK_PRESSURE_PLATE);
            item(items, id + "_pressure_plate", p -> new BlockItem(plate, p),
                    new Item.Properties().useBlockDescriptionPrefix(), "pressure_plate");
            item(items, id + "_sword", Item::new,
                    new Item.Properties().sword(ToolMaterial.WOOD, 3.0F, -2.4F), "sword");
            item(items, id + "_spear", Item::new,
                    new Item.Properties().spear(ToolMaterial.WOOD, 0.65F, 0.7F, 0.75F,
                            5.0F, 14.0F, 10.0F, 5.1F, 15.0F, 4.6F), "spear");
        }
        FloraWoodworksPlatform.finish();
    }

    private static Block block(Map<String, Block> blocks, String name,
                               Function<BlockBehaviour.Properties, Block> factory, Block template) {
        ResourceKey<Block> key = ResourceKey.create(Registries.BLOCK, ChromusFlora.id(name));
        BlockBehaviour.Properties properties = BlockBehaviour.Properties.ofFullCopy(template).setId(key)
                .overrideLootTable(Optional.of(ResourceKey.create(Registries.LOOT_TABLE, ChromusFlora.id("blocks/" + name))))
                .overrideDescription("block.chromusflora." + name);
        Block block = Registry.register(BuiltInRegistries.BLOCK, key, factory.apply(properties));
        blocks.put(name, block);
        return block;
    }

    private static void item(List<Item> items, String name, Function<Item.Properties, Item> factory,
                             Item.Properties properties, String kind) {
        ResourceKey<Item> key = ResourceKey.create(Registries.ITEM, ChromusFlora.id(name));
        Item item = Registry.register(BuiltInRegistries.ITEM, key,
                factory.apply(FloraWoodworksPlatform.properties(properties.setId(key), kind)));
        if (item instanceof BlockItem blockItem) {
            blockItem.registerBlocks(Item.BY_BLOCK, item);
        }
        items.add(item);
        FloraWoodworksPlatform.fuel(item, kind);
    }
}
