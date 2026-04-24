from krita import Krita
from PyQt5.QtCore import Qt, QSize, pyqtSignal, QTimer
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QToolButton, QWidget, QHBoxLayout, QVBoxLayout, QLabel, QCheckBox, QPushButton

class PreviewWindow(QWidget):
    def __init__(
            self,
            refresh_callback: callable,
            timer_duration: int = 1000,
            timer_tick: int = 10,
            window_size: list[int] = [480, 270, 640, 360],
            aspect_ratio: int = 16 / 9,
            timer_tick_label: str = "Refreshing preview in {:.3f} s",
    ):
        super().__init__()
        
        self._refresh_callback: callable = refresh_callback
        self._timer_duration: int = timer_duration
        self._timer_tick: int = timer_tick
        self.window_size: list[int] = window_size
        self._aspect_ration: int = aspect_ratio
        self._timer_tick_label: str = timer_tick_label

        self._timer: QTimer = QTimer()
        self._timer_countdown: int = 0
        self._timer.timeout.connect(self._on_timer_tick)

        layout: QVBoxLayout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        controls_layout: QHBoxLayout = QHBoxLayout()

        self._auto_update_preview_checkbox: QCheckBox = QCheckBox("Auto-update Preview")
        self._auto_update_preview_checkbox.setChecked(True)
        self._auto_update_preview_checkbox.toggled.connect(self.request_refresh)

        self._manual_update_button: QPushButton = QPushButton("Refresh")
        self._manual_update_button.clicked.connect(self.force_refresh)

        controls_layout.addWidget(self._auto_update_preview_checkbox)
        controls_layout.addWidget(self._manual_update_button)
        
        self._window: QLabel = QLabel()
        self._window.setMinimumSize(self.window_size[0], self.window_size[1])
        self._window.setMaximumSize(self.window_size[2], self.window_size[3])
        
        self._window.setSizePolicy(
            self._window.sizePolicy().Expanding,
            self._window.sizePolicy().Expanding
        )
        self._window.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._window.setStyleSheet("""
            QLabel {
                background-color: #313131;
                border-radius: 4px;
            }"""
        )

        self._export_size_label: QLabel = QLabel()
        self._export_size_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._export_size_label.setToolTip("The preview image is scaled down for faster rendering, resulting in a lower quality image.")

        layout.addLayout(controls_layout)
        layout.addWidget(self._window)
        layout.addWidget(self._export_size_label)
        
        self.setLayout(layout)
    
    def request_refresh(self):
        if self._auto_update_preview_checkbox.isChecked():
            self._timer_countdown = self._timer_duration
            self._timer.start(self._timer_tick)
        else:
            self._timer.stop()
            self._window.setText("Preview out of date")
    
    def force_refresh(self):
        self._timer.stop()
        self._refresh()
    
    def _refresh(self):
        if not self._refresh_callback: return

        self._window.clear()
        self._window.setText("Rendering...")

        q_image, arguments = self._refresh_callback()

        if q_image:
            self._window.setPixmap(QPixmap.fromImage(q_image))

            export_size: list[int] = arguments.get("export_size")
            if export_size:
                self._export_size_label.show()
                self._export_size_label.setText(f"Export Size: {export_size[0]}x{export_size[1]} px")
            else:
                self._export_size_label.hide()

    def _on_timer_tick(self):
        self._timer_countdown -= self._timer_tick

        if self._timer_countdown > 0:
            time = self._timer_countdown / 1000.0
            self._window.setText(self._timer_tick_label.format(time))
        else:
            self._timer.stop()
            self._refresh()

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