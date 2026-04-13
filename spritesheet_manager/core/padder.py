import os
from krita import InfoObject
from PyQt5.QtWidgets import QFileDialog
from .pixel import read_pixels, write_pixels, repeat_row_vertically

EXPORT_FILTERS = (
    "PNG Image (*.png);;"
    "JPEG Image (*.jpg *.jpeg);;"
    "WebP Image (*.webp);;"
    "TIFF Image (*.tiff *.tif);;"
    "BMP Image (*.bmp)"
)

class Padder():
    def __init__(
            self,
            document,
            tile_size: list[int, int],
            grid_size: list[int, int],
            padding_size: list[int, int],
            is_anti_bleed: bool,
            export_name: str,
            is_export_kra: bool,
            is_export_image: bool
    ):
        self._document = document
        self._tile_size = tile_size
        self._grid_size = grid_size
        self._padding_size = padding_size
        self._is_anti_bleed = is_anti_bleed
        self._export_name = export_name
        self._is_export_kra = is_export_kra
        self._is_export_image = is_export_image
    
    def run(self):
        stride_width: int = self._tile_size[0] + (self._padding_size[0] * 2)
        stride_height: int = self._tile_size[1] + (self._padding_size[1] * 2)

        padded_document_width: int = self._grid_size[0] * stride_width
        padded_document_height: int = self._grid_size[1] * stride_height

        padded_document = app.createDocument(
            padded_document_width, padded_document_height,
            self._export_name,
            self._document.colorModel(),
            self._document.colorDepth(),
            self._document.colorProfile(),
            self._document.resolution()
        )

        root_layer = padded_document.root_layerNode()
        for child in root_layer.childNodes():
            root_layer.removeChildNode(child)

        padded_layer = padded_document.createNode("Padded Spritesheet", "paintlayer")
        root_layer.addChildNode(padded_layer, None)

        for row in range(self._grid_size[1]):
            for column in range(self._grid_size[0]):
                source_x: int = column * self._tile_size[0]
                source_y: int = row * self._tile_size[1]
                destination_x: int = (column * stride_width) + self._padding_size[0]
                destination_y: int = (row * stride_height) + self._padding_size[1]

                tile_data = self._document.pixelData(
                    self._document,
                    source_x, source_y,
                    self._tile_size[0], self._tile_size[1]
                
                )
                padded_layer.setPixelData(
                    padded_layer,
                    tile_data,
                    destination_x, destination_y,
                    self._tile_size[0], self._tile_size[1]
                )

                if self._is_anti_bleed and (self._padding_size[0] > 0 or self._padding_size[1] > 0):
                    self.anti_bleed(
                        self._document,
                        padded_layer,
                        source_x, source_y,
                        destination_x, destination_y,
                        self._tile_size[0], self._tile_size[1],
                        self._padding_size[0], self._padding_size[1]
                    )

        padded_document.refreshProjection()

        source_path = document.fileName()
        folder = os.path.direxport_name(source_path) if source_path else ""

        # Only open the document in Krita when keeping the .kra file
        if is_export_kra:
            app.activeWindow().addView(padded_document)
            if folder:
                kra_path = os.path.join(folder, export_name + ".kra")
                padded_document.setFileexport_name(kra_path)
                padded_document.save()

        if is_export_image:
            _export_with_dialog(padded_document, folder, export_name)

        # If not keeping the .kra, close the temporary document
        if not is_export_kra:
            padded_document.close()

        return padded_document

    def _export_with_dialog(self, doc, default_folder, default_export_name):
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
    
    def anti_bleed(self, source_doc, dest_layer, source_x, source_y, dest_x, dest_y,
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