package dev.chromus.flora;

import java.util.Collections;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import net.minecraft.core.Registry;
import net.minecraft.core.dispenser.BoatDispenseItemBehavior;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.core.registries.Registries;
import net.minecraft.resources.ResourceKey;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.MobCategory;
import net.minecraft.world.entity.vehicle.boat.Boat;
import net.minecraft.world.item.BoatItem;
import net.minecraft.world.item.Item;
import net.minecraft.world.level.block.DispenserBlock;

public final class FloraBoats {
    private static final Map<String, EntityType<Boat>> TYPES = new LinkedHashMap<>();
    private static final Map<String, BoatItem> ITEMS = new LinkedHashMap<>();
    private static final Map<String, EntityType<Boat>> VIEW = Collections.unmodifiableMap(TYPES);

    private FloraBoats() {}

    public static Map<String, EntityType<Boat>> types() { return VIEW; }

    public static List<BoatItem> register() {
        for (FloraCatalog.Tree tree : FloraCatalog.get().trees()) {
            String species = tree.id();
            String name = species + "_boat";
            ResourceKey<EntityType<?>> entityKey = ResourceKey.create(Registries.ENTITY_TYPE, ChromusFlora.id(name));
            EntityType<Boat> type = Registry.register(BuiltInRegistries.ENTITY_TYPE, entityKey,
                    EntityType.Builder.<Boat>of((entityType, level) -> new Boat(entityType, level,
                            () -> Objects.requireNonNull(ITEMS.get(species), "Unregistered Flora boat item")), MobCategory.MISC)
                            .noLootTable().sized(1.375F, 0.5625F).eyeHeight(0.5625F).clientTrackingRange(10).build(entityKey));
            ResourceKey<Item> itemKey = ResourceKey.create(Registries.ITEM, ChromusFlora.id(name));
            BoatItem item = Registry.register(BuiltInRegistries.ITEM, itemKey,
                    new BoatItem(type, new Item.Properties().setId(itemKey).stacksTo(1)));
            TYPES.put(species, type);
            ITEMS.put(species, item);
            DispenserBlock.registerBehavior(item, new BoatDispenseItemBehavior(type));
        }
        return List.copyOf(ITEMS.values());
    }
}
