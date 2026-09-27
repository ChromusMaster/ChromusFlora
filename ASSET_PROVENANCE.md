# English

This is an independent recreation. No BYG/BWG Java implementation, texture,
model geometry, sound, structure NBT or logo is bundled in the active mod.
Changing a copyrighted asset's colors alone does not establish permission.

The supplied archives were inspected for factual biome/tree identifiers and
their occurrence in each catalogue. Shared identifiers select the BWG
successor catalogue; unique identifiers remain represented. Archive names and
Minecraft versions alone do not prove the last edit date of an individual
asset. No such asset is extracted into this release.

The official icon and texture atlas were generated specifically for this
project with OpenAI image generation on 2026-09-25. They were not made by
editing the supplied mods' images. The delivered 64-pixel texture tiles are
crops of that original atlas. No external stock asset was required. This
document does not assert exclusive copyright over AI-generated images.

The NBT structures, block geometry, recipes and Java/Python/PowerShell code
were newly authored. Tree proportions and biome compositions intentionally
differ from the source mods; this is not a visual or behavioral replica.

Minecraft's vanilla biome definitions provide the base spawn, carver and
feature settings for the new datapack biomes. The resource snapshot under
`atelier/vanilla-biome-reference.json` is Minecraft material, not covered by
this project's MIT grant. Vanilla identifiers/model parents refer to the
installed game. Minecraft belongs to Mojang/Microsoft; this is an unofficial
mod and includes no Minecraft executable or jar.

TerraBlender, Oh The Trees You'll Grow, Fabric, Jade, ModMenu and AppleSkin are
external dependencies, not vendored implementations. Their own licenses apply.
JaizMod is neither modified nor bundled. Compatibility data records public
registry identifiers and integration settings from the supplied 2.3.11 source.
The older source tree, if retained when applying this overlay, keeps its own
licenses and is excluded from the active compilation and source jar.

# Português do Brasil

Esta é uma recriação independente. Nenhuma implementação Java, textura,
geometria de modelo, som, estrutura NBT ou logotipo de BYG/BWG integra o mod
ativo. Apenas trocar as cores de um recurso protegido não concede autorização.

Os pacotes fornecidos foram consultados para identificar biomas, árvores e a
presença de cada identificador nos catálogos. Identificadores compartilhados
usam o catálogo sucessor BWG; os exclusivos continuam representados. O nome
do ZIP e a versão do Minecraft não comprovam a revisão mais recente de cada
recurso. Nenhum desses recursos foi extraído para esta entrega.

O ícone oficial e o atlas de texturas foram gerados especificamente para este
projeto com geração de imagens da OpenAI em 25/09/2026, sem editar imagens dos
mods fornecidos. As texturas de 64 pixels são recortes desse atlas original.
Não foi necessário usar imagens de bancos externos. Não se afirma exclusividade
autoral sobre as imagens geradas por IA.

Estruturas NBT, geometria dos blocos, receitas e código Java/Python/PowerShell
foram criados para o projeto. Proporções das árvores e composições dos biomas
diferem dos mods de origem; não são réplicas visuais ou comportamentais.

As definições de bioma do Minecraft fornecem a base de criaturas, escavações e
decorações. `atelier/vanilla-biome-reference.json` é material do Minecraft e
não recebe a licença MIT deste projeto. Referências a modelos vanilla usam
o jogo instalado. Minecraft pertence à Mojang/Microsoft; este mod não é oficial
e não inclui executáveis nem jars do Minecraft.

As bibliotecas externas mantêm suas próprias licenças. JaizMod não foi alterado
nem incluído. Os dados de compatibilidade registram identificadores públicos e
configurações de integração do código 2.3.11 fornecido. Se a árvore antiga for
mantida ao aplicar a sobreposição, suas licenças permanecem válidas; ela não
participa da compilação ativa nem do jar de fontes.

## Fix 9 — original wood art / madeira original

Six additional atlases provide the 83 wood families (332 individual textures).
Created with OpenAI's built-in image-generation tool, using textual species/color
briefs rather than images from the original mods. The briefs and crop mapping are
in atelier/wood/species.json; generation instructions are in atelier/wood/PROMPTS.md.
The older original atlas now supplies leaves only. The original icon is retained.

Seis novos atlas originais fornecem as madeiras. Não foram usados recortes de BYG/BWG
ou Jaiz como referência visual. As cores interpretam os nomes; não são uma reprodução
botânica exata. O atlas anterior permanece necessário para regenerar as folhas.

## Fix 10 — seams and branches / emendas e galhos

The six project-owned wood atlases were edited with OpenAI image generation, retaining
the established palettes. No original-mod assets were used as visual references.
The resource generator crops inside each tile and reconciles opposite edge bands
with a deterministic sampler (tools/texture_tiles.py). This is reproducible from
the delivered atlases. Normal and giant tree NBT layouts are newly generated by
our tools/tree_shapes.py. User-supplied real-tree photos informed the branching
layout only; no photograph pixels are bundled in textures.

Os atlas próprios foram ajustados; as bordas passam por validação de continuidade.
As fotografias reais enviadas orientaram a distribuição dos galhos e não foram
incorporadas às texturas. As estruturas são originais do gerador do projeto.
