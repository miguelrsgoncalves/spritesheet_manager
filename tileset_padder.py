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

        width = doc.width()
        height = doc.height()
        import os
        orig_path = doc.fileName()
        if orig_path:
            folder = os.path.dirname(orig_path)
            base = os.path.splitext(os.path.basename(orig_path))[0]
            new_name = base + "_padded"
        else:
            folder = ""
            new_name = doc.name() + "_padded"

        result = self.openDialog(width, height, new_name)
        if result is None:
            return

        tile_size, padding, columns, rows, anti_bleed, name = result


        color_model = doc.colorModel()
        color_depth = doc.colorDepth()
        profile = doc.colorProfile()
        resolution = doc.resolution()

        new_doc = app.createDocument(
            doc.width(),
            doc.height(),
            name,
            color_model,
            color_depth,
            profile,
            resolution
        )

        new_root = new_doc.rootNode()
        old_root = doc.rootNode()

        for child in new_root.childNodes():
            new_root.removeChildNode(child)

        for child in old_root.childNodes():
            dup = child.clone()
            new_root.addChildNode(dup, None)


        app.activeWindow().addView(new_doc)
        new_doc.refreshProjection()

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
        columns.setValue(int(width / tile_size.value()))
        columns.setMaximum(999999)
        columns_row.addWidget(columns_label)
        columns_row.addWidget(columns)
        layout.addLayout(columns_row)

        # Rows (Tiles Y)
        rows_row = QHBoxLayout()
        rows_label = QLabel("Rows (Tiles Y)")
        rows = QSpinBox()
        rows.setValue(int(height / tile_size.value()))
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
            if not auto_update.isChecked():
                return

            padding.setValue(max(0, int(tile_size.value() / 8)))
            columns.setValue(max(0, int(width / tile_size.value())))
            rows.setValue(max(0, int(height / tile_size.value())))

        tile_size.valueChanged.connect(update_fields)

        # Auto Update Checkbox
        anti_pixeL_bleed_padding = QCheckBox("Add anti-pixel-bleed pixels to the padding")
        anti_pixeL_bleed_padding.setChecked(True)
        layout.addWidget(anti_pixeL_bleed_padding)

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
                anti_pixeL_bleed_padding.isChecked(),
                name.text()
            )


Krita.instance().addExtension(TilesetPadder(Krita.instance()))
