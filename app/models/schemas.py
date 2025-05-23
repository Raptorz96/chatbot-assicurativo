# app/models/schemas.py
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class ChatRequest(BaseModel):
    user_id: str
    message: str
    conversation_id: Optional[str] = None
    # Potresti aggiungere altri campi come metadata della richiesta se necessario

class Intent(BaseModel):
    type: str = "sconosciuto"
    confidence: float = 0.0
    entities: Optional[Dict[str, Any]] = Field(default_factory=dict)

# Modello per rappresentare una singola fonte di documento
class SourceDocument(BaseModel):
    source: str
    content_preview: Optional[str] = None
    # Potresti aggiungere altri metadati utili qui, es:
    # page_number: Optional[int] = None
    # score: Optional[float] = None

# NUOVO MODELLO: SuggestedAction
class SuggestedAction(BaseModel):
    label: str  # Testo visualizzato sul pulsante/link
    type: str   # Tipo di azione, es. "query", "link", "event"
    payload: str # Valore associato all'azione (es. la query da inviare, l'URL, nome evento)

class ChatResponse(BaseModel):
    message: str
    conversation_id: str
    # MODIFICATO: Ora usa il modello SuggestedAction
    suggested_actions: Optional[List[SuggestedAction]] = Field(default_factory=list)
    sources: Optional[List[SourceDocument]] = Field(default_factory=list)
    # Potresti aggiungere altri campi come metadata della risposta, intent rilevato, ecc.
    # intent_data: Optional[Intent] = None # Esempio

# Esempio di altri schemi che potresti avere o aggiungere:
class HealthStatus(BaseModel):
    status: str
    timestamp: str
    components: Dict[str, Any]
    version: str

class CacheClearResponse(BaseModel):
    status: str
    timestamp: str
    message: str

# Aggiungi altri schemi Pydantic secondo necessità per la tua applicazione
