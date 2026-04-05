import os
from krita import Krita, Extension
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QSpinBox, QCheckBox, QPushButton, QLineEdit
)

class SpritesheetManager(Extension):

    def __init__(self, parent):
        super().__init__(parent)

    def setup(self):
        pass

    def createActions(self, window):
        action = window.createAction("spritesheet_manager", "Spritesheet Manager", "tools/scripts")
        action.triggered.connect(self.run)

    def run(self):
        app = Krita.instance()
        doc = app.activeDocument()

        if not doc:
            return

        original_width = doc.width()
        original_height = doc.height()

        original_path = doc.fileName()
        if original_path:
            folder = os.path.dirname(original_path)
            base = os.path.splitext(os.path.basename(original_path))[0]
            new_name = base + "_padded"
        else:
            folder = ""
            new_name = doc.name() + "_padded"

        result = self.openDialog(original_width, original_height, new_name)
        if result is None:
            return

        tile_size, padding_amount, columns_count, rows_count, anti_bleed, name = result

        stride = tile_size + (padding_amount * 2)
        new_width = columns_count * stride
        new_height = rows_count * stride
        
        if new_width == 0: new_width = original_width
        if new_height == 0: new_height = original_height

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

        new_layer = new_doc.createNode("Padded Sprite Sheet", "paintlayer")
        new_root.addChildNode(new_layer, None)

        for row_index in range(rows_count):
            for col_index in range(columns_count):
                source_x = col_index * tile_size
                source_y = row_index * tile_size
                
                destination_x = (col_index * stride) + padding_amount
                destination_y = (row_index * stride) + padding_amount

                if source_x >= original_width or source_y >= original_height:
                    continue

                tile_bytes = doc.pixelData(source_x, source_y, tile_size, tile_size)
                
                new_layer.setPixelData(tile_bytes, destination_x, destination_y, tile_size, tile_size)

                if anti_bleed and padding_amount > 0:
                    self.apply_anti_bleed(
                        doc, new_layer, 
                        source_x, source_y, 
                        destination_x, destination_y, 
                        tile_size, padding_amount
                    )

        new_doc.refreshProjection()
        app.activeWindow().addView(new_doc)

        if folder:
            save_path = os.path.join(folder, name + ".kra")
            new_doc.setFileName(save_path)
            new_doc.save()

    def apply_anti_bleed(self, source_doc, destination_layer, source_x, source_y, destination_x, destination_y, tile_size, padding_amount):
        # Top Edge
        top_row_pixels = source_doc.pixelData(source_x, source_y, tile_size, 1)
        top_block_pixels = top_row_pixels * padding_amount 
        destination_layer.setPixelData(top_block_pixels, destination_x, destination_y - padding_amount, tile_size, padding_amount)

        # Bottom Edge
        bottom_row_pixels = source_doc.pixelData(source_x, source_y + tile_size - 1, tile_size, 1)
        bottom_block_pixels = bottom_row_pixels * padding_amount
        destination_layer.setPixelData(bottom_block_pixels, destination_x, destination_y + tile_size, tile_size, padding_amount)
        
        # Left and Right Edges
        left_column_pixels = source_doc.pixelData(source_x, source_y, 1, tile_size)
        right_column_pixels = source_doc.pixelData(source_x + tile_size - 1, source_y, 1, tile_size)

        for i in range(1, padding_amount + 1):
            destination_layer.setPixelData(left_column_pixels, destination_x - i, destination_y, 1, tile_size)
            destination_layer.setPixelData(right_column_pixels, destination_x + tile_size + i - 1, destination_y, 1, tile_size)

        # Top-Left Corner
        top_left_pixel = source_doc.pixelData(source_x, source_y, 1, 1)
        destination_layer.setPixelData(top_left_pixel * (padding_amount * padding_amount), destination_x - padding_amount, destination_y - padding_amount, padding_amount, padding_amount)

        # Top-Right Corner
        top_right_pixel = source_doc.pixelData(source_x + tile_size - 1, source_y, 1, 1)
        destination_layer.setPixelData(top_right_pixel * (padding_amount * padding_amount), destination_x + tile_size, destination_y - padding_amount, padding_amount, padding_amount)

        # Bottom-Left Corner
        bottom_left_pixel = source_doc.pixelData(source_x, source_y + tile_size - 1, 1, 1)
        destination_layer.setPixelData(bottom_left_pixel * (padding_amount * padding_amount), destination_x - padding_amount, destination_y + tile_size, padding_amount, padding_amount)

        # Bottom-Right Corner
        bottom_right_pixel = source_doc.pixelData(source_x + tile_size - 1, source_y + tile_size - 1, 1, 1)
        destination_layer.setPixelData(bottom_right_pixel * (padding_amount * padding_amount), destination_x + tile_size, destination_y + tile_size, padding_amount, padding_amount)


    def openDialog(self, width, height, default_name):
        dlg = QDialog()
        dlg.setWindowTitle("Sprite Sheet Padder — Add padding to Sprite Sheet")

        layout = QVBoxLayout()

        # Tile Size
        tile_row = QHBoxLayout()
        tile_label = QLabel("Tile size")
        tile_size_spinner = QSpinBox()
        tile_size_spinner.setValue(64)
        tile_size_spinner.setMaximum(999999)
        tile_row.addWidget(tile_label)
        tile_row.addWidget(tile_size_spinner)
        layout.addLayout(tile_row)

        # Padding
        padding_row = QHBoxLayout()
        padding_label = QLabel("Padding")
        padding_spinner = QSpinBox()
        padding_spinner.setValue(int(tile_size_spinner.value() / 8))
        padding_spinner.setMaximum(999999)
        padding_row.addWidget(padding_label)
        padding_row.addWidget(padding_spinner)
        layout.addLayout(padding_row)

        # Columns (Tiles X)
        columns_row = QHBoxLayout()
        columns_label = QLabel("Columns (Tiles X)")
        columns_spinner = QSpinBox()
        initial_cols = int(width / tile_size_spinner.value()) if tile_size_spinner.value() > 0 else 1
        columns_spinner.setValue(initial_cols)
        columns_spinner.setMaximum(999999)
        columns_row.addWidget(columns_label)
        columns_row.addWidget(columns_spinner)
        layout.addLayout(columns_row)

        # Rows (Tiles Y)
        rows_row = QHBoxLayout()
        rows_label = QLabel("Rows (Tiles Y)")
        rows_spinner = QSpinBox()
        initial_rows = int(height / tile_size_spinner.value()) if tile_size_spinner.value() > 0 else 1
        rows_spinner.setValue(initial_rows)
        rows_spinner.setMaximum(999999)
        rows_row.addWidget(rows_label)
        rows_row.addWidget(rows_spinner)
        layout.addLayout(rows_row)

        # Auto Update Checkbox
        auto_update = QCheckBox("Auto update input values")
        auto_update.setChecked(True)
        layout.addWidget(auto_update)

        # Auto update input values
        def update_fields():
            if not auto_update.isChecked() or tile_size_spinner.value() == 0:
                return

            padding_spinner.setValue(max(0, int(tile_size_spinner.value() / 8)))
            columns_spinner.setValue(max(0, int(width / tile_size_spinner.value())))
            rows_spinner.setValue(max(0, int(height / tile_size_spinner.value())))

        tile_size_spinner.valueChanged.connect(update_fields)

        # Anti-bleed Checkbox
        anti_pixel_bleed_padding = QCheckBox("Add anti-pixel-bleed pixels to the padding")
        anti_pixel_bleed_padding.setChecked(True)
        layout.addWidget(anti_pixel_bleed_padding)

        name_row = QHBoxLayout()
        name_label = QLabel("Padded file name")
        name_input = QLineEdit()
        name_input.setText(default_name)
        name_row.addWidget(name_label)
        name_row.addWidget(name_input)
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
                tile_size_spinner.value(),
                padding_spinner.value(),
                columns_spinner.value(),
                rows_spinner.value(),
                anti_pixel_bleed_padding.isChecked(),
                name_input.text()
            )

Krita.instance().addExtension(SpritesheetManager(Krita.instance()))