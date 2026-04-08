import json
from PyQt5.QtCore import QByteArray

ANNOTATION_KEY = "spritesheet_manager"

def load_document_state(doc):
    if not doc: return {}
    
    annotation = doc.annotation(ANNOTATION_KEY)

    if not annotation or len(annotation) == 0:
        return {}
    try:
        raw = bytes(annotation).decode("utf-8")
        return json.loads(raw)
    except Exception:
        return {}

def save_document_state(doc, state: dict):
    if not doc: return
    
    try:
        raw = json.dumps(state).encode("utf-8")
        doc.setAnnotation(ANNOTATION_KEY, "Spritesheet Manager State", QByteArray(raw))
    except Exception:
        pass