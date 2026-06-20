from krita import Krita
from .spritesheet_manager import SpritesheetManager

Krita.instance().addExtension(SpritesheetManager(Krita.instance()))