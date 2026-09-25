package dev.chromus.flora.client;

import dev.chromus.flora.ChromusFlora;
import dev.chromus.flora.FloraCatalog;
import dev.chromus.flora.block.FloraSapling;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.Identifier;
import snownee.jade.api.BlockAccessor;
import snownee.jade.api.IBlockComponentProvider;
import snownee.jade.api.ITooltip;
import snownee.jade.api.IWailaClientRegistration;
import snownee.jade.api.IWailaPlugin;
import snownee.jade.api.config.IPluginConfig;

public final class FloraJade implements IWailaPlugin {
    @Override
    public void registerClient(IWailaClientRegistration registration) {
        registration.registerBlockComponent(TreeInfo.INSTANCE, FloraSapling.class);
    }

    private enum TreeInfo implements IBlockComponentProvider {
        INSTANCE;

        @Override
        public Identifier getUid() {
            return ChromusFlora.id("tree_height");
        }

        @Override
        public void appendTooltip(ITooltip tooltip, BlockAccessor accessor, IPluginConfig config) {
            String path = BuiltInRegistries.BLOCK.getKey(accessor.getBlock()).getPath();
            String id = path.substring(0, path.length() - "_sapling".length());
            for (FloraCatalog.Tree tree : FloraCatalog.get().trees()) {
                if (tree.id().equals(id)) {
                    tooltip.add(Component.translatable("tooltip.chromusflora.height", 3, tree.maxHeight()));
                    return;
                }
            }
        }
    }
}
