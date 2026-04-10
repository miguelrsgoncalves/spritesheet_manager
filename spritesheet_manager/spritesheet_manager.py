from krita import Extension
from PyQt5.QtWidgets import QMenu
from .atlas_editor.actions import create_atlas_editor_actions
from .spritesheet_editor.actions import create_spritesheet_editor_actions

PLUGIN_VERSION: str = "1.0.0"

class SpritesheetManagerExtension(Extension):
    def __init__(self, parent):
        super().__init__(parent)

    def setup(self):
        pass

    def createActions(self, window):
        # Spritesheet Manager menu
        spritesheet_manager_menu: QMenu = QMenu("Spritesheet Manager", window)
        window.menuBar().addMenu(spritesheet_manager_menu)

        # Atlas Editor submenu
        atlas_editor_submenu: QMenu = spritesheet_manager_menu.addMenu("Atlas Editor")
        create_atlas_editor_actions(self, window, atlas_editor_submenu)

        # Spritesheet Editor submenu
        spritesheet_editor_submenu: QMenu = spritesheet_manager_menu.addMenu("Spritesheet Editor")
        create_spritesheet_editor_actions(self, window, spritesheet_editor_submenu)