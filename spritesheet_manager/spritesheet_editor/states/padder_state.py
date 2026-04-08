from ...core.serialization import load_document_state, save_document_state

PADDER_KEY = "padder"

PADDER_DEFAULTS = {
    "tile_width": 64,
    "tile_height": 64,
    "padding_x": 8,
    "padding_y": 8,
    "columns": 1,
    "rows": 1,
    "anti_bleed": True,
    "save_kra": False,
    "export_image": True,
}

def load_padder_state(doc):
    saved = load_document_state(doc).get(PADDER_KEY, {})
    result = dict(PADDER_DEFAULTS)
    result.update(saved)
    return result

def save_padder_state(doc, state):
    full_state = load_document_state(doc)
    full_state[PADDER_KEY] = state
    save_document_state(doc, full_state)