import os
from krita import Krita
from PyQt5.QtWidgets import QMainWindow, QAction
from .widgets.padder_widget import PadderDialog

def create_spritesheet_editor_actions(plugin_instance, window, menu):
    main_window: QMainWindow = window.qwindow()

    padder_action = QAction("Padder", main_window)
    padder_action.triggered.connect(run_padder_dialog)
    menu.addAction(padder_action)

def run_padder_dialog():
    if not has_active_document: return
    PadderDialog()

def has_active_document() -> bool:
    return True if Krita.instance().activeDocument() else False