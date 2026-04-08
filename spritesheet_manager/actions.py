from krita import Krita
from PyQt5.QtWidgets import QMenu, QAction
from .spritesheet_editor.spritesheet_editor_controller import SpritesheetEditorController

_editor_controller = None

def _get_editor_controller():
    global _editor_controller
    if _editor_controller is None:
        _editor_controller = SpritesheetEditorController()
    return _editor_controller

def register_actions(window):
    main_window = window.qwindow()
    menu_bar = main_window.menuBar()

    # Spritesheet Manager menu
    ssm_menu = QMenu("Spritesheet Manager", main_window)
    menu_bar.addMenu(ssm_menu)

    # Atlas Editor submenu
    atlas_menu = ssm_menu.addMenu("Atlas Editor")
    open_atlas_action = QAction("Show Atlas Docker", main_window)
    open_atlas_action.triggered.connect(lambda: _show_atlas_docker(window))
    atlas_menu.addAction(open_atlas_action)

    # Spritesheet Editor submenu
    editor_menu = ssm_menu.addMenu("Spritesheet Editor")
    padding_action = QAction("Padder", main_window)
    padding_action.triggered.connect(_get_editor_controller().run_padder_dialog)
    editor_menu.addAction(padding_action)

def _show_atlas_docker(window):
    docker = next(
        (d for d in window.qwindow().findChildren(object) if hasattr(d, 'windowTitle') and d.windowTitle() == "Atlas Editor"),
        None
    )
    if docker:
        docker.setVisible(True)