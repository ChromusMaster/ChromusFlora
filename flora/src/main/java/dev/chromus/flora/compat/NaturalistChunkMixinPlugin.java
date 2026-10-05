package dev.chromus.flora.compat;

import java.util.List;
import java.util.Set;
import net.fabricmc.loader.api.FabricLoader;
import org.jspecify.annotations.Nullable;
import org.objectweb.asm.Opcodes;
import org.objectweb.asm.tree.ClassNode;
import org.objectweb.asm.tree.MethodInsnNode;
import org.objectweb.asm.tree.MethodNode;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.spongepowered.asm.mixin.extensibility.IMixinConfigPlugin;
import org.spongepowered.asm.mixin.extensibility.IMixinInfo;

/** Optional compatibility: no Naturalist classes are linked when that mod is absent. */
public final class NaturalistChunkMixinPlugin implements IMixinConfigPlugin {
    private static final Logger LOGGER = LoggerFactory.getLogger("ChromusFlora/ChunkSafety");
    private static final String TARGET = "com.crispytwig.naturalist.world.entity.animal.hippo.Hippo";
    private static final String MIXIN = "dev.chromus.flora.mixin.NaturalistHippoCompatibility";
    private static final String DESCRIPTOR = "(Lnet/minecraft/world/entity/EntityType;"
            + "Lnet/minecraft/world/level/ServerLevelAccessor;Lnet/minecraft/world/entity/EntitySpawnReason;"
            + "Lnet/minecraft/core/BlockPos;Lnet/minecraft/util/RandomSource;)Z";
    private boolean enabled;

    @Override
    public void onLoad(String mixinPackage) {
        FabricLoader.getInstance().getModContainer("naturalist").ifPresent(mod -> {
            String version = mod.getMetadata().getVersion().getFriendlyString();
            enabled = "2.0.6".equals(version);
            if (!enabled) {
                LOGGER.warn("Naturalist {}: hippo worldgen read guard is not enabled for this unreviewed version", version);
            }
        });
    }

    @Override
    public @Nullable String getRefMapperConfig() { return null; }

    @Override
    public boolean shouldApplyMixin(String targetClassName, String mixinClassName) {
        return enabled && TARGET.equals(targetClassName) && MIXIN.equals(mixinClassName);
    }

    @Override
    public void acceptTargets(Set<String> myTargets, Set<String> otherTargets) { }

    @Override
    public List<String> getMixins() { return List.of(); }

    @Override
    public void preApply(String targetClassName, ClassNode targetClass, String mixinClassName, IMixinInfo mixinInfo) {
        List<MethodNode> candidates = targetClass.methods.stream()
                .filter(method -> "checkHippoSpawnRules".equals(method.name) && DESCRIPTOR.equals(method.desc))
                .toList();
        if (candidates.size() != 1 || (candidates.getFirst().access & Opcodes.ACC_STATIC) == 0) {
            throw new IllegalStateException("Chromus Flora: Naturalist hippo spawn method differs from the reviewed API");
        }
        int probes = 0;
        for (var instruction : candidates.getFirst().instructions) {
            if (instruction instanceof MethodInsnNode call && call.getOpcode() == Opcodes.INVOKEINTERFACE
                    && "net/minecraft/world/level/ServerLevelAccessor".equals(call.owner)
                    && "hasChunk".equals(call.name) && "(II)Z".equals(call.desc)) {
                probes++;
            }
        }
        if (probes != 1) {
            throw new IllegalStateException("Chromus Flora: expected one Naturalist hippo terrain probe, found " + probes);
        }
    }

    @Override
    public void postApply(String targetClassName, ClassNode targetClass, String mixinClassName, IMixinInfo mixinInfo) {
        LOGGER.info("Applied Naturalist 2.0.6 hippo worldgen read guard (Chromus Flora hotfix 3)");
    }
}
