# app/modules/dialogue_manager.py
import random
from typing import Dict, List, Any, Optional
from app.models.schemas import Intent, SuggestedAction # SuggestedAction è importato correttamente
from app.utils.logging_config import logger

class DialogueManager:
    """
    Gestisce il flusso del dialogo e determina le azioni suggerite
    in base all'intento e al contesto
    """
    
    def __init__(self):
        # Definisci le azioni suggerite per ogni tipo di intento
        # CORREZIONE: Usare 'label' e 'payload' invece di 'text' e 'value'
        self.intent_actions: Dict[str, List[SuggestedAction]] = {
            "preventivo": [
                SuggestedAction(
                    type="link",
                    label="Compila modulo preventivo", # CORRETTO
                    payload="/form/quote"              # CORRETTO
                ),
                SuggestedAction(
                    type="contact",
                    label="Parla con un agente",        # CORRETTO
                    payload="contact"                  # CORRETTO
                ),
                SuggestedAction(
                    type="message", # 'message' suggerisce che il payload è un testo di query
                    label="Quali documenti servono?", # CORRETTO
                    payload="Quali documenti servono per un preventivo?" # CORRETTO
                )
            ],
            "reclamo": [
                SuggestedAction(
                    type="link",
                    label="Apri un ticket",
                    payload="/support/ticket"
                ),
                SuggestedAction(
                    type="contact",
                    label="Assistenza telefonica",
                    payload="phone"
                ),
                SuggestedAction(
                    type="message",
                    label="Tempi di risposta?",
                    payload="Quali sono i tempi di risposta per un reclamo?"
                )
            ],
            "sinistro": [
                SuggestedAction(
                    type="link",
                    label="Documenta il sinistro",
                    payload="/sinistri/nuovo"
                ),
                SuggestedAction(
                    type="contact",
                    label="Assistenza immediata",
                    payload="emergency"
                ),
                SuggestedAction(
                    type="message",
                    label="Tempi di rimborso?",
                    payload="Quali sono i tempi di rimborso per un sinistro?"
                )
            ],
            "copertura": [
                SuggestedAction(
                    type="link",
                    label="Verifica copertura",
                    payload="/polizze/verifica"
                ),
                SuggestedAction(
                    type="message",
                    label="Coperture opzionali",
                    payload="Quali sono le coperture opzionali disponibili?"
                )
            ],
            "saluto": [
                SuggestedAction(
                    type="message",
                    label="Informazioni sulle polizze",
                    payload="Che tipo di polizze offrite?"
                ),
                SuggestedAction(
                    type="message",
                    label="Richiedi preventivo",
                    payload="Vorrei un preventivo per un'assicurazione"
                )
            ],
            "ringraziamento": [
                SuggestedAction(
                    type="message",
                    label="Hai altre domande?",
                    payload="Ho un'altra domanda"
                ),
                SuggestedAction(
                    type="link",
                    label="Valuta assistenza",
                    payload="/feedback"
                )
            ],
            "congedo": [
                SuggestedAction(
                    type="link",
                    label="Resta aggiornato",
                    payload="/newsletter"
                ),
                SuggestedAction(
                    type="message",
                    label="In futuro", # Potrebbe essere più chiaro come "Ti ricontatterò"
                    payload="Ti ricontatterò in futuro"
                )
            ],
            "informazioni_generali": [
                SuggestedAction(
                    type="link",
                    label="Scopri le nostre polizze",
                    payload="/products"
                ),
                SuggestedAction(
                    type="link",
                    label="FAQ",
                    payload="/faq"
                ),
                SuggestedAction(
                    type="message",
                    label="Come funziona la polizza auto?",
                    payload="Come funziona la polizza auto?"
                )
            ]
            # Aggiungi qui altre azioni per intenti specifici se necessario
        }
    
    def get_response_prefix(self, intent: Intent) -> str:
        """
        Genera un prefisso per la risposta basato sull'intento
        
        Args:
            intent: L'intento rilevato
            
        Returns:
            Un prefisso appropriato per la risposta
        """
        prefixes = {
            "preventivo": [
                "Sarei felice di aiutarti con un preventivo. ",
                "Posso sicuramente assisterti per un preventivo. ",
                "Per quanto riguarda il preventivo, "
            ],
            "reclamo": [
                "Mi dispiace per il problema riscontrato. ",
                "Comprendo il tuo disagio. ",
                "Siamo qui per risolvere il problema. "
            ],
            "sinistro": [
                "Per quanto riguarda il sinistro, ",
                "In merito alla gestione del sinistro, ",
                "Ecco come procedere per il sinistro: "
            ],
            "copertura": [
                "Riguardo alle coperture assicurative, ",
                "Ecco le informazioni sulle coperture: ",
                "Per quanto riguarda la copertura, "
            ],
            "saluto": [ # Questi prefissi potrebbero non essere usati se get_direct_response gestisce 'saluto'
                "Ciao! ",
                "Buongiorno! ",
                "Salve! "
            ],
            "ringraziamento": [ # Come sopra
                "Prego! ",
                "Non c'è di che! ",
                "È un piacere! "
            ],
            "congedo": [ # Come sopra
                "Arrivederci! ",
                "A presto! ",
                "Buona giornata! "
            ],
            "informazioni_generali": [
                "Ecco le informazioni che cerchi. ",
                "Posso fornirti queste informazioni. ",
                "Riguardo alla tua richiesta, "
            ]
        }
        
        if intent.type in prefixes:
            return random.choice(prefixes[intent.type])
        
        return ""
    
    def get_direct_response(self, intent: Intent) -> Optional[str]:
        """
        Fornisce una risposta diretta completa per intenti conversazionali.
        """
        direct_responses = {
            "saluto": [
                "Ciao! Sono il tuo assistente assicurativo virtuale. Come posso aiutarti oggi?",
                "Buongiorno! Sono qui per rispondere alle tue domande sulle nostre polizze assicurative. Cosa ti interessa sapere?",
                "Salve! Sono lieto di assisterti. Posso aiutarti con informazioni sulle nostre polizze, preventivi o gestione sinistri."
            ],
            "ringraziamento": [
                "Prego, è un piacere poterti aiutare! C'è altro di cui hai bisogno?",
                "Non c'è di che! Sono qui apposta. Posso fare qualcos'altro per te?",
                "Di nulla! Sono felice di essere stato utile. Sono qui se hai altre domande."
            ],
            "congedo": [
                "Arrivederci! Grazie per avermi contattato. Torna pure quando hai bisogno di assistenza.",
                "A presto! È stato un piacere aiutarti. Sarò qui se avrai bisogno di ulteriori informazioni.",
                "Grazie per la conversazione! Ti auguro una buona giornata. Non esitare a contattarmi di nuovo per qualsiasi necessità."
            ]
        }
        
        if intent.type in direct_responses:
            return random.choice(direct_responses[intent.type])
        
        return None
    
    def get_fallback_response(self, intent: Intent) -> str:
        """
        Fornisce una risposta di fallback se il sistema RAG fallisce o produce una risposta inadeguata.
        """
        prefix = self.get_response_prefix(intent)
        
        fallback_responses = {
            "preventivo": [
                "Posso aiutarti con un preventivo personalizzato. Per procedere, avrei bisogno di alcune informazioni come il tipo di polizza che ti interessa e alcuni dettagli specifici. Vuoi procedere?",
                "Per fornirti un preventivo accurato, avrei bisogno di qualche informazione in più. Che tipo di polizza ti interessa?"
            ],
            "reclamo": [
                "Mi dispiace per i problemi riscontrati. Per gestire al meglio la tua segnalazione, posso metterti in contatto con un nostro operatore o aiutarti ad aprire un ticket formale. Cosa preferisci?",
                "Comprendo la tua insoddisfazione. Per risolvere al meglio il problema, sarebbe utile avere maggiori dettagli sul disservizio riscontrato."
            ],
            "sinistro": [
                "Per la gestione dei sinistri è importante seguire la procedura corretta. Posso guidarti nei passaggi o metterti in contatto con un nostro specialista. Come preferisci procedere?",
                "La corretta gestione di un sinistro richiede alcuni passaggi specifici. Puoi fornirmi maggiori dettagli sul tipo di sinistro da denunciare?"
            ],
            "copertura": [
                "Le nostre polizze offrono diverse tipologie di copertura personalizzabili in base alle tue esigenze. Posso darti informazioni più specifiche se mi indichi quale tipo di polizza ti interessa (auto, casa, etc.).",
                "Offriamo coperture assicurative per diverse necessità. Per aiutarti meglio, potresti specificare per quale tipo di rischio cerchi copertura?"
            ],
            "informazioni_generali": [
                "Posso fornirti informazioni sulle nostre polizze assicurative, aiutarti con preventivi o assisterti nella gestione di sinistri. Cosa ti interessa in particolare?",
                "Sono il tuo assistente virtuale per tutto ciò che riguarda le nostre polizze assicurative. Come posso aiutarti oggi?"
            ]
        }
        
        if intent.type in fallback_responses:
            fallback = random.choice(fallback_responses[intent.type])
            # Se l'intento è già di tipo conversazionale, la risposta di fallback
            # è già completa e non necessita di prefisso (a meno che il prefisso non sia vuoto)
            if intent.type in ["saluto", "ringraziamento", "congedo"] and not prefix.strip():
                return fallback
            return prefix + fallback
        
        return prefix + "Mi dispiace, ma non sono riuscito a trovare informazioni specifiche. Posso aiutarti con informazioni sulle nostre polizze, preventivi o assistenza per sinistri. Cosa ti interessa?"
    
    def get_suggested_actions(
        self, 
        intent: Intent, 
        conversation_history: Optional[List[Dict[str, Any]]] = None
    ) -> List[SuggestedAction]:
        """
        Determina le azioni suggerite in base all'intento e al contesto
        """
        # Logica di esempio per contestualizzare le azioni suggerite
        if conversation_history:
            if intent.type == "saluto" and len(conversation_history) <= 2: # Primo messaggio o quasi
                return self.intent_actions.get("saluto", self.intent_actions.get("informazioni_generali", []))
                
            if intent.type == "ringraziamento" and len(conversation_history) > 2:
                return self.intent_actions.get("ringraziamento", []) # Potrebbe offrire di terminare o chiedere altro

        # Se l'intento ha azioni predefinite, usale
        if intent.type in self.intent_actions:
            return self.intent_actions[intent.type]
        
        # Fallback a azioni generiche se l'intento non ha azioni specifiche
        # o se non ci sono condizioni contestuali particolari
        logger.debug(f"Nessuna azione specifica per l'intento '{intent.type}', uso azioni per 'informazioni_generali'.")
        return self.intent_actions.get("informazioni_generali", []) # Restituisce lista vuota se anche informazioni_generali non è definito
    
    def should_end_conversation(self, intent: Intent) -> bool:
        """
        Determina se la conversazione dovrebbe terminare in base all'intento
        """
        return intent.type == "congedo" and intent.confidence > 0.6 # Soglia leggermente più alta per terminare

# Crea un'istanza globale
dialogue_manager = DialogueManager()
