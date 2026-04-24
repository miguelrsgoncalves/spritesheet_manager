from krita import Krita, DockWidgetFactory, DockWidgetFactoryBase
from PyQt5.QtWidgets import QMainWindow, QAction
from ..core.widgets import ActiveDocumentWarningMessage
from .widgets.atlas_editor_widget import AtlasEditorDock

def create_atlas_editor_actions(plugin_instance, window, menu):
    main_window: QMainWindow = window.qwindow()

    setup_dockers()
    
    atlas_editor_dock_action: QAction = QAction("Open Dock", main_window)
    atlas_editor_dock_action.triggered.connect(lambda: run_atlas_editor_dock(main_window))
    atlas_editor_dock_action.setToolTip("Open Atlas Editor dock.")
    menu.addAction(atlas_editor_dock_action)

def setup_dockers():
    atlas_editor_docker_factory = DockWidgetFactory(
        AtlasEditorDock.DOCKER_KEY, 
        DockWidgetFactoryBase.DockRight, 
        AtlasEditorDock
    )
    
    Krita.instance().addDockWidgetFactory(atlas_editor_docker_factory)

def run_atlas_editor_dock(main_window):    
    dockers = main_window.dockers()
    for docker in dockers:
        if docker.objectName() == AtlasEditorDock.DOCKER_KEY:
            docker.setVisible(True)
            docker.raise_()
            return

def has_active_document(main_window) -> bool:
    document = Krita.instance().activeDocument()
    if document is not None: return True

    ActiveDocumentWarningMessage(main_window)

    return False