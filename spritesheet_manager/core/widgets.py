from krita import Krita
from PyQt5.QtCore import Qt, QSize, pyqtSignal, QTimer
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtWidgets import QToolButton, QWidget, QHBoxLayout, QVBoxLayout, QLabel, QCheckBox, QPushButton

class LinkButton(QToolButton):
    link_changed = pyqtSignal(bool)

    def __init__(self):        
        super().__init__()

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
            refresh_callback: callable,
            timer_interval: int = 1000,
            timer_tick_interval: int = 10,
            timer_tick_label: str = "Refreshing preview in {:.3f} s",
            aspect_ratio: int = 16 / 9,
            window_size: list[int] = [480, 270, 640, 360],
    ):
        super().__init__()
        
        self._refresh_callback: callable = refresh_callback
        self._timer_interval: int = timer_interval
        self._timer_tick_interval: int = timer_tick_interval
        self._timer_tick_label: str = timer_tick_label
        self._aspect_ration: int = aspect_ratio
        self._window_size: list[int] = window_size

        self._preview_timer: QTimer = QTimer()
        self._preview_timer_interval: int = 0
        self._preview_timer.timeout.connect(self._on_timer_tick)

        preview_layout: QVBoxLayout = QVBoxLayout(self)
        preview_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        preview_controls_layout: QHBoxLayout = QHBoxLayout()

        self._auto_update_preview_checkbox: QCheckBox = QCheckBox("Auto-update Preview")
        self._auto_update_preview_checkbox.setChecked(True)
        self._auto_update_preview_checkbox.toggled.connect(self.request_refresh)

        self._preview_manual_update_button: QPushButton = QPushButton("Refresh")
        self._preview_manual_update_button.clicked.connect(self.force_refresh)

        preview_controls_layout.addWidget(self._auto_update_preview_checkbox)
        preview_controls_layout.addWidget(self._preview_manual_update_button)
        
        self._preview_window: QLabel = QLabel()
        self._preview_window.setMinimumSize(self._window_size[0], self._window_size[1])
        self._preview_window.setMaximumSize(self._window_size[2], self._window_size[3])
        
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

        self._preview_resolution_label: QLabel = QLabel("Export Resolution: 0x0 px")
        self._preview_resolution_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._preview_resolution_label.setToolTip("The preview image is scaled down, resulting in a lower quality image.")

        preview_layout.addLayout(preview_controls_layout)
        preview_layout.addWidget(self._preview_window)
        preview_layout.addWidget(self._preview_resolution_label)
        
        self.setLayout(preview_layout)
    
    def request_refresh(self):
        if self._auto_update_preview_checkbox.isChecked():
            self._preview_timer_interval = self._timer_interval
            self._preview_timer.start(self._timer_tick_interval)
        else:
            self._preview_timer.stop()
            self._preview_window.setText("Preview out of date")
    
    def force_refresh(self):
        self._preview_timer.stop()
        self._refresh()
    
    def _refresh(self):
        if not self._refresh_callback: return

        self._preview_window.clear()
        self._preview_window.setText("Rendering...")

        q_image, width, height = self._refresh_callback()

        if q_image:
            self._preview_window.setPixmap(QPixmap.fromImage(q_image))
            self._preview_resolution_label.setText(f"Export Resolution: {width}x{height} px")

    def _on_timer_tick(self):
        self._preview_timer_interval -= self._timer_tick_interval

        if self._preview_timer_interval > 0:
            time = self._preview_timer_interval / 1000.0
            self._preview_window.setText(self._timer_tick_label.format(time))
        else:
            self._preview_timer.stop()
            self._refresh()