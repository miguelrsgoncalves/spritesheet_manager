import os
from krita import Krita, InfoObject
from enum import Enum

PREVIEW_RESOLUTION_SCALING = 0.15

class AnimationExporter:
    class PackingType(Enum):
        HORIZONTAL = 1
        VERTICAL = 2
        SQUARE = 3
    

    def __init__(
            self,
            document,
            start_frame: int,
            end_frame: int,
            frame_step: int,
            columns: int,
            rows: int,
            packing_type: PackingType,
            export_name: str,
            is_export_kra: bool,
            is_export_image: bool,
    ):
        self._document = document
        self._start_frame = start_frame
        self._end_frame = end_frame
        self._frame_step = frame_step
        self._columns = columns
        self._rows = rows
        self._packing_type = packing_type
        self._export_name = export_name
        self._is_export_kra = is_export_kra
        self._is_export_image = is_export_image

    def run(self, is_preview: bool = False):
        krita = Krita.instance()

        #region preview_scaling

        if is_preview:
            self._document = self._document.clone()
            
            self._document.scaleImage(
                int(self._document.width() * PREVIEW_RESOLUTION_SCALING), 
                int(self._document.height() * PREVIEW_RESOLUTION_SCALING), 
                16, 16,
                "Box"
            )

        #endregion

        frame_width: int = self._document.width()
        frame_height: int = self._document.height()
        
        animation_document_width: int = frame_width * self._columns
        animation_document_height: int = frame_height * self._rows
        
        animation_document = krita.createDocument(
            animation_document_width, animation_document_height,
            self._export_name,
            self._document.colorModel(),
            self._document.colorDepth(),
            self._document.colorProfile(),
            self._document.resolution(),
        )
        
        root_layer = animation_document.rootNode()
        for child in root_layer.childNodes():
            root_layer.removeChildNode(child)

        animation_layer = animation_document.createNode("Animation Spritesheet", "paintlayer")
        root_layer.addChildNode(animation_layer, None)

        self._document.setBatchmode(True)
        animation_document.setBatchmode(True)

        frame_list: list[int] = list(range(self._start_frame, self._end_frame + 1, self._frame_step))

        for index, frame_index in enumerate(frame_list):
            self._document.setCurrentTime(frame_index)
            self._document.waitForDone()
            
            pixel_data = self._document.pixelData(0, 0, frame_width, frame_height)
            
            destination_x: int = 0
            destination_y: int = 0
            
            match self._packing_type:
                case self.PackingType.HORIZONTAL | self.PackingType.SQUARE:
                    destination_x = (index % self._columns) * frame_width
                    destination_y = (index // self._columns) * frame_height
                case self.PackingType.VERTICAL:
                    destination_x = (index // self._rows) * frame_width
                    destination_y = (index % self._rows) * frame_height
            
            animation_layer.setPixelData(pixel_data, destination_x, destination_y, frame_width, frame_height)

        animation_document.refreshProjection()

        if is_preview:
            return animation_document, animation_document_width, animation_document_height
        
        #region export

        source_path: str = self._document.fileName()
        source_folder: str = os.path.dirname(source_path)

        if self._is_export_kra:
            krita.activeWindow().addView(animation_document)
            if source_folder:
                kra_path: str = os.path.join(source_folder, self._export_name + ".kra")
                animation_document.setFileName(kra_path)
                animation_document.save()

        if self._is_export_image:
            image_path: str = os.path.join(source_folder, self._export_name + ".png")
            animation_document.exportImage(image_path, InfoObject())
        
        #endregion
            
        self._document.setBatchmode(False)
        
        if not self._is_export_kra:
            animation_document.close()
            animation_document.setBatchmode(False)