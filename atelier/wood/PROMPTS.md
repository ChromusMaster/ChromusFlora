# Wood atlas generation specification

Built-in OpenAI image generation; original voxel-game pixel art. No original-mod
image references. Six sheets, 7 columns and 8 rows. Each group of four rows contains
bark side, cut end, stripped grain, and planks. First seven species occupy rows 0–3;
next seven occupy rows 4–7. No labels, watermarks, 3D perspective or lighting gradients.
Distinct palettes and bark motifs by name. Species briefs and grid positions are in
species.json. Explicit crop boundaries account for generated grid spacing; inset
removes separators before nearest-neighbor downsampling to 64×64. The sixth sheet's
unused last column is not shipped as a game texture.

## Fix 10 edit prompt (applied to each of the six project-owned sheets)

Edit this original voxel-game texture atlas. Preserve ALL species palette colors,
the same texture styles and species order, precisely 7 columns x 8 rows. This is
technical seam repair only, not redesign. Remove ALL dark border lines separating
cells. EVERY individual tile must be seamless when repeated horizontally and
vertically: connect vertical bark grain and stripped wood fibers at top and bottom;
match the color and pattern at left and right. Do not draw frames or horizontal bands
around bark tiles. Keep bark row, cut end row, stripped grain row and plank row in
the existing order, repeated for bottom half. Keep round end grain patterns and
plank courses. Exact equal square cells covering canvas 7:8. No margins, no separators,
no labels, no perspective, no drop shadows. This will be cropped into 56 standalone
repeating material tiles.

Production extraction uses the explicit crop grid, 8 source pixels of inset and an
8-pixel symmetric edge blend after 64x64 sampling. Matching end rows and columns are
verified on the shipped PNG files, independently of image-generation compliance.
