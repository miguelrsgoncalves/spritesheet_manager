from krita import Extension
from .actions import register_actions

class SpritesheetManagerExtension(Extension):

    def __init__(self, parent):
        super().__init__(parent)

    def setup(self):
        pass

    def createActions(self, window):
        register_actions(window)