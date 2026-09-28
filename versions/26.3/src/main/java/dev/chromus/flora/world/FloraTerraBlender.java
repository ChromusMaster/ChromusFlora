package dev.chromus.flora.world;

import com.mojang.datafixers.util.Pair;
import dev.chromus.flora.ChromusFlora;
import dev.chromus.flora.FloraCatalog;
import dev.chromus.flora.FloraConfig;
import java.util.ArrayList;
import java.util.List;
import java.util.function.Consumer;
import net.minecraft.core.HolderGetter;
import net.minecraft.core.Registry;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.core.registries.Registries;
import net.minecraft.resources.Identifier;
import net.minecraft.resources.ResourceKey;
import net.minecraft.world.level.biome.Biome;
import net.minecraft.world.level.biome.Climate;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.levelgen.material.MaterialRules;
import net.minecraft.world.level.levelgen.material.rule.MaterialRule;
import net.minecraft.world.level.levelgen.placement.CaveSurface;
import net.minecraft.world.level.levelgen.VerticalAnchor;
import terrablender.api.EndBiomeRegistry;
import terrablender.api.Region;
import terrablender.api.RegionType;
import terrablender.api.Regions;
import terrablender.api.MaterialRuleManager;
import terrablender.api.TerraBlenderApi;

public final class FloraTerraBlender implements TerraBlenderApi {
    public static ResourceKey<Biome> key(String id) {
        return ResourceKey.create(Registries.BIOME, ChromusFlora.id(id));
    }

    @Override
    public void onTerraBlenderInitialized() {
        int weight = FloraConfig.get().regionWeight();
        for (FloraCatalog.Biome biome : FloraCatalog.get().biomes()) {
            if (biome.dimension().equals("end")) {
                EndBiomeRegistry.registerHighlandsBiome(key(biome.id()), weight);
                EndBiomeRegistry.registerMidlandsBiome(key(biome.id()), weight);
                if (biome.id().contains("isle") || biome.id().contains("island")) {
                    EndBiomeRegistry.registerIslandBiome(key(biome.id()), weight);
                }
            } else {
                Regions.register(new FloraRegion(biome, weight));
            }
        }
        for (MaterialRuleManager.RuleCategory category : MaterialRuleManager.RuleCategory.values()) {
            MaterialRuleManager.addRules(category, ChromusFlora.ID,
                    registries -> surfaceRules(registries.lookupOrThrow(Registries.BIOME), category));
        }
    }

    private static MaterialRule surfaceRules(HolderGetter<Biome> registry,
                                                       MaterialRuleManager.RuleCategory category) {
        List<MaterialRule> rules = new ArrayList<>();
        if (category != MaterialRuleManager.RuleCategory.END) {
            rules.add(MaterialRules.ifTrue(MaterialRules.verticalGradient("bedrock_floor",
                    VerticalAnchor.bottom(), VerticalAnchor.aboveBottom(5)),
                    MaterialRules.state(Blocks.BEDROCK.defaultBlockState())));
        }
        if (category == MaterialRuleManager.RuleCategory.NETHER) {
            rules.add(MaterialRules.ifTrue(MaterialRules.not(MaterialRules.verticalGradient("bedrock_roof",
                    VerticalAnchor.belowTop(5), VerticalAnchor.top())),
                    MaterialRules.state(Blocks.BEDROCK.defaultBlockState())));
        }
        for (FloraCatalog.Biome biome : FloraCatalog.get().biomes()) {
            if (!biome.dimension().equalsIgnoreCase(category.name())) {
                continue;
            }
            Block top = BuiltInRegistries.BLOCK.getOptional(Identifier.parse(biome.surface()))
                    .orElseThrow(() -> new IllegalStateException("Unknown surface " + biome.surface()));
            Block under = switch (biome.dimension()) {
                case "nether" -> Blocks.NETHERRACK;
                case "end" -> Blocks.END_STONE;
                default -> biome.surface().contains("sand") ? Blocks.SANDSTONE : Blocks.DIRT;
            };
            MaterialRule layers = MaterialRules.sequence(
                    MaterialRules.ifTrue(MaterialRules.stoneDepthCheck(0, false, CaveSurface.FLOOR), MaterialRules.state(top.defaultBlockState())),
                    MaterialRules.ifTrue(MaterialRules.stoneDepthCheck(0, true, CaveSurface.FLOOR), MaterialRules.state(under.defaultBlockState())));
            if (biome.dimension().equals("overworld")) {
                layers = MaterialRules.ifTrue(MaterialRules.abovePreliminarySurface(), layers);
            }
            rules.add(MaterialRules.ifTrue(MaterialRules.isBiome(registry, key(biome.id())), layers));
        }
        Block fallback = switch (category) {
            case NETHER -> Blocks.NETHERRACK;
            case END -> Blocks.END_STONE;
            case OVERWORLD -> Blocks.STONE;
        };
        rules.add(MaterialRules.state(fallback.defaultBlockState()));
        return MaterialRules.sequence(rules.toArray(MaterialRule[]::new));
    }

    private static final class FloraRegion extends Region {
        private final FloraCatalog.Biome biome;

        private FloraRegion(FloraCatalog.Biome biome, int weight) {
            super(ChromusFlora.id("region/" + biome.id()),
                    biome.dimension().equals("nether") ? RegionType.NETHER : RegionType.OVERWORLD, weight);
            this.biome = biome;
        }

        @Override
        public void addBiomes(Registry<Biome> registry,
                              Consumer<Pair<Climate.ParameterPoint, ResourceKey<Biome>>> mapper) {
            if (biome.dimension().equals("nether")) {
                Climate.ParameterPoint point = switch (biome.vanilla()) {
                    case "minecraft:crimson_forest" -> Climate.parameters(0.4F, 0, 0, 0, 0, 0, 0);
                    case "minecraft:warped_forest" -> Climate.parameters(0, 0.5F, 0, 0, 0, 0, 0.375F);
                    case "minecraft:soul_sand_valley" -> Climate.parameters(0, -0.5F, 0, 0, 0, 0, 0);
                    case "minecraft:basalt_deltas" -> Climate.parameters(-0.5F, 0, 0, 0, 0, 0, 0.175F);
                    default -> Climate.parameters(0, 0, 0, 0, 0, 0, 0);
                };
                addBiome(mapper, point, key(biome.id()));
            } else {
                ResourceKey<Biome> original = ResourceKey.create(Registries.BIOME, Identifier.parse(biome.vanilla()));
                addBiomeSimilar(mapper, original, key(biome.id()));
            }
        }
    }
}
