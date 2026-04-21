from krita import Krita
from PyQt5.QtCore import Qt, QSize, pyqtSignal, QTimer
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtWidgets import QToolButton, QWidget, QDialog, QGroupBox, QGridLayout, QHBoxLayout, QVBoxLayout, QLabel, QSpinBox, QCheckBox, QLineEdit, QDialogButtonBox, QComboBox, QPushButton

class LinkButton(QToolButton):
    link_changed = pyqtSignal(bool)

    def __init__(self, parent = None):
        super().__init__(parent)
        
        self.setIconSize(QSize(8, 24))
        self.setFixedSize(16, 32)
        self.setAutoRaise(True)

        self._is_linked: bool = None
        self.clicked.connect(self._on_button_clicked)
        self.set_link(True)

    def set_link(self, is_linked: bool):
        if self._is_linked == is_linked: return

        self._is_linked = is_linked

        icon_name: str = "chain-icon" if is_linked else "chain-broken-icon"
        self.setIcon(Krita.instance().icon(icon_name))

        self.link_changed.emit(self._is_linked)
        self.update()

    def is_linked(self) -> bool:
        return self._is_linked

    def _on_button_clicked(self):
        self.set_link(not self._is_linked)

class PreviewWindow(QWidget):
    def __init__(
            self,
            parent = None,
            timer_interval = 1000,
            timer_tick_interval = 10,
            timer_tick_label = "Refreshing preview in {:.3f} s",
            aspect_ratio = 16 / 9,
            window_size = [480, 270, 640, 360],
    ):
        self._timer_interval = timer_interval
        self._timer_tick_interval = timer_tick_interval
        self._timer_tick_label = timer_tick_label
        self._aspect_ration = aspect_ratio
        self._window_size = window_size

