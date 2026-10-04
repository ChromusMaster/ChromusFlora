package dev.chromus.flora.mixin;

import net.minecraft.world.level.chunk.storage.SerializableChunkData;
import org.spongepowered.asm.mixin.Mixin;

@Mixin(value = SerializableChunkData.class, priority = 100, remap = false)
public abstract class ChunkReadCompatibility {
}
