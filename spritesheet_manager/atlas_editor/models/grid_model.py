class GridModel:
    def __init__(self):
        self.label = "New Grid"
        self.x = 0
        self.y = 0
        self.tile_width = 16
        self.tile_height = 16
        self.columns = 8
        self.rows = 4
        self.color = "#4a8fcc"
        self.source_path = ""

    @property
    def pixel_width(self):
        return self.columns * self.tile_width

    @property
    def pixel_height(self):
        return self.rows * self.tile_height

    def to_dict(self):
        return {
            "label": self.label,
            "x": self.x,
            "y": self.y,
            "tile_width": self.tile_width,
            "tile_height": self.tile_height,
            "columns": self.columns,
            "rows": self.rows,
            "color": self.color,
            "source_path": self.source_path,
        }

    @classmethod
    def from_dict(cls, data):
        grid = cls()
        grid.label = data.get("label", "Grid")
        grid.x = data.get("x", 0)
        grid.y = data.get("y", 0)
        grid.tile_width = data.get("tile_width", 16)
        grid.tile_height = data.get("tile_height", 16)
        grid.columns = data.get("columns", 8)
        grid.rows = data.get("rows", 4)
        grid.color = data.get("color", "#4a8fcc")
        grid.source_path = data.get("source_path", "")
        return grid