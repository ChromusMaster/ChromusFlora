from PIL import Image


def periodic_tile(tile, band=8):
    tile = tile.convert('RGBA')
    width, height = tile.size
    pixels = list(tile.getdata())
    for axis, size, other in ((0, width, height), (1, height, width)):
        source = pixels[:]
        for distance in range(band):
            t = distance / (band - 1)
            weight = 1 - t * t * (3 - 2 * t)
            for position in range(other):
                a = position * width + distance if axis == 0 else distance * width + position
                b = position * width + size - 1 - distance if axis == 0 else (size - 1 - distance) * width + position
                mean = tuple((source[a][c] + source[b][c]) / 2 for c in range(4))
                for index in (a, b):
                    pixels[index] = tuple(round(source[index][c] * (1 - weight) + mean[c] * weight) for c in range(4))
    result = Image.new('RGBA', (width, height))
    result.putdata(pixels)
    return result
