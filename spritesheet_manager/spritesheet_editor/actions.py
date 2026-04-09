from PyQt5.QtWidgets import QAction
from .spritesheet_editor import run_padder_dialog

def create_spritesheet_editor_actions(extension_instance, window, menu):
    padder_action = QAction("Padder", window)
    padder_action.triggered.connect(run_padder_dialog)
    menu.addAction(padder_action)