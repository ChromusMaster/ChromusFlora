package dev.chromus.flora.compat;

import java.util.ArrayList;
import java.util.List;
import java.util.Set;
import net.fabricmc.loader.api.FabricLoader;
import org.jspecify.annotations.Nullable;
import org.objectweb.asm.Opcodes;
import org.objectweb.asm.tree.AbstractInsnNode;
import org.objectweb.asm.tree.AnnotationNode;
import org.objectweb.asm.tree.ClassNode;
import org.objectweb.asm.tree.FieldInsnNode;
import org.objectweb.asm.tree.JumpInsnNode;
import org.objectweb.asm.tree.LdcInsnNode;
import org.objectweb.asm.tree.MethodInsnNode;
import org.objectweb.asm.tree.MethodNode;
import org.objectweb.asm.tree.TypeInsnNode;
import org.objectweb.asm.tree.VarInsnNode;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.spongepowered.asm.mixin.extensibility.IMixinConfigPlugin;
import org.spongepowered.asm.mixin.extensibility.IMixinInfo;

public final class ChunkReadMixinPlugin implements IMixinConfigPlugin {
    private static final Logger LOGGER = LoggerFactory.getLogger("ChromusFlora/ChunkRead");
    private static final String TARGET = "net.minecraft.world.level.chunk.storage.SerializableChunkData";
    private static final String MARKER = "dev.chromus.flora.mixin.ChunkReadCompatibility";
    private static final String UPSTREAM = "dev.corgitaco.ohthetreesyoullgrow.mixin.chunk.MixinChunkSerializer";
    private static final String COMPOUND = "net/minecraft/nbt/CompoundTag";
    private static final String TICKS = "scheduled_random_ticks";
    private static final Set<String> REVIEWED = Set.of("11.0.1", "12.0.0");
    private String treesVersion = "unknown";

    @Override
    public void onLoad(String mixinPackage) {
        treesVersion = FabricLoader.getInstance().getModContainer("ohthetreesyoullgrow")
                .orElseThrow(() -> new IllegalStateException("Missing required OTTYG dependency"))
                .getMetadata().getVersion().getFriendlyString();
        if (!REVIEWED.contains(treesVersion)) {
            LOGGER.info("OTTYG {}: version-specific chunk-read repair is not enabled", treesVersion);
        }
    }

    @Override
    public @Nullable String getRefMapperConfig() { return null; }

    @Override
    public boolean shouldApplyMixin(String targetClassName, String mixinClassName) {
        return REVIEWED.contains(treesVersion) && TARGET.equals(targetClassName) && MARKER.equals(mixinClassName);
    }

    @Override
    public void acceptTargets(Set<String> myTargets, Set<String> otherTargets) { }

    @Override
    public List<String> getMixins() { return List.of(); }

    @Override
    public void preApply(String targetClassName, ClassNode targetClass, String mixinClassName, IMixinInfo mixinInfo) { }

    @Override
    public void postApply(String targetClassName, ClassNode targetClass, String mixinClassName, IMixinInfo mixinInfo) {
        if (!TARGET.equals(targetClassName) || !MARKER.equals(mixinClassName) || !REVIEWED.contains(treesVersion)) {
            throw incompatible("unexpected transformation target");
        }
        List<MethodNode> candidates = targetClass.methods.stream()
                .filter(method -> method.name.endsWith("$readScheduledRandomTicks") && fromUpstream(method))
                .toList();
        if (candidates.size() != 1) {
            throw incompatible("expected exactly one OTTYG chunk-read handler, found " + candidates.size());
        }
        repair(candidates.getFirst());
    }

    private static boolean fromUpstream(MethodNode method) {
        return hasOrigin(method.visibleAnnotations) || hasOrigin(method.invisibleAnnotations);
    }

    private static boolean hasOrigin(@Nullable List<AnnotationNode> annotations) {
        if (annotations == null) { return false; }
        for (AnnotationNode annotation : annotations) {
            if (!"Lorg/spongepowered/asm/mixin/transformer/meta/MixinMerged;".equals(annotation.desc)
                    || annotation.values == null) { continue; }
            for (int i = 0; i + 1 < annotation.values.size(); i += 2) {
                if ("mixin".equals(annotation.values.get(i)) && UPSTREAM.equals(annotation.values.get(i + 1))) {
                    return true;
                }
            }
        }
        return false;
    }

    private static void repair(MethodNode method) {
        List<AbstractInsnNode> code = new ArrayList<>();
        for (AbstractInsnNode instruction : method.instructions) {
            if (instruction.getOpcode() >= 0) { code.add(instruction); }
        }
        if (code.size() < 25
                || !variable(code.get(0), Opcodes.ALOAD, 0)
                || !(code.get(1) instanceof FieldInsnNode field)
                || field.getOpcode() != Opcodes.GETFIELD || !"structureData".equals(field.name)
                || !("L" + COMPOUND + ";").equals(field.desc)
                || !(code.get(2) instanceof VarInsnNode parent) || parent.getOpcode() != Opcodes.ASTORE
                || !variable(code.get(3), Opcodes.ALOAD, parent.var)
                || !literal(code.get(4), "ohthetreesyoullgrow")
                || !call(code.get(5), COMPOUND, "contains", "(Ljava/lang/String;)Z")
                || !(code.get(6) instanceof JumpInsnNode outerGuard) || outerGuard.getOpcode() != Opcodes.IFEQ
                || !variable(code.get(7), Opcodes.ALOAD, parent.var)
                || !literal(code.get(8), "ohthetreesyoullgrow")
                || !call(code.get(9), COMPOUND, "getCompound", "(Ljava/lang/String;)Ljava/util/Optional;")
                || !call(code.get(10), "java/util/Optional", "orElseThrow", "()Ljava/lang/Object;")
                || !cast(code.get(11), COMPOUND)
                || !(code.get(12) instanceof VarInsnNode nested) || nested.getOpcode() != Opcodes.ASTORE
                || nested.var == parent.var
                || !variable(code.get(13), Opcodes.ALOAD, nested.var)
                || !literal(code.get(14), TICKS)
                || !call(code.get(15), COMPOUND, "contains", "(Ljava/lang/String;)Z")
                || !(code.get(16) instanceof JumpInsnNode listGuard) || listGuard.getOpcode() != Opcodes.IFEQ
                || !(code.get(17) instanceof VarInsnNode receiver) || receiver.getOpcode() != Opcodes.ALOAD
                || (receiver.var != parent.var && receiver.var != nested.var)
                || !literal(code.get(18), TICKS)
                || !call(code.get(19), COMPOUND, "getList", "(Ljava/lang/String;)Ljava/util/Optional;")
                || !call(code.get(20), "java/util/Optional", "orElseThrow", "()Ljava/lang/Object;")
                || !cast(code.get(21), "net/minecraft/nbt/ListTag")
                || !call(code.get(22), "net/minecraft/nbt/ListTag", "iterator", "()Ljava/util/Iterator;")) {
            throw incompatible("OTTYG handler has an unreviewed instruction layout");
        }
        long listReads = code.stream().filter(node -> call(node, COMPOUND, "getList", "(Ljava/lang/String;)Ljava/util/Optional;")).count();
        if (listReads != 1) { throw incompatible("ambiguous OTTYG scheduled tick list read"); }
        if (receiver.var == nested.var) {
            LOGGER.info("OTTYG scheduled tick chunk reader already uses the nested tag; no change needed");
            return;
        }
        receiver.var = nested.var;
        LOGGER.info("Applied OTTYG scheduled tick chunk-read repair (nested tag receiver)");
    }

    private static boolean variable(AbstractInsnNode node, int opcode, int slot) {
        return node instanceof VarInsnNode variable && variable.getOpcode() == opcode && variable.var == slot;
    }

    private static boolean literal(AbstractInsnNode node, String value) {
        return node instanceof LdcInsnNode constant && value.equals(constant.cst);
    }

    private static boolean cast(AbstractInsnNode node, String type) {
        return node instanceof TypeInsnNode cast && cast.getOpcode() == Opcodes.CHECKCAST && type.equals(cast.desc);
    }

    private static boolean call(AbstractInsnNode node, String owner, String name, String descriptor) {
        return node instanceof MethodInsnNode call && call.getOpcode() == Opcodes.INVOKEVIRTUAL
                && owner.equals(call.owner) && name.equals(call.name) && descriptor.equals(call.desc);
    }

    private static IllegalStateException incompatible(String detail) {
        return new IllegalStateException("Chromus Flora: cannot safely apply the OTTYG chunk-read repair: " + detail
                + ". Keep the world backup and report the full log; do not delete chunks.");
    }
}
