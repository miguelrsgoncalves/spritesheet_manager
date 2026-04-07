import os
from krita import Krita, InfoObject
from PyQt5.QtWidgets import QFileDialog
from .pixel import read_pixels, write_pixels, repeat_row_vertically, get_bytes_per_pixel

EXPORT_FILTERS = (
    "PNG Image (*.png);;"
    "JPEG Image (*.jpg *.jpeg);;"
    "WebP Image (*.webp);;"
    "TIFF Image (*.tiff *.tif);;"
    "BMP Image (*.bmp)"
)

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
    save_kra: bool,
    export_image: bool
):
    app = Krita.instance()

    # Each tile slot is the tile size plus padding on both sides
    stride_x = tile_width + (padding_x * 2)
    stride_y = tile_height + (padding_y * 2)
    new_width = columns * stride_x
    new_height = rows * stride_y

    # New document inherits colour settings from the source
    new_doc = app.createDocument(
        new_width, new_height, name,
        source_doc.colorModel(),
        source_doc.colorDepth(),
        source_doc.colorProfile(),
        source_doc.resolution()
    )

    # Remove the default blank layer Krita adds to every new document
    root = new_doc.rootNode()
    for child in root.childNodes():
        root.removeChildNode(child)

    layer = new_doc.createNode("Padded Spritesheet", "paintlayer")
    root.addChildNode(layer, None)

    source_width = source_doc.width()
    source_height = source_doc.height()

    # Copy each tile from the source into its padded position in the new document
    for row in range(rows):
        for col in range(columns):
            source_x = col * tile_width
            source_y = row * tile_height

            if source_x >= source_width or source_y >= source_height:
                continue

            dest_x = (col * stride_x) + padding_x
            dest_y = (row * stride_y) + padding_y

            tile_data = read_pixels(source_doc, source_x, source_y, tile_width, tile_height)
            write_pixels(layer, tile_data, dest_x, dest_y, tile_width, tile_height)

            if anti_bleed and (padding_x > 0 or padding_y > 0):
                _apply_anti_bleed(
                    source_doc, layer,
                    source_x, source_y,
                    dest_x, dest_y,
                    tile_width, tile_height,
                    padding_x, padding_y
                )

    new_doc.refreshProjection()

    original_path = source_doc.fileName()
    folder = os.path.dirname(original_path) if original_path else ""

    if save_kra:
        app.activeWindow().addView(new_doc)
        if folder:
            kra_path = os.path.join(folder, name + ".kra")
            new_doc.setFileName(kra_path)
            new_doc.save()

    if export_image:
        _export_with_dialog(new_doc, folder, name)

    if not save_kra:
        new_doc.close()

    return new_doc


def _export_with_dialog(doc, default_folder, default_name):
    default_path = os.path.join(default_folder, default_name + ".png") if default_folder else default_name + ".png"

    export_path, _ = QFileDialog.getSaveFileName(
        None,
        "Export Spritesheet",
        default_path,
        EXPORT_FILTERS
    )

    if not export_path:
        return

    doc.exportImage(export_path, InfoObject())


def _apply_anti_bleed(source_doc, dest_layer, source_x, source_y, dest_x, dest_y, tile_width, tile_height, padding_x, padding_y):

    # Top and bottom edge bands
    if padding_y > 0:
        top_row = read_pixels(source_doc, source_x, source_y, tile_width, 1)
        bottom_row = read_pixels(source_doc, source_x, source_y + tile_height - 1, tile_width, 1)
        write_pixels(dest_layer, repeat_row_vertically(top_row, padding_y),
                     dest_x, dest_y - padding_y, tile_width, padding_y)
        write_pixels(dest_layer, repeat_row_vertically(bottom_row, padding_y),
                     dest_x, dest_y + tile_height, tile_width, padding_y)

    # Left and right edge bands
    if padding_x > 0:
        left_col = read_pixels(source_doc, source_x, source_y, 1, tile_height)
        right_col = read_pixels(source_doc, source_x + tile_width - 1, source_y, 1, tile_height)
        for i in range(1, padding_x + 1):
            write_pixels(dest_layer, left_col, dest_x - i, dest_y, 1, tile_height)
            write_pixels(dest_layer, right_col, dest_x + tile_width + i - 1, dest_y, 1, tile_height)

    # Corner blocks filled with the single nearest corner pixel repeated
    if padding_x > 0 and padding_y > 0:
        corners = [
            (source_x, source_y, dest_x - padding_x, dest_y - padding_y),
            (source_x + tile_width - 1, source_y, dest_x + tile_width, dest_y - padding_y),
            (source_x, source_y + tile_height - 1, dest_x - padding_x, dest_y + tile_height),
            (source_x + tile_width - 1, source_y + tile_height - 1, dest_x + tile_width, dest_y + tile_height),
        ]

        for corner_source_x, corner_source_y, corner_dest_x, corner_dest_y in corners:
            pixel = read_pixels(source_doc, corner_source_x, corner_source_y, 1, 1)
            write_pixels(dest_layer, pixel * (padding_x * padding_y), corner_dest_x, corner_dest_y, padding_x, padding_y)