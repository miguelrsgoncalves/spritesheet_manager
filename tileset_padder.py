from krita import Krita, Extension
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QSpinBox, QCheckBox, QPushButton
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
        if doc is None:
            return

        width = doc.width()
        height = doc.height()

        self.openDialog(width, height)

    def openDialog(self, width, height):
        dlg = QDialog()
        dlg.setWindowTitle("Tileset Padder — Add padding to tileset")

        layout = QVBoxLayout()

        # Tile Size
        tile_row = QHBoxLayout()
        tile_label = QLabel("Tile size")
        tile_size = QSpinBox()
        tile_size.setValue(64)
        tile_row.addWidget(tile_label)
        tile_row.addWidget(tile_size)
        layout.addLayout(tile_row)

        # Padding
        padding_row = QHBoxLayout()
        padding_label = QLabel("Padding")
        padding = QSpinBox()
        padding.setValue(int(tile_size.value() / 8))
        padding_row.addWidget(padding_label)
        padding_row.addWidget(padding)
        layout.addLayout(padding_row)

        # Columns (Tiles X)
        columns_row = QHBoxLayout()
        columns_label = QLabel("Columns (Tiles X)")
        columns = QSpinBox()
        columns.setValue(int(width / tile_size.value()))
        columns_row.addWidget(columns_label)
        columns_row.addWidget(columns)
        layout.addLayout(columns_row)

        # Rows (Tiles Y)
        rows_row = QHBoxLayout()
        rows_label = QLabel("Rows (Tiles Y)")
        rows = QSpinBox()
        rows.setValue(int(height / tile_size.value()))
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

            tile_size = tile_size.value()
            padding.setValue(max(0, int(tile_size / 8)))
            columns.setValue(max(0, int(width / tile_size)))
            rows.setValue(max(0, int(height / tile_size)))

        tile_size.valueChanged.connect(update_fields)

        # OK Button
        btn = QPushButton("OK")
        btn.clicked.connect(dlg.accept)
        layout.addWidget(btn)

        dlg.setLayout(layout)
        dlg.exec_()


Krita.instance().addExtension(TilesetPadder(Krita.instance()))
