import os
from krita import Krita
from .core.padder import run_padder
from .ui.widgets.padder import PadderDialog

def run_padder_dialog():
    krita = Krita.instance()
    document = krita.activeDocument()
    if not document: return

    padder_arguments = PadderDialog(document).run()
    if padder_arguments is None: return

    run_padder(document=document, **padder_arguments)