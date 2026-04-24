import os
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QSpinBox, QPushButton, QGroupBox, QColorDialog, QFileDialog
)
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QColor, QIcon

_ICONS_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
    "ui", "icons"
)

def _load_link_icon(linked):
    filename = "link.svg" if linked else "unlink.svg"
    path = os.path.join(_ICONS_DIR, filename)
    if os.path.exists(path):
        return QIcon(path)
    return QIcon.fromTheme("insert-link")


class AtlasPanel(QWidget):
    grid_changed = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._grid = None
        self._updating = False
        self._tile_size_linked = True

        layout = QVBoxLayout()
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(6)

        layout.addWidget(self._build_identity_group())
        layout.addWidget(self._build_tile_size_group())
        layout.addWidget(self._build_grid_size_group())
        layout.addWidget(self._build_source_group())
        layout.addWidget(self._build_appearance_group())
        layout.addStretch()

        self.setLayout(layout)
        self.setEnabled(False)

    def _build_identity_group(self):
        group = QGroupBox("Grid")
        layout = QHBoxLayout()
        layout.addWidget(QLabel("Label"))
        self._label_input = QLineEdit()
        self._label_input.textChanged.connect(self._on_label_changed)
        layout.addWidget(self._label_input)
        group.setLayout(layout)
        return group

    def _build_tile_size_group(self):
        group = QGroupBox("Tile Size")
        layout = QHBoxLayout()
        layout.setSpacing(6)

        self._tile_width_spin = QSpinBox()
        self._tile_width_spin.setRange(1, 99999)
        self._tile_height_spin = QSpinBox()
        self._tile_height_spin.setRange(1, 99999)

        self._tile_link_button = QPushButton()
        self._tile_link_button.setFixedSize(22, 22)
        self._tile_link_button.setFlat(True)
        self._tile_link_button.setCheckable(True)
        self._tile_link_button.setChecked(True)
        self._tile_link_button.setIcon(_load_link_icon(True))
        self._tile_link_button.toggled.connect(self._on_tile_link_toggled)

        layout.addWidget(QLabel("W"))
        layout.addWidget(self._tile_width_spin)
        layout.addWidget(self._tile_link_button)
        layout.addWidget(QLabel("H"))
        layout.addWidget(self._tile_height_spin)

        group.setLayout(layout)

        self._tile_width_spin.valueChanged.connect(self._on_tile_width_changed)
        self._tile_height_spin.valueChanged.connect(self._on_tile_height_changed)

        return group

    def _build_grid_size_group(self):
        group = QGroupBox("Grid Size")
        layout = QHBoxLayout()
        layout.setSpacing(6)

        self._columns_spin = QSpinBox()
        self._columns_spin.setRange(1, 99999)
        self._rows_spin = QSpinBox()
        self._rows_spin.setRange(1, 99999)

        layout.addWidget(QLabel("Columns"))
        layout.addWidget(self._columns_spin)
        layout.addWidget(QLabel("Rows"))
        layout.addWidget(self._rows_spin)

        group.setLayout(layout)

        self._columns_spin.valueChanged.connect(self._on_grid_size_changed)
        self._rows_spin.valueChanged.connect(self._on_grid_size_changed)

        return group

    def _build_source_group(self):
        group = QGroupBox("Source Image")
        layout = QVBoxLayout()
        layout.setSpacing(4)

        self._source_label = QLabel("No image assigned")
        self._source_label.setWordWrap(True)
        layout.addWidget(self._source_label)

        button_row = QHBoxLayout()
        browse_button = QPushButton("Browse…")
        browse_button.clicked.connect(self._on_browse_source)
        clear_button = QPushButton("Clear")
        clear_button.clicked.connect(self._on_clear_source)
        button_row.addWidget(browse_button)
        button_row.addWidget(clear_button)
        layout.addLayout(button_row)

        group.setLayout(layout)
        return group

    def _build_appearance_group(self):
        group = QGroupBox("Appearance")
        layout = QHBoxLayout()

        layout.addWidget(QLabel("Color"))
        self._color_button = QPushButton()
        self._color_button.setFixedWidth(48)
        self._color_button.clicked.connect(self._on_color_clicked)
        layout.addWidget(self._color_button)
        layout.addStretch()

        group.setLayout(layout)
        return group

    def load_grid(self, grid):
        # Populate all fields from the given grid model
        self._grid = grid
        self._updating = True

        if grid is None:
            self.setEnabled(False)
            self._updating = False
            return

        self.setEnabled(True)
        self._label_input.setText(grid.label)
        self._tile_width_spin.setValue(grid.tile_width)
        self._tile_height_spin.setValue(grid.tile_height)
        self._columns_spin.setValue(grid.columns)
        self._rows_spin.setValue(grid.rows)
        self._update_color_button(grid.color)
        self._update_source_label(grid.source_path)

        self._updating = False

    def _update_color_button(self, hex_color):
        self._color_button.setStyleSheet(
            "background-color: {}; border: 1px solid #666;".format(hex_color)
        )

    def _update_source_label(self, path):
        if path:
            self._source_label.setText(os.path.basename(path))
            self._source_label.setToolTip(path)
        else:
            self._source_label.setText("No image assigned")
            self._source_label.setToolTip("")

    def _on_label_changed(self, text):
        if self._updating or not self._grid:
            return
        self._grid.label = text
        self.grid_changed.emit()

    def _on_tile_link_toggled(self, linked):
        self._tile_size_linked = linked
        self._tile_link_button.setIcon(_load_link_icon(linked))

    def _on_tile_width_changed(self, value):
        if self._updating or not self._grid:
            return
        if self._tile_size_linked:
            self._tile_height_spin.blockSignals(True)
            self._tile_height_spin.setValue(value)
            self._tile_height_spin.blockSignals(False)
            self._grid.tile_height = value
        self._grid.tile_width = value
        self.grid_changed.emit()

    def _on_tile_height_changed(self, value):
        if self._updating or not self._grid:
            return
        if self._tile_size_linked:
            self._tile_width_spin.blockSignals(True)
            self._tile_width_spin.setValue(value)
            self._tile_width_spin.blockSignals(False)
            self._grid.tile_width = value
        self._grid.tile_height = value
        self.grid_changed.emit()

    def _on_grid_size_changed(self):
        if self._updating or not self._grid:
            return
        self._grid.columns = self._columns_spin.value()
        self._grid.rows = self._rows_spin.value()
        self.grid_changed.emit()

    def _on_browse_source(self):
        if not self._grid:
            return
        path, _ = QFileDialog.getOpenFileName(
            self, "Select Source Image", "",
            "Images (*.png *.jpg *.jpeg *.bmp *.tiff *.tif *.webp)"
        )
        if path:
            self._grid.source_path = path
            self._update_source_label(path)
            self.grid_changed.emit()

    def _on_clear_source(self):
        if not self._grid:
            return
        self._grid.source_path = ""
        self._update_source_label("")
        self.grid_changed.emit()

    def _on_color_clicked(self):
        if not self._grid:
            return
        color = QColorDialog.getColor(QColor(self._grid.color), self, "Pick Grid Color")
        if color.isValid():
            self._grid.color = color.name()
            self._update_color_button(self._grid.color)
            self.grid_changed.emit()