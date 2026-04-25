from krita import Krita, DockWidget
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QDialog, QGroupBox, QGridLayout, QHBoxLayout, QVBoxLayout, QLabel, QSpinBox, QCheckBox, QLineEdit, QDialogButtonBox
from ...core.serializer import Serializer

MAX_INT: int = 2147483647

class AtlasEditorWidget(QWidget):
    WIDGET_KEY: str = "ATLAS_EDITOR"
    WIDGET_DESCRIPTION: str = "Atlas Editor settings"

    DEFAULTS: dict[str, any] = {
    }

    def __init__(self, parent, document):
        super().__init__(parent)

        self._document = document

        layout: QVBoxLayout = QVBoxLayout()

        layout.addWidget(self._build_options_group)

        self.setLayout(layout)

        self._load_state()

        self.refresh_ui()

    #region functions

    def run_renderer(self):
        pass
    
    def _get_renderer_arguments(self) -> dict[str, any]:
        return {
            
        }

    def refresh_ui(self):
        pass
    
    #endregion

    #region groups

    def _build_options_group(self):
        group : QGroupBox= QGroupBox("")
        return group

    #endregion

    #region state

    def load_state(self):
        state: dict[str, any] = Serializer.load_state(self._document, self.WIDGET_KEY)
        self._set_state(state)
    
    def _set_state(self, state):
        self.refresh_ui()

    def save_state(self):
        data: dict[str, any] = self._get_state()
        Serializer.save_state(self._document, self.WIDGET_KEY, data, self.WIDGET_DESCRIPTION)
    
    def _get_state(self) -> dict[str, any]:
        return {

        }
    
    #endregion

    #region signalswd

    def _on_renderer_argument_changed(self):
        self.refresh_ui()

    #endregion

class AtlasEditorDocker(DockWidget):
    DOCKER_KEY: str = "ATLAS_EDITOR_DOCKER"
    
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("Atlas Editor")

        document = Krita.instance().activeDocument()
        
        self._atlas_editor_widget: AtlasEditorWidget = AtlasEditorWidget(self, document)
        self.setWidget(self._atlas_editor_widget)

    def canvasChanged(self, canvas):
        self._atlas_editor_widget._document = Krita.instance().activeDocument()
        self._atlas_editor_widget._load_state()