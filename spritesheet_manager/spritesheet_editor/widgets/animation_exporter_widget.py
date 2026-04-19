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