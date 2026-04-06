from krita import Krita
from PyQt5.QtWidgets import QMenu, QAction
from .spritesheet_editor.editor_controller import EditorController

_controller = None

def _get_controller():
    global _controller
    if _controller is None:
        _controller = EditorController()
    return _controller

def register_actions(window):
    main_window = window.qwindow()
    menu_bar = main_window.menuBar()

    # Manager menu
    ssm_menu = QMenu("Spritesheet Manager", main_window)
    menu_bar.addMenu(ssm_menu)

    # Atlas Manager submenu
    atlas_menu = ssm_menu.addMenu("Atlas Manager")
    
    atlas_placeholder = QAction("Open Atlas Manager", main_window)
    atlas_placeholder.setEnabled(False)
    atlas_menu.addAction(atlas_placeholder)

    # Spritesheet Editor submenu
    editor_menu = ssm_menu.addMenu("Sheet Editor")

    padding_action = QAction("Add Padding", main_window)
    padding_action.triggered.connect(_get_controller().run_padding_dialog)
    editor_menu.addAction(padding_action)