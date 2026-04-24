from krita import Krita
from PyQt5.QtWidgets import QMainWindow, QAction, QMessageBox
from ..core.widgets import ActiveDocumentWarningMessage

def create_spritesheet_editor_actions(plugin_instance, window, menu):
    main_window: QMainWindow = window.qwindow()

    padder_action: QAction = QAction("Padder", main_window)
    padder_action.triggered.connect(lambda: run_padder_dialog(main_window))
    padder_action.setToolTip("Add padding to a spritesheet.")
    menu.addAction(padder_action)

    animation_exporter_action: QAction = QAction("Animation Exporter", main_window)
    animation_exporter_action.triggered.connect(lambda: run_animation_exporter_dialog(main_window))
    animation_exporter_action.setToolTip("Export an animation as a spritesheet.")
    menu.addAction(animation_exporter_action)

def run_padder_dialog(main_window):
    if not has_active_document(): return
    PadderDialog(main_window)

def run_animation_exporter_dialog(main_window):
    if not has_active_document(): return
    AnimationExporterDialog(main_window)

def has_active_document(main_window) -> bool:
    document = Krita.instance().activeDocument()
    if document is not None: return True

    ActiveDocumentWarningMessage(main_window)

    return False





def create_atlas_editor_actions(plugin_instance, window, menu):
    atlas_action = QAction("Show Atlas Docker", window)
    atlas_action.triggered.connect(lambda: _show_atlas_docker(window))
    menu.addAction(atlas_action)

def _show_atlas_docker(main_window):
    for docker in main_window.findChildren(object):
        if hasattr(docker, "windowTitle") and docker.windowTitle() == "Atlas Editor":
            docker.setVisible(True)
            docker.raise_()
            return
        

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