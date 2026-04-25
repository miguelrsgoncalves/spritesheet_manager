from krita import Krita
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QDialog, QGroupBox, QGridLayout, QHBoxLayout, QVBoxLayout, QLabel, QSpinBox, QCheckBox, QLineEdit, QDialogButtonBox
from ...core.serializer import Serializer
from ...core.padder import Padder
from ...core.widgets import PreviewWindow, LinkButton

MAX_INT: int = 2147483647

class PadderWidget(QWidget):
    WIDGET_KEY: str = "PADDER"
    WIDGET_DESCRIPTION: str = "Padder settings"

    DEFAULTS: dict[str, any] = {
        "tile_size": [64, 64],
        "grid_size": [1, 1],
        "grid_size_auto_update": True,
        "padding_size": [8, 8],
        "padding_size_auto_update": True,
        "is_anti_bleed": True,
        "is_export_kra": False,
        "is_export_image": True,
        "padded_file_suffix": "_padded"
    }

    def __init__(self, parent, document):
        super().__init__(parent)

        self._document = document

        layout: QVBoxLayout = QVBoxLayout()

        self._preview_window: PreviewWindow = PreviewWindow(self._refresh_preview)

        layout.addWidget(self._preview_window)
        layout.addWidget(self._build_padding_settings_group())
        layout.addWidget(self._build_options_group())
        layout.addWidget(self._build_output_group())

        self.setLayout(layout)

        self.load_state()

        self.refresh_ui()

    #region functions

    def run_padder(self):
        padder: Padder = Padder(**self._get_padder_arguments())
        padder.run()
    
    def _get_padder_arguments(self) -> dict[str, any]:
        return {
            "document": self._document,
            "tile_size": [self._tile_width_input.value(), self._tile_height_input.value()],
            "grid_size": [self._grid_columns_input.value(), self._grid_rows_input.value()],
            "padding_size": [self._padding_width_input.value(), self._padding_height_input.value()],
            "is_anti_bleed": self._is_anti_bleed_input.isChecked(),
            "export_name": self._export_name_input.text(),
            "is_export_kra": self._is_export_kra_input.isChecked(),
            "is_export_image": self._is_export_image_input.isChecked(),
        }

    def refresh_ui(self):
        self._on_tile_size_changed()
        self._on_grid_auto_update_toggled()
        self._on_padding_auto_update_toggled()
        self._on_padder_argument_changed()
    
    def _refresh_preview(self):
        padder_arguments: dict[str, any] = self._get_padder_arguments()
        exporter: Padder = Padder(**padder_arguments)
        preview_image, preview_arguments = exporter.run(True, [self._preview_window.window_size[0], self._preview_window.window_size[1]])
        return (preview_image, preview_arguments) if preview_image else (None, {})
    
    def _get_default_padded_export_name(self) -> str:
        return self._document.name() + self.DEFAULTS.get("padded_file_suffix") if self._document else "Padded Spritesheet"
    
    #endregion

    #region groups

    def _build_padding_settings_group(self):
        group: QGroupBox = QGroupBox("Padding Settings")
        padding_settings_layout: QHBoxLayout = QHBoxLayout()

        #region tile_size

        tile_size_layout: QGridLayout = QGridLayout()
        tile_size_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self._tile_width_input: QSpinBox = QSpinBox()
        self._tile_width_input.setRange(1, MAX_INT)
        self._tile_width_input.setValue(self.DEFAULTS.get("tile_size")[0])
        self._tile_width_input.valueChanged.connect(self._on_tile_size_changed)
        self._tile_width_input.valueChanged.connect(self._on_padder_argument_changed)
        
        self._tile_height_input: QSpinBox = QSpinBox()
        self._tile_height_input.setRange(1, MAX_INT)
        self._tile_height_input.setValue(self.DEFAULTS.get("tile_size")[1])
        self._tile_height_input.valueChanged.connect(self._on_tile_size_changed)
        self._tile_height_input.valueChanged.connect(self._on_padder_argument_changed)

        self._tile_size_link_button: LinkButton = LinkButton()
        self._tile_size_link_button.setToolTip("Link values")
        self._tile_size_link_button.link_changed.connect(self._on_tile_size_changed)

        tile_size_layout.addWidget(QLabel("Tile Size"), 0, 0, 1, 3, Qt.AlignmentFlag.AlignLeft)
        tile_size_layout.addWidget(QLabel("Width:"), 1, 0, Qt.AlignmentFlag.AlignRight)
        tile_size_layout.addWidget(self._tile_width_input, 1, 1)
        tile_size_layout.addWidget(QLabel("Height:"), 2, 0, Qt.AlignmentFlag.AlignRight)
        tile_size_layout.addWidget(self._tile_height_input, 2, 1)
        tile_size_layout.addWidget(self._tile_size_link_button, 1, 3, 2, 3, Qt.AlignmentFlag.AlignVCenter)

        #endregion

        #region grid_size

        grid_size_layout: QGridLayout = QGridLayout()
        grid_size_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self._grid_columns_input: QSpinBox = QSpinBox()
        self._grid_columns_input.setRange(1, MAX_INT)
        self._grid_columns_input.setValue(self.DEFAULTS.get("grid_size")[0])
        self._grid_columns_input.valueChanged.connect(self._on_grid_size_changed)
        self._grid_columns_input.valueChanged.connect(self._on_padder_argument_changed)
        
        self._grid_rows_input: QSpinBox = QSpinBox()
        self._grid_rows_input.setRange(1, MAX_INT)
        self._grid_rows_input.setValue(self.DEFAULTS.get("grid_size")[1])
        self._grid_rows_input.valueChanged.connect(self._on_grid_size_changed)
        self._grid_rows_input.valueChanged.connect(self._on_padder_argument_changed)

        self._grid_size_auto_update_checkbox: QCheckBox = QCheckBox("Auto-update")
        self._grid_size_auto_update_checkbox.setChecked(self.DEFAULTS.get("grid_size_auto_update"))
        self._grid_size_auto_update_checkbox.setToolTip("Auto-update the grid size using the tile size and the document's size.")
        self._grid_size_auto_update_checkbox.toggled.connect(self._on_grid_auto_update_toggled)

        self._grid_size_link_button: LinkButton = LinkButton()
        self._grid_size_link_button.setToolTip("Link values")
        self._grid_size_link_button.link_changed.connect(self._on_grid_size_changed)

        grid_size_layout.addWidget(QLabel("Grid Size"), 0, 0, 1, 3, Qt.AlignmentFlag.AlignLeft)
        grid_size_layout.addWidget(QLabel("Columns:"), 1, 0, Qt.AlignmentFlag.AlignRight)
        grid_size_layout.addWidget(self._grid_columns_input, 1, 1)
        grid_size_layout.addWidget(QLabel("Rows:"), 2, 0, Qt.AlignmentFlag.AlignRight)
        grid_size_layout.addWidget(self._grid_rows_input, 2, 1)
        grid_size_layout.addWidget(self._grid_size_link_button, 1, 3, 2, 3, Qt.AlignmentFlag.AlignVCenter)
        grid_size_layout.addWidget(self._grid_size_auto_update_checkbox, 3, 0, 1, 3, Qt.AlignmentFlag.AlignLeft)

        #endregion

        #region padding_size
        
        padding_size_layout: QGridLayout = QGridLayout()
        padding_size_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self._padding_width_input: QSpinBox = QSpinBox()
        self._padding_width_input.setRange(1, MAX_INT)
        self._padding_width_input.setValue(self.DEFAULTS.get("padding_size")[0])
        self._padding_width_input.valueChanged.connect(self._on_padding_size_changed)
        self._padding_width_input.valueChanged.connect(self._on_padder_argument_changed)
        
        self._padding_height_input: QSpinBox = QSpinBox()
        self._padding_height_input.setRange(1, MAX_INT)
        self._padding_height_input.setValue(self.DEFAULTS.get("padding_size")[1])
        self._padding_height_input.valueChanged.connect(self._on_padding_size_changed)
        self._padding_height_input.valueChanged.connect(self._on_padder_argument_changed)

        self._padding_size_auto_update_checkbox: QCheckBox = QCheckBox("Auto-update")
        self._padding_size_auto_update_checkbox.setChecked(self.DEFAULTS.get("padding_size_auto_update"))
        self._padding_size_auto_update_checkbox.setToolTip("Auto-update the padding size using the tile size, by default it's tile_size / 8.")
        self._padding_size_auto_update_checkbox.toggled.connect(self._on_padding_auto_update_toggled)

        self._padding_size_link_button: LinkButton = LinkButton()
        self._padding_size_link_button.setToolTip("Link values")
        self._padding_size_link_button.link_changed.connect(self._on_padding_size_changed)

        padding_size_layout.addWidget(QLabel("Padding Size"), 0, 0, 1, 3, Qt.AlignmentFlag.AlignLeft)
        padding_size_layout.addWidget(QLabel("Width:"), 1, 0, Qt.AlignmentFlag.AlignRight)
        padding_size_layout.addWidget(self._padding_width_input, 1, 1)
        padding_size_layout.addWidget(QLabel("Height:"), 2, 0, Qt.AlignmentFlag.AlignRight)
        padding_size_layout.addWidget(self._padding_height_input, 2, 1)
        padding_size_layout.addWidget(self._padding_size_link_button, 1, 3, 2, 3, Qt.AlignmentFlag.AlignVCenter)
        padding_size_layout.addWidget(self._padding_size_auto_update_checkbox, 3, 0, 1, 3, Qt.AlignmentFlag.AlignLeft)

        #endregion

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

        self._is_anti_bleed_input: QCheckBox = QCheckBox("Anti-pixel-bleed padding")
        self._is_anti_bleed_input.setChecked(self.DEFAULTS.get("is_anti_bleed"))
        self._is_anti_bleed_input.setToolTip("Repeats edge pixels into the padding area to prevent colour bleeding at tile seams.")
        self._is_anti_bleed_input.toggled.connect(self._on_padder_argument_changed)

        options_layout.addWidget(self._is_anti_bleed_input)

        group.setLayout(options_layout)
        return group

    def _build_output_group(self):
        group: QGroupBox = QGroupBox("Output")
        output_layout: QHBoxLayout = QVBoxLayout()

        export_name_layout: QHBoxLayout = QHBoxLayout()
        export_name_layout.addWidget(QLabel("File name"))
        self._export_name_input: QLineEdit = QLineEdit(self._get_default_padded_export_name())
        export_name_layout.addWidget(self._export_name_input)
        self._is_export_kra_input: QCheckBox = QCheckBox("Save .kra")
        self._is_export_kra_input.setChecked(False)
        self._is_export_image_input: QCheckBox = QCheckBox("Export image")
        self._is_export_image_input.setChecked(True)

        output_layout.addLayout(export_name_layout)
        output_layout.addWidget(self._is_export_kra_input)
        output_layout.addWidget(self._is_export_image_input)

        group.setLayout(output_layout)
        return group

    #endregion

    #region state

    def load_state(self):
        state: dict[str, any] = Serializer.load_state(self._document, self.WIDGET_KEY)
        self._set_state(state)
    
    def _set_state(self, state):
        tile_width, tile_height = state.get("tile_size", self.DEFAULTS["tile_size"])
        self._tile_width_input.setValue(tile_width)
        self._tile_height_input.setValue(tile_height)

        columns, rows = state.get("grid_size", self.DEFAULTS["grid_size"])
        self._grid_columns_input.setValue(columns)
        self._grid_rows_input.setValue(rows)

        padding_width, padding_height = state.get("padding_size", self.DEFAULTS["padding_size"])
        self._padding_width_input.setValue(padding_width)
        self._padding_height_input.setValue(padding_height)

        self._is_anti_bleed_input.setChecked(state.get("is_anti_bleed", self.DEFAULTS["is_anti_bleed"]))
        self._is_export_kra_input.setChecked(state.get("is_export_kra", self.DEFAULTS["is_export_kra"]))
        self._is_export_image_input.setChecked(state.get("is_export_image", self.DEFAULTS["is_export_image"]))

        self.refresh_ui()

    def save_state(self):
        data: dict[str, any] = self._get_state()
        Serializer.save_state(self._document, self.WIDGET_KEY, data, self.WIDGET_DESCRIPTION)
    
    def _get_state(self) -> dict[str, any]:
        return {
            "tile_size": [self._tile_width_input.value(), self._tile_height_input.value()],
            "grid_size": [self._grid_columns_input.value(), self._grid_rows_input.value()],
            "padding_size": [self._padding_width_input.value(), self._padding_height_input.value()],
            "is_anti_bleed": self._is_anti_bleed_input.isChecked(),
            "is_export_kra": self._is_export_kra_input.isChecked(),
            "is_export_image": self._is_export_image_input.isChecked(),
        }
    
    #endregion

    #region signals

    def _on_padder_argument_changed(self):
        self._preview_window.request_refresh()
    
    def _on_tile_size_changed(self):
        if self._tile_size_link_button.is_linked():
            sender = self.sender()
            
            if sender == self._tile_width_input:
                self._tile_height_input.blockSignals(True)
                self._tile_height_input.setValue(self._tile_width_input.value())
                self._tile_height_input.blockSignals(False)
            
            else:
                self._tile_width_input.blockSignals(True)
                self._tile_width_input.setValue(self._tile_height_input.value())
                self._tile_width_input.blockSignals(False)


        if self._grid_size_auto_update_checkbox.isChecked() or self._padding_size_auto_update_checkbox.isChecked():
            tile_width = self._tile_width_input.value()
            tile_height = self._tile_height_input.value()

            if self._grid_size_auto_update_checkbox.isChecked() and self._document:
                document_width, document_height = self._document.width(), self._document.height()
                self._grid_columns_input.setValue(max(1, document_width // tile_width))
                self._grid_rows_input.setValue(max(1, document_height // tile_height))
            
            if self._padding_size_auto_update_checkbox.isChecked() and self._document:
                self._padding_width_input.setValue(max(0, tile_width // 8))
                self._padding_height_input.setValue(max(0, tile_height // 8))
    
    def _on_grid_size_changed(self):
        if not self._grid_size_auto_update_checkbox.isChecked() and self._grid_size_link_button.is_linked():
            sender = self.sender()

            if sender == self._grid_columns_input:
                self._grid_rows_input.blockSignals(True)
                self._grid_rows_input.setValue(self._grid_columns_input.value())
                self._grid_rows_input.blockSignals(False)
            else:
                self._grid_columns_input.blockSignals(True)
                self._grid_columns_input.setValue(self._grid_rows_input.value())
                self._grid_columns_input.blockSignals(False)
    
    def _on_grid_auto_update_toggled(self):
        grid_auto_update: bool = self._grid_size_auto_update_checkbox.isChecked()
        self._grid_columns_input.setEnabled(not grid_auto_update)
        self._grid_rows_input.setEnabled(not grid_auto_update)
        self._grid_size_link_button.setEnabled(not grid_auto_update)

        if grid_auto_update == True:
            self._on_tile_size_changed()

    def _on_padding_size_changed(self):
        if not self._padding_size_auto_update_checkbox.isChecked() and self._padding_size_link_button.is_linked():
            sender = self.sender()

            if sender == self._padding_width_input:
                self._padding_height_input.blockSignals(True)
                self._padding_height_input.setValue(self._padding_width_input.value())
                self._padding_height_input.blockSignals(False)
            else:
                self._padding_width_input.blockSignals(True)
                self._padding_width_input.setValue(self._padding_height_input.value())
                self._padding_width_input.blockSignals(False)
    
    def _on_padding_auto_update_toggled(self):
        padding_auto_update: bool = self._padding_size_auto_update_checkbox.isChecked()
        self._padding_width_input.setEnabled(not padding_auto_update)
        self._padding_height_input.setEnabled(not padding_auto_update)
        self._padding_size_link_button.setEnabled(not padding_auto_update)

        if padding_auto_update == True:
            self._on_tile_size_changed()

    #endregion

class PadderDialog(QDialog):
    def __init__(self, parent = None):
        super().__init__(parent)
        
        self.setWindowTitle("Spritesheet Editor: Padder")

        layout: QVBoxLayout = QVBoxLayout()

        document = Krita.instance().activeDocument()
        padder_widget: PadderWidget = PadderWidget(self, document)

        layout.addWidget(padder_widget)

        layout.addStretch(1)

        buttons: QDialogButtonBox = QDialogButtonBox(QDialogButtonBox.Cancel | QDialogButtonBox.Ok)
        buttons.button(QDialogButtonBox.Ok).setText("Apply Padding")
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        self.setLayout(layout)

        if self.exec_() != QDialog.Accepted: return None

        padder_widget.save_state()

        padder_widget.run_padder()