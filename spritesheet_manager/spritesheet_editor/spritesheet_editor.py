import os
from krita import Krita
from PyQt5.QtWidgets import QMainWindow, QAction, QMessageBox
from ..core.widgets import ActiveDocumentWarningMessage
from .widgets.padder_widget import PadderDialog
from .widgets.animation_exporter_widget import AnimationExporterDialog

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
    if not has_active_document(main_window): return
    PadderDialog(main_window)

def run_animation_exporter_dialog(main_window):
    if not has_active_document(main_window): return
    AnimationExporterDialog(main_window)

def has_active_document(main_window) -> bool:
    document = Krita.instance().activeDocument()
    if document is not None: return True

    ActiveDocumentWarningMessage(main_window)

    return False
