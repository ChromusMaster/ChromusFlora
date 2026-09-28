package dev.chromus.flora.world;

import dev.corgitaco.ohthetreesyoullgrow.world.level.levelgen.feature.TYGFeatures;
import dev.corgitaco.ohthetreesyoullgrow.world.level.levelgen.feature.configurations.TreeFromStructureNBTConfigV2;
import net.minecraft.core.BlockPos;
import net.minecraft.core.Vec3i;
import net.minecraft.resources.Identifier;
import net.minecraft.server.level.WorldGenRegion;
import net.minecraft.world.level.WorldGenLevel;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.levelgen.feature.Feature;
import net.minecraft.world.level.levelgen.feature.FeaturePlaceContext;
import net.minecraft.world.level.levelgen.structure.templatesystem.StructureTemplate;
import net.minecraft.world.level.levelgen.structure.templatesystem.StructureTemplateManager;

public final class BoundedTreeFeature extends Feature<TreeFromStructureNBTConfigV2> {
    public BoundedTreeFeature() {
        super(TreeFromStructureNBTConfigV2.CODEC);
    }

    @Override
    public boolean place(FeaturePlaceContext<TreeFromStructureNBTConfigV2> context) {
        WorldGenLevel level = context.level();
        BlockPos origin = context.origin();
        TreeFromStructureNBTConfigV2 config = context.config();
        if (!TreeFootprint.allows(level, origin, config)) {
            return false;
        }
        return TYGFeatures.TREE_FROM_NBT_V2.get().place(context);
    }

}
