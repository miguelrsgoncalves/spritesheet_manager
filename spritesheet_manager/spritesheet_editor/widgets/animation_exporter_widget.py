from krita import Krita
from PyQt5.QtWidgets import QWidget, QDialog, QVBoxLayout, QDialogButtonBox
from ...core.animation_exporter import AnimationExporter

class AnimationExporterWidget(QWidget):
    def __init__(self, document):
        super().__init__()
        self._document = document
    
    def run_animation_exporter(self):
        animation_exporter: AnimationExporter = AnimationExporter(self._document)
        animation_exporter.run()

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