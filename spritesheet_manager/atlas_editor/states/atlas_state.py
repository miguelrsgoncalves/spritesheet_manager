from ...core.serialization import load_document_state, save_document_state

ATLAS_KEY = "atlas"

def load_atlas_state(doc):
    return load_document_state(doc).get(ATLAS_KEY, {})

def save_atlas_state(doc, state):
    full_state = load_document_state(doc)
    full_state[ATLAS_KEY] = state
    save_document_state(doc, full_state)