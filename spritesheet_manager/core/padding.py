import os
from krita import Krita
from .pixel import read_pixels, write_pixels, repeat_row_vertically, tile_pixel_size

def create_padded_document(
    source_doc,
    tile_width: int,
    tile_height: int,
    padding_x: int,
    padding_y: int,
    columns: int,
    rows: int,
    anti_bleed: bool,
    name: str,
    save_kra: bool
):
    app = Krita.instance()

    stride_x = tile_width  + (padding_x * 2)
    stride_y = tile_height + (padding_y * 2)
    new_width = columns * stride_x
    new_height = rows * stride_y

    new_doc = app.createDocument(
        new_width, new_height, name,
        source_doc.colorModel(),
        source_doc.colorDepth(),
        source_doc.colorProfile(),
        source_doc.resolution()
    )

    root = new_doc.rootNode()
    for child in root.childNodes():
        root.removeChildNode(child)

    layer = new_doc.createNode("Padded Spritesheet", "paintlayer")
    root.addChildNode(layer, None)

    src_w = source_doc.width()
    src_h = source_doc.height()

    for row in range(rows):
        for col in range(columns):
            src_x = col * tile_width
            src_y = row * tile_height

            if src_x >= src_w or src_y >= src_h:
                continue

            dst_x = (col * stride_x) + padding_x
            dst_y = (row * stride_y) + padding_y

            tile_data = read_pixels(source_doc, src_x, src_y, tile_width, tile_height)
            write_pixels(layer, tile_data, dst_x, dst_y, tile_width, tile_height)

            if anti_bleed and (padding_x > 0 or padding_y > 0):
                _apply_anti_bleed(
                    source_doc, layer,
                    src_x, src_y,
                    dst_x, dst_y,
                    tile_width, tile_height,
                    padding_x, padding_y
                )

    new_doc.refreshProjection()
    app.activeWindow().addView(new_doc)

    if save_kra:
        original_path = source_doc.fileName()
        if original_path:
            folder = os.path.dirname(original_path)
            kra_path = os.path.join(folder, name + ".kra")
            new_doc.setFileName(kra_path)
            new_doc.save()

    return new_doc


def _apply_anti_bleed(source_doc, dest_layer, src_x, src_y, dst_x, dst_y, tile_w, tile_h, pad_x, pad_y):
    bpp = tile_pixel_size(source_doc)

    if pad_y > 0:
        top_row = read_pixels(source_doc, src_x, src_y, tile_w, 1)
        bottom_row = read_pixels(source_doc, src_x, src_y + tile_h - 1, tile_w, 1)
        write_pixels(dest_layer, repeat_row_vertically(top_row, pad_y), dst_x, dst_y - pad_y, tile_w, pad_y)
        write_pixels(dest_layer, repeat_row_vertically(bottom_row, pad_y), dst_x, dst_y + tile_h, tile_w, pad_y)

    if pad_x > 0:
        left_col = read_pixels(source_doc, src_x, src_y, 1, tile_h)
        right_col = read_pixels(source_doc, src_x + tile_w - 1, src_y, 1, tile_h)
        for i in range(1, pad_x + 1):
            write_pixels(dest_layer, left_col,  dst_x - i, dst_y, 1, tile_h)
            write_pixels(dest_layer, right_col, dst_x + tile_w + i - 1, dst_y, 1, tile_h)

    if pad_x > 0 and pad_y > 0:
        corners = [
            (src_x, src_y, dst_x - pad_x,  dst_y - pad_y),
            (src_x + tile_w - 1, src_y, dst_x + tile_w, dst_y - pad_y),
            (src_x, src_y + tile_h - 1, dst_x - pad_x,  dst_y + tile_h),
            (src_x + tile_w - 1, src_y + tile_h - 1, dst_x + tile_w, dst_y + tile_h),
        ]

        for cx, cy, ddx, ddy in corners:
            pixel = read_pixels(source_doc, cx, cy, 1, 1)
            write_pixels(dest_layer, pixel * (pad_x * pad_y), ddx, ddy, pad_x, pad_y)