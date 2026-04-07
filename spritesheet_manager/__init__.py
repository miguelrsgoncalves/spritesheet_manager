from krita import Krita
from .extension import SpritesheetManagerExtension

Krita.instance().addExtension(SpritesheetManagerExtension(Krita.instance()))