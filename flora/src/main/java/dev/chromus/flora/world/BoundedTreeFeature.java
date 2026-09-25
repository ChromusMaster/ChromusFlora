package dev.chromus.flora.world;

import dev.corgitaco.ohthetreesyoullgrow.world.level.levelgen.feature.TYGFeatures;
import dev.corgitaco.ohthetreesyoullgrow.world.level.levelgen.feature.configurations.TreeFromStructureNBTConfigV2;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Vec3i;
import net.minecraft.world.level.WorldGenLevel;
import net.minecraft.world.level.levelgen.feature.Feature;
import net.minecraft.world.level.levelgen.feature.FeaturePlaceContext;
import net.minecraft.world.level.levelgen.structure.templatesystem.StructureTemplate;

public final class BoundedTreeFeature extends Feature<TreeFromStructureNBTConfigV2> {
    public BoundedTreeFeature() {
        super(TreeFromStructureNBTConfigV2.CODEC);
    }

    @Override
    public boolean place(FeaturePlaceContext<TreeFromStructureNBTConfigV2> context) {
        WorldGenLevel level = context.level();
        BlockPos origin = context.origin();
        TreeFromStructureNBTConfigV2 config = context.config();
        StructureTemplate canopy = level.getLevel().getStructureManager().get(config.canopyLocation())
                .orElseThrow(() -> new IllegalStateException("Missing tree canopy " + config.canopyLocation()));
        Vec3i size = canopy.getSize();
        if (origin.getY() <= level.getMinY()
                || origin.getY() + config.height().maxInclusive() + size.getY() >= level.getMaxY()) {
            return false;
        }
        int radius = Math.max(size.getX(), size.getZ());
        for (int x = (origin.getX() - radius) >> 4; x <= (origin.getX() + radius) >> 4; x++) {
            for (int z = (origin.getZ() - radius) >> 4; z <= (origin.getZ() + radius) >> 4; z++) {
                if (!level.hasChunk(x, z)) {
                    return false;
                }
            }
        }
        return TYGFeatures.TREE_FROM_NBT_V2.get().place(context);
    }
}
