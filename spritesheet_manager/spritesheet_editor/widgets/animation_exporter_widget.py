from krita import Krita
from PyQt5.QtWidgets import QWidget
from ...core.animation_exporter import AnimationExporter

class AnimationExporterWidget(QWidget):
    def __init__(self, document):
        super().__init__()
        self._document = document

class AnimationExporterDialog(QDialog):
    def __init__(self):
        super().__init__()
        pass