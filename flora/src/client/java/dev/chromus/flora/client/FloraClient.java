package dev.chromus.flora.client;

import dev.chromus.flora.FloraBoats;
import dev.chromus.flora.FloraFurniture;
import net.fabricmc.api.ClientModInitializer;
import net.minecraft.client.renderer.blockentity.BlockEntityRenderers;
import net.minecraft.client.renderer.entity.EntityRenderers;

public final class FloraClient implements ClientModInitializer {
    @Override
    public void onInitializeClient() {
        BlockEntityRenderers.register(FloraFurniture.chestType(), FloraChestRenderer::new);
        FloraBoats.types().forEach((species, type) -> EntityRenderers.register(type,
                context -> new FloraBoatRenderer(context, species)));
    }
}
