package dev.chromus.flora.world;

import dev.chromus.flora.FloraPlatform;
import dev.corgitaco.ohthetreesyoullgrow.world.level.levelgen.feature.configurations.TreeFromStructureNBTConfigV2;
import net.minecraft.core.BlockPos;
import org.jspecify.annotations.Nullable;
import net.minecraft.core.Vec3i;
import net.minecraft.resources.Identifier;
import net.minecraft.server.level.WorldGenRegion;
import net.minecraft.world.level.WorldGenLevel;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.levelgen.structure.templatesystem.StructureTemplate;
import net.minecraft.world.level.levelgen.structure.templatesystem.StructureTemplateManager;

public final class TreeFootprint {
    private TreeFootprint() {}

    public static boolean allows(WorldGenLevel level, BlockPos origin, TreeFromStructureNBTConfigV2 config) {
        if (config.orientation() != TreeFromStructureNBTConfigV2.Orientation.STANDARD
                || !config.treeDecorators().isEmpty()) {
            throw new IllegalArgumentException("bounded_tree requires STANDARD orientation and no decorators: "
                    + config.canopyLocation());
        }
        StructureTemplateManager manager = FloraPlatform.structureTemplates(level);
        StructureTemplate base = template(manager, config.baseLocation());
        StructureTemplate canopy = template(manager, config.canopyLocation());
        int radius = Math.addExact(horizontalRadius(base, config.baseLocation()),
                horizontalRadius(canopy, config.canopyLocation()));
        int minY = Math.subtractExact(origin.getY(), config.maxLogDepth());
        int maxY = Math.addExact(origin.getY(), Math.addExact(config.height().maxInclusive(),
                Math.addExact(base.getSize().getY(), canopy.getSize().getY())));
        if (minY <= level.getMinY() || maxY >= level.getMaxY()) {
            return false;
        }
        int minX = Math.subtractExact(origin.getX(), radius);
        int maxX = Math.addExact(origin.getX(), radius);
        int minZ = Math.subtractExact(origin.getZ(), radius);
        int maxZ = Math.addExact(origin.getZ(), radius);
        int readRadius = Math.addExact(radius, 1);
        for (int x = Math.subtractExact(origin.getX(), readRadius) >> 4;
                x <= Math.addExact(origin.getX(), readRadius) >> 4; x++) {
            for (int z = Math.subtractExact(origin.getZ(), readRadius) >> 4;
                    z <= Math.addExact(origin.getZ(), readRadius) >> 4; z++) {
                if (!level.hasChunk(x, z)) {
                    return false;
                }
            }
        }
        for (int x = minX >> 4; x <= maxX >> 4; x++) {
            for (int z = minZ >> 4; z <= maxZ >> 4; z++) {
                BlockPos lower = new BlockPos(Math.max(minX, x << 4), minY, Math.max(minZ, z << 4));
                BlockPos upper = new BlockPos(lower.getX(), maxY, lower.getZ());
                if (level instanceof WorldGenRegion region && !region.isWithinWriteZone(lower)) {
                    return false;
                }
                if (!level.ensureCanWrite(lower) || !level.ensureCanWrite(upper)) {
                    return false;
                }
            }
        }
        return true;
    }
    private static StructureTemplate template(StructureTemplateManager manager, Identifier id) {
        return manager.get(id).orElseThrow(() -> new IllegalStateException("Missing tree template " + id));
    }

    private static int horizontalRadius(StructureTemplate template, Identifier id) {
        Vec3i size = template.getSize();
        if (size.getX() <= 0 || size.getY() <= 0 || size.getZ() <= 0 || template.palettes.isEmpty()) {
            throw new IllegalArgumentException("Empty tree template " + id);
        }
        int radius = 0;
        for (StructureTemplate.Palette palette : template.palettes) {
            @Nullable BlockPos anchor = null;
            int minX = size.getX();
            int maxX = 0;
            int minZ = size.getZ();
            int maxZ = 0;
            for (StructureTemplate.StructureBlockInfo info : palette.blocks()) {
                BlockPos pos = info.pos();
                if (pos.getX() < 0 || pos.getX() >= size.getX() || pos.getY() < 0
                        || pos.getY() >= size.getY() || pos.getZ() < 0 || pos.getZ() >= size.getZ()) {
                    throw new IllegalArgumentException("Block outside tree template bounds in " + id);
                }
                minX = Math.min(minX, pos.getX());
                maxX = Math.max(maxX, pos.getX());
                minZ = Math.min(minZ, pos.getZ());
                maxZ = Math.max(maxZ, pos.getZ());
                if (info.state().is(Blocks.WOOL.white())) {
                    if (anchor != null) {
                        throw new IllegalArgumentException("Multiple tree anchors in " + id);
                    }
                    anchor = info.pos();
                }
            }
            if (anchor == null) {
                throw new IllegalArgumentException("Missing or invalid tree anchor in " + id);
            }
            radius = Math.max(radius, Math.max(Math.max(anchor.getX() - minX, maxX - anchor.getX()),
                    Math.max(anchor.getZ() - minZ, maxZ - anchor.getZ())));
        }
        return radius;
    }
}
