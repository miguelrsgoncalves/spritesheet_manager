from PyQt5.QtWidgets import QWidget, QSizePolicy
from PyQt5.QtCore import Qt, QPoint, QPointF, QRectF, pyqtSignal
from PyQt5.QtGui import QPainter, QColor, QPen, QFont, QPixmap, QBrush

class AtlasCanvas(QWidget):
    grid_selected = pyqtSignal(int)
    grid_moved = pyqtSignal()

    COLOR_BACKGROUND = QColor(30, 30, 30)
    COLOR_CANVAS_BG = QColor(45, 45, 45)
    COLOR_CANVAS_BORDER = QColor(120, 120, 120)
    COLOR_GRID_LINES = QColor(255, 255, 255, 40)
    COLOR_SELECTED_BORDER = QColor(255, 210, 60)
    COLOR_LABEL = QColor(255, 255, 255, 220)
    COLOR_ORIGIN = QColor(70, 70, 70)
    CHECKERBOARD_A = QColor(60, 60, 60)
    CHECKERBOARD_B = QColor(80, 80, 80)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._model = None
        self._zoom = 1.0
        self._pan = QPointF(32.0, 32.0)
        self._selected_index = -1

        # Source image pixmap cache keyed by file path
        self._pixmap_cache = {}

        # Left-drag state for moving grids
        self._drag_index = -1
        self._drag_start_mouse = QPointF()
        self._drag_start_grid = QPointF()

        # Middle-drag state for panning the canvas view
        self._panning = False
        self._pan_start_mouse = QPoint()
        self._pan_start_offset = QPointF()

        self.setMouseTracking(True)
        self.setMinimumSize(300, 200)
        self.setFocusPolicy(Qt.ClickFocus)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

    def set_model(self, model):
        self._model = model
        self._pixmap_cache.clear()
        self.update()

    def get_selected_index(self):
        return self._selected_index

    def set_selected_index(self, index):
        self._selected_index = index
        self.update()

    def invalidate_pixmap_cache(self):
        # Call this when a grid's source path changes
        self._pixmap_cache.clear()
        self.update()

    def fit_in_view(self):
        # Zoom and pan so the full atlas canvas rectangle fills the widget with margin
        if not self._model:
            return
        margin = 48
        zoom_x = (self.width() - margin * 2) / max(1, self._model.canvas_width)
        zoom_y = (self.height() - margin * 2) / max(1, self._model.canvas_height)
        self._zoom = max(0.05, min(zoom_x, zoom_y))
        self._pan = QPointF(
            margin + (self.width() - margin * 2 - self._model.canvas_width * self._zoom) / 2,
            margin + (self.height() - margin * 2 - self._model.canvas_height * self._zoom) / 2,
        )
        self.update()

    def _to_screen(self, doc_x, doc_y):
        return QPointF(
            self._pan.x() + doc_x * self._zoom,
            self._pan.y() + doc_y * self._zoom,
        )

    def _to_doc(self, screen_x, screen_y):
        return QPointF(
            (screen_x - self._pan.x()) / self._zoom,
            (screen_y - self._pan.y()) / self._zoom,
        )

    def _grid_at(self, screen_pos):
        # Returns the index of the topmost grid under screen_pos, or -1
        if not self._model:
            return -1
        for i in range(len(self._model.grids) - 1, -1, -1):
            g = self._model.grids[i]
            tl = self._to_screen(g.x, g.y)
            br = self._to_screen(g.x + g.pixel_width, g.y + g.pixel_height)
            if tl.x() <= screen_pos.x() <= br.x() and tl.y() <= screen_pos.y() <= br.y():
                return i
        return -1

    def wheelEvent(self, event):
        factor = 1.15 if event.angleDelta().y() > 0 else 1.0 / 1.15
        mouse = QPointF(event.pos())
        doc_pos = self._to_doc(mouse.x(), mouse.y())
        self._zoom = max(0.05, min(64.0, self._zoom * factor))
        self._pan = QPointF(
            mouse.x() - doc_pos.x() * self._zoom,
            mouse.y() - doc_pos.y() * self._zoom,
        )
        self.update()

    def mousePressEvent(self, event):
        if event.button() == Qt.MiddleButton:
            self._panning = True
            self._pan_start_mouse = event.pos()
            self._pan_start_offset = QPointF(self._pan)
            self.setCursor(Qt.ClosedHandCursor)
            return

        if event.button() == Qt.LeftButton:
            hit = self._grid_at(QPointF(event.pos()))
            self._selected_index = hit
            self.grid_selected.emit(hit)
            if hit >= 0:
                g = self._model.grids[hit]
                self._drag_index = hit
                self._drag_start_mouse = QPointF(event.pos())
                self._drag_start_grid = QPointF(g.x, g.y)
            self.update()

    def mouseMoveEvent(self, event):
        if self._panning:
            delta = event.pos() - self._pan_start_mouse
            self._pan = self._pan_start_offset + QPointF(delta)
            self.update()
            return

        if self._drag_index >= 0 and (event.buttons() & Qt.LeftButton):
            delta = QPointF(event.pos()) - self._drag_start_mouse
            g = self._model.grids[self._drag_index]
            raw_x = self._drag_start_grid.x() + delta.x() / self._zoom
            raw_y = self._drag_start_grid.y() + delta.y() / self._zoom
            # Snap to the grid's own tile size so it always aligns cleanly
            g.x = round(raw_x / g.tile_width) * g.tile_width
            g.y = round(raw_y / g.tile_height) * g.tile_height
            self.grid_moved.emit()
            self.update()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MiddleButton:
            self._panning = False
            self.setCursor(Qt.ArrowCursor)
        if event.button() == Qt.LeftButton:
            self._drag_index = -1

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.SmoothPixmapTransform, True)

        # Outer background
        painter.fillRect(self.rect(), self.COLOR_BACKGROUND)

        if not self._model:
            return

        # Atlas canvas rectangle
        canvas_tl = self._to_screen(0, 0)
        canvas_w = self._model.canvas_width * self._zoom
        canvas_h = self._model.canvas_height * self._zoom
        canvas_rect = QRectF(canvas_tl.x(), canvas_tl.y(), canvas_w, canvas_h)

        # Checkerboard fill inside the canvas bounds to indicate transparency
        self._draw_checkerboard(painter, canvas_rect)

        # Clip all grid drawing to the canvas rectangle
        painter.save()
        painter.setClipRect(canvas_rect)

        for index, grid in enumerate(self._model.grids):
            self._draw_grid(painter, index, grid)

        painter.restore()

        # Canvas border drawn on top so it's always visible
        painter.setPen(QPen(self.COLOR_CANVAS_BORDER, 1))
        painter.drawRect(canvas_rect)

    def _draw_checkerboard(self, painter, rect):
        # Draws a subtle checkerboard inside the canvas area to indicate transparency
        cell = max(8, int(16 * self._zoom))
        x = int(rect.x())
        y = int(rect.y())
        width = int(rect.width())
        height = int(rect.height())

        col = 0
        cx = x
        while cx < x + width:
            row = 0
            cy = y
            while cy < y + height:
                color = self.CHECKERBOARD_A if (col + row) % 2 == 0 else self.CHECKERBOARD_B
                cell_w = min(cell, x + width - cx)
                cell_h = min(cell, y + height - cy)
                painter.fillRect(cx, cy, cell_w, cell_h, color)
                cy += cell
                row += 1
            cx += cell
            col += 1

    def _draw_grid(self, painter, index, grid):
        tl = self._to_screen(grid.x, grid.y)
        grid_w = grid.pixel_width * self._zoom
        grid_h = grid.pixel_height * self._zoom
        tile_w = grid.tile_width * self._zoom
        tile_h = grid.tile_height * self._zoom
        grid_rect = QRectF(tl.x(), tl.y(), grid_w, grid_h)

        is_selected = (index == self._selected_index)
        base_color = QColor(grid.color)

        # Source image behind the grid if one is assigned and the file exists
        if grid.source_path:
            pixmap = self._get_pixmap(grid.source_path)
            if pixmap:
                painter.drawPixmap(grid_rect, pixmap, QRectF(pixmap.rect()))

        # Semi-transparent colour tint over the image (lighter when selected)
        tint = QColor(base_color)
        tint.setAlpha(30 if is_selected else 55)
        painter.fillRect(grid_rect, tint)

        # Tile grid lines — skip if tiles are too small to see clearly
        if tile_w >= 4:
            painter.setPen(QPen(self.COLOR_GRID_LINES, 1))
            for col in range(1, grid.columns):
                x = tl.x() + col * tile_w
                painter.drawLine(QPointF(x, tl.y()), QPointF(x, tl.y() + grid_h))
            for row in range(1, grid.rows):
                y = tl.y() + row * tile_h
                painter.drawLine(QPointF(tl.x(), y), QPointF(tl.x() + grid_w, y))

        # Outer border — gold and thicker when selected
        border_color = self.COLOR_SELECTED_BORDER if is_selected else base_color
        border_width = 2 if is_selected else 1
        painter.setPen(QPen(border_color, border_width))
        painter.drawRect(grid_rect)

        # Label in the top-left corner when the grid is large enough
        if grid_w > 40 and grid_h > 18:
            painter.setPen(QPen(self.COLOR_LABEL))
            font = QFont()
            font.setPointSize(8)
            painter.setFont(font)
            painter.drawText(int(tl.x()) + 4, int(tl.y()) + 13, grid.label)

    def _get_pixmap(self, path):
        # Loads and caches pixmaps by file path. Returns None if unloadable.
        if path in self._pixmap_cache:
            return self._pixmap_cache[path]
        pixmap = QPixmap(path)
        if pixmap.isNull():
            self._pixmap_cache[path] = None
            return None
        self._pixmap_cache[path] = pixmap
        return pixmap