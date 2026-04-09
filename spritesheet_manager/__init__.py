from krita import Krita
from .spritesheet_manager import SpritesheetManagerExtension

Krita.instance().addExtension(SpritesheetManagerExtension(Krita.instance()))