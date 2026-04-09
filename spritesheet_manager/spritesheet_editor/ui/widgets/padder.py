from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QWidget, QDialog, QVBoxLayout, QHBoxLayout, QLabel, QSpinBox, QCheckBox, QPushButton, QLineEdit, QGroupBox, QDialogButtonBox

class PadderWidget(QWidget):
    accept_requested = pyqtSignal(dict)

    def __init__(self, document):
        super().__init__()

        self._doc_width = document.width
        self._doc_height = document.height
        self._tile_size_linked = True

        root_layout = QVBoxLayout()
        #root_layout.setContentsMargins(8, 8, 8, 8)
        #root_layout.setSpacing(8)

        root_layout.addWidget(self._build_tile_size_group())
        root_layout.addWidget(self._build_padding_group())
        root_layout.addWidget(self._build_grid_group())
        root_layout.addWidget(self._build_options_group())
        root_layout.addWidget(self._build_output_group(document.name()))

        root_layout.addStretch()
        self.setLayout(root_layout)

        # Apply saved state first, then recalc on top if auto-update is on
        if saved_state:
            self._apply_saved_state(saved_state)
        else:
            self._on_tile_size_changed()

        self._update_auto_update_state(self._auto_update_checkbox.isChecked())

    def _apply_saved_state(self, state):
        # Restore previously saved settings for this document
        self._tile_width_spin.setValue(state.get("tile_width", 64))
        self._tile_height_spin.setValue(state.get("tile_height", 64))
        self._padding_x_spin.setValue(state.get("padding_x", 8))
        self._padding_y_spin.setValue(state.get("padding_y", 8))
        self._columns_spin.setValue(state.get("columns", 1))
        self._rows_spin.setValue(state.get("rows", 1))
        self._anti_bleed_checkbox.setChecked(state.get("anti_bleed", True))
        self._save_kra_checkbox.setChecked(state.get("save_kra", False))
        self._export_image_checkbox.setChecked(state.get("export_image", True))

    def _build_tile_size_group(self):
        group = QGroupBox("Tile Size")
        layout = QHBoxLayout()
        layout.setSpacing(6)

        self._tile_width_spin = QSpinBox()
        self._tile_width_spin.setRange(1, 999999)
        self._tile_width_spin.setValue(64)

        self._tile_height_spin = QSpinBox()
        self._tile_height_spin.setRange(1, 999999)
        self._tile_height_spin.setValue(64)

        self._link_button = QPushButton()
        self._link_button.setFixedSize(22, 22)
        self._link_button.setCheckable(True)
        self._link_button.setChecked(True)
        self._link_button.setFlat(True)
        self._link_button.setIcon(_load_link_icon(True))
        self._link_button.setToolTip("Link Width and Height")
        self._link_button.toggled.connect(self._on_link_toggled)

        layout.addWidget(QLabel("Width"))
        layout.addWidget(self._tile_width_spin)
        layout.addWidget(self._link_button)
        layout.addWidget(QLabel("Height"))
        layout.addWidget(self._tile_height_spin)

        group.setLayout(layout)

        self._tile_width_spin.valueChanged.connect(self._on_tile_width_changed)
        self._tile_height_spin.valueChanged.connect(self._on_tile_height_changed)

        return group

    def _build_padding_group(self):
        group = QGroupBox("Padding")
        layout = QHBoxLayout()
        layout.setSpacing(6)

        self._padding_x_spin = QSpinBox()
        self._padding_x_spin.setRange(0, 999999)
        self._padding_x_spin.setValue(8)

        self._padding_y_spin = QSpinBox()
        self._padding_y_spin.setRange(0, 999999)
        self._padding_y_spin.setValue(8)

        layout.addWidget(QLabel("Horizontal"))
        layout.addWidget(self._padding_x_spin)
        layout.addWidget(QLabel("Vertical"))
        layout.addWidget(self._padding_y_spin)

        group.setLayout(layout)
        return group

    def _build_grid_group(self):
        group = QGroupBox("Grid")
        layout = QVBoxLayout()
        layout.setSpacing(6)

        counts_row = QHBoxLayout()
        self._columns_spin = QSpinBox()
        self._columns_spin.setRange(1, 999999)
        self._rows_spin = QSpinBox()
        self._rows_spin.setRange(1, 999999)
        counts_row.addWidget(QLabel("Columns"))
        counts_row.addWidget(self._columns_spin)
        counts_row.addWidget(QLabel("Rows"))
        counts_row.addWidget(self._rows_spin)
        layout.addLayout(counts_row)

        self._auto_update_checkbox = QCheckBox("Auto-update from tile size")
        self._auto_update_checkbox.setChecked(True)
        self._auto_update_checkbox.toggled.connect(self._update_auto_update_state)
        layout.addWidget(self._auto_update_checkbox)

        group.setLayout(layout)
        return group

    def _build_options_group(self):
        group = QGroupBox("Options")
        layout = QVBoxLayout()

        self._anti_bleed_checkbox = QCheckBox("Anti-pixel-bleed padding")
        self._anti_bleed_checkbox.setChecked(True)
        self._anti_bleed_checkbox.setToolTip(
            "Repeats edge pixels into the padding area to prevent colour bleeding at tile seams"
        )
        layout.addWidget(self._anti_bleed_checkbox)

        group.setLayout(layout)
        return group

    def _build_output_group(self, default_name):
        group = QGroupBox("Output")
        layout = QVBoxLayout()
        layout.setSpacing(6)

        name_row = QHBoxLayout()
        name_row.addWidget(QLabel("File name"))
        self._name_input = QLineEdit(default_name)
        name_row.addWidget(self._name_input)
        layout.addLayout(name_row)

        self._save_kra_checkbox = QCheckBox("Save as .kra file")
        self._save_kra_checkbox.setChecked(False)

        self._export_image_checkbox = QCheckBox("Export image")
        self._export_image_checkbox.setChecked(True)

        def _on_save_kra_toggled(checked):
            if not checked:
                self._export_image_checkbox.setChecked(True)
                self._export_image_checkbox.setEnabled(False)
            else:
                self._export_image_checkbox.setEnabled(True)

        self._save_kra_checkbox.toggled.connect(_on_save_kra_toggled)

        layout.addWidget(self._save_kra_checkbox)
        layout.addWidget(self._export_image_checkbox)

        group.setLayout(layout)
        return group

    def set_doc_size(self, width, height):
        self._doc_width = width
        self._doc_height = height
        self._on_tile_size_changed()

    def set_default_name(self, name):
        self._name_input.setText(name)

    def get_values(self):
        return {
            "tile_width": self._tile_width_spin.value(),
            "tile_height": self._tile_height_spin.value(),
            "padding_x": self._padding_x_spin.value(),
            "padding_y": self._padding_y_spin.value(),
            "columns": self._columns_spin.value(),
            "rows": self._rows_spin.value(),
            "anti_bleed": self._anti_bleed_checkbox.isChecked(),
            "name": self._name_input.text(),
            "save_kra": self._save_kra_checkbox.isChecked(),
            "export_image": self._export_image_checkbox.isChecked(),
        }

    def _update_auto_update_state(self, auto_on):
        # When auto-update is on, padding and grid fields are read-only
        self._padding_x_spin.setEnabled(not auto_on)
        self._padding_y_spin.setEnabled(not auto_on)
        self._columns_spin.setEnabled(not auto_on)
        self._rows_spin.setEnabled(not auto_on)
        if auto_on:
            self._on_tile_size_changed()

    def _on_link_toggled(self, linked: bool):
        self._tile_size_linked = linked
        self._link_button.setIcon(_load_link_icon(linked))
        if linked:
            self._link_button.setToolTip("Link Width and Height")
        else:
            self._link_button.setToolTip("Unlink Width and Height")

    def _on_tile_width_changed(self, value):
        if self._tile_size_linked:
            self._tile_height_spin.blockSignals(True)
            self._tile_height_spin.setValue(value)
            self._tile_height_spin.blockSignals(False)
        self._on_tile_size_changed()

    def _on_tile_height_changed(self, value):
        if self._tile_size_linked:
            self._tile_width_spin.blockSignals(True)
            self._tile_width_spin.setValue(value)
            self._tile_width_spin.blockSignals(False)
        self._on_tile_size_changed()

    def _on_tile_size_changed(self):
        if not self._auto_update_checkbox.isChecked():
            return
        tile_width = self._tile_width_spin.value()
        tile_height = self._tile_height_spin.value()
        if self._doc_width > 0:
            self._columns_spin.setValue(max(1, self._doc_width // tile_width))
        if self._doc_height > 0:
            self._rows_spin.setValue(max(1, self._doc_height // tile_height))
        self._padding_x_spin.setValue(max(0, tile_width // 8))
        self._padding_y_spin.setValue(max(0, tile_height // 8))

    def _on_apply(self):
        self.accept_requested.emit(self.get_values())

class PadderDialog:
    def __init__(self, document):
        self._document = document

    def run(self):
        dialog = QDialog()
        dialog.setWindowTitle("Spritesheet Editor: Padder")

        layout = QVBoxLayout()

        widget = PadderWidget(
            document = self.document,
        )

        layout.addWidget(widget)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.button(QDialogButtonBox.Ok).setText("Apply Padding")
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)

        dialog.setLayout(layout)

        if dialog.exec_() != QDialog.Accepted:
            return None

        return widget.get_values()