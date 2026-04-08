from .grid_model import GridModel

class AtlasModel:
    def __init__(self):
        self.canvas_width = 512
        self.canvas_height = 512
        self.grids = []

    def add_grid(self):
        grid = GridModel()
        offset = len(self.grids) * 24
        grid.x = offset
        grid.y = offset
        grid.label = "Grid {}".format(len(self.grids) + 1)
        self.grids.append(grid)
        return grid

    def remove_grid(self, index):
        if 0 <= index < len(self.grids):
            self.grids.pop(index)

    def to_dict(self):
        return {
            "canvas_width": self.canvas_width,
            "canvas_height": self.canvas_height,
            "grids": [g.to_dict() for g in self.grids],
        }

    @classmethod
    def from_dict(cls, data):
        model = cls()
        model.canvas_width = data.get("canvas_width", 512)
        model.canvas_height = data.get("canvas_height", 512)
        for grid_data in data.get("grids", []):
            model.grids.append(GridModel.from_dict(grid_data))
        return model