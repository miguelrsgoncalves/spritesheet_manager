import os
from krita import Krita
from ..core.padder import create_padded_document

class EditorController:

    def run_padding_dialog(self):
        app = Krita.instance()
        doc = app.activeDocument()
        if not doc:
            return

        from .ui.panels.padder_panel import PaddingDialog

        original_path = doc.fileName()
        if original_path:
            base_name = os.path.splitext(os.path.basename(original_path))[0]
            default_name = base_name + "_padded"
        else:
            default_name = doc.name() + "_padded"

        result = PaddingDialog(doc.width(), doc.height(), default_name).run()
        if result is None:
            return

        create_padded_document(
            source_doc=doc,
            tile_width=result["tile_width"],
            tile_height=result["tile_height"],
            padding_x=result["padding_x"],
            padding_y=result["padding_y"],
            columns=result["columns"],
            rows=result["rows"],
            anti_bleed=result["anti_bleed"],
            name=result["name"],
            save_kra=result["save_kra"],
            export_image=result["export_image"]
        )

    def run_padding_from_widget(self, values: dict):
        app = Krita.instance()
        doc = app.activeDocument()
        if not doc:
            return
        create_padded_document(source_doc=doc, **values)