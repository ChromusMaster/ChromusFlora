package dev.chromus.flora;

import dev.chromus.flora.compat.JaizCompatibility;
import dev.chromus.flora.world.BoundedTreeFeature;
import net.fabricmc.api.ModInitializer;
import net.minecraft.core.Registry;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.resources.Identifier;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public final class ChromusFlora implements ModInitializer {
    public static final String ID = "chromusflora";
    public static final Logger LOGGER = LoggerFactory.getLogger(ID);

    public static Identifier id(String path) {
        return Identifier.fromNamespaceAndPath(ID, path);
    }

    @Override
    public void onInitialize() {
        FloraConfig.load();
        FloraPlatform.registerFeature();
        FloraContent.register();
        FloraFurniture.register();
        JaizCompatibility.register();
        LOGGER.info("Chromus Flora: {} biomes and {} tree families registered",
                FloraCatalog.get().biomes().size(), FloraCatalog.get().trees().size());
    }
}
