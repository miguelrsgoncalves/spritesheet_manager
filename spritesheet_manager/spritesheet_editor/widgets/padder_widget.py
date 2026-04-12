from krita import Krita
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QDialog, QGroupBox, QGridLayout, QHBoxLayout, QVBoxLayout, QLabel, QSpinBox, QCheckBox, QLineEdit, QDialogButtonBox
from ...core.serializer import Serializer
from ..core.padder import Padder
from ...ui.widgets import LinkButton

MAX_INT = 2147483647

WIDGET_KEY: str = "PADDER"
WIDGET_DESCRIPTION: str = "Padder settings"

DEFAULTS: dict[str, any] = {
    "tile_size": [64, 64],
    "grid_size": [1, 1],
    "grid_size_auto_update": True,
    "padding_size": [8, 8],
    "padding_size_auto_update": True,
    "anti_bleed": True,
    "export_kra": False,
    "export_image": True,
    "padded_file_suffix": "_padded"
}

class PadderWidget(QWidget):
    def __init__(self, document):
        super().__init__()
        self._document: any = document

        layout: QVBoxLayout = QVBoxLayout()

        layout.addWidget(self._build_padding_settings_group())
        layout.addWidget(self._build_options_group())
        layout.addWidget(self._build_output_group())

        self.setLayout(layout)

        self.refresh_ui()

    #region functions

    def run_padder(self):
        Padder.run(self._get_padder_arguments())
    
    def _get_padder_arguments(self):
        return {
            "tile_size": [self._tile_width_input.value(), self._tile_height_input.value()],
            "grid_size": [self._grid_columns_input.value(), self._grid_rows_input.value()],
            "padding_size": [self._padding_width_input.value(), self._padding_height_input.value()],
            "anti_bleed": self._anti_bleed_input.isChecked(),
            "name": self._name_input.text(),
            "export_kra": self._export_kra_input.isChecked(),
            "export_image": self._export_image_input.isChecked(),
        }

    def refresh_ui(self):
        self._on_tile_size_changed()
        self._on_grid_auto_update_toggled()
        self._on_padding_auto_update_toggled()
    
    def _get_default_padded_file_name(self) -> str:
        return self._document.name() + DEFAULTS.get("padded_file_suffix") if self._document else "Padded Spritesheet"
    
    #endregion

    #region groups

    def _build_padding_settings_group(self):
        group: QGroupBox = QGroupBox("Padding Settings")
        padding_settings_layout: QHBoxLayout = QHBoxLayout()

        tile_size_layout: QVBoxLayout = QVBoxLayout()
        tile_size_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        tile_width_layout: QHBoxLayout = QHBoxLayout()
        self._tile_width_input: QSpinBox = QSpinBox()
        self._tile_width_input.setRange(1, MAX_INT)
        self._tile_width_input.setValue(DEFAULTS.get("tile_size")[0])
        self._tile_width_input.valueChanged.connect(self._on_tile_size_changed)
        tile_width_layout.addWidget(QLabel("Width:"))
        tile_width_layout.addWidget(self._tile_width_input)
        tile_height_layout: QHBoxLayout = QHBoxLayout()
        self._tile_height_input: QSpinBox = QSpinBox()
        self._tile_height_input.setRange(1, MAX_INT)
        self._tile_height_input.setValue(DEFAULTS.get("tile_size")[1])
        self._tile_height_input.valueChanged.connect(self._on_tile_size_changed)
        tile_height_layout.addWidget(QLabel("Height:"))
        tile_height_layout.addWidget(self._tile_height_input)
        tile_size_layout.addWidget(QLabel("Tile Size"))
        tile_size_layout.addLayout(tile_width_layout)
        tile_size_layout.addLayout(tile_height_layout)
        self._tile_size_link_input: LinkButton = LinkButton()
        self._tile_size_link_input.setToolTip("Constrain proportions")
        tile_size_layout.addWidget(self._tile_size_link_input)

        grid_size_layout: QVBoxLayout = QVBoxLayout()
        grid_size_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        grid_width_layout: QHBoxLayout = QHBoxLayout()
        self._grid_columns_input: QSpinBox = QSpinBox()
        self._grid_columns_input.setRange(1, MAX_INT)
        self._grid_columns_input.setValue(DEFAULTS.get("grid_size")[0])
        grid_width_layout.addWidget(QLabel("Columns:"))
        grid_width_layout.addWidget(self._grid_columns_input)
        grid_height_layout: QHBoxLayout = QHBoxLayout()
        self._grid_rows_input: QSpinBox = QSpinBox()
        self._grid_rows_input.setRange(1, MAX_INT)
        self._grid_rows_input.setValue(DEFAULTS.get("grid_size")[1])
        grid_height_layout.addWidget(QLabel("Rows:"))
        grid_height_layout.addWidget(self._grid_rows_input)
        self._grid_size_auto_update_input: QCheckBox = QCheckBox("Auto-update")
        self._grid_size_auto_update_input.setChecked(DEFAULTS.get("grid_size_auto_update"))
        self._grid_size_auto_update_input.setToolTip("Auto-update the grid size using the tile size and the document's size.")
        self._grid_size_auto_update_input.toggled.connect(self._on_grid_auto_update_toggled)
        grid_size_layout.addWidget(QLabel("Grid Size"))
        grid_size_layout.addLayout(grid_width_layout)
        grid_size_layout.addLayout(grid_height_layout)
        grid_size_layout.addWidget(self._grid_size_auto_update_input)

        padding_size_layout: QVBoxLayout = QVBoxLayout()
        padding_size_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        padding_width_layout: QHBoxLayout = QHBoxLayout()
        self._padding_width_input: QSpinBox = QSpinBox()
        self._padding_width_input.setRange(0, MAX_INT)
        self._padding_width_input.setValue(DEFAULTS.get("padding_size")[0])
        padding_width_layout.addWidget(QLabel("Width:"))
        padding_width_layout.addWidget(self._padding_width_input)
        padding_height_layout: QHBoxLayout = QHBoxLayout()
        self._padding_height_input: QSpinBox = QSpinBox()
        self._padding_height_input.setRange(0, MAX_INT)
        self._padding_height_input.setValue(DEFAULTS.get("padding_size")[1])
        padding_height_layout.addWidget(QLabel("Height:"))
        padding_height_layout.addWidget(self._padding_height_input)
        self._padding_size_auto_update_input: QCheckBox = QCheckBox("Auto-update")
        self._padding_size_auto_update_input.setChecked(DEFAULTS.get("padding_size_auto_update"))
        self._padding_size_auto_update_input.setToolTip("Auto-update the padding size using the tile size, by default dividing the tile size by 8.")
        self._padding_size_auto_update_input.toggled.connect(self._on_padding_auto_update_toggled)
        padding_size_layout.addWidget(QLabel("Padding Size"))
        padding_size_layout.addLayout(padding_width_layout)
        padding_size_layout.addLayout(padding_height_layout)
        padding_size_layout.addWidget(self._padding_size_auto_update_input)

        padding_settings_layout.addLayout(tile_size_layout)
        padding_settings_layout.addSpacing(24)
        padding_settings_layout.addLayout(grid_size_layout)
        padding_settings_layout.addSpacing(24)
        padding_settings_layout.addLayout(padding_size_layout)

        group.setLayout(padding_settings_layout)
        return group

    def _build_options_group(self):
        group : QGroupBox= QGroupBox("Options")
        options_layout: QVBoxLayout = QVBoxLayout()

        self._anti_bleed_input: QCheckBox = QCheckBox("Anti-pixel-bleed padding")
        self._anti_bleed_input.setChecked(DEFAULTS.get("anti_bleed"))
        self._anti_bleed_input.setToolTip("Repeats edge pixels into the padding area to prevent colour bleeding at tile seams.")

        options_layout.addWidget(self._anti_bleed_input)

        group.setLayout(options_layout)
        return group

    def _build_output_group(self):
        group: QGroupBox = QGroupBox("Output")
        output_layout: QHBoxLayout = QVBoxLayout()

        file_name_layout: QHBoxLayout = QHBoxLayout()
        file_name_layout.addWidget(QLabel("File name"))
        self._file_name_input: QLineEdit = QLineEdit(self._get_default_padded_file_name())
        file_name_layout.addWidget(self._file_name_input)
        self._export_kra_input: QCheckBox = QCheckBox("Save .kra")
        self._export_kra_input.setChecked(False)
        self._export_image_input: QCheckBox = QCheckBox("Export image")
        self._export_image_input.setChecked(True)

        output_layout.addLayout(file_name_layout)
        output_layout.addWidget(self._export_kra_input)
        output_layout.addWidget(self._export_image_input)

        group.setLayout(output_layout)
        return group

    #endregion

    #region state

    def _load_state(self):
        krita = Krita.instance()
        document = krita.activeDocument()

        state: dict[str, any] = Serializer.load_state(document, WIDGET_KEY)
        self._set_state(state)
    
    def _set_state(self, state):
        tile_width, tile_height = state.get("tile_size", DEFAULTS["tile_size"])
        self._tile_width_input.setValue(tile_width)
        self._tile_height_input.setValue(tile_height)

        columns, rows = state.get("grid_size", DEFAULTS["grid_size"])
        self._grid_columns_input.setValue(columns)
        self._grid_rows_input.setValue(rows)

        padding_width, padding_height = state.get("padding_size", DEFAULTS["padding_size"])
        self._padding_width_input.setValue(padding_width)
        self._padding_height_input.setValue(padding_height)

        self._anti_bleed_input.setChecked(state.get("anti_bleed", DEFAULTS["anti_bleed"]))
        self._export_kra_input.setChecked(state.get("export_kra", DEFAULTS["export_kra"]))
        self._export_image_input.setChecked(state.get("export_image", DEFAULTS["export_image"]))

        self.refresh_ui()

    def _save_state(self):
        krita = Krita.instance()
        document = krita.activeDocument()

        data: dict[str, any] = self._get_state()
        Serializer.save_state(document, WIDGET_KEY, data, WIDGET_DESCRIPTION)
    
    def _get_state(self) -> dict[str, any]:
        return {
            "tile_size": [self._tile_width_input.value(), self._tile_height_input.value()],
            "grid_size": [self._grid_columns_input.value(), self._grid_rows_input.value()],
            "padding_size": [self._padding_width_input.value(), self._padding_height_input.value()],
            "anti_bleed": self._anti_bleed_input.isChecked(),
            "export_kra": self._export_kra_input.isChecked(),
            "export_image": self._export_image_input.isChecked(),
        }
    
    #endregion

    #region signals
    
    def _on_tile_size_changed(self):
        if not self._grid_size_auto_update_input.isChecked() and not self._padding_size_auto_update_input.isChecked(): return

        tile_width = self._tile_width_input.value()
        tile_height = self._tile_height_input.value()

        if self._grid_size_auto_update_input.isChecked() and self._document:
            document_width, document_height = self._document.width(), self._document.height()
            self._grid_columns_input.setValue(max(1, document_width // tile_width))
            self._grid_rows_input.setValue(max(1, document_height // tile_height))
        
        if self._padding_size_auto_update_input.isChecked() and self._document:
            self._padding_width_input.setValue(max(0, tile_width // 8))
            self._padding_height_input.setValue(max(0, tile_height // 8))
    
    def _on_grid_auto_update_toggled(self):
        grid_auto_update: bool = self._grid_size_auto_update_input.isChecked()
        self._grid_columns_input.setEnabled(not grid_auto_update)
        self._grid_rows_input.setEnabled(not grid_auto_update)
    
    def _on_padding_auto_update_toggled(self):
        padding_auto_update: bool = self._padding_size_auto_update_input.isChecked()
        self._padding_width_input.setEnabled(not padding_auto_update)
        self._padding_height_input.setEnabled(not padding_auto_update)

    #endregion

class PadderDialog:
    def __init__(self):
        dialog: QDialog = QDialog()
        dialog.setWindowTitle("Spritesheet Editor: Padder")

        layout: QVBoxLayout = QVBoxLayout()

        document: any = Krita.instance().activeDocument()
        padder_widget: PadderWidget = PadderWidget(document)

        layout.addWidget(padder_widget)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.button(QDialogButtonBox.Ok).setText("Apply Padding")
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)

        dialog.setLayout(layout)

        if dialog.exec_() != QDialog.Accepted: return None

        padder_widget.run_padder()