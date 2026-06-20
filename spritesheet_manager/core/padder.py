import os
from krita import Krita, InfoObject
from PyQt5.QtGui import QImage

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
    
    def run(self, is_preview: bool = False, preview_size: list[int] = [], quality_scale: int = 30):
        krita = Krita.instance()

        #region preview_scaling

        if is_preview:
            self._document = self._document.clone()
            
            scale_factor: float = quality_scale / 100.0
            self._document.scaleImage(
                int(self._document.width() * scale_factor), 
                int(self._document.height() * scale_factor), 
                16, 16,
                "Box"
            )
            
            self._tile_size = [max(1, int(x * scale_factor)) for x in self._tile_size]
            self._padding_size = [int(x * scale_factor) for x in self._padding_size]

        #endregion

        stride_width: int = self._tile_size[0] + (self._padding_size[0] * 2)
        stride_height: int = self._tile_size[1] + (self._padding_size[1] * 2)

        padded_document_width: int = self._grid_size[0] * stride_width
        padded_document_height: int = self._grid_size[1] * stride_height

        padded_document = krita.createDocument(
            padded_document_width, padded_document_height,
            self._export_name,
            self._document.colorModel(),
            self._document.colorDepth(),
            self._document.colorProfile(),
            self._document.resolution()
        )

        root_layer = padded_document.rootNode()
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
                    source_x, source_y,
                    self._tile_size[0], self._tile_size[1]
                )

                padded_layer.setPixelData(
                    tile_data,
                    destination_x, destination_y,
                    self._tile_size[0], self._tile_size[1]
                )

                if self._is_anti_bleed and (self._padding_size[0] > 0 or self._padding_size[1] > 0):
                    self.apply_anti_bleed(
                        self._document,
                        padded_layer,
                        source_x, source_y,
                        destination_x, destination_y
                    )

        padded_document.refreshProjection()

        if is_preview:
            preview_image: QImage = padded_document.thumbnail(preview_size[0], preview_size[1])

            preview_arguments: dict[str, any] = {
                "export_size": [
                    padded_document_height,
                    padded_document_width
                ],
            }

            padded_document.close()
            return preview_image, preview_arguments
        
        #region export

        source_path: str = self._document.fileName()
        source_folder: str = os.path.dirname(source_path)

        if self._is_export_kra:
            krita.activeWindow().addView(padded_document)
            if source_folder:
                kra_path: str = os.path.join(source_folder, self._export_name + ".kra")
                padded_document.setFileName(kra_path)
                padded_document.save()

        if self._is_export_image:
            image_path: str = os.path.join(source_folder, self._export_name + ".png")
            padded_document.exportImage(image_path, InfoObject())
        
        #endregion

        if not self._is_export_kra:
            padded_document.close()

        return padded_document
    
    #region anti_bleed

    def apply_anti_bleed(self, source_document, destination_layer, source_x, source_y, destination_x, destination_y):
        if self._padding_size[0] > 0:
            left_column = source_document.pixelData(source_x, source_y, 1, self._tile_size[1])
            right_column = source_document.pixelData(source_x + self._tile_size[0] - 1, source_y, 1, self._tile_size[1])

            for i in range(1, self._padding_size[0] + 1):
                destination_layer.setPixelData(left_column, destination_x - i, destination_y, 1, self._tile_size[1])
                destination_layer.setPixelData(right_column, destination_x + self._tile_size[0] + i - 1, destination_y, 1, self._tile_size[1])

        if self._padding_size[1] > 0:
            top_row = source_document.pixelData(source_x, source_y, self._tile_size[0], 1)
            bottom_row = source_document.pixelData(source_x, source_y + self._tile_size[1] - 1, self._tile_size[0], 1)

            for i in range(1, self._padding_size[1] + 1):
                destination_layer.setPixelData(top_row, destination_x, destination_y - i, self._tile_size[0], 1)
                destination_layer.setPixelData(bottom_row, destination_x, destination_y + self._tile_size[1] + i - 1, self._tile_size[0], 1)

        if self._padding_size[0] > 0 and self._padding_size[1] > 0:
            corners = [
                (source_x, source_y, destination_x - self._padding_size[0], destination_y - self._padding_size[1]),
                (source_x + self._tile_size[0] - 1, source_y, destination_x + self._tile_size[0], destination_y - self._padding_size[1]),
                (source_x, source_y + self._tile_size[1] - 1, destination_x - self._padding_size[0], destination_y + self._tile_size[1]),
                (source_x + self._tile_size[0] - 1, source_y + self._tile_size[1] - 1, destination_x + self._tile_size[0], destination_y + self._tile_size[1]),
            ]

            for corner_source_x, corner_source_y, corner_destination_x, corner_destination_y in corners:
                pixel = source_document.pixelData(corner_source_x, corner_source_y, 1, 1)
                
                corner_block = pixel * (self._padding_size[0] * self._padding_size[1])

                destination_layer.setPixelData(corner_block, corner_destination_x, corner_destination_y, self._padding_size[0], self._padding_size[1])
    
    #endregion