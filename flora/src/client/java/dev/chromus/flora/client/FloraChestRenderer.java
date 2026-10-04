package dev.chromus.flora.client;

import com.mojang.blaze3d.vertex.PoseStack;
import dev.chromus.flora.ChromusFlora;
import dev.chromus.flora.FloraCatalog;
import dev.chromus.flora.FloraContent;
import dev.chromus.flora.block.FloraChestEntity;
import java.util.IdentityHashMap;
import java.util.Map;
import java.util.Objects;
import net.minecraft.client.model.geom.ModelLayerLocation;
import net.minecraft.client.model.geom.ModelPart;
import net.minecraft.client.model.object.chest.ChestModel;
import net.minecraft.client.renderer.MultiblockChestResources;
import net.minecraft.client.renderer.Sheets;
import net.minecraft.client.renderer.SubmitNodeCollector;
import net.minecraft.client.renderer.blockentity.BlockEntityRendererProvider;
import net.minecraft.client.renderer.blockentity.ChestRenderer;
import net.minecraft.client.renderer.blockentity.state.ChestRenderState;
import net.minecraft.client.renderer.feature.ModelFeatureRenderer;
import net.minecraft.client.renderer.state.level.CameraRenderState;
import net.minecraft.client.resources.model.sprite.SpriteGetter;
import net.minecraft.client.resources.model.sprite.SpriteId;
import net.minecraft.resources.Identifier;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.phys.Vec3;
import org.jspecify.annotations.Nullable;

public final class FloraChestRenderer extends ChestRenderer<FloraChestEntity> {
    private static final SpriteId HARDWARE = Sheets.BLOCKS_MAPPER.apply(Identifier.withDefaultNamespace("iron_block"));
    private final SpriteGetter sprites;
    private final MultiblockChestResources<ChestModel> bodies;
    private final MultiblockChestResources<ChestModel> lids;
    private final MultiblockChestResources<ChestModel> locks;
    private final Map<Block, Materials> materials = new IdentityHashMap<>();

    private record Materials(SpriteId wood, SpriteId lid) {}

    public static final class State extends ChestRenderState {
        private @Nullable Materials materials;
    }

    public FloraChestRenderer(BlockEntityRendererProvider.Context context) {
        super(context);
        sprites = context.sprites();
        bodies = LAYERS.map(layer -> part(context, layer, "bottom"));
        lids = LAYERS.map(layer -> part(context, layer, "lid"));
        locks = LAYERS.map(layer -> part(context, layer, "lock"));
        for (FloraCatalog.Tree tree : FloraCatalog.get().trees()) {
            Block block = Objects.requireNonNull(FloraContent.blocks().get(tree.id() + "_chest"));
            String path = "wood/" + tree.id() + "/";
            materials.put(block, new Materials(Sheets.BLOCKS_MAPPER.apply(ChromusFlora.id(path + "planks")),
                    Sheets.BLOCKS_MAPPER.apply(ChromusFlora.id(path + "stripped"))));
        }
    }

    private static ChestModel part(BlockEntityRendererProvider.Context context, ModelLayerLocation layer, String visible) {
        ModelPart root = context.bakeLayer(layer);
        root.getChild("bottom").visible = "bottom".equals(visible);
        root.getChild("lid").visible = "lid".equals(visible);
        root.getChild("lock").visible = "lock".equals(visible);
        return new ChestModel(root);
    }

    @Override
    public State createRenderState() { return new State(); }

    @Override
    public void extractRenderState(FloraChestEntity entity, ChestRenderState state, float partialTick,
                                   Vec3 camera, ModelFeatureRenderer.@Nullable CrumblingOverlay overlay) {
        super.extractRenderState(entity, state, partialTick, camera, overlay);
        ((State) state).materials = Objects.requireNonNull(materials.get(entity.getBlockState().getBlock()));
    }

    @Override
    public void submit(ChestRenderState state, PoseStack poses, SubmitNodeCollector collector, CameraRenderState camera) {
        Materials selected = Objects.requireNonNull(((State) state).materials);
        float closed = 1.0F - state.open;
        float opening = 1.0F - closed * closed * closed;
        poses.pushPose();
        poses.mulPose(modelTransformation(state.facing));
        FloraRenderSubmission.chestPart(bodies.select(state.type), opening, poses, collector, state, selected.wood(), sprites);
        FloraRenderSubmission.chestPart(lids.select(state.type), opening, poses, collector, state, selected.lid(), sprites);
        FloraRenderSubmission.chestPart(locks.select(state.type), opening, poses, collector, state, HARDWARE, sprites);
        poses.popPose();
    }
}
