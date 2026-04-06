from PyQt5.QtWidgets import (
    QWidget, QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QSpinBox, QCheckBox, QPushButton, QLineEdit, QGroupBox,
    QDialogButtonBox, QFrame
)
from PyQt5.QtCore import pyqtSignal


class PaddingWidget(QWidget):
    apply_requested = pyqtSignal(dict)

    def __init__(self, doc_width: int = 0, doc_height: int = 0,
                 default_name: str = "spritesheet_padded",
                 show_apply_button: bool = False,
                 parent=None):
        super().__init__(parent)
        self._doc_width   = doc_width
        self._doc_height  = doc_height

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        # Tile size group
        tile_box = QGroupBox("Tile Size")
        tile_layout = QHBoxLayout()
        self._tw_spin = QSpinBox()
        self._tw_spin.setRange(1, 999999)
        self._tw_spin.setValue(64)
        self._th_spin = QSpinBox()
        self._th_spin.setRange(1, 999999)
        self._th_spin.setValue(64)
        tile_layout.addWidget(QLabel("Width"))
        tile_layout.addWidget(self._tw_spin)
        tile_layout.addWidget(QLabel("Height"))
        tile_layout.addWidget(self._th_spin)
        tile_box.setLayout(tile_layout)
        layout.addWidget(tile_box)

        # Padding group
        pad_box = QGroupBox("Padding")
        pad_layout = QHBoxLayout()
        self._px_spin = QSpinBox()
        self._px_spin.setRange(0, 999999)
        self._px_spin.setValue(8)
        self._py_spin = QSpinBox()
        self._py_spin.setRange(0, 999999)
        self._py_spin.setValue(8)
        pad_layout.addWidget(QLabel("Horizontal"))
        pad_layout.addWidget(self._px_spin)
        pad_layout.addWidget(QLabel("Vertical"))
        pad_layout.addWidget(self._py_spin)
        pad_box.setLayout(pad_layout)
        layout.addWidget(pad_box)

        # Grid group
        grid_box = QGroupBox("Grid")
        grid_layout = QVBoxLayout()

        counts_row = QHBoxLayout()
        self._cols_spin = QSpinBox()
        self._cols_spin.setRange(1, 999999)
        self._rows_spin = QSpinBox()
        self._rows_spin.setRange(1, 999999)
        counts_row.addWidget(QLabel("Columns"))
        counts_row.addWidget(self._cols_spin)
        counts_row.addWidget(QLabel("Rows"))
        counts_row.addWidget(self._rows_spin)
        grid_layout.addLayout(counts_row)

        self._auto_cb = QCheckBox("Auto-update from tile size")
        self._auto_cb.setChecked(True)
        grid_layout.addWidget(self._auto_cb)

        grid_box.setLayout(grid_layout)
        layout.addWidget(grid_box)

        # Options group
        options_box = QGroupBox("Options")
        options_layout = QVBoxLayout()
        self._anti_bleed_cb = QCheckBox("Anti-pixel-bleed padding")
        self._anti_bleed_cb.setChecked(True)
        options_layout.addWidget(self._anti_bleed_cb)
        options_box.setLayout(options_layout)
        layout.addWidget(options_box)

        # Output group
        output_box = QGroupBox("Output")
        output_layout = QVBoxLayout()

        name_row = QHBoxLayout()
        name_row.addWidget(QLabel("File name"))
        self._name_input = QLineEdit(default_name)
        name_row.addWidget(self._name_input)
        output_layout.addLayout(name_row)

        self._save_kra_cb = QCheckBox("Save as .kra file")
        self._save_kra_cb.setChecked(True)
        output_layout.addWidget(self._save_kra_cb)

        output_box.setLayout(output_layout)
        layout.addWidget(output_box)

        # Apply button
        if show_apply_button:
            apply_btn = QPushButton("Apply Padding")
            apply_btn.clicked.connect(self._on_apply)
            layout.addWidget(apply_btn)

        layout.addStretch()
        self.setLayout(layout)

        # Signals
        self._tw_spin.valueChanged.connect(self._recalc)
        self._th_spin.valueChanged.connect(self._recalc)
        self._recalc()

    def set_doc_size(self, width: int, height: int):
        self._doc_width  = width
        self._doc_height = height
        self._recalc()

    def set_default_name(self, name: str):
        self._name_input.setText(name)

    def get_values(self) -> dict:
        return {
            "tile_width":  self._tw_spin.value(),
            "tile_height": self._th_spin.value(),
            "padding_x":   self._px_spin.value(),
            "padding_y":   self._py_spin.value(),
            "columns":     self._cols_spin.value(),
            "rows":        self._rows_spin.value(),
            "anti_bleed":  self._anti_bleed_cb.isChecked(),
            "name":        self._name_input.text(),
            "save_kra":    self._save_kra_cb.isChecked(),
        }

    def _recalc(self):
        if not self._auto_cb.isChecked():
            return
        tw = self._tw_spin.value()
        th = self._th_spin.value()
        if self._doc_width  > 0: self._cols_spin.setValue(max(1, self._doc_width  // tw))
        if self._doc_height > 0: self._rows_spin.setValue(max(1, self._doc_height // th))
        self._px_spin.setValue(max(0, tw // 8))
        self._py_spin.setValue(max(0, th // 8))

    def _on_apply(self):
        self.apply_requested.emit(self.get_values())


class PaddingDialog:
    def __init__(self, doc_width: int, doc_height: int, default_name: str):
        self._doc_width   = doc_width
        self._doc_height  = doc_height
        self._default_name = default_name

    def run(self) -> dict | None:
        dlg = QDialog()
        dlg.setWindowTitle("Add Padding — Spritesheet Editor")

        layout = QVBoxLayout()

        widget = PaddingWidget(
            doc_width = self._doc_width,
            doc_height = self._doc_height,
            default_name = self._default_name,
            show_apply_button = False
        )
        layout.addWidget(widget)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.button(QDialogButtonBox.Ok).setText("Apply Padding")
        buttons.accepted.connect(dlg.accept)
        buttons.rejected.connect(dlg.reject)
        layout.addWidget(buttons)

        dlg.setLayout(layout)

        if dlg.exec_() != QDialog.Accepted:
            return None

        return widget.get_values()