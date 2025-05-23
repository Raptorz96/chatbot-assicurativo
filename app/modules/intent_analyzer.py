# app/modules/intent_analyzer.py
import re
import spacy
from typing import Dict, List, Optional, Union # Union potrebbe non essere strettamente necessario qui se entities è sempre Dict[str, str]
from app.utils.logging_config import logger
from app.models.schemas import Intent

# Carica il modello spaCy (italiano o inglese)
# Per installare i modelli:
# python -m spacy download it_core_news_sm  # Per italiano
# python -m spacy download en_core_web_sm   # Per inglese
try:
    nlp = spacy.load("it_core_news_sm")  # Modello italiano
    logger.info("Modello spaCy italiano (it_core_news_sm) caricato.")
except OSError:
    logger.warning("Modello spaCy italiano (it_core_news_sm) non trovato. Tentativo con en_core_web_sm.")
    try:
        nlp = spacy.load("en_core_web_sm")  # Fallback al modello inglese
        logger.info("Modello spaCy inglese (en_core_web_sm) caricato come fallback.")
    except OSError:
        logger.error("Nessun modello spaCy (it_core_news_sm, en_core_web_sm) trovato. L'analisi dell'intento sarà basata solo su keyword.")
        nlp = None

# Definizione delle keyword con pesi per ciascun intento
# Un peso maggiore indica una keyword più significativa
INTENT_KEYWORDS = {
    "preventivo": {
        "preventivo": 1.5, "costo": 1.0, "prezzo": 1.0, "quanto costa": 1.5,
        "pagare": 0.8, "spendere": 0.8, "costare": 0.8, "tariffa": 0.9,
        "economico": 0.7, "conveniente": 0.7
    },
    "reclamo": {
        "problema": 1.0, "reclamo": 1.5, "insoddisfatto": 1.2, "lamentela": 1.2,
        "disservizio": 1.3, "lamentare": 1.0, "insoddisfazione": 1.1, "pessimo": 0.9,
        "malfunzionamento": 1.0, "scadente": 0.8
    },
    "sinistro": {
        "sinistro": 1.5, "incidente": 1.3, "danno": 1.0, "danneggiato": 1.0,
        "rotto": 0.8, "furto": 1.2, "rubato": 1.2, "incendio": 1.0,
        "allagamento": 1.0, "collisione": 1.0
    },
    "copertura": {
        "coperto": 1.0, "copertura": 1.5, "incluso": 0.9, "compreso": 0.9,
        "garantito": 1.0, "assicurato": 1.2, "protezione": 1.0, "garanzia": 1.0,
        "polizza": 0.8, "tutela": 0.8
    },
    "saluto": {
        "ciao": 1.0, "buongiorno": 1.0, "buonasera": 1.0, "salve": 1.0,
        "hey": 0.8, "ehilà": 0.8 # Aggiunto "hey" ed "ehilà"
    },
    "ringraziamento": {
        "grazie": 1.2, "ti ringrazio": 1.2, "gentile": 0.8, "apprezzo": 0.9
    },
    "congedo": {
        "arrivederci": 1.0, "a presto": 0.9, "alla prossima": 0.9,
        "ci sentiamo": 0.8, "addio": 0.7 # "addio" potrebbe essere meno comune per un chatbot
    },
    "informazioni_generali": {
        "informazioni su": 1.0, "dettagli su": 0.9, "spiegami": 0.8,
        "parlami di": 0.8, "vorrei sapere": 0.7, "come funziona": 0.9,
        # Parole interrogative generiche con pesi bassi
        "cosa": 0.4, "come": 0.4, "perché": 0.4, "quando": 0.4,
        "dove": 0.4, "chi": 0.4, "quale": 0.4
    }
}

def analyze_intent(message: str) -> Intent:
    """
    Analizza il messaggio dell'utente per determinare l'intento.
    Utilizza spaCy per l'estrazione di entità se disponibile,
    e un approccio basato su keyword pesate per la classificazione dell'intento.

    Args:
        message: Il messaggio dell'utente.

    Returns:
        Un oggetto Intent con tipo, confidenza ed eventuali entità.
    """
    normalized_message = message.lower()
    entities: Dict[str, str] = {} # Lo schema Intent si aspetta Dict[str, str] per entities

    # Se spaCy è disponibile, usa l'analisi NLP per estrarre entità
    if nlp:
        doc = nlp(normalized_message)
        
        extracted_entities_spacy: Dict[str, List[str]] = {}
        for ent in doc.ents:
            if ent.label_ not in extracted_entities_spacy:
                extracted_entities_spacy[ent.label_] = []
            extracted_entities_spacy[ent.label_].append(ent.text)
        
        for label, texts_list in extracted_entities_spacy.items():
            entities[label] = texts_list[0] if len(texts_list) == 1 else ", ".join(texts_list)
        
        if entities:
            logger.debug(f"Entità estratte da spaCy: {entities}")
    
    # Analisi per parole chiave con pesi e matching di parole intere
    intent_scores: Dict[str, float] = {}
    matched_keywords_per_intent: Dict[str, List[str]] = {}
    
    for intent_type, keywords_with_weights in INTENT_KEYWORDS.items():
        current_intent_score = 0.0
        current_matched_keywords = []
        
        for keyword, weight in keywords_with_weights.items():
            pattern = r'\b' + re.escape(keyword) + r'\b'
            if re.search(pattern, normalized_message):
                current_intent_score += weight
                current_matched_keywords.append(keyword)
        
        if current_intent_score > 0:
            intent_scores[intent_type] = current_intent_score
            matched_keywords_per_intent[intent_type] = current_matched_keywords
            
    logger.debug(f"Punteggi intenti: {intent_scores}")
    if matched_keywords_per_intent:
        logger.debug(f"Keyword trovate per intento: {matched_keywords_per_intent}")
    
    # Determina l'intento migliore
    max_score = 0.0
    if intent_scores:
        max_score = max(intent_scores.values())

    if max_score == 0:
        logger.info("Nessuna keyword ha prodotto un punteggio. Default a 'informazioni_generali' con confidenza molto bassa.")
        final_intent_type = "informazioni_generali"
        final_confidence = 0.1
    else:
        top_scored_intents = [intent for intent, score in intent_scores.items() if score == max_score]
        
        if len(top_scored_intents) > 1:
            logger.info(f"Rilevata ambiguità tra intenti con punteggio {max_score}: {top_scored_intents}.")
            
            # Se "informazioni_generali" è uno degli intenti in pareggio, e ci sono altri intenti specifici,
            # prova a dare priorità agli intenti più specifici.
            specific_top_intents = [i for i in top_scored_intents if i != "informazioni_generali"]
            
            if specific_top_intents: # Se ci sono intenti specifici nel pareggio
                if len(specific_top_intents) == 1:
                    final_intent_type = specific_top_intents[0]
                    logger.info(f"Risolta ambiguità preferendo l'intento specifico: {final_intent_type}")
                else: # Ancora un pareggio tra intenti specifici
                    logger.info(f"Ancora ambiguità tra intenti specifici: {specific_top_intents}. Uso il numero di keyword matchate.")
                    final_intent_type = max(specific_top_intents, key=lambda i: len(matched_keywords_per_intent.get(i, [])))
            else: # Il pareggio era solo con "informazioni_generali" o tra "informazioni_generali" e nessun altro specifico
                  # (quest'ultimo caso non dovrebbe accadere se specific_top_intents è vuoto e top_scored_intents non lo era)
                  # In questo caso, o si sceglie "informazioni_generali" o si usa il tie-breaker standard.
                  # Per semplicità, usiamo il tie-breaker standard su tutti i top_scored_intents originali.
                final_intent_type = max(top_scored_intents, key=lambda i: len(matched_keywords_per_intent.get(i, [])))
            
            logger.info(f"Tie-breaker ha selezionato: {final_intent_type}")
        else: # Nessun pareggio, un solo intento con punteggio massimo
            final_intent_type = top_scored_intents[0]
        
        # Calcola la confidenza
        total_possible_weight_for_intent = sum(INTENT_KEYWORDS[final_intent_type].values())
        if total_possible_weight_for_intent > 0:
            final_confidence = min(max_score / total_possible_weight_for_intent, 1.0)
        else: 
            final_confidence = 0.5 if max_score > 0 else 0.0
        
        # Aggiustamento specifico della confidenza per "informazioni_generali"
        if final_intent_type == "informazioni_generali":
            # Controlla se sono state matchate solo parole interrogative generiche
            # (assumendo che queste siano le uniche keyword a basso peso che vuoi penalizzare)
            generic_interrogatives = ["cosa", "come", "perché", "quando", "dove", "chi", "quale"]
            matched_kws_for_general_info = matched_keywords_per_intent.get("informazioni_generali", [])
            
            # Verifica se TUTTE le keyword matchate per questo intento sono nella lista delle interrogative generiche
            # E che almeno una keyword sia stata effettivamente matchata per questo intento
            if matched_kws_for_general_info and all(kw in generic_interrogatives for kw in matched_kws_for_general_info):
                # Se il punteggio deriva SOLO da queste keyword generiche, riduci la confidenza.
                # Questo evita che una singola "cosa" con peso 0.4 dia una confidenza troppo alta se normalizzata.
                final_confidence *= 0.5 # Riduci la confidenza (es. del 50%)
                logger.info(f"Rilevati solo match su keyword interrogative generiche per 'informazioni_generali'. Confidenza aggiustata a: {final_confidence:.2f}")

    return Intent(
        type=final_intent_type,
        confidence=round(final_confidence, 2),
        entities=entities if entities else None
    )

