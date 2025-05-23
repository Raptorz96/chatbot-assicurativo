import spacy
import string
from typing import Optional, Any # Aggiunta importazione di Optional e Any per Language
from spacy.language import Language # Per il type hinting più specifico

# Variabile globale per conservare il modello spaCy caricato
# e assicurarsi che venga caricato solo una volta.
NLP_PROCESSOR: Optional[Language] = None # Ora Optional è definito
NLP_MODEL_NAME = "it_core_news_sm" # Modello piccolo per l'italiano, efficiente.
                                   # Per maggiore accuratezza, si potrebbe usare "it_core_news_md" o "it_core_news_lg"
                                   # ma richiedono più risorse e un download separato.

def load_spacy_model(model_name: str = NLP_MODEL_NAME) -> Language:
    """
    Carica un modello linguistico spaCy. Se già caricato, restituisce l'istanza esistente.
    Cerca di scaricare il modello se non è presente.
    """
    global NLP_PROCESSOR
    # Controllo più robusto per assicurarsi che il modello corretto sia caricato se NLP_PROCESSOR non è None
    if NLP_PROCESSOR is None or NLP_PROCESSOR.meta.get("name") != model_name.split('_', 1)[0] or NLP_PROCESSOR.meta.get("lang") != model_name.split('_', 1)[0]:
        try:
            NLP_PROCESSOR = spacy.load(model_name)
            print(f"Modello spaCy '{model_name}' caricato con successo.")
        except OSError:
            print(f"Modello spaCy '{model_name}' non trovato. Tentativo di download...")
            try:
                spacy.cli.download(model_name)
                NLP_PROCESSOR = spacy.load(model_name) # Ricarica dopo il download
                print(f"Modello spaCy '{model_name}' scaricato e caricato con successo.")
            except Exception as e:
                print(f"Errore durante il download o caricamento del modello spaCy '{model_name}': {e}")
                print(f"Assicurati di aver eseguito 'python -m spacy download {model_name}' (o il modello desiderato).")
                # Considera se vuoi che l'applicazione si fermi qui o continui senza NLP
                # Per ora, rilanciamo l'eccezione se il caricamento fallisce completamente.
                raise 
    return NLP_PROCESSOR

def normalize_text(text: str, nlp: Language) -> str:
    """
    Normalizza il testo dato utilizzando spaCy per:
    1. Conversione in minuscolo.
    2. Tokenizzazione.
    3. Lemmatizzazione.
    4. Rimozione di punteggiatura e simboli non strettamente alfanumerici (mantenendo spazi).
    5. Rimozione delle stop words.
    6. Rimozione di spazi multipli.
    I numeri vengono mantenuti.

    Args:
        text (str): Il testo da normalizzare.
        nlp (Language): L'istanza del modello spaCy caricato.

    Returns:
        str: Il testo normalizzato.
    """
    if not text or not isinstance(text, str):
        return ""

    doc = nlp(text.lower()) 

    normalized_tokens = []
    for token in doc:
        if not token.is_stop and not token.is_punct and not token.is_space:
            normalized_tokens.append(token.lemma_)

    normalized_string = " ".join(normalized_tokens)
    normalized_string = " ".join(normalized_string.split()) 
    
    return normalized_string

if __name__ == "__main__":
    try:
        # Test di caricamento modello
        print(f"Tentativo di caricare il modello: {NLP_MODEL_NAME}")
        nlp_processor_instance = load_spacy_model()
        print(f"Modello caricato: {nlp_processor_instance.meta['lang']}_{nlp_processor_instance.meta['name']}@{nlp_processor_instance.meta['version']}")

        testo_esempio = """
        Questo è un Testo di Esempio per la normalizzazione!! 
        Contiene Punteggiatura, parole INUTILI come il e lo, e numeri 123.
        L'obiettivo è pulirlo per l'analisi RAG. Speriamo funzioni bene.
        I cani correvano velocemente verso le case colorate.
        """
        testo_normalizzato = normalize_text(testo_esempio, nlp_processor_instance)
        
        print("\n--- Testo Originale ---")
        print(testo_esempio)
        print("\n--- Testo Normalizzato ---")
        print(testo_normalizzato)

        print("\n--- Altro Testo ---")
        testo_2 = "Polizza N. 123/AB - Scadenza: 15/07/2025. Importo: € 500,00."
        normalizzato_2 = normalize_text(testo_2, nlp_processor_instance)
        print(f"Originale: {testo_2}")
        print(f"Normalizzato: {normalizzato_2}")
        # Output atteso (circa): "polizza 123 ab scadenza 15 07 2025 importo 500 00"
        # (spaCy potrebbe rimuovere "N." e "€" come punteggiatura)

    except Exception as e:
        print(f"Errore nell'esempio di text_processing.py: {e}")

