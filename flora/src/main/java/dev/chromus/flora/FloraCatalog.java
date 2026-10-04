package dev.chromus.flora;

import org.jspecify.annotations.Nullable;
import com.google.gson.Gson;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.nio.charset.StandardCharsets;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.function.Function;
import java.util.stream.Collectors;

public final class FloraCatalog {
    public record Tree(String id, String shape, int palette, String dimension, int maxHeight) {}
    public record Biome(String id, String dimension, String vanilla, String surface,
                        List<String> trees, int density) {
        public Biome {
            trees = List.copyOf(trees);
        }
    }
    public record Catalog(List<Tree> trees, List<Biome> biomes) {
        public Catalog {
            trees = List.copyOf(trees);
            biomes = List.copyOf(biomes);
        }
    }
    private static final Catalog INSTANCE = read("/chromusflora/catalog.json", Catalog.class);
    private static final Map<String, Tree> TREES = INSTANCE.trees().stream()
            .collect(Collectors.toUnmodifiableMap(Tree::id, Function.identity()));
    private static final Map<String, Biome> BIOMES = INSTANCE.biomes().stream()
            .collect(Collectors.toUnmodifiableMap(Biome::id, Function.identity()));

    private FloraCatalog() {}

    public static Catalog get() {
        return INSTANCE;
    }

    public static @Nullable Tree tree(String id) {
        return TREES.get(id);
    }

    public static @Nullable Biome biome(String id) {
        return BIOMES.get(id);
    }

    public static <T> T read(String path, Class<T> type) {
        InputStream stream = Objects.requireNonNull(FloraCatalog.class.getResourceAsStream(path), path);
        try (InputStreamReader reader = new InputStreamReader(stream, StandardCharsets.UTF_8)) {
            return Objects.requireNonNull(new Gson().fromJson(reader, type), path);
        } catch (IOException exception) {
            throw new IllegalStateException("Cannot load " + path, exception);
        }
    }
}
