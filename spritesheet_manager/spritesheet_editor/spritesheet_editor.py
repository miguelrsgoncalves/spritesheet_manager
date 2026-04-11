import os
from krita import Krita
from .widgets.padder_widget import PadderDialog

def run_padder_dialog():
    if not has_active_document: return
    PadderDialog()

def has_active_document() -> bool:
    return True if Krita.instance().activeDocument() else False