import os
from krita import InfoObject
from PyQt5.QtWidgets import QFileDialog
from ...core.pixel import read_pixels, write_pixels, repeat_row_vertically

EXPORT_FILTERS = (
    "PNG Image (*.png);;"
    "JPEG Image (*.jpg *.jpeg);;"
    "WebP Image (*.webp);;"
    "TIFF Image (*.tiff *.tif);;"
    "BMP Image (*.bmp)"
)

class Padder():
    @staticmethod
    def run(
        document,
        tile_size: list[int, int],
        grid_size: list[int, int],
        padding_size: list[int, int],
        anti_bleed: bool,
        export_name: str,
        export_kra: bool,
        export_image: bool
    ):

        stride_width = tile_size[0] + (padding_size[0] * 2)
        stride_height = tile_size[1] + (padding_size[1] * 2)

        padded_document_width = grid_size[0] * stride_width
        padded_document_height = grid_size[1] * stride_height

        # New document inherits colour settings from the source
        new_kra = app.createDocument(
            padded_document_width, padded_document_height, export_name,
            document.colorModel(),
            document.colorDepth(),
            document.colorProfile(),
            document.resolution()
        )

        # Remove the default blank layer Krita adds to every new document
        root = new_kra.rootNode()
        for child in root.childNodes():
            root.removeChildNode(child)

        layer = new_kra.createNode("Padded Spritesheet", "paintlayer")
        root.addChildNode(layer, None)

        source_width = document.width()
        source_height = document.height()

        # Copy each tile from the source into its padded position in the new document
        for row in range(grid_size[1]):
            for col in range(grid_size[0]):
                source_x = col * tile_size[0]
                source_y = row * tile_size[1]

                if source_x >= source_width or source_y >= source_height:
                    continue

                dest_x = (col * stride_width) + padding_size[0]
                dest_y = (row * stride_height) + padding_size[1]

                tile_data = read_pixels(document, source_x, source_y, tile_size[0], tile_size[1])
                write_pixels(layer, tile_data, dest_x, dest_y, tile_size[0], tile_size[1])

                if anti_bleed and (padding_size[0] > 0 or padding_size[1] > 0):
                    anti_bleed(
                        document, layer,
                        source_x, source_y,
                        dest_x, dest_y,
                        tile_size[0], tile_size[1],
                        padding_size[0], padding_size[1]
                    )

        new_kra.refreshProjection()

        original_path = document.fileexport_name()
        folder = os.path.direxport_name(original_path) if original_path else ""

        # Only open the document in Krita when keeping the .kra file
        if export_kra:
            app.activeWindow().addView(new_kra)
            if folder:
                kra_path = os.path.join(folder, export_name + ".kra")
                new_kra.setFileexport_name(kra_path)
                new_kra.save()

        if export_image:
            _export_with_dialog(new_kra, folder, export_name)

        # If not keeping the .kra, close the temporary document
        if not export_kra:
            new_kra.close()

        return new_kra

    @staticmethod
    def _export_with_dialog(doc, default_folder, default_export_name):
        default_path = os.path.join(default_folder, default_export_name + ".png") if default_folder else default_export_name + ".png"

        export_path, _ = QFileDialog.getSaveFileexport_name(
            None,
            "Export Spritesheet",
            default_path,
            EXPORT_FILTERS
        )

        if not export_path:
            return

        doc.exportImage(export_path, InfoObject())
    
    @staticmethod
    def anti_bleed(source_doc, dest_layer, source_x, source_y, dest_x, dest_y,
                        tile_size[0], tile_size[1], padding_size[0], padding_size[1]):

        # Top and bottom edge bands
        if padding_size[1] > 0:
            top_row = read_pixels(source_doc, source_x, source_y, tile_size[0], 1)
            bottom_row = read_pixels(source_doc, source_x, source_y + tile_size[1] - 1, tile_size[0], 1)
            write_pixels(dest_layer, repeat_row_vertically(top_row, padding_size[1]), dest_x, dest_y - padding_size[1], tile_size[0], padding_size[1])
            write_pixels(dest_layer, repeat_row_vertically(bottom_row, padding_size[1]), dest_x, dest_y + tile_size[1], tile_size[0], padding_size[1])

        # Left and right edge bands
        if padding_size[0] > 0:
            left_col = read_pixels(source_doc, source_x, source_y, 1, tile_size[1])
            right_col = read_pixels(source_doc, source_x + tile_size[0] - 1, source_y, 1, tile_size[1])
            for i in range(1, padding_size[0] + 1):
                write_pixels(dest_layer, left_col, dest_x - i, dest_y, 1, tile_size[1])
                write_pixels(dest_layer, right_col, dest_x + tile_size[0] + i - 1, dest_y, 1, tile_size[1])

        # Corner blocks filled with the single nearest corner pixel repeated
        if padding_size[0] > 0 and padding_size[1] > 0:
            corners = [
                (source_x, source_y, dest_x - padding_size[0], dest_y - padding_size[1]),
                (source_x + tile_size[0] - 1, source_y, dest_x + tile_size[0], dest_y - padding_size[1]),
                (source_x, source_y + tile_size[1] - 1, dest_x - padding_size[0], dest_y + tile_size[1]),
                (source_x + tile_size[0] - 1, source_y + tile_size[1] - 1, dest_x + tile_size[0], dest_y + tile_size[1]),
            ]

            for corner_source_x, corner_source_y, corner_dest_x, corner_dest_y in corners:
                pixel = read_pixels(source_doc, corner_source_x, corner_source_y, 1, 1)
                write_pixels(dest_layer, pixel * (padding_size[0] * padding_size[1]), corner_dest_x, corner_dest_y, padding_size[0], padding_size[1])