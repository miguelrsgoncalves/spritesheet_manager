from krita import Krita

class AnimationExporter:
    def __init__(self, document):
        self._document = document

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