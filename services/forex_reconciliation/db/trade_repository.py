import json
from services.firebase_client import get_firestore_client

def load_trades_fofo():
    db = get_firestore_client()
    system_a = [doc.to_dict() for doc in db.collection("fx_systemA_capture").stream()]
    system_b = [doc.to_dict() for doc in db.collection("fx_systemB_capture").stream()]
    return system_a, system_b

def load_trades_fobo():
    db = get_firestore_client()
    front_office = [doc.to_dict() for doc in db.collection("fx_FOentry_capture").stream()]
    back_office = [doc.to_dict() for doc in db.collection("fx_BOentry_capture").stream()]
    return front_office, back_office
