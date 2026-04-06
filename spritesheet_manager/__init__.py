from .extension import SpritesheetManagerExtension
from krita import Krita

Krita.instance().addExtension(SpritesheetManagerExtension(Krita.instance()))