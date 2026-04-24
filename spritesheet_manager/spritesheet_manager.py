from krita import Extension, DockWidgetFactory, DockWidgetFactoryBase
from PyQt5.QtWidgets import QMainWindow, QMenu
from .atlas_editor.atlas_editor import create_atlas_editor_actions, setup_atlas_editor_dockers_factory
from .spritesheet_editor.spritesheet_editor import create_spritesheet_editor_actions

class SpritesheetManagerExtension(Extension):
    def __init__(self, parent):
        super().__init__(parent)

    def setup(self):
        setup_atlas_editor_dockers_factory()

    def createActions(self, window):
        main_window: QMainWindow = window.qwindow()

        # Spritesheet Manager menu
        spritesheet_manager_menu: QMenu = QMenu("Spritesheet Manager", main_window)
        main_window.menuBar().addMenu(spritesheet_manager_menu)

        # Atlas Editor submenu
        atlas_editor_submenu: QMenu = spritesheet_manager_menu.addMenu("Atlas Editor")
        create_atlas_editor_actions(self, window, atlas_editor_submenu)

        # Spritesheet Editor submenu
        spritesheet_editor_submenu: QMenu = spritesheet_manager_menu.addMenu("Spritesheet Editor")
        create_spritesheet_editor_actions(self, window, spritesheet_editor_submenu)