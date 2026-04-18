from krita import Krita
from PyQt5.QtWidgets import QMainWindow, QAction, QMessageBox
from .models.atlas_model import AtlasModel
from .states.atlas_state import load_atlas_state, save_atlas_state

class AtlasEditor:

    def __init__(self):
        self._model = AtlasModel()

    def get_model(self):
        return self._model

    def load_from_document(self, doc):
        state = load_atlas_state(doc)
        if state:
            self._model = AtlasModel.from_dict(state)
        else:
            self._model = AtlasModel()

    def save_to_document(self, doc):
        if doc:
            save_atlas_state(doc, self._model.to_dict())

    def add_grid(self, doc):
        grid = self._model.add_grid()
        self.save_to_document(doc)
        return grid

    def remove_grid(self, index, doc):
        self._model.remove_grid(index)
        self.save_to_document(doc)

    def on_grid_changed(self, doc):
        self.save_to_document(doc)

def has_active_document() -> bool:
    document = Krita.instance().activeDocument()
    if document is not None: return True
    
    warning_message: QMessageBox = QMessageBox()
    warning_message.setIcon(QMessageBox.Warning)
    warning_message.setText("No Active Document Found!")
    warning_message.setInformativeText("You need to have a document open to use the Spritesheet Manager tools!")
    warning_message.setWindowTitle("Spritesheet Manager")
    warning_message.setStandardButtons(QMessageBox.Ok)
    warning_message.exec_()
    
    return False