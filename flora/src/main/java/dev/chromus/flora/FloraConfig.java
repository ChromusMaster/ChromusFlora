package dev.chromus.flora;

import org.jspecify.annotations.Nullable;
import com.google.gson.Gson;
import com.google.gson.GsonBuilder;
import com.google.gson.JsonParseException;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.AtomicMoveNotSupportedException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.StandardCopyOption;
import net.fabricmc.loader.api.FabricLoader;

public final class FloraConfig {
    public record Settings(int regionWeight, boolean jaizSpawns, boolean jaizFeatures) {
        public Settings {
            if (regionWeight < 1 || regionWeight > 5) {
                throw new IllegalArgumentException("regionWeight must be between 1 and 5");
            }
        }
    }

    private static final Gson GSON = new GsonBuilder().setPrettyPrinting().create();
    private static final Path PATH = FabricLoader.getInstance().getConfigDir().resolve("chromusflora.json");
    private static Settings current = new Settings(1, true, true);
    private static @Nullable Settings nextLaunch;
    private static boolean loaded;

    private FloraConfig() {}

    public static synchronized Settings get() {
        load();
        return current;
    }

    public static synchronized Settings draftForNextLaunch() {
        load();
        @Nullable Settings draft = nextLaunch;
        return draft == null ? current : draft;
    }

    public static synchronized void load() {
        if (loaded) {
            return;
        }
        if (Files.exists(PATH)) {
            try {
                @Nullable Settings parsed = GSON.fromJson(Files.readString(PATH, StandardCharsets.UTF_8), Settings.class);
                if (parsed == null) {
                    throw new IllegalArgumentException("Empty configuration");
                }
                current = parsed;
            } catch (IOException | JsonParseException | IllegalArgumentException exception) {
                throw new IllegalStateException("Invalid Chromus Flora configuration: " + PATH, exception);
            }
        } else {
            writeForNextLaunch(current);
        }
        loaded = true;
    }

    public static synchronized void writeForNextLaunch(Settings settings) {
        @Nullable Path temporary = null;
        try {
            Files.createDirectories(PATH.getParent());
            temporary = Files.createTempFile(PATH.getParent(), "chromusflora-", ".json.tmp");
            Files.writeString(temporary, GSON.toJson(settings) + System.lineSeparator(), StandardCharsets.UTF_8);
            try {
                Files.move(temporary, PATH, StandardCopyOption.ATOMIC_MOVE, StandardCopyOption.REPLACE_EXISTING);
            } catch (AtomicMoveNotSupportedException exception) {
                Files.move(temporary, PATH, StandardCopyOption.REPLACE_EXISTING);
            }
            nextLaunch = settings;
        } catch (IOException exception) {
            throw new IllegalStateException("Cannot save Chromus Flora configuration", exception);
        } finally {
            if (temporary != null) {
                try {
                    Files.deleteIfExists(temporary);
                } catch (IOException exception) {
                    ChromusFlora.LOGGER.error("Cannot remove temporary configuration {}", temporary, exception);
                }
            }
        }
    }
}
