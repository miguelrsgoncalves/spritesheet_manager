import os
from krita import Krita
from PyQt5.QtWidgets import QMainWindow, QAction, QMessageBox
from .widgets.padder_widget import PadderDialog
from .widgets.animation_exporter_widget import AnimationExporterDialog

def create_spritesheet_editor_actions(plugin_instance, window, menu):
    main_window: QMainWindow = window.qwindow()

    padder_action: QAction = QAction("Padder", main_window)
    padder_action.triggered.connect(run_padder_dialog)
    padder_action.setToolTip("Add padding to a spritesheet.")
    menu.addAction(padder_action)

    animation_exporter_action: QAction = QAction("Animation Exporter", main_window)
    animation_exporter_action.triggered.connect(run_animation_exporter_dialog)
    animation_exporter_action.setToolTip("Export an animation as a spritesheet.")
    menu.addAction(animation_exporter_action)

def run_padder_dialog():
    if not has_active_document(): return
    PadderDialog()

def run_animation_exporter_dialog():
    if not has_active_document(): return
    AnimationExporterDialog()

def has_active_document() -> bool:
    document = Krita.instance().activeDocument()
    if document is not None: return True
    
    warning_message: QMessageBox = QMessageBox()
    warning_message.setIcon(QMessageBox.Warning)
    warning_message.setText("No Active Document Found!")
    warning_message.setInformativeText("You need to have a document open to use the Spritesheet Manager tools!")
    warning_message.setWindowTitle("Spritesheet Manager")
    warning_message.setStandardButtons(QMessageBox.Ok)
    warning_message.exec_()
    
    return False
