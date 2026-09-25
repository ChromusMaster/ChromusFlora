package dev.chromus.flora.client;

import dev.chromus.flora.FloraConfig;
import dev.chromus.flora.ChromusFlora;
import net.minecraft.client.gui.GuiGraphicsExtractor;
import net.minecraft.client.gui.components.Button;
import net.minecraft.client.gui.components.StringWidget;
import net.minecraft.client.gui.screens.Screen;
import net.minecraft.network.chat.Component;

public final class FloraSettingsScreen extends Screen {
    private final Screen parent;
    private FloraConfig.Settings draft;
    private Component status = Component.translatable("screen.chromusflora.restart");

    public FloraSettingsScreen(Screen parent) {
        super(Component.translatable("screen.chromusflora.title"));
        this.parent = parent;
        this.draft = FloraConfig.draftForNextLaunch();
    }

    @Override
    protected void init() {
        int x = width / 2 - 120;
        int top = Math.max(28, height / 2 - 84);
        addRenderableWidget(new StringWidget(x, top - 24, 240, 20, title, font));
        addRenderableWidget(Button.builder(Component.translatable("screen.chromusflora.weight", draft.regionWeight()), button -> {
            draft = new FloraConfig.Settings(draft.regionWeight() % 5 + 1, draft.jaizSpawns(), draft.jaizFeatures());
            rebuildWidgets();
        }).bounds(x, top, 240, 20).build());
        addRenderableWidget(Button.builder(toggle("screen.chromusflora.spawns", draft.jaizSpawns()), button -> {
            draft = new FloraConfig.Settings(draft.regionWeight(), !draft.jaizSpawns(), draft.jaizFeatures());
            rebuildWidgets();
        }).bounds(x, top + 26, 240, 20).build());
        addRenderableWidget(Button.builder(toggle("screen.chromusflora.features", draft.jaizFeatures()), button -> {
            draft = new FloraConfig.Settings(draft.regionWeight(), draft.jaizSpawns(), !draft.jaizFeatures());
            rebuildWidgets();
        }).bounds(x, top + 52, 240, 20).build());
        addRenderableWidget(new StringWidget(x - 60, top + 80, 360, 20, status, font));
        addRenderableWidget(Button.builder(Component.translatable("screen.chromusflora.save"), button -> {
            try {
                FloraConfig.writeForNextLaunch(draft);
                status = Component.translatable("screen.chromusflora.saved");
            } catch (IllegalStateException exception) {
                ChromusFlora.LOGGER.error("Cannot save settings", exception);
                status = Component.translatable("screen.chromusflora.save_failed");
            }
            rebuildWidgets();
        }).bounds(x, top + 108, 116, 20).build());
        addRenderableWidget(Button.builder(Component.translatable("gui.back"), button -> onClose())
                .bounds(x + 124, top + 108, 116, 20).build());
    }

    private static Component toggle(String key, boolean enabled) {
        return Component.translatable(key, Component.translatable(enabled ? "options.on" : "options.off"));
    }

    @Override
    public void extractRenderState(GuiGraphicsExtractor graphics, int mouseX, int mouseY, float partialTick) {
        extractBackground(graphics, mouseX, mouseY, partialTick);
        super.extractRenderState(graphics, mouseX, mouseY, partialTick);
    }

    @Override
    public void onClose() {
        minecraft.setScreen(parent);
    }
}
