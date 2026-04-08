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

def get_padder_state(doc):
    return load_document_state(doc).get("padder", {})

def save_padder_state(doc, padder_state: dict):
    state = load_document_state(doc)
    state["padder"] = padder_state
    save_document_state(doc, state)

def get_atlas_state(doc):
    return load_document_state(doc).get("atlas", {})

def save_atlas_state(doc, atlas_state: dict):
    state = load_document_state(doc)
    state["atlas"] = atlas_state
    save_document_state(doc, state)