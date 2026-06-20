from krita import Krita, DockWidgetFactory, DockWidgetFactoryBase
from PyQt5.QtWidgets import QMainWindow, QAction
from ..core.widgets import ActiveDocumentWarningMessage
from .widgets.atlas_editor_widget import AtlasEditorDocker

def create_atlas_editor_actions(plugin_instance, window, menu):
    main_window: QMainWindow = window.qwindow()

    atlas_editor_docker_action: QAction = QAction("Open Docker", main_window)
    atlas_editor_docker_action.triggered.connect(lambda: run_atlas_editor_docker(main_window))
    atlas_editor_docker_action.setToolTip("Open Atlas Editor docker.")
    menu.addAction(atlas_editor_docker_action)

def setup_atlas_editor_dockers_factory():
    atlas_editor_docker_factory = DockWidgetFactory(
        AtlasEditorDocker.DOCKER_KEY,
        DockWidgetFactoryBase.DockRight,
        AtlasEditorDocker
    )
    
    Krita.instance().addDockWidgetFactory(atlas_editor_docker_factory)

def run_atlas_editor_docker(main_window):
    if not has_active_document(main_window): return
    
    window = Krita.instance().activeWindow()
    if not window: return

    for docker in window.dockers():
        if docker.objectName() == AtlasEditorDocker.DOCKER_KEY:
            docker.setVisible(True)
            docker.raise_()
            return

def has_active_document(main_window) -> bool:
    document = Krita.instance().activeDocument()
    if document is not None: return True

    ActiveDocumentWarningMessage(main_window)

    return False