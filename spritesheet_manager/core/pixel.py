def read_pixels(doc, x, y, width, height) -> bytes:
    return doc.pixelData(x, y, width, height)

def write_pixels(layer, data: bytes, x, y, width, height) -> None:
    layer.setPixelData(data, x, y, width, height)

def tile_pixel_size(doc) -> int:
    model = doc.colorModel()
    depth = doc.colorDepth()
    channels = {"RGBA": 4, "RGB": 3, "GRAYA": 2, "GRAY": 1, "CMYKA": 5, "CMYK": 4}
    bits = {"U8": 1, "U16": 2, "F16": 2, "F32": 4}
    return channels.get(model, 4) * bits.get(depth, 1)

def repeat_row_vertically(row_bytes: bytes, times: int) -> bytes:
    return row_bytes * times

def repeat_col_horizontally(col_bytes: bytes, times: int, bytes_per_pixel: int) -> bytes:
    if bytes_per_pixel == 0:
        return b""
    height = len(col_bytes) // bytes_per_pixel
    result = bytearray()
    for row in range(height):
        pixel = col_bytes[row * bytes_per_pixel:(row + 1) * bytes_per_pixel]
        result += pixel * times
    return bytes(result)