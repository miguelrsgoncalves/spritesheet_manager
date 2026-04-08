import os
from krita import Krita
from .core.padder import run_padder
from ..core.serialization import get_padder_state, save_padder_state

class SpritesheetEditorController:

    def run_padder_dialog(self):
        app = Krita.instance()
        doc = app.activeDocument()

        if not doc: return

        from .ui.panels.padder_panel import PadderDialog

        original_path = doc.fileName()
        if original_path:
            base_name = os.path.splitext(os.path.basename(original_path))[0]
            default_name = base_name + "_padded"
        else:
            default_name = doc.name() + "_padded"

        # Load State
        saved_state = get_padder_state(doc)

        result = PadderDialog(doc.width(), doc.height(), default_name, saved_state).run()

        if result is None: return

        # Save State
        state_to_save = {k: v for k, v in result.items() if k != "name"}
        save_padder_state(doc, state_to_save)

        run_padder(source_doc=doc, **result)

    def run_padder_from_widget(self, values):
        app = Krita.instance()
        doc = app.activeDocument()

        if not doc: return

        state_to_save = {k: v for k, v in values.items() if k != "name"}
        save_padder_state(doc, state_to_save)

        run_padder(source_doc=doc, **values)