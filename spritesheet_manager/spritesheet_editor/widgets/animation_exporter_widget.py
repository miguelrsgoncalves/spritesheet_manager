from krita import Krita
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtWidgets import QWidget, QDialog, QGroupBox, QGridLayout, QHBoxLayout, QVBoxLayout, QLabel, QSpinBox, QCheckBox, QLineEdit, QDialogButtonBox, QComboBox, QPushButton
from ...core.serializer import Serializer
from ...core.animation_exporter import AnimationExporter
import math

MAX_INT = 2147483647
PREVIEW_TIMER_INTERVAL = 1000
PREVIEW_ASPECT_RATIO = 16 / 9
PREVIEW_WINDOW_SIZE = [480, 270, 640, 360]

WIDGET_KEY: str = "ANIMATION_EXPORTER"
WIDGET_DESCRIPTION: str = "Animation Exporter settings"

DEFAULTS: dict[str, any] = {
    "start_frame": 0,
    "frame_step": 1,
    "packing_type": 0,
    "grid_size": [11, 1],
    "grid_size_auto_update": True,
    "is_export_kra": False,
    "is_export_image": True,
    "animation_file_suffix": "_animation"
}

class AnimationExporterWidget(QWidget):
    def __init__(self, document):
        super().__init__()
        self._document = document

        self._preview_timer: QTimer = QTimer()
        self._preview_timer.setSingleShot(True)
        self._preview_timer.timeout.connect(self._update_preview)

        layout: QVBoxLayout = QVBoxLayout()

        layout.addWidget(self._build_preview_group())
        layout.addWidget(self._build_animation_settings_group())
        layout.addWidget(self._build_output_group())

        self.setLayout(layout)

        self.refresh_ui()
    
    #region functions
    
    def run_animation_exporter(self):
        animation_exporter: AnimationExporter = AnimationExporter(**self._get_animation_exporter_arguments())
        animation_exporter.run()
    
    def _get_animation_exporter_arguments(self) -> dict[str, any]:
        packing_type = list(AnimationExporter.PackingType)[self._packing_type_input.currentIndex()]

        return {
            "document": self._document,
            "start_frame": self._start_frame_input.value(),
            "end_frame": self._end_frame_input.value(),
            "frame_step": self._frame_step_input.value(),
            "columns": self._grid_columns_input.value(),
            "rows": self._grid_rows_input.value(),
            "packing_type": packing_type,
            "export_name": self._export_name_input.text(),
            "is_export_kra": self._is_export_kra_input.isChecked(),
            "is_export_image": self._is_export_image_input.isChecked(),
        }

    def refresh_ui(self):
        self._on_grid_auto_update_toggled()
        self._on_exporter_argument_changed()

    def _update_preview(self):
        self._preview_window.clear()
        self._preview_status_label.setText("Updating preview...")

        animation_exporter_arguments: dict[str, any] = self._get_animation_exporter_arguments()
        exporter: AnimationExporter = AnimationExporter(**animation_exporter_arguments)
        preview_document, final_width, final_height = exporter.run(True)

        if preview_document:
            q_image: QImage = preview_document.thumbnail(PREVIEW_WINDOW_SIZE[0], PREVIEW_WINDOW_SIZE[1])
            preview_document.close()

            self._preview_window.setPixmap(QPixmap.fromImage(q_image))
            self._preview_label.setText(f"Export Resolution: {final_width}x{final_height} px")

        self._preview_status_label.setText("")
    
    def _get_default_animation_export_name(self) -> str:
        return self._document.name() + DEFAULTS.get("animation_file_suffix") if self._document else "Animation Spritesheet"
    
    #endregion
    
    #region groups

    def _build_preview_group(self):
        group: QWidget = QWidget()
        
        preview_layout: QVBoxLayout = QVBoxLayout(group)
        preview_layout.setAlignment(Qt.AlignCenter)

        self._preview_window: QLabel = QLabel()
        self._preview_window.setMinimumSize(PREVIEW_WINDOW_SIZE[0], PREVIEW_WINDOW_SIZE[1])
        self._preview_window.setMaximumSize(PREVIEW_WINDOW_SIZE[2], PREVIEW_WINDOW_SIZE[3])
        
        self._preview_window.setSizePolicy(
            self._preview_window.sizePolicy().Expanding,
            self._preview_window.sizePolicy().Expanding
        )
        self._preview_window.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._preview_window.setStyleSheet("""
            QLabel {
                background-color: #313131;
                border-radius: 4px;
            }"""
        )

        self._preview_label: QLabel = QLabel("Export Resolution: 0x0 px")
        self._preview_label.setAlignment(Qt.AlignCenter)
        self._preview_label.setToolTip("The preview image is scaled down, resulting in a lower quality image.")

        controls_layout: QHBoxLayout = QHBoxLayout()
        self._preview_status_label: QLabel = QLabel("Preview up to date.")
        
        self._auto_update_preview_checkbox: QCheckBox = QCheckBox("Auto-update Preview")
        self._auto_update_preview_checkbox.setChecked(True)
        self._auto_update_preview_checkbox.toggled.connect(self._on_exporter_argument_changed)

        self._manual_update_button: QPushButton = QPushButton("Refresh")
        self._manual_update_button.clicked.connect(self._update_preview)

        controls_layout.addWidget(self._preview_status_label)
        controls_layout.addWidget(self._auto_update_preview_checkbox)
        controls_layout.addWidget(self._manual_update_button)

        preview_layout.addWidget(self._preview_window)
        preview_layout.addWidget(self._preview_label)
        preview_layout.addLayout(controls_layout)

        return group

    def _build_animation_settings_group(self):
        group: QGroupBox = QGroupBox("Animation Exporter Settings")
        animation_exporter_settings_layout: QHBoxLayout = QHBoxLayout()

        #region frame_settings

        frame_settings_layout: QGridLayout = QGridLayout()
        frame_settings_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self._start_frame_input: QSpinBox = QSpinBox()
        self._start_frame_input.setRange(0, MAX_INT)
        self._start_frame_input.setValue(DEFAULTS.get("start_frame"))
        self._start_frame_input.valueChanged.connect(self._on_frames_changed)
        
        animation_length: int = self._document.animationLength()
        self._end_frame_input: QSpinBox = QSpinBox()
        self._end_frame_input.setRange(0, MAX_INT)
        self._end_frame_input.setValue(animation_length)
        self._end_frame_input.valueChanged.connect(self._on_frames_changed)

        self._frame_step_input: QSpinBox = QSpinBox()
        self._frame_step_input.setRange(1, MAX_INT)
        self._frame_step_input.setValue(DEFAULTS.get("frame_step"))
        self._frame_step_input.valueChanged.connect(self._on_frames_changed)

        frame_settings_layout.addWidget(QLabel("Animation Settings"), 0, 0, 1, 2, Qt.AlignmentFlag.AlignLeft)
        frame_settings_layout.addWidget(QLabel("Start Frame:"), 1, 0, Qt.AlignmentFlag.AlignRight)
        frame_settings_layout.addWidget(self._start_frame_input, 1, 1)
        frame_settings_layout.addWidget(QLabel("End Frame:"), 2, 0, Qt.AlignmentFlag.AlignRight)
        frame_settings_layout.addWidget(self._end_frame_input, 2, 1)
        frame_settings_layout.addWidget(QLabel("Frame Step:"), 3, 0, Qt.AlignmentFlag.AlignRight)
        frame_settings_layout.addWidget(self._frame_step_input, 3, 1)

        #endregion

        #region grid_size

        grid_size_layout: QGridLayout = QGridLayout()
        grid_size_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self._packing_type_input: QComboBox = QComboBox()
        self._packing_type_input.addItems(["Horizontal", "Vertical", "Square"])
        self._packing_type_input.setCurrentIndex(DEFAULTS.get("packing_type"))
        self._packing_type_input.currentIndexChanged.connect(self._on_frames_changed)

        self._grid_columns_input: QSpinBox = QSpinBox()
        self._grid_columns_input.setRange(1, MAX_INT)
        self._grid_columns_input.setValue(DEFAULTS.get("grid_size")[0])
        self._grid_columns_input.valueChanged.connect(self._on_grid_size_changed)
        
        self._grid_rows_input: QSpinBox = QSpinBox()
        self._grid_rows_input.setRange(1, MAX_INT)
        self._grid_rows_input.setValue(DEFAULTS.get("grid_size")[1])
        self._grid_rows_input.valueChanged.connect(self._on_grid_size_changed)

        self._grid_size_auto_update_checkbox: QCheckBox = QCheckBox("Auto-calculate Layout")
        self._grid_size_auto_update_checkbox.setChecked(DEFAULTS.get("grid_size_auto_update"))
        self._grid_size_auto_update_checkbox.setToolTip("Auto-calculate columns and rows based on frames and packing type.")
        self._grid_size_auto_update_checkbox.toggled.connect(self._on_grid_auto_update_toggled)

        grid_size_layout.addWidget(QLabel("Layout Strategy"), 0, 0, 1, 2, Qt.AlignmentFlag.AlignLeft)
        grid_size_layout.addWidget(QLabel("Packing:"), 1, 0, Qt.AlignmentFlag.AlignRight)
        grid_size_layout.addWidget(self._packing_type_input, 1, 1)
        grid_size_layout.addWidget(QLabel("Columns:"), 2, 0, Qt.AlignmentFlag.AlignRight)
        grid_size_layout.addWidget(self._grid_columns_input, 2, 1)
        grid_size_layout.addWidget(QLabel("Rows:"), 3, 0, Qt.AlignmentFlag.AlignRight)
        grid_size_layout.addWidget(self._grid_rows_input, 3, 1)
        grid_size_layout.addWidget(self._grid_size_auto_update_checkbox, 4, 0, 1, 2, Qt.AlignmentFlag.AlignLeft)

        #endregion

        animation_exporter_settings_layout.addLayout(frame_settings_layout)
        animation_exporter_settings_layout.addSpacing(24)
        animation_exporter_settings_layout.addLayout(grid_size_layout)

        group.setLayout(animation_exporter_settings_layout)
        return group

    def _build_output_group(self):
        group: QGroupBox = QGroupBox("Output")
        output_layout: QVBoxLayout = QVBoxLayout()

        export_name_layout: QHBoxLayout = QHBoxLayout()
        export_name_layout.addWidget(QLabel("File name"))
        self._export_name_input: QLineEdit = QLineEdit(self._get_default_animation_export_name())
        export_name_layout.addWidget(self._export_name_input)
        
        self._is_export_kra_input: QCheckBox = QCheckBox("Save .kra")
        self._is_export_kra_input.setChecked(DEFAULTS.get("is_export_kra"))

        self._is_export_image_input: QCheckBox = QCheckBox("Export image")
        self._is_export_image_input.setChecked(DEFAULTS.get("is_export_image"))

        output_layout.addLayout(export_name_layout)
        output_layout.addWidget(self._is_export_kra_input)
        output_layout.addWidget(self._is_export_image_input)

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
        self._start_frame_input.setValue(state.get("start_frame", DEFAULTS["start_frame"]))
        self._end_frame_input.setValue(state.get("end_frame", DEFAULTS["end_frame"]))
        self._frame_step_input.setValue(state.get("frame_step", DEFAULTS["frame_step"]))
        self._packing_type_input.setCurrentIndex(state.get("packing_type", DEFAULTS["packing_type"]))

        columns, rows = state.get("grid_size", DEFAULTS["grid_size"])
        self._grid_columns_input.setValue(columns)
        self._grid_rows_input.setValue(rows)

        self._grid_size_auto_update_checkbox.setChecked(state.get("grid_size_auto_update", DEFAULTS["grid_size_auto_update"]))
        self._is_export_kra_input.setChecked(state.get("is_export_kra", DEFAULTS["is_export_kra"]))
        self._is_export_image_input.setChecked(state.get("is_export_image", DEFAULTS["is_export_image"]))

        self.refresh_ui()

    def _save_state(self):
        krita = Krita.instance()
        document = krita.activeDocument()

        data: dict[str, any] = self._get_state()
        Serializer.save_state(document, WIDGET_KEY, data, WIDGET_DESCRIPTION)
    
    def _get_state(self) -> dict[str, any]:
        return {
            "start_frame": self._start_frame_input.value(),
            "end_frame": self._end_frame_input.value(),
            "frame_step": self._frame_step_input.value(),
            "packing_type": self._packing_type_input.currentIndex(),
            "grid_size": [self._grid_columns_input.value(), self._grid_rows_input.value()],
            "grid_size_auto_update": self._grid_size_auto_update_checkbox.isChecked(),
            "is_export_kra": self._is_export_kra_input.isChecked(),
            "is_export_image": self._is_export_image_input.isChecked(),
        }
    
    #endregion

    #region signals

    def _on_exporter_argument_changed(self):
        self._preview_window.clear()
        self._preview_window.setText("Preview out of date")

        if self._auto_update_preview_checkbox.isChecked():
            self._preview_status_label.setText("Preview update scheduled")
            self._preview_timer.start(PREVIEW_TIMER_INTERVAL)
    
    def _on_frames_changed(self):
        if self._start_frame_input.value() > self._end_frame_input.value():
            self._end_frame_input.blockSignals(True)
            self._end_frame_input.setValue(self._start_frame_input.value())
            self._end_frame_input.blockSignals(False)

        if self._grid_size_auto_update_checkbox.isChecked():
            start = self._start_frame_input.value()
            end = self._end_frame_input.value()
            step = self._frame_step_input.value()
            
            total_frames = max(1, ((end - start) // step) + 1)
            packing = self._packing_type_input.currentIndex()

            columns = 1
            rows = 1

            if packing == 0:
                columns = total_frames
                rows = 1
            elif packing == 1:
                columns = 1
                rows = total_frames
            elif packing == 2:
                columns = max(1, math.ceil(math.sqrt(total_frames)))
                rows = max(1, math.ceil(total_frames / columns))
            
            self._grid_columns_input.blockSignals(True)
            self._grid_rows_input.blockSignals(True)
            
            self._grid_columns_input.setValue(columns)
            self._grid_rows_input.setValue(rows)
            
            self._grid_columns_input.blockSignals(False)
            self._grid_rows_input.blockSignals(False)

        self._on_exporter_argument_changed()
    
    def _on_grid_size_changed(self):
        if not self._grid_size_auto_update_checkbox.isChecked():
            sender = self.sender()
            
            start = self._start_frame_input.value()
            end = self._end_frame_input.value()
            step = self._frame_step_input.value()
            total_frames = max(1, ((end - start) // step) + 1)

            if sender == self._grid_columns_input:
                columns = self._grid_columns_input.value()
                calculated_rows = max(1, math.ceil(total_frames / columns))
                
                self._grid_rows_input.blockSignals(True)
                self._grid_rows_input.setValue(calculated_rows)
                self._grid_rows_input.blockSignals(False)
                
            elif sender == self._grid_rows_input:
                rows = self._grid_rows_input.value()
                calculated_columns = max(1, math.ceil(total_frames / rows))
                
                self._grid_columns_input.blockSignals(True)
                self._grid_columns_input.setValue(calculated_columns)
                self._grid_columns_input.blockSignals(False)
        
        self._on_exporter_argument_changed()
    
    def _on_grid_auto_update_toggled(self):
        auto_update: bool = self._grid_size_auto_update_checkbox.isChecked()
        self._grid_columns_input.setEnabled(not auto_update)
        self._grid_rows_input.setEnabled(not auto_update)

        if auto_update:
            self._on_frames_changed()

class AnimationExporterDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Spritesheet Editor: Animation Exporter")

        layout: QVBoxLayout = QVBoxLayout()

        document = Krita.instance().activeDocument()
        animation_exporter_widget: AnimationExporterWidget = AnimationExporterWidget(document)

        layout.addWidget(animation_exporter_widget)

        layout.addStretch(1)

        buttons: QDialogButtonBox = QDialogButtonBox(QDialogButtonBox.Cancel | QDialogButtonBox.Ok)
        buttons.button(QDialogButtonBox.Ok).setText("Export Animation")
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        self.setLayout(layout)

        if self.exec_() != QDialog.Accepted: return None

        animation_exporter_widget.run_animation_exporter()