import math
from krita import Krita
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QWidget, QDialog, QVBoxLayout, QHBoxLayout, QLabel, QSpinBox, QCheckBox, QPushButton, QLineEdit, QGroupBox, QDialogButtonBox
from ...core.serializer import Serializer
from ..core.padder import Padder

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

    def __init__(self, document):
        super().__init__()
        self.document: any = document

        layout: QVBoxLayout = QVBoxLayout()

        layout.addWidget(self._build_padding_settings_group())
        layout.addWidget(self._build_options_widget())
        layout.addWidget(self._build_output_widget())

        self.setLayout(layout)

    #region functions

    def get_padder_arguments(self):
        return {
            "tile_size": [self.tile_width_input.value(), self.tile_height_input.value()],
            "grid_size": [self.grid_columns_input.value(), self.grid_rows_input.value()],
            "padding_size": [self.padding_width_input.value(), self.padding_height_input.value()],
            "anti_bleed": self._anti_bleed_checkbox.isChecked(),
            "name": self._name_input.text(),
            "export_kra": self._save_kra_checkbox.isChecked(),
            "export_image": self._export_image_checkbox.isChecked(),
        }

    def _update_auto_update_state(self, auto_on):
        self.padding_width_input.setEnabled(not auto_on)
        self.padding_height_input.setEnabled(not auto_on)
        self.grid_columns_input.setEnabled(not auto_on)
        self.grid_rows_input.setEnabled(not auto_on)
        if auto_on:
            self._on_tile_size_changed()

    def _on_tile_size_changed(self):
        if not self._auto_update_checkbox.isChecked():
            return
            
        tile_width = self.tile_width_input.value()
        tile_height = self.tile_height_input.value()
        
        document_width, document_height = self._document_size
        
        if document_width > 0:
            self.grid_columns_input.setValue(max(1, document_width // tile_width))
        if document_height > 0:
            self.grid_rows_input.setValue(max(1, document_height // tile_height))
            
        self.padding_width_input.setValue(max(0, tile_width // 8))
        self.padding_height_input.setValue(max(0, tile_height // 8))

    def _on_apply(self):
        self.accept_requested.emit(self.get_values())
    
    #endregion

    #region groups

    def _build_padding_settings_group(self):
        group: QGroupBox = QGroupBox("Padding Settings")

        padding_settings_layout: QHBoxLayout = QHBoxLayout()

        tile_size_layout: QVBoxLayout = QVBoxLayout()

        tile_width_layout: QHBoxLayout = QHBoxLayout()
        self.tile_width_input: QSpinBox = QSpinBox()
        self.tile_width_input.setRange(1, math.inf)
        self.tile_width_input.setValue(DEFAULTS.get("tile_size")[0])
        tile_width_layout.addWidget(QLabel("Width:"))
        tile_width_layout.addWidget(self.tile_width_input)

        tile_height_layout: QHBoxLayout = QHBoxLayout()
        self.tile_height_input: QSpinBox = QSpinBox()
        self.tile_height_input.setRange(1, math.inf)
        self.tile_height_input.setValue(DEFAULTS.get("tile_size")[1])
        tile_height_layout.addWidget(QLabel("Height:"))
        tile_height_layout.addWidget(self.tile_height_input)

        tile_size_layout.addWidget(QLabel("Tile Size"))
        tile_size_layout.addWidget(tile_width_layout)
        tile_size_layout.addWidget(tile_height_layout)
        padding_settings_layout.addWidget(tile_size_layout)

        grid_size_layout: QVBoxLayout = QVBoxLayout()

        grid_width_layout: QHBoxLayout = QHBoxLayout()
        self.grid_columns_input: QSpinBox = QSpinBox()
        self.grid_columns_input.setRange(1, math.inf)
        self.grid_columns_input.setValue(DEFAULTS.get("grid_size")[0])
        grid_width_layout.addWidget(QLabel("Columns:"))
        grid_width_layout.addWidget(self.padding_width_input)

        grid_height_layout: QHBoxLayout = QHBoxLayout()
        self.grid_rows_input: QSpinBox = QSpinBox()
        self.grid_rows_input.setRange(1, math.inf)
        self.grid_rows_input.setValue(DEFAULTS.get("grid_size")[1])
        grid_height_layout.addWidget(QLabel("Rows:"))
        grid_height_layout.addWidget(self.grid_rows_input)

        grid_size_layout.addWidget(QLabel("Grid Size"))
        grid_size_layout.addWidget(grid_width_layout)
        grid_size_layout.addWidget(grid_width_layout)
        padding_settings_layout.addWidget(grid_size_layout)

        padding_size_layout: QVBoxLayout = QVBoxLayout()

        padding_width_layout: QHBoxLayout = QHBoxLayout()
        self.padding_width_input: QSpinBox = QSpinBox()
        self.padding_width_input.setRange(0, math.inf)
        self.padding_width_input.setValue(DEFAULTS.get("padding_size")[0])
        padding_width_layout.addWidget(QLabel("Width:"))
        padding_width_layout.addWidget(self.padding_width_input)

        padding_height_layout: QHBoxLayout = QHBoxLayout()
        self.padding_height_input = QSpinBox()
        self.padding_height_input.setRange(0, math.inf)
        self.padding_height_input.setValue(DEFAULTS.get("padding_size")[1])
        padding_height_layout.addWidget(QLabel("Height:"))
        padding_height_layout.addWidget(self.padding_height_layout)

        padding_size_layout.addWidget(QLabel("Padding Size"))
        padding_size_layout.addWidget(padding_width_layout)
        padding_size_layout.addWidget(padding_height_layout)
        padding_settings_layout.addWidget(padding_size_layout)

        group.setLayout(padding_settings_layout)
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
        self.tile_width_input.setValue(tile_width)
        self.tile_height_input.setValue(tile_height)

        columns, rows = state.get("grid_size", DEFAULTS["grid_size"])
        self.grid_columns_input.setValue(columns)
        self.grid_rows_input.setValue(rows)

        padding_width, padding_height = state.get("padding_size", DEFAULTS["padding_size"])
        self.padding_width_input.setValue(padding_width)
        self.padding_height_input.setValue(padding_height)

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
            "tile_size": [self.tile_width_input.value(), self.tile_height_input.value()],
            "grid_size": [self.grid_columns_input.value(), self.grid_rows_input.value()],
            "padding_size": [self.padding_width_input.value(), self.padding_height_input.value()],
            
            "anti_bleed": self._anti_bleed_checkbox.isChecked(),
            "export_kra": self._save_kra_checkbox.isChecked(),
            "export_image": self._export_image_checkbox.isChecked(),
        }
    
    #endregion

    #region signals

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
        dialog: QDialog = QDialog()
        dialog.setile_widthindowTitle("Spritesheet Editor: Padder")

        layout: QVBoxLayout = QVBoxLayout()

        document: any = Krita.instance().activeDocument()
        padder_widget: PadderWidget = PadderWidget(self, document)

        layout.addWidget(padder_widget)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.button(QDialogButtonBox.Ok).setText("Apply Padding")
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)

        dialog.setLayout(layout)

        if dialog.exec_() != QDialog.Accepted: return None

        self.run_padder(padder_widget.get_padder_arguments())

    def run_padder(padder_arguments: dict[str, any]):
        Padder.run(padder_arguments)