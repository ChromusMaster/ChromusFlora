package dev.chromus.flora.client;

import dev.chromus.flora.FloraBoats;
import dev.chromus.flora.FloraFurniture;
import net.fabricmc.api.ClientModInitializer;
import net.fabricmc.fabric.api.client.rendering.v1.BlockEntityRendererRegistry;
import net.fabricmc.fabric.api.client.rendering.v1.EntityRendererRegistry;

public final class FloraClient implements ClientModInitializer {
    @Override
    public void onInitializeClient() {
        BlockEntityRendererRegistry.register(FloraFurniture.chestType(), FloraChestRenderer::new);
        FloraBoats.types().forEach((species, type) -> EntityRendererRegistry.register(type,
                context -> new FloraBoatRenderer(context, species)));
    }
}
