from krita import Krita
from PyQt5.QtCore import QSize, pyqtSignal
from PyQt5.QtWidgets import QToolButton

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