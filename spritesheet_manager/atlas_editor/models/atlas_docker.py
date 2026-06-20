from krita import DockWidget, Krita
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QSplitter, QSpinBox, QLabel, QGroupBox
)
from PyQt5.QtCore import Qt
from .atlas_canvas import AtlasCanvas
from .atlas_panel import AtlasPanel
from ..atlas_editor import get_controller


class AtlasDocker(DockWidget):

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Atlas Editor")
        self._controller = get_controller()

        # Build canvas and panel first, toolbar references _canvas so it must exist
        self._canvas = AtlasCanvas()
        self._panel = AtlasPanel()

        self._setup_ui()

    def _setup_ui(self):
        root = QWidget()
        root_layout = QVBoxLayout()
        root_layout.setContentsMargins(4, 4, 4, 4)
        root_layout.setSpacing(4)

        root_layout.addWidget(self._build_canvas_size_bar())
        root_layout.addWidget(self._build_toolbar())

        # Splitter: canvas on top, panel below
        splitter = QSplitter(Qt.Vertical)

        self._canvas.grid_selected.connect(self._on_grid_selected)
        self._canvas.grid_moved.connect(self._on_grid_moved)
        splitter.addWidget(self._canvas)

        self._panel.grid_changed.connect(self._on_grid_changed)
        splitter.addWidget(self._panel)

        # Canvas gets most of the vertical space
        splitter.setStretchFactor(0, 3)
        splitter.setStretchFactor(1, 1)

        root_layout.addWidget(splitter)
        root.setLayout(root_layout)
        self.setWidget(root)

        self._canvas.set_model(self._controller.get_model())

    def _build_canvas_size_bar(self):
        group = QGroupBox("Atlas Canvas Size")
        layout = QHBoxLayout()
        layout.setSpacing(4)

        layout.addWidget(QLabel("W"))
        self._canvas_width_spin = QSpinBox()
        self._canvas_width_spin.setRange(1, 99999)
        self._canvas_width_spin.setValue(512)
        self._canvas_width_spin.valueChanged.connect(self._on_canvas_size_changed)
        layout.addWidget(self._canvas_width_spin)

        layout.addWidget(QLabel("H"))
        self._canvas_height_spin = QSpinBox()
        self._canvas_height_spin.setRange(1, 99999)
        self._canvas_height_spin.setValue(512)
        self._canvas_height_spin.valueChanged.connect(self._on_canvas_size_changed)
        layout.addWidget(self._canvas_height_spin)

        group.setLayout(layout)
        return group

    def _build_toolbar(self):
        widget = QWidget()
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)

        add_button = QPushButton("+ Add Grid")
        add_button.clicked.connect(self._on_add_grid)
        layout.addWidget(add_button)

        remove_button = QPushButton("Remove")
        remove_button.clicked.connect(self._on_remove_grid)
        layout.addWidget(remove_button)

        # _canvas already exists at this point so this is safe
        fit_button = QPushButton("Fit View")
        fit_button.clicked.connect(self._canvas.fit_in_view)
        layout.addWidget(fit_button)

        layout.addStretch()
        widget.setLayout(layout)
        return widget

    def _current_doc(self):
        return Krita.instance().activeDocument()

    def _on_canvas_size_changed(self):
        model = self._controller.get_model()
        model.canvas_width = self._canvas_width_spin.value()
        model.canvas_height = self._canvas_height_spin.value()
        self._canvas.update()
        self._controller.on_grid_changed(self._current_doc())

    def _on_add_grid(self):
        doc = self._current_doc()
        self._controller.add_grid(doc)
        model = self._controller.get_model()
        self._canvas.set_model(model)
        last_index = len(model.grids) - 1
        self._canvas.set_selected_index(last_index)
        self._panel.load_grid(model.grids[last_index])

    def _on_remove_grid(self):
        index = self._canvas.get_selected_index()
        if index < 0:
            return
        self._controller.remove_grid(index, self._current_doc())
        self._canvas.set_model(self._controller.get_model())
        self._canvas.set_selected_index(-1)
        self._panel.load_grid(None)

    def _on_grid_selected(self, index):
        model = self._controller.get_model()
        if 0 <= index < len(model.grids):
            self._panel.load_grid(model.grids[index])
        else:
            self._panel.load_grid(None)

    def _on_grid_moved(self):
        self._controller.on_grid_changed(self._current_doc())

    def _on_grid_changed(self):
        # A property changed in the panel — invalidate image cache and redraw
        self._canvas.invalidate_pixmap_cache()
        self._controller.on_grid_changed(self._current_doc())

    def canvasChanged(self, canvas):
        # Called by Krita when the active document changes
        doc = Krita.instance().activeDocument()
        self._controller.load_from_document(doc)
        model = self._controller.get_model()

        self._canvas_width_spin.blockSignals(True)
        self._canvas_height_spin.blockSignals(True)
        self._canvas_width_spin.setValue(model.canvas_width)
        self._canvas_height_spin.setValue(model.canvas_height)
        self._canvas_width_spin.blockSignals(False)
        self._canvas_height_spin.blockSignals(False)

        self._canvas.set_model(model)
        self._canvas.set_selected_index(-1)
        self._panel.load_grid(None)