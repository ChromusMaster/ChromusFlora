package dev.chromus.flora.client;

import com.mojang.blaze3d.vertex.PoseStack;
import net.minecraft.client.model.Model;
import net.minecraft.client.model.object.chest.ChestModel;
import net.minecraft.client.renderer.SubmitNodeCollector;
import net.minecraft.client.renderer.blockentity.state.ChestRenderState;
import net.minecraft.client.renderer.texture.OverlayTexture;
import net.minecraft.client.resources.model.sprite.SpriteGetter;
import net.minecraft.client.resources.model.sprite.SpriteId;
import net.minecraft.resources.Identifier;
import net.minecraft.util.Unit;

public final class FloraRenderSubmission {
    private FloraRenderSubmission() {}

    public static void waterPatch(Model.Simple model, PoseStack poses, SubmitNodeCollector collector,
                                  Identifier texture, int light, int outline) {
        collector.submitModel(model, Unit.INSTANCE, poses, texture, light, OverlayTexture.NO_OVERLAY, outline, null);
    }

    public static void chestPart(ChestModel model, float opening, PoseStack poses, SubmitNodeCollector collector,
                                 ChestRenderState state, SpriteId sprite, SpriteGetter sprites) {
        collector.submitModel(model, opening, poses, state.lightCoords,
                OverlayTexture.NO_OVERLAY, -1, sprite, sprites, 0, state.breakProgress);
    }
}
