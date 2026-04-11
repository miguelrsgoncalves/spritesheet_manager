from PyQt5.QtWidgets import QMainWindow, QAction
from .spritesheet_editor import run_padder_dialog

def create_spritesheet_editor_actions(plugin_instance, window, menu):
    main_window: QMainWindow = window.qwindow()

    padder_action = QAction("Padder", main_window)
    padder_action.triggered.connect(run_padder_dialog)
    menu.addAction(padder_action)