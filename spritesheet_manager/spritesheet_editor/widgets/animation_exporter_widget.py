from krita import Krita
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtWidgets import QWidget, QDialog, QGroupBox, QGridLayout, QHBoxLayout, QVBoxLayout, QLabel, QSpinBox, QCheckBox, QLineEdit, QDialogButtonBox
from ...core.serializer import Serializer
from ...core.animation_exporter import AnimationExporter
from ...ui.widgets import LinkButton

MAX_INT = 2147483647
PREVIEW_TIMER_INTERVAL = 1000
PREVIEW_ASPECT_RATIO = 16 / 9
PREVIEW_WINDOW_SIZE = [480, 270, 640, 360]

WIDGET_KEY: str = "ANIMATION_EXPORTER"
WIDGET_DESCRIPTION: str = "Animation Exporter settings"

DEFAULTS: dict[str, any] = {
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
        layout.addWidget(self._build_options_group())
        layout.addWidget(self._build_output_group())

        self.setLayout(layout)

        self.refresh_ui()
    
    def run_animation_exporter(self):
        animation_exporter: AnimationExporter = AnimationExporter(**self._get_animation_exporter_arguments())
        animation_exporter.run()
    
    def _get_animation_exporter_arguments(self) -> dict[str, any]:
        return {
            "document": self._document,
            "export_name": self._export_name_input.text(),
            "is_export_kra": self._is_export_kra_input.isChecked(),
            "is_export_image": self._is_export_image_input.isChecked(),
        }

    def refresh_ui(self):
        self._on_tile_size_changed()
        self._on_grid_auto_update_toggled()
        self._on_padding_auto_update_toggled()
    
    def _update_preview(self):
        animation_exporter_arguments: dict[str, any] = self._get_animation_exporter_arguments()
        padder: AnimationExporter = AnimationExporter(**animation_exporter_arguments)
        preview_document, final_width, final_height = padder.run(True)

        if preview_document:
            q_image: QImage = preview_document.thumbnail(PREVIEW_WINDOW_SIZE[0], PREVIEW_WINDOW_SIZE[1])
            preview_document.close()

            self._preview_window.setPixmap(QPixmap.fromImage(q_image))
            self._preview_label.setText(f"Export Resolution: {final_width}x{final_height} px")

    
    def _get_default_animation_export_name(self) -> str:
        return self._document.name() + DEFAULTS.get("padded_file_suffix") if self._document else "Animation Spritesheet"
    
    #endregion


class AnimationExporterDialog(QDialog):
    def __init__(self):
        dialog: QDialog = QDialog()
        dialog.setWindowTitle("Spritesheet Editor: Animation Exporter")

        layout: QVBoxLayout = QVBoxLayout()

        document = Krita.instance().activeDocument()
        animation_exporter_widget: AnimationExporterWidget = AnimationExporterWidget(document)

        layout.addWidget(animation_exporter_widget)

        layout.addStretch(1)

        buttons: QDialogButtonBox = QDialogButtonBox(QDialogButtonBox.Cancel | QDialogButtonBox.Ok)
        buttons.button(QDialogButtonBox.Ok).setText("Export Animation")
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)

        dialog.setLayout(layout)

        if dialog.exec_() != QDialog.Accepted: return None

        animation_exporter_widget.run_animation_exporter()