from krita import Krita
from PyQt5.QtCore import QByteArray
from ..spritesheet_manager import PLUGIN_VERSION
import json

PLUGIN_KEY: str = "SPRITESHEET_MANAGER"

def load_setting(key: str, default_value: str = "") -> str:
    return Krita.instance().readSetting(PLUGIN_KEY, key, str(default_value))

def save_setting(key: str, value: str):
    Krita.instance().writeSetting(PLUGIN_KEY, key, str(value))

def load_state(document, key: str) -> dict:
    if not document: return {}

    state_key: str = PLUGIN_KEY + "_" + key
    
    annotation: str = document.annotation(state_key)

    if not annotation or len(annotation) == 0: return {}
    
    try:
        data: str = bytes(annotation).decode("utf-8")
        return json.loads(data)
    except Exception:
        return {}

def save_state(document, key: str, data: dict, description: str = ""):
    if not document: return

    data["_version"] = PLUGIN_VERSION
    
    state_key: str = PLUGIN_KEY + "_" + key

    try:
        data: bytes = json.dumps(data).encode("utf-8")
        document.setAnnotation(state_key, description, QByteArray(data))
    except Exception:
        pass