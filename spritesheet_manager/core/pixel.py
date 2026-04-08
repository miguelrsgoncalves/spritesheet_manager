def read_pixels(doc, x, y, width, height) -> bytes:
    return doc.pixelData(x, y, width, height)

def write_pixels(layer, data: bytes, x, y, width, height) -> None:
    layer.setPixelData(data, x, y, width, height)

def get_bytes_per_pixel(doc) -> int:
    channels_by_model = {"RGBA": 4, "RGB": 3, "GRAYA": 2, "GRAY": 1, "CMYKA": 5, "CMYK": 4}
    bytes_by_depth = {"U8": 1, "U16": 2, "F16": 2, "F32": 4}
    
    return channels_by_model.get(doc.colorModel(), 4) * bytes_by_depth.get(doc.colorDepth(), 1)

def repeat_row_vertically(row_bytes: bytes, times: int) -> bytes:
    return row_bytes * times

def repeat_column_horizontally(column_bytes: bytes, times: int, bytes_per_pixel: int) -> bytes:
    if bytes_per_pixel == 0:
        return b""
    
    height = len(column_bytes) // bytes_per_pixel
    result = bytearray()

    for row in range(height):
        pixel = column_bytes[row * bytes_per_pixel:(row + 1) * bytes_per_pixel]
        result += pixel * times
    
    return bytes(result)