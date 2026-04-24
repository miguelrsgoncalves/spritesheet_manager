from krita import Krita, DockWidget
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QDialog, QGroupBox, QGridLayout, QHBoxLayout, QVBoxLayout, QLabel, QSpinBox, QCheckBox, QLineEdit, QDialogButtonBox
from ...core.serializer import Serializer

class AtlasEditorWidget:
    WIDGET_KEY: str = "ATLAS_EDITOR"
    
    def __init__(self, parent, document):
        super().__init__(parent)

        self._layout: QVBoxLayout = QVBoxLayout()
        
        self._document_label: QLabel = QLabel("No Active Document")
        self._document_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self._layout.addWidget(self._document_label)
        self.setLayout(self._layout)
        
        self.refresh_ui()
    
    def refresh_ui(self):
        document = Krita.instance().activeDocument()
        if document:
            self._document_label.setText(f"Active Document: {document.name()}")
        else:
            self._document_label.setText("No Active Document")

class AtlasEditorDocker(DockWidget):
    DOCKER_KEY: str = "ATLAS_EDITOR_DOCKER"
    
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("Atlas Editor")
        
        self._widget: AtlasEditorWidget = AtlasEditorWidget(self)
        self.setWidget(self._widget)

    def canvasChanged(self, canvas):
        self._widget.refresh_ui()