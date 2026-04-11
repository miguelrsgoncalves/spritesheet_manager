from krita import Krita
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QWidget, QDialog, QVBoxLayout, QHBoxLayout, QLabel, QSpinBox, QCheckBox, QPushButton, QLineEdit, QGroupBox, QDialogButtonBox
from ....core.serializer import Serializer
from ...core.padder import Padder

# TODO: REVIEW ALL USAGE OF activeDocument on all files and classes
# TODO: FINISH PADDER INTEGRATION

WIDGET_KEY: str = "PADDER"
WIDGET_DESCRIPTION: str = "Padder settings"

DEFAULTS: dict[str, any] = {
    "tile_size": [64, 64],
    "grid_size": [1, 1],
    "padding_size": [8, 8],
    "anti_bleed": True,
    "export_kra": False,
    "export_image": True,
}

class PadderWidget(QWidget):
    accept_requested = pyqtSignal(dict)


    def __init__(self):
        super().__init__()
        self.document: any = Krita.instance().activeDocument()

        root_layout = QVBoxLayout()

        root_layout.addWidget(self._build_tile_size_widget())
        root_layout.addWidget(self._build_padding_widget())
        root_layout.addWidget(self._build_grid_widget())
        root_layout.addWidget(self._build_options_widget())
        root_layout.addWidget(self._build_output_widget())

        self.setLayout(root_layout)

        self.setup_signals(self)

    #region functions

    def get_padder_arguments(self):
        return {
            "tile_size": [self._tile_width_spin.value(), self._tile_height_spin.value()],
            "grid_size": [self._columns_spin.value(), self._rows_spin.value()],
            "padding_size": [self._padding_width_spin.value(), self._padding_height_spin.value()],
            "anti_bleed": self._anti_bleed_checkbox.isChecked(),
            "name": self._name_input.text(),
            "export_kra": self._save_kra_checkbox.isChecked(),
            "export_image": self._export_image_checkbox.isChecked(),
        }

    def _update_auto_update_state(self, auto_on):
        self._padding_width_spin.setEnabled(not auto_on)
        self._padding_height_spin.setEnabled(not auto_on)
        self._columns_spin.setEnabled(not auto_on)
        self._rows_spin.setEnabled(not auto_on)
        if auto_on:
            self._on_tile_size_changed()

    def _on_tile_size_changed(self):
        if not self._auto_update_checkbox.isChecked():
            return
            
        tile_width = self._tile_width_spin.value()
        tile_height = self._tile_height_spin.value()
        
        document_width, document_height = self._document_size
        
        if document_width > 0:
            self._columns_spin.setValue(max(1, document_width // tile_width))
        if document_height > 0:
            self._rows_spin.setValue(max(1, document_height // tile_height))
            
        self._padding_width_spin.setValue(max(0, tile_width // 8))
        self._padding_height_spin.setValue(max(0, tile_height // 8))

    def _on_apply(self):
        self.accept_requested.emit(self.get_values())
    
    #endregion

    #region widgets

    def _build_tile_size_widget(self):
        widget = QGroupBox("Tile Size")
        layout = QHBoxLayout()

        self._tile_width_spin = QSpinBox()
        self._tile_width_spin.setRange(1, 999999)
        self._tile_width_spin.setValue(64)

        self._tile_height_spin = QSpinBox()
        self._tile_height_spin.setRange(1, 999999)
        self._tile_height_spin.setValue(64)

        layout.addWidget(QLabel("Width"))
        layout.addWidget(self._tile_width_spin)
        layout.addWidget(self._link_button)
        layout.addWidget(QLabel("Height"))
        layout.addWidget(self._tile_height_spin)

        widget.setLayout(layout)

        return widget

    def _build_padding_widget(self):
        group = QGroupBox("Padding")
        layout = QHBoxLayout()
        layout.setSpacing(6)

        self._padding_width_spin = QSpinBox()
        self._padding_width_spin.setRange(0, 999999)
        self._padding_width_spin.setValue(8)

        self._padding_height_spin = QSpinBox()
        self._padding_height_spin.setRange(0, 999999)
        self._padding_height_spin.setValue(8)

        layout.addWidget(QLabel("Horizontal"))
        layout.addWidget(self._padding_width_spin)
        layout.addWidget(QLabel("Vertical"))
        layout.addWidget(self._padding_height_spin)

        group.setLayout(layout)
        return group

    def _build_grid_widget(self):
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

    def _build_options_widget(self):
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

    def _build_output_widget(self, default_name):
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

    #endregion

    #region state

    def load_state(self):
        krita = Krita.instance()
        document = krita.activeDocument()

        state: dict[str, any] = Serializer.load_state(document, WIDGET_KEY)
        self.set_state(state)
    
    def set_state(self, state):
        tile_width, tile_height = state.get("tile_size", DEFAULTS["tile_size"])
        self._tile_width_spin.setValue(tile_width)
        self._tile_height_spin.setValue(tile_height)

        columns, rows = state.get("grid_size", DEFAULTS["grid_size"])
        self._columns_spin.setValue(columns)
        self._rows_spin.setValue(rows)

        padding_width, padding_height = state.get("padding_size", DEFAULTS["padding_size"])
        self._padding_width_spin.setValue(padding_width)
        self._padding_height_spin.setValue(padding_height)

        self._anti_bleed_checkbox.setChecked(state.get("anti_bleed", DEFAULTS["anti_bleed"]))
        self._save_kra_checkbox.setChecked(state.get("export_kra", DEFAULTS["export_kra"]))
        self._export_image_checkbox.setChecked(state.get("export_image", DEFAULTS["export_image"]))

    def save_state(self):
        krita = Krita.instance()
        document = krita.activeDocument()

        data: dict[str, any] = self.get_state()
        Serializer.save_state(document, WIDGET_KEY, data, WIDGET_DESCRIPTION)
    
    def get_state(self) -> dict[str, any]:
        return {
            "tile_size": [self._tile_width_spin.value(), self._tile_height_spin.value()],
            "grid_size": [self._columns_spin.value(), self._rows_spin.value()],
            "padding_size": [self._padding_width_spin.value(), self._padding_height_spin.value()],
            
            "anti_bleed": self._anti_bleed_checkbox.isChecked(),
            "export_kra": self._save_kra_checkbox.isChecked(),
            "export_image": self._export_image_checkbox.isChecked(),
        }
    
    #endregion

    #region signals

    def setup_signals(self):
        notifier = Krita.instance().notifier()
        notifier.activeCanvasChanged.connect(self.on_active_canvas_changed)

    def on_active_canvas_changed(self):
        self.document = Krita.instance().activeDocument()
        self.load_state()

    #endregion

    def closeEvent(self, a0):
        try:
            notifier = Krita.instance().notifier()
            notifier.activeCanvasChanged.disconnect(self.on_active_canvas_changed)
        except:
            pass
        return super().closeEvent(a0)

class PadderDialog:
    def __init__(self):
        dialog = QDialog()
        dialog.setile_widthindowTitle("Spritesheet Editor: Padder")

        layout = QVBoxLayout()

        widget = PadderWidget()

        layout.addWidget(widget)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.button(QDialogButtonBox.Ok).setText("Apply Padding")
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)

        dialog.setLayout(layout)

        if dialog.exec_() != QDialog.Accepted: return None

        self.run_padder(widget.get_padder_arguments())

    def run_padder(padder_arguments: dict[str, any]):
        Padder.run(padder_arguments)