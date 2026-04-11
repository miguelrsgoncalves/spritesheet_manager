from krita import Krita
from PyQt5.QtCore import QByteArray
from ..version import PLUGIN_VERSION
import json

PLUGIN_KEY: str = "SPRITESHEET_MANAGER"
WIDGET_DESCRIPTION_PREFIX: str ="Spritesheet Manager: "

class Serializer:
    @staticmethod
    def load_setting(key: str, default_value: str = "") -> str:
        return Krita.instance().readSetting(PLUGIN_KEY, key, str(default_value))

    @staticmethod
    def save_setting(key: str, value: str):
        Krita.instance().writeSetting(PLUGIN_KEY, key, str(value))

    @staticmethod
    def load_state(document, key: str) -> dict:
        if not document: return {}

        state_key: str = PLUGIN_KEY + "_" + key
        
        annotation: str = document.annotation(state_key)

        if not annotation or len(annotation) == 0: return {}
        
        try:
            raw_data: str = bytes(annotation).decode("utf-8")
            return json.loads(raw_data)
        except Exception:
            return {}

    @staticmethod
    def save_state(document, key: str, data: dict, description: str = ""):
        if not document: return

        data["_version"] = PLUGIN_VERSION
        
        state_key: str = PLUGIN_KEY + "_" + key
        state_description: str = WIDGET_DESCRIPTION_PREFIX + description

        try:
            raw_data: bytes = json.dumps(data).encode("utf-8")
            document.setAnnotation(state_key, state_description, QByteArray(raw_data))
        except Exception:
            pass