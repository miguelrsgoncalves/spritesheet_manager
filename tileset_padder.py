import os
from krita import Krita, Extension
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QSpinBox, QCheckBox, QPushButton, QLineEdit
)

class TilesetPadder(Extension):

    def __init__(self, parent):
        super().__init__(parent)

    def setup(self):
        pass

    def createActions(self, window):
        action = window.createAction("tileset_padder", "Add padding to tileset", "tools/scripts")
        action.triggered.connect(self.run)

    def run(self):
        app = Krita.instance()
        doc = app.activeDocument()

        if not doc:
            return

        orig_width = doc.width()
        orig_height = doc.height()

        orig_path = doc.fileName()
        if orig_path:
            folder = os.path.dirname(orig_path)
            base = os.path.splitext(os.path.basename(orig_path))[0]
            new_name = base + "_padded"
        else:
            folder = ""
            new_name = doc.name() + "_padded"

        result = self.openDialog(orig_width, orig_height, new_name)
        if result is None:
            return

        tile_size, padding, columns, rows, anti_bleed, name = result

        pixel_bytes = doc.pixelData(0, 0, orig_width, orig_height)

        new_width = columns * (tile_size + (padding * 2))
        new_height = rows * (tile_size + (padding * 2))
        
        if new_width == 0: new_width = orig_width
        if new_height == 0: new_height = orig_height

        new_doc = app.createDocument(
            new_width,
            new_height,
            name,
            doc.colorModel(),
            doc.colorDepth(),
            doc.colorProfile(),
            doc.resolution()
        )

        new_root = new_doc.rootNode()
        for child in new_root.childNodes():
            new_root.removeChildNode(child)

        new_layer = new_doc.createNode("Padded Tileset", "paintlayer")
        new_root.addChildNode(new_layer, None)

        new_layer.setPixelData(pixel_bytes, 0, 0, orig_width, orig_height)

        new_doc.refreshProjection()
        app.activeWindow().addView(new_doc)

        if folder:
            save_path = os.path.join(folder, name + ".kra")
            new_doc.setFileName(save_path)
            new_doc.save()

    def openDialog(self, width, height, default_name):
        dlg = QDialog()
        dlg.setWindowTitle("Tileset Padder — Add padding to tileset")

        layout = QVBoxLayout()

        # Tile Size
        tile_row = QHBoxLayout()
        tile_label = QLabel("Tile size")
        tile_size = QSpinBox()
        tile_size.setValue(64)
        tile_size.setMaximum(999999)
        tile_row.addWidget(tile_label)
        tile_row.addWidget(tile_size)
        layout.addLayout(tile_row)

        # Padding
        padding_row = QHBoxLayout()
        padding_label = QLabel("Padding")
        padding = QSpinBox()
        padding.setValue(int(tile_size.value() / 8))
        padding.setMaximum(999999)
        padding_row.addWidget(padding_label)
        padding_row.addWidget(padding)
        layout.addLayout(padding_row)

        # Columns (Tiles X)
        columns_row = QHBoxLayout()
        columns_label = QLabel("Columns (Tiles X)")
        columns = QSpinBox()
        initial_cols = int(width / tile_size.value()) if tile_size.value() > 0 else 1
        columns.setValue(initial_cols)
        columns.setMaximum(999999)
        columns_row.addWidget(columns_label)
        columns_row.addWidget(columns)
        layout.addLayout(columns_row)

        # Rows (Tiles Y)
        rows_row = QHBoxLayout()
        rows_label = QLabel("Rows (Tiles Y)")
        rows = QSpinBox()
        initial_rows = int(height / tile_size.value()) if tile_size.value() > 0 else 1
        rows.setValue(initial_rows)
        rows.setMaximum(999999)
        rows_row.addWidget(rows_label)
        rows_row.addWidget(rows)
        layout.addLayout(rows_row)

        # Auto Update Checkbox
        auto_update = QCheckBox("Auto update input values")
        auto_update.setChecked(True)
        layout.addWidget(auto_update)

        # Auto update input values
        def update_fields():
            if not auto_update.isChecked() or tile_size.value() == 0:
                return

            padding.setValue(max(0, int(tile_size.value() / 8)))
            columns.setValue(max(0, int(width / tile_size.value())))
            rows.setValue(max(0, int(height / tile_size.value())))

        tile_size.valueChanged.connect(update_fields)

        # Anti-bleed Checkbox
        anti_pixel_bleed_padding = QCheckBox("Add anti-pixel-bleed pixels to the padding")
        anti_pixel_bleed_padding.setChecked(True)
        layout.addWidget(anti_pixel_bleed_padding)

        name_row = QHBoxLayout()
        name_label = QLabel("Padded file name")
        name = QLineEdit()
        name.setText(default_name)
        name_row.addWidget(name_label)
        name_row.addWidget(name)
        layout.addLayout(name_row)

        # OK Button
        btn = QPushButton("OK")
        btn.clicked.connect(dlg.accept)
        layout.addWidget(btn)

        dlg.setLayout(layout)
        if dlg.exec_() != QDialog.Accepted:
            return None
        else:
            return (
                tile_size.value(),
                padding.value(),
                columns.value(),
                rows.value(),
                anti_pixel_bleed_padding.isChecked(),
                name.text()
            )

Krita.instance().addExtension(TilesetPadder(Krita.instance()))