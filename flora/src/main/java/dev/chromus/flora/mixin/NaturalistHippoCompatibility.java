package dev.chromus.flora.mixin;

import net.minecraft.server.level.WorldGenRegion;
import net.minecraft.world.level.ChunkPos;
import net.minecraft.world.level.ServerLevelAccessor;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.Pseudo;
import org.spongepowered.asm.mixin.injection.At;
import org.spongepowered.asm.mixin.injection.Redirect;


@Pseudo
@Mixin(targets = "com.crispytwig.naturalist.world.entity.animal.hippo.Hippo", remap = false)
public abstract class NaturalistHippoCompatibility {
    @Redirect(
            method = "checkHippoSpawnRules(Lnet/minecraft/world/entity/EntityType;"
                    + "Lnet/minecraft/world/level/ServerLevelAccessor;"
                    + "Lnet/minecraft/world/entity/EntitySpawnReason;Lnet/minecraft/core/BlockPos;"
                    + "Lnet/minecraft/util/RandomSource;)Z",
            at = @At(value = "INVOKE", target = "Lnet/minecraft/world/level/ServerLevelAccessor;hasChunk(II)Z"),
            require = 1, expect = 1, allow = 1, remap = false)
    private static boolean chromusflora$allowHippoWaterProbe(ServerLevelAccessor level, int chunkX, int chunkZ) {


        if (level instanceof WorldGenRegion region) {
            ChunkPos center = region.getCenter();
            if (chunkX != center.x() || chunkZ != center.z()) {
                return false;
            }
        }

        return level.hasChunk(chunkX, chunkZ);
    }
}
