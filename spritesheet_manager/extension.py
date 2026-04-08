from krita import Extension, DockWidgetFactory, DockWidgetFactoryBase, Krita
from .actions import register_actions
from .atlas_editor.ui.atlas_docker import AtlasDocker

class SpritesheetManagerExtension(Extension):

    def __init__(self, parent):
        super().__init__(parent)

    def setup(self):
        Krita.instance().addDockWidgetFactory(
            DockWidgetFactory(
                "spritesheet_atlas_editor",
                DockWidgetFactoryBase.DockRight,
                AtlasDocker
            )
        )

    def createActions(self, window):
        register_actions(window)