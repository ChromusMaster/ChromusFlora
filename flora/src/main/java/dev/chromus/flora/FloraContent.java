package dev.chromus.flora;

import dev.chromus.flora.block.FloraSapling;
import dev.chromus.flora.block.FloraChest;
import dev.chromus.flora.block.FloraCraftingTable;
import dev.chromus.flora.block.FloraDoor;
import dev.chromus.flora.block.FloraTrapDoor;
import dev.chromus.flora.block.FloraStairs;
import java.util.ArrayList;
import java.util.Collections;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.function.Function;
import net.fabricmc.fabric.api.creativetab.v1.FabricCreativeModeTab;
import net.fabricmc.fabric.api.registry.FlammableBlockRegistry;
import net.minecraft.core.Registry;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.core.registries.Registries;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceKey;
import net.minecraft.world.food.FoodProperties;
import net.minecraft.world.item.BlockItem;
import net.minecraft.world.item.DoubleHighBlockItem;
import net.minecraft.world.level.block.DoorBlock;
import java.util.Objects;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.FenceBlock;
import net.minecraft.world.level.block.FenceGateBlock;
import net.minecraft.world.level.block.FlowerPotBlock;
import net.minecraft.world.level.block.RotatedPillarBlock;
import net.minecraft.world.level.block.SlabBlock;
import net.minecraft.world.level.block.TintedParticleLeavesBlock;
import net.minecraft.world.level.block.grower.TreeGrower;
import net.minecraft.world.level.block.state.BlockBehaviour;
import net.minecraft.world.level.block.state.properties.WoodType;

public final class FloraContent {
    private static final Map<String, Block> BLOCKS = new LinkedHashMap<>();
    private static final Map<String, Block> BLOCK_VIEW = Collections.unmodifiableMap(BLOCKS);
    private static final List<Item> ITEMS = new ArrayList<>();

    private FloraContent() {}

    public static Map<String, Block> blocks() {
        return BLOCK_VIEW;
    }

    public static void register() {
        for (FloraCatalog.Tree tree : FloraCatalog.get().trees()) {
            String id = tree.id();
            Block log = block(id + "_log", RotatedPillarBlock::new, Blocks.OAK_LOG, true);
            Block stripped = block("stripped_" + id + "_log", RotatedPillarBlock::new, Blocks.STRIPPED_OAK_LOG, true);
            Block wood = block(id + "_wood", RotatedPillarBlock::new, Blocks.OAK_WOOD, true);
            Block strippedWood = block("stripped_" + id + "_wood", RotatedPillarBlock::new, Blocks.STRIPPED_OAK_WOOD, true);
            block(id + "_crafting_table", FloraCraftingTable::new, Blocks.CRAFTING_TABLE, true);
            block(id + "_chest", FloraChest::new, Blocks.CHEST, true);
            block(id + "_door", FloraDoor::new, Blocks.OAK_DOOR, true);
            block(id + "_trapdoor", FloraTrapDoor::new, Blocks.OAK_TRAPDOOR, true);
            Block leaves = block(id + "_leaves", properties -> new TintedParticleLeavesBlock(0.01F, properties), Blocks.OAK_LEAVES, true);
            Block planks = block(id + "_planks", Block::new, Blocks.OAK_PLANKS, true);
            block(id + "_slab", SlabBlock::new, Blocks.OAK_SLAB, true);
            block(id + "_stairs", properties -> new FloraStairs(planks.defaultBlockState(), properties), Blocks.OAK_STAIRS, true);
            block(id + "_fence", FenceBlock::new, Blocks.OAK_FENCE, true);
            block(id + "_fence_gate", properties -> new FenceGateBlock(WoodType.OAK, properties), Blocks.OAK_FENCE_GATE, true);
            TreeGrower grower = FloraPlatform.grower(id);
            Block sapling = block(id + "_sapling", properties -> new FloraSapling(grower, properties), Blocks.OAK_SAPLING, true);
            block("potted_" + id + "_sapling", properties -> new FlowerPotBlock(sapling, properties), Blocks.POTTED_OAK_SAPLING, false);
            FloraPlatform.compost(sapling, 0.3F);
            FloraPlatform.compost(leaves, 0.3F);
            FloraPlatform.strip(log, stripped);
            FloraPlatform.strip(wood, strippedWood);
            if (!tree.dimension().equals("nether")) {
                FlammableBlockRegistry.getDefaultInstance().add(log, 5, 5);
                FlammableBlockRegistry.getDefaultInstance().add(stripped, 5, 5);
                FlammableBlockRegistry.getDefaultInstance().add(wood, 5, 5);
                FlammableBlockRegistry.getDefaultInstance().add(strippedWood, 5, 5);
                FlammableBlockRegistry.getDefaultInstance().add(leaves, 30, 60);
                for (String suffix : List.of("planks", "slab", "stairs", "fence", "fence_gate", "door", "trapdoor", "crafting_table", "chest")) {
                    FlammableBlockRegistry.getDefaultInstance().add(Objects.requireNonNull(BLOCKS.get(id + "_" + suffix)), 5, 20);
                }
            }
        }
        ITEMS.addAll(FloraBoats.register());
        ResourceKey<Item> fruitKey = ResourceKey.create(Registries.ITEM, ChromusFlora.id("grove_fruit"));
        Item fruit = Registry.register(BuiltInRegistries.ITEM, fruitKey, new Item(new Item.Properties()
                .setId(fruitKey).food(new FoodProperties.Builder().nutrition(4).saturationModifier(0.3F).build())));
        ITEMS.add(fruit);
        FloraPlatform.compost(fruit, 0.65F);
        Registry.register(BuiltInRegistries.CREATIVE_MODE_TAB, ChromusFlora.id("flora"),
                FabricCreativeModeTab.builder().title(Component.translatable("itemGroup.chromusflora"))
                        .icon(() -> new ItemStack(ITEMS.getFirst()))
                        .displayItems((parameters, output) -> ITEMS.forEach(output::accept)).build());
    }

    private static Block block(String name, Function<BlockBehaviour.Properties, Block> factory,
                               Block template, boolean withItem) {
        ResourceKey<Block> key = ResourceKey.create(Registries.BLOCK, ChromusFlora.id(name));
        Block block = Registry.register(BuiltInRegistries.BLOCK, key,
                factory.apply(BlockBehaviour.Properties.ofFullCopy(template).setId(key)));
        BLOCKS.put(name, block);
        if (withItem) {
            ResourceKey<Item> itemKey = ResourceKey.create(Registries.ITEM, ChromusFlora.id(name));
            Item.Properties properties = new Item.Properties().setId(itemKey).useBlockDescriptionPrefix();
            Item item = Registry.register(BuiltInRegistries.ITEM, itemKey,
                    block instanceof DoorBlock ? new DoubleHighBlockItem(block, properties) : new BlockItem(block, properties));
            ITEMS.add(item);
        }
        return block;
    }
}
