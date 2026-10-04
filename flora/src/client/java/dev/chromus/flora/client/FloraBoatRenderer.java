package dev.chromus.flora.client;

import com.mojang.blaze3d.vertex.PoseStack;
import dev.chromus.flora.ChromusFlora;
import net.minecraft.client.model.EntityModel;
import net.minecraft.client.model.Model;
import net.minecraft.client.model.geom.ModelLayers;
import net.minecraft.client.model.object.boat.BoatModel;
import net.minecraft.client.renderer.SubmitNodeCollector;
import net.minecraft.client.renderer.entity.AbstractBoatRenderer;
import net.minecraft.client.renderer.entity.EntityRendererProvider;
import net.minecraft.client.renderer.entity.state.BoatRenderState;
import net.minecraft.client.renderer.rendertype.RenderTypes;
import net.minecraft.client.renderer.texture.OverlayTexture;
import net.minecraft.util.Unit;

public final class FloraBoatRenderer extends AbstractBoatRenderer {
    private final BoatModel boat;
    private final Model.Simple waterPatch;

    public FloraBoatRenderer(EntityRendererProvider.Context context, String species) {
        super(context, ChromusFlora.id("textures/block/wood/" + species + "/planks.png"));
        boat = new BoatModel(context.bakeLayer(ModelLayers.OAK_BOAT));
        waterPatch = new Model.Simple(context.bakeLayer(ModelLayers.BOAT_WATER_PATCH), ignored -> RenderTypes.waterMask());
    }

    @Override
    protected EntityModel<BoatRenderState> model() { return boat; }

    @Override
    protected void submitTypeAdditions(BoatRenderState state, PoseStack poses, SubmitNodeCollector collector, int light) {
        if (!state.isUnderWater) {
            collector.submitModel(waterPatch, Unit.INSTANCE, poses, texture,
                    light, OverlayTexture.NO_OVERLAY, state.outlineColor, null);
        }
    }
}
