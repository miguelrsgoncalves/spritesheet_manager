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

    def run(self):
        if not self._document: return
        
        animation_document_width: int = self._document.width() * self._columns
        animation_document_height: int = self._document.height() * self._rows
        
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