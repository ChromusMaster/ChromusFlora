package dev.chromus.flora.client;

import java.util.EnumSet;
import java.util.Set;
import net.minecraft.client.model.geom.PartPose;
import net.minecraft.client.model.geom.builders.CubeListBuilder;
import net.minecraft.client.model.geom.builders.LayerDefinition;
import net.minecraft.client.model.geom.builders.MeshDefinition;
import net.minecraft.client.model.geom.builders.PartDefinition;
import net.minecraft.client.model.object.chest.ChestModel;
import net.minecraft.core.Direction;
import net.minecraft.world.level.block.state.properties.ChestType;


final class FloraChestModel {
    private FloraChestModel() {}

    static ChestModel create(ChestType type, boolean interior) {
        float minX = type == ChestType.LEFT ? 0.0F : 1.0F;
        float maxX = type == ChestType.RIGHT ? 16.0F : 15.0F;
        float innerMinX = type == ChestType.LEFT ? 0.0F : 2.0F;
        float innerMaxX = type == ChestType.RIGHT ? 16.0F : 14.0F;
        CubeListBuilder cubes = CubeListBuilder.create().texOffs(0, 19);
        if (interior) {
            top(cubes, innerMinX, 2.0F, innerMaxX - innerMinX, 12.0F);
        } else {
            Set<Direction> sides = EnumSet.allOf(Direction.class);
            sides.remove(Direction.UP);
            if (type == ChestType.LEFT) sides.remove(Direction.WEST);
            if (type == ChestType.RIGHT) sides.remove(Direction.EAST);

            cubes.addBox(minX, 0.0F, 1.0F, maxX - minX, 9.0F, 14.0F, sides);
            top(cubes, minX, 1.0F, maxX - minX, 1.0F);
            top(cubes, minX, 14.0F, maxX - minX, 1.0F);
            if (type != ChestType.LEFT) top(cubes, 1.0F, 2.0F, 1.0F, 12.0F);
            if (type != ChestType.RIGHT) top(cubes, 14.0F, 2.0F, 1.0F, 12.0F);
        }
        MeshDefinition mesh = new MeshDefinition();
        PartDefinition root = mesh.getRoot();
        root.addOrReplaceChild("bottom", cubes, PartPose.ZERO);

        root.addOrReplaceChild("lid", CubeListBuilder.create(), PartPose.ZERO);
        root.addOrReplaceChild("lock", CubeListBuilder.create(), PartPose.ZERO);
        return new ChestModel(LayerDefinition.create(mesh, 64, 64).bakeRoot());
    }

    private static void top(CubeListBuilder cubes, float x, float z, float width, float depth) {
        cubes.addBox(x, 9.0F, z, width, 0.0F, depth, Set.of(Direction.UP));
    }
}
