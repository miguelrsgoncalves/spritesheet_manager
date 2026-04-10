import os
from krita import Krita
from .ui.widgets.padder import PadderDialog

def run_padder_dialog():
    krita = Krita.instance()
    document = krita.activeDocument()
    if not document: return
    PadderDialog()