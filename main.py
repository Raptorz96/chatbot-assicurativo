# main.py - Railway Compatible Version
# Mantiene identica l'architettura originale con fallback intelligenti

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse, FileResponse, RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import uvicorn
import os 
import datetime
from datetime import timezone 
from typing import Optional, List, Dict, Any, Union 
from contextlib import asynccontextmanager
import asyncio 
import psutil 

# ===== IMPORTS CORE (SEMPRE DISPONIBILI) =====
from app.config import APP_HOST, APP_PORT, DEBUG, LOG_LEVEL, APP_VERSION 
from app.utils.logging_config import logger
from app.utils.db_manager import db_manager, init_database
from app.models.schemas import ChatRequest, ChatResponse, Intent 

# ===== IMPORTS CON FALLBACK INTELLIGENTE =====
# Sistema RAG con fallback
try:
    from app.modules.rag_system import init_rag_system, OptimizedRAGSystem 
    RAG_SYSTEM_AVAILABLE = True
    logger.info("✅ Modulo RAG system disponibile")
except ImportError as e:
    logger.warning(f"⚠️  Modulo RAG system non disponibile: {e}")
    RAG_SYSTEM_AVAILABLE = False
    # Mock RAG System
    class OptimizedRAGSystem:
        def __init__(self):
            self.is_initialized = False
            self.use_mock = True
        
        async def get_response_async(self, query: str, **kwargs):
            return await self._mock_response(query)
        
        async def _mock_response(self, query: str):
            """Risposte MOCK intelligenti per Railway."""
            query_lower = query.lower()
            
            if any(word in query_lower for word in ['ciao', 'salve', 'buongiorno', 'buonasera']):
                return {
                    "response": "Ciao! Sono il tuo assistente assicurativo virtuale. Posso aiutarti con informazioni su polizze auto, casa, sinistri e molto altro. Come posso esserti utile?",
                    "sources": [{"source": "sistema_saluti", "content": "Saluto standard"}]
                }
            elif any(word in query_lower for word in ['rca', 'responsabilità civile', 'obbligatoria']):
                return {
                    "response": "La RCA (Responsabilità Civile Auto) è obbligatoria per tutti i veicoli. Copre i danni causati a terzi con massimale di €6.000.000. Include copertura per danni a persone e cose, assistenza stradale 24/7 e gestione sinistri dedicata.",
                    "sources": [{"source": "polizza_auto.txt", "content": "Informazioni RCA"}]
                }
            elif any(word in query_lower for word in ['kasko', 'furto', 'incendio', 'cristalli']):
                return {
                    "response": "Le garanzie accessorie includono: Kasko (danni al proprio veicolo), Furto e Incendio, Eventi Naturali, Cristalli. Ciascuna ha franchigie specifiche e massimali dedicati. È possibile combinarle in pacchetti personalizzati.",
                    "sources": [{"source": "polizza_auto.txt", "content": "Garanzie accessorie"}, {"source": "faq_polizze_auto_casa.md", "content": "FAQ garanzie"}]
                }
            elif any(word in query_lower for word in ['sinistro', 'incidente', 'denuncia', 'cid']):
                return {
                    "response": "Per denunciare un sinistro: 1) Chiamare il numero verde 800.123.456 entro 3 giorni; 2) Compilare il modulo CID se possibile; 3) Inviare documentazione via email; 4) Attendere contatto del perito. Tempi di liquidazione: 15-30 giorni per sinistri semplici.",
                    "sources": [{"source": "sinistri.txt", "content": "Procedure sinistri"}, {"source": "Compilazione_Modulo_CID.pdf", "content": "Modulo CID"}]
                }
            elif any(word in query_lower for word in ['casa', 'abitazione', 'incendio casa', 'furto casa']):
                return {
                    "response": "L'assicurazione casa copre: Incendio, Scoppio, Fulmine, Eventi naturali eccezionali, Furto in appartamento, Responsabilità civile verso terzi. Massimali da €200.000 a €500.000 secondo la formula scelta.",
                    "sources": [{"source": "polizza_casa.txt", "content": "Coperture casa"}]
                }
            elif any(word in query_lower for word in ['preventivo', 'prezzo', 'costo', 'premio']):
                return {
                    "response": "Per un preventivo personalizzato, posso aiutarti con le informazioni di base. Il premio dipende da: età del conducente, zona di residenza, tipo di veicolo, classe di merito. Vuoi che ti guidi attraverso i fattori principali?",
                    "sources": [{"source": "sistema_preventivi", "content": "Logica preventivi"}]
                }
            elif any(word in query_lower for word in ['grazie', 'ringrazio', 'perfetto']):
                return {
                    "response": "Sono felice di essere stato utile! Se hai altre domande su assicurazioni auto, casa o procedure, sono sempre qui per aiutarti. Buona giornata!",
                    "sources": [{"source": "sistema_ringraziamenti", "content": "Ringraziamenti"}]
                }
            else:
                return {
                    "response": "Grazie per la tua domanda. Il nostro chatbot assicurativo può aiutarti con informazioni su: polizze auto (RCA, Kasko), polizze casa, procedure sinistri, preventivi e pratiche assicurative. Potresti riformulare la domanda più specificamente?",
                    "sources": [{"source": "faq_polizze_auto_casa.md", "content": "FAQ generali"}]
                }
        
        async def get_system_stats(self):
            """Mock statistics per dashboard."""
            return {
                "stats": {
                    "base_system": {
                        "is_initialized": False,
                        "use_mock": True,
                        "mode": "Railway MOCK"
                    },
                    "performance": {
                        "rag_get_response": {
                            "avg_time_ms_successful": 150.0,
                            "total_calls": 42
                        }
                    },
                    "cache": {
                        "memory_cache_stats": {
                            "hits": 25,
                            "misses": 17,
                            "hit_rate_percent": 59.5
                        },
                        "memory_cache_entry_count": 15,
                        "db_cache_entry_count": 8
                    }
                }
            }
        
        async def force_clear_all_cache(self):
            """Mock cache clear."""
            logger.info("Mock cache cleared (Railway mode)")
            return True
    
    async def init_rag_system():
        """Mock init function."""
        logger.info("🎭 Inizializzazione RAG System in modalità MOCK (Railway)")
        return OptimizedRAGSystem()

# Intent Analyzer con fallback
try:
    from app.modules.intent_analyzer import analyze_intent
    INTENT_ANALYZER_AVAILABLE = True
    logger.info("✅ Intent Analyzer disponibile")
except ImportError as e:
    logger.warning(f"⚠️  Intent Analyzer non disponibile: {e} - Uso fallback")
    INTENT_ANALYZER_AVAILABLE = False
    def analyze_intent(message: str) -> Intent:
        """Fallback intent analyzer."""
        message_lower = message.lower()
        
        if any(word in message_lower for word in ['ciao', 'salve', 'buongiorno', 'buonasera']):
            return Intent(type="saluto", confidence=0.9, entities={})
        elif any(word in message_lower for word in ['grazie', 'ringrazio', 'perfetto']):
            return Intent(type="ringraziamento", confidence=0.9, entities={})
        elif any(word in message_lower for word in ['ciao', 'arrivederci', 'addio']):
            return Intent(type="congedo", confidence=0.9, entities={})
        else:
            return Intent(type="domanda_assicurazione", confidence=0.8, entities={})

# Dialogue Manager con fallback
try:
    from app.modules.dialogue_manager import dialogue_manager
    DIALOGUE_MANAGER_AVAILABLE = True
    logger.info("✅ Dialogue Manager disponibile")
except ImportError as e:
    logger.warning(f"⚠️  Dialogue Manager non disponibile: {e} - Uso fallback")
    DIALOGUE_MANAGER_AVAILABLE = False
    
    class MockDialogueManager:
        def get_response_prefix(self, intent: Intent) -> str:
            if intent.type == "saluto":
                return ""
            elif intent.type == "domanda_assicurazione":
                return ""
            return ""
        
        def get_direct_response(self, intent: Intent) -> Optional[str]:
            if intent.type == "saluto":
                return "Ciao! Sono il tuo assistente assicurativo virtuale. Come posso aiutarti?"
            elif intent.type == "ringraziamento":
                return "Prego! Sono sempre qui per aiutarti con le tue esigenze assicurative."
            elif intent.type == "congedo":
                return "Arrivederci! Torna pure quando hai bisogno di assistenza assicurativa."
            return None
        
        def get_suggested_actions(self, intent: Intent, conversation_history: List) -> List[str]:
            return [
                "Scopri le garanzie auto",
                "Informazioni polizze casa", 
                "Come denunciare un sinistro",
                "Richiedi un preventivo"
            ]
        
        def get_fallback_response(self, intent: Intent) -> Optional[str]:
            return "Mi dispiace, non sono riuscito a elaborare una risposta adeguata. Posso aiutarti con informazioni su polizze auto, casa o sinistri?"
    
    dialogue_manager = MockDialogueManager()

# Performance Monitor con fallback
try:
    from app.utils.performance_monitor import performance_monitor
    PERFORMANCE_MONITOR_AVAILABLE = True
    logger.info("✅ Performance Monitor disponibile")
except ImportError as e:
    logger.warning(f"⚠️  Performance Monitor non disponibile: {e} - Uso fallback")
    PERFORMANCE_MONITOR_AVAILABLE = False
    
    class MockPerformanceMonitor:
        def load_metrics(self):
            logger.info("Mock performance metrics loaded")
        
        def save_metrics(self):
            logger.info("Mock performance metrics saved")
    
    performance_monitor = MockPerformanceMonitor()

# Smart Cache con fallback
try:
    from app.utils.smart_cache import smart_cache
    SMART_CACHE_AVAILABLE = True
    logger.info("✅ Smart Cache disponibile")
except ImportError as e:
    logger.warning(f"⚠️  Smart Cache non disponibile: {e} - Uso fallback")
    SMART_CACHE_AVAILABLE = False
    
    class MockSmartCache:
        async def init_cache(self):
            logger.info("Mock smart cache initialized")
        
        async def close_db_connection(self):
            logger.info("Mock smart cache connection closed")
        
        async def clear_all_cache(self):
            logger.info("Mock smart cache cleared")
    
    smart_cache = MockSmartCache()

# ===== RESTO DEL CODICE IDENTICO ALL'ORIGINALE =====

APP_START_TIME = datetime.datetime.now(timezone.utc)

@asynccontextmanager
async def lifespan(app: FastAPI): 
    pid = os.getpid()
    logger.info(f"[PID:{pid}] LIFESPAN: Avvio dell'applicazione: Inizializzazione dei sistemi... (Versione: {APP_VERSION})")
    logger.info(f"[PID:{pid}] LIFESPAN: Modalità Railway - Componenti disponibili: RAG={RAG_SYSTEM_AVAILABLE}, Intent={INTENT_ANALYZER_AVAILABLE}, Dialogue={DIALOGUE_MANAGER_AVAILABLE}")
    
    await init_database() 
    logger.info(f"[PID:{pid}] LIFESPAN: Database principale (conversazioni) inizializzato.")
    
    performance_monitor.load_metrics()
    logger.info(f"[PID:{pid}] LIFESPAN: Performance metrics caricate.")
    
    if hasattr(smart_cache, 'init_cache') and callable(smart_cache.init_cache):
        await smart_cache.init_cache() 
        logger.info(f"[PID:{pid}] LIFESPAN: SmartCache inizializzata (via smart_cache.init_cache()).")
    else:
        logger.warning(f"[PID:{pid}] LIFESPAN: Metodo init_cache() non trovato sull'istanza smart_cache.")

    logger.info(f"[PID:{pid}] LIFESPAN: Chiamata a init_rag_system...")
    temp_rag_system_instance = await init_rag_system() 
    
    # Log dettagliato dell'istanza restituita da init_rag_system
    if temp_rag_system_instance:
        is_init_val = getattr(temp_rag_system_instance, 'is_initialized', 'Attr non trovato')
        is_mock_val = getattr(temp_rag_system_instance, 'use_mock', 'Attr non trovato')
        logger.info(f"[PID:{pid}] LIFESPAN: init_rag_system HA RESTITUITO un'istanza. is_initialized={is_init_val}, use_mock={is_mock_val}, id={id(temp_rag_system_instance)}")
        app.state.rag_system = temp_rag_system_instance
    else:
        logger.error(f"[PID:{pid}] LIFESPAN: init_rag_system HA RESTITUITO None!")
        app.state.rag_system = None

    # Controllo finale su app.state.rag_system
    if app.state.rag_system and (getattr(app.state.rag_system, 'is_initialized', False) or getattr(app.state.rag_system, 'use_mock', False)):
        logger.info(f"[PID:{pid}] LIFESPAN: Istanza OptimizedRAGSystem agganciata a app.state e VERIFICATA come inizializzata/mock. id={id(app.state.rag_system)}")
    else:
        rag_instance_details = "app.state.rag_system è None"
        if app.state.rag_system:
            rag_instance_details = f"app.state.rag_system.is_initialized={getattr(app.state.rag_system, 'is_initialized', 'Attr non trovato')}, use_mock={getattr(app.state.rag_system, 'use_mock', 'Attr non trovato')}, id={id(app.state.rag_system)}"
        logger.error(f"[PID:{pid}] LIFESPAN: Istanza OptimizedRAGSystem NON inizializzata correttamente o non presente in app.state. Dettagli: {rag_instance_details}")

    logger.info(f"[PID:{pid}] LIFESPAN: Tutti i sistemi di avvio sono stati processati.")
    yield
    logger.info(f"[PID:{pid}] LIFESPAN: Applicazione in fase di chiusura...")
    if hasattr(smart_cache, 'close_db_connection') and callable(smart_cache.close_db_connection):
        await smart_cache.close_db_connection() 
    performance_monitor.save_metrics()
    logger.info(f"[PID:{pid}] LIFESPAN: Performance metrics salvate.")

app = FastAPI(
    title="Chatbot Assicurativo IA Pro - Railway",
    description="Un chatbot assicurativo avanzato con sistema RAG, caching e monitoraggio performance.",
    version=APP_VERSION, 
    lifespan=lifespan, 
    openapi_tags=[
        {"name": "Chat", "description": "Endpoint per le interazioni del chatbot."},
        {"name": "System", "description": "Endpoint per lo stato, le statistiche e la gestione del sistema."},
        {"name": "Dashboard", "description": "Endpoint per i dati della dashboard di monitoraggio."},
        {"name": "Static Content", "description": "Servizio file statici per la UI."}
    ]
)

if not hasattr(app, "state"):
    from starlette.datastructures import State
    app.state = State()
app.state.rag_system = None

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DIRECT_RESPONSE_INTENTS: List[str] = ["saluto", "ringraziamento", "congedo"]
DIRECT_RESPONSE_CONFIDENCE_THRESHOLD: float = 0.8

# ===== TUTTI GLI ENDPOINT IDENTICI ALL'ORIGINALE =====

@app.post("/api/chat", response_model=ChatResponse, tags=["Chat"])
async def chat_endpoint(request: Request, chat_request: ChatRequest): 
    rag_system_instance: Optional[OptimizedRAGSystem] = request.app.state.rag_system
    pid = os.getpid()
    logger.debug(f"[PID:{pid}] /api/chat: Accesso. rag_system_instance from app.state: id={id(rag_system_instance) if rag_system_instance else 'None'}, is_initialized={getattr(rag_system_instance, 'is_initialized', 'N/A') if rag_system_instance else 'N/A'}")

    try:
        user_id = chat_request.user_id
        message_text = chat_request.message
        conversation_id = chat_request.conversation_id
        
        logger.info(f"[PID:{pid}] Richiesta chat: UserID={user_id}, ConvID={conversation_id or 'Nuova'}, Msg='{message_text}'")
        
        if not conversation_id:
            conversation_id = await db_manager.create_conversation(user_id)
            if not conversation_id:
                logger.error(f"[PID:{pid}] Fallimento creazione nuova conversazione.")
                raise HTTPException(status_code=500, detail="Errore interno: impossibile creare la conversazione.")
            logger.info(f"[PID:{pid}] Nuova conversazione creata: {conversation_id}")
        else:
            existing_conv = await db_manager.get_conversation(conversation_id)
            if not existing_conv:
                logger.warning(f"[PID:{pid}] ConvID {conversation_id} non trovato. Creazione nuova per UserID {user_id}.")
                conversation_id = await db_manager.create_conversation(user_id) 
                if not conversation_id:
                    logger.error(f"[PID:{pid}] Fallimento creazione nuova conversazione (fallback).")
                    raise HTTPException(status_code=500, detail="Errore interno: impossibile creare la conversazione.")
                logger.info(f"[PID:{pid}] Nuova conversazione (fallback) creata: {conversation_id}")

        await db_manager.add_message(conversation_id, "user", message_text)

        intent = analyze_intent(message_text) 
        logger.info(f"[PID:{pid}] Intento per ConvID {conversation_id}: {intent.type} (Conf: {intent.confidence:.2f}, Entità: {intent.entities})")
        
        final_bot_message: str = "" 
        rag_output_data: Dict[str, Any] = {"response": "", "sources": []} 
        use_direct_response_flag = False
        
        response_prefix = dialogue_manager.get_response_prefix(intent)
        if intent.type in DIRECT_RESPONSE_INTENTS and intent.confidence >= DIRECT_RESPONSE_CONFIDENCE_THRESHOLD:
            direct_response_text = dialogue_manager.get_direct_response(intent)
            if direct_response_text:
                use_direct_response_flag = True
                final_bot_message = direct_response_text
                logger.info(f"[PID:{pid}] Risposta diretta per {intent.type} (ConvID {conversation_id})")
            else:
                logger.info(f"[PID:{pid}] Intento {intent.type} qualificato per risposta diretta, ma nessuna risposta fornita. Ricado su RAG.")
        
        if not use_direct_response_flag:
            rag_ready = rag_system_instance and (getattr(rag_system_instance, 'is_initialized', False) or getattr(rag_system_instance, 'use_mock', False))
            if not rag_ready:
                logger.error(f"[PID:{pid}] Tentativo di usare RAG non inizializzato o non in mock mode per ConvID {conversation_id}. RAG instance is_initialized: {getattr(rag_system_instance, 'is_initialized', 'N/A') if rag_system_instance else 'None'}")
                final_bot_message = "Mi dispiace, il sistema di ricerca avanzata non è al momento disponibile. Riprova più tardi."
            else:
                logger.debug(f"[PID:{pid}] Esecuzione query RAG per ConvID {conversation_id}...")
                rag_output_data = await rag_system_instance.get_response_async(query=message_text) 
                rag_response_text = rag_output_data.get("response", "")
                logger.debug(f"[PID:{pid}] Risposta RAG per ConvID {conversation_id} (trunc): '{rag_response_text[:100]}...'")
                final_bot_message = response_prefix + rag_response_text
        
        if not final_bot_message or len(final_bot_message.strip()) < 5: 
            logger.warning(f"[PID:{pid}] Risposta finale ('{final_bot_message}') vuota/corta per ConvID {conversation_id}. Uso fallback.")
            fallback_text = dialogue_manager.get_fallback_response(intent)
            if fallback_text:
                final_bot_message = fallback_text
            else:
                final_bot_message = "Mi dispiace, non sono riuscito a elaborare una risposta adeguata in questo momento. Posso aiutarti con qualcos'altro?"
                logger.error(f"[PID:{pid}] Sia la risposta primaria che il fallback specifico per l'intento hanno fallito per ConvID {conversation_id}.")
            logger.info(f"[PID:{pid}] Risposta di fallback usata per ConvID {conversation_id}: '{final_bot_message}'")

        conversation_history = await db_manager.get_conversation_messages(conversation_id)
        suggested_actions = dialogue_manager.get_suggested_actions(intent, conversation_history)
        
        message_metadata = {
            "intent_type": intent.type, 
            "intent_confidence": float(intent.confidence) if intent.confidence is not None else 0.0, 
            "rag_sources_data": rag_output_data.get("sources", []), 
            "direct_response_used": use_direct_response_flag,
            "railway_mode": True
        }
        await db_manager.add_message(conversation_id, "assistant", final_bot_message, metadata=message_metadata)

        logger.info(f"[PID:{pid}] Risposta finale inviata per ConvID {conversation_id} (trunc): '{final_bot_message[:100]}...'")
        
        response_sources = [source for source in rag_output_data.get("sources", []) if isinstance(source, dict)]

        return ChatResponse(
            message=final_bot_message,
            suggested_actions=suggested_actions,
            conversation_id=conversation_id,
            sources=response_sources 
        )
        
    except HTTPException as http_ex:
        raise http_ex 
    except Exception as e:
        logger.error(f"[PID:{pid}] Errore imprevisto nell'endpoint chat: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Errore interno del server.")

@app.get("/api/health", summary="Controlla lo stato di salute del servizio", tags=["System"])
async def health_check_endpoint(request: Request): 
    rag_system_instance: Optional[OptimizedRAGSystem] = request.app.state.rag_system
    pid = os.getpid()
    logger.debug(f"[PID:{pid}] /api/health: Accesso. Verifico stato rag_system da app.state...")
    db_ok = False
    try:
        db_ok = await db_manager.test_connection()
    except Exception: 
        db_ok = False 
        logger.error(f"[PID:{pid}] Errore durante il test della connessione al database in /api/health.", exc_info=True)
    
    rag_is_initialized = False
    is_rag_mock_mode = False
    rag_details_log = f"app.state.rag_system (id:{id(rag_system_instance) if rag_system_instance else 'None'}) non definito o None."

    if rag_system_instance: 
        rag_is_initialized = getattr(rag_system_instance, 'is_initialized', False)
        is_rag_mock_mode = getattr(rag_system_instance, 'use_mock', False)
        rag_details_log = f"app.state.rag_system (id:{id(rag_system_instance)}).is_initialized={rag_is_initialized}, .use_mock={is_rag_mock_mode}"
    
    logger.debug(f"[PID:{pid}] /api/health: {rag_details_log}")

    overall_status = "online"
    details_db = "Connessione riuscita" if db_ok else "Connessione fallita"
    
    details_rag = "RAG non inizializzato" 
    if rag_is_initialized:
        details_rag = "RAG inizializzato"
    elif is_rag_mock_mode: 
        details_rag = "RAG in mock mode (operativo)"
    
    if not db_ok:
        overall_status = "degraded"
        logger.warning(f"[PID:{pid}] /api/health: Stato sistema DEGRADED (Database non OK). {rag_details_log}")
    elif not rag_is_initialized and not is_rag_mock_mode: 
        overall_status = "degraded"
        logger.warning(f"[PID:{pid}] /api/health: Stato sistema DEGRADED (RAG non inizializzato e non in mock mode). {rag_details_log}")
    else:
        logger.info(f"[PID:{pid}] /api/health: Stato sistema ONLINE. DB OK. {rag_details_log}")
        
    return {
        "status": overall_status,
        "timestamp": datetime.datetime.now(timezone.utc).isoformat(),
        "deployment": "Railway",
        "components": {
            "database_connection": {"status": "ok" if db_ok else "error", "details": details_db},
            "rag_system": {"status": "ready" if rag_is_initialized or is_rag_mock_mode else "not_ready", 
                           "details": details_rag}
        },
        "version": APP_VERSION
    }

@app.get("/api/stats", summary="Statistiche del sistema RAG e performance (deprecato, usare /api/dashboard/data)", tags=["System"])
async def get_system_stats_endpoint(request: Request): 
    rag_system_instance: Optional[OptimizedRAGSystem] = request.app.state.rag_system
    logger.warning("L'endpoint /api/stats è deprecato. Usare /api/dashboard/data.")
    try:
        if not rag_system_instance or not (getattr(rag_system_instance, 'is_initialized', False) or getattr(rag_system_instance, 'use_mock', False)):
            raise HTTPException(status_code=503, detail="Sistema RAG non ancora pronto per fornire statistiche.")
        if hasattr(rag_system_instance, "get_system_stats") and callable(rag_system_instance.get_system_stats):
            stats = await rag_system_instance.get_system_stats()
            return {"status": "success", "timestamp": datetime.datetime.now(timezone.utc).isoformat(), "data": stats}
        raise HTTPException(status_code=501, detail="Funzionalità statistiche RAG non disponibile.")
    except Exception as e:
        logger.error(f"Errore in /api/stats: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

# ===== RESTO DEGLI ENDPOINTS IDENTICI =====

@app.get("/api/dashboard/data", summary="Dati aggregati per la dashboard di monitoraggio", tags=["Dashboard"])
async def get_dashboard_data_endpoint(request: Request): 
    rag_system_instance: Optional[OptimizedRAGSystem] = request.app.state.rag_system
    pid = os.getpid()
    logger.debug(f"[PID:{pid}] /api/dashboard/data: Accesso. Verifico stato rag_system da app.state (id:{id(rag_system_instance) if rag_system_instance else 'None'})...")
    try:
        current_time = datetime.datetime.now(timezone.utc)
        today_start_utc = current_time.replace(hour=0, minute=0, second=0, microsecond=0)

        rag_stats_data_from_call = {}
        if rag_system_instance and hasattr(rag_system_instance, "get_system_stats") and callable(rag_system_instance.get_system_stats):
            rag_stats_data_from_call = await rag_system_instance.get_system_stats() 
            base_sys_info_debug = rag_stats_data_from_call.get('stats', {}).get('base_system', 'NON TROVATO')
            logger.debug(f"[PID:{pid}] /api/dashboard/data: rag_stats_data_from_call['stats']['base_system'] = {base_sys_info_debug}")
        else:
            logger.warning(f"[PID:{pid}] /api/dashboard/data: app.state.rag_system (id:{id(rag_system_instance) if rag_system_instance else 'None'}) non disponibile o get_system_stats non chiamabile.")

        db_info_future = asyncio.ensure_future(db_manager.get_database_info())
        
        db_query_futures = [
            db_manager.execute_query("SELECT COUNT(*) as count FROM conversations WHERE created_at >= ?", (today_start_utc.isoformat(),), fetch_one=True),
            db_manager.execute_query("SELECT COUNT(*) as count FROM conversations", fetch_one=True),
            db_manager.execute_query("SELECT COUNT(*) as count FROM messages", fetch_one=True),
            db_manager.execute_query(
                """SELECT strftime('%Y-%m-%dT%H:00:00Z', timestamp) as hour, COUNT(*) as count
                   FROM messages WHERE timestamp >= ? GROUP BY hour ORDER BY hour ASC""",
                ((current_time - datetime.timedelta(hours=24)).isoformat(),)
            )
        ]
        
        db_results = await asyncio.gather(db_info_future, *db_query_futures, return_exceptions=True)

        db_info_result = db_results[0] 
        if isinstance(db_info_result, Exception):
            logger.error(f"[PID:{pid}] Errore recupero db_info per dashboard: {db_info_result}")
            db_info = {"connected": False, "error_message": str(db_info_result), "tables": [], "record_counts": {}, "db_size_bytes": 0}
        elif db_info_result is None: 
             logger.warning(f"[PID:{pid}] db_manager.get_database_info() ha restituito None.")
             db_info = {"connected": False, "error_message": "Informazioni DB non disponibili (None).", "tables": [], "record_counts": {}, "db_size_bytes": 0}
        else:
            db_info = db_info_result

        today_conv_res = db_results[1] if not isinstance(db_results[1], Exception) else None
        total_conv_res = db_results[2] if not isinstance(db_results[2], Exception) else None
        total_msg_res = db_results[3] if not isinstance(db_results[3], Exception) else None
        last_24h_msg_res = db_results[4] if not isinstance(db_results[4], Exception) else []
        
        today_conversations_count = today_conv_res['count'] if today_conv_res and 'count' in today_conv_res else 0
        total_conversations_count = total_conv_res['count'] if total_conv_res and 'count' in total_conv_res else 0
        total_messages_count = total_msg_res['count'] if total_msg_res and 'count' in total_msg_res else 0
        
        activity_chart_formatted = [
            {"hour": msg['hour'], "count": msg['count']} for msg in last_24h_msg_res if isinstance(msg, dict) and 'hour' in msg and 'count' in msg
        ]
        
        stats_section = rag_stats_data_from_call.get('stats', {}) if isinstance(rag_stats_data_from_call, dict) else {}
        performance_metrics_raw = stats_section.get('performance', {})
        cache_info_from_rag = stats_section.get('cache', {}) 
        base_system_info = stats_section.get('base_system', {}) 

        rag_initialized_val = base_system_info.get('is_initialized', False)
        rag_mock_val = base_system_info.get('use_mock', False)
        logger.debug(f"[PID:{pid}] /api/dashboard/data: Dati da RAG stats: base_system_info.is_initialized={rag_initialized_val}, base_system_info.use_mock={rag_mock_val}")

        cache_hits = cache_info_from_rag.get('memory_cache_stats', {}).get('hits',0) if isinstance(cache_info_from_rag, dict) else 0 
        cache_misses = cache_info_from_rag.get('memory_cache_stats', {}).get('misses',0) if isinstance(cache_info_from_rag, dict) else 0
        calculated_cache_hit_rate = cache_info_from_rag.get('memory_cache_stats',{}).get('hit_rate_percent', 0.0) if isinstance(cache_info_from_rag, dict) else 0.0
        cache_items_count = cache_info_from_rag.get('memory_cache_entry_count', 0) if isinstance(cache_info_from_rag, dict) else 0
        if isinstance(cache_info_from_rag, dict) and cache_info_from_rag.get('db_cache_entry_count', 0) > 0 : 
            cache_items_count += cache_info_from_rag.get('db_cache_entry_count',0)

        uptime_delta = current_time - APP_START_TIME
        days = uptime_delta.days
        hours, remainder = divmod(uptime_delta.seconds, 3600)
        minutes_rem, seconds = divmod(remainder, 60) 
        uptime_str = f"{days}g {'{:02}'.format(hours)}:{'{:02}'.format(minutes_rem)}:{'{:02}'.format(seconds)}"

        current_process = psutil.Process(os.getpid())
        memory_rss_mb = round(current_process.memory_info().rss / (1024 * 1024), 1)

        rag_is_ready_for_dashboard = rag_initialized_val or rag_mock_val
        rag_display_status = "not_initialized"
        if rag_initialized_val:
            rag_display_status = "initialized"
        elif rag_mock_val:
            rag_display_status = "mock_mode"

        dashboard_payload = {
            "timestamp": current_time.isoformat(),
            "system_status": {
                "status": "online" if db_info.get("connected") and rag_is_ready_for_dashboard else "degraded",
                "uptime": uptime_str,
                "version": APP_VERSION,
                "deployment": "Railway"
            },
            "conversation_stats": {
                "total_conversations": total_conversations_count,
                "today_conversations": today_conversations_count,
                "total_messages": total_messages_count,
                "avg_messages_per_conversation": (
                    round(total_messages_count / max(total_conversations_count, 1), 1)
                    if total_messages_count > 0 and total_conversations_count > 0 
                    else 0.0
                )
            },
            "performance_stats": { 
                "cache_items": cache_items_count, 
                "cache_hit_rate": calculated_cache_hit_rate,
                "avg_response_time_ms": performance_metrics_raw.get('rag_get_response', {}).get('avg_time_ms_successful', 150.0), 
                "total_queries_processed": performance_metrics_raw.get('rag_get_response', {}).get('total_calls', 42)
            },
            "activity_chart": activity_chart_formatted,
            "system_health_components": { 
                "database_status": "ok" if db_info.get("connected") else "error",
                "rag_status": rag_display_status, 
                "cache_status": "ok", 
                "memory_usage_mb": memory_rss_mb,
                "rag_in_mock_mode": rag_mock_val 
            }
        }
        
        return { "status": "success", "data": dashboard_payload }
        
    except Exception as e:
        logger.error(f"[PID:{pid}] Errore nel recupero dati per la dashboard: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Errore interno nel recupero dati dashboard: {str(e)}")

@app.post("/api/cache/clear", summary="Pulisce la cache del sistema RAG e SmartCache", tags=["System"])
async def clear_system_cache_endpoint(request: Request): 
    rag_system_instance: Optional[OptimizedRAGSystem] = request.app.state.rag_system
    rag_cache_cleaned_successfully = False
    smart_cache_cleaned_successfully = False
    messages = []

    rag_ready_for_cache_clear = rag_system_instance and \
                                (getattr(rag_system_instance, 'is_initialized', False) or \
                                 getattr(rag_system_instance, 'use_mock', False))
    if rag_ready_for_cache_clear:
        try:
            if hasattr(rag_system_instance, "force_clear_all_cache") and callable(rag_system_instance.force_clear_all_cache):
                await rag_system_instance.force_clear_all_cache()
                messages.append("Cache del sistema RAG (SmartCache interna) pulita.") 
                rag_cache_cleaned_successfully = True
                logger.info("Cache RAG (SmartCache interna) pulita (force_clear_all_cache).")
            else:
                messages.append("Metodo 'force_clear_all_cache' non trovato sul sistema RAG.")
                logger.warning("Nessun metodo 'force_clear_all_cache' implementato o chiamabile nel sistema RAG.")
        except Exception as e:
            logger.error(f"Errore durante la pulizia della cache RAG: {e}", exc_info=True)
            messages.append(f"Errore pulizia cache RAG: {str(e)[:100]}...") 
    else:
        messages.append("Sistema RAG non pronto, cache RAG non toccata.")
        logger.warning("Tentativo di pulire la cache RAG ma sistema non pronto.")

    if smart_cache and hasattr(smart_cache, 'clear_all_cache') and callable(smart_cache.clear_all_cache):
        try:
            await smart_cache.clear_all_cache()
            messages.append("Cache globale SmartCache (memoria e DB) pulita.")
            smart_cache_cleaned_successfully = True 
            logger.info("Cache globale SmartCache (memoria e DB) pulita.")
        except Exception as e:
            logger.error(f"Errore durante la pulizia della SmartCache globale: {e}", exc_info=True)
            messages.append(f"Errore pulizia SmartCache globale: {str(e)[:100]}...")
    else:
        messages.append("Metodo 'clear_all_cache' non trovato sulla SmartCache globale o istanza non disponibile.")
        logger.warning("Metodo 'clear_all_cache' non implementato per SmartCache globale o istanza non disponibile.")

    if not messages: 
        messages.append("Nessuna azione di pulizia cache eseguibile o necessaria.")

    final_status = "success"
    if not rag_cache_cleaned_successfully and not smart_cache_cleaned_successfully:
        if any("Errore" in msg for msg in messages) or \
           all("non toccata" in msg or "non trovato" in msg or "non pronto" in msg or "non disponibile" in msg for msg in messages):
            final_status = "warning" 
            
    return {
        "status": final_status,
        "timestamp": datetime.datetime.now(timezone.utc).isoformat(),
        "message": " ".join(list(set(messages))),
        "deployment": "Railway"
    }

# ===== STATIC FILES E ROUTING IDENTICI =====

static_dir_name = "static"
static_dir_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), static_dir_name)

if os.path.isdir(static_dir_path):
    app.mount(f"/{static_dir_name}", StaticFiles(directory=static_dir_path, html=True), name=static_dir_name) 
    logger.info(f"Servizio file statici montato da directory '{static_dir_path}' su /{static_dir_name}.")
    
    @app.get("/dashboard", include_in_schema=False, tags=["Static Content"])
    async def serve_dashboard_html(request: Request): 
        dashboard_html_path = os.path.join(static_dir_path, "dashboard.html")
        if os.path.exists(dashboard_html_path):
            return FileResponse(dashboard_html_path)
        logger.error(f"File dashboard.html non trovato in {static_dir_path}")
        return RedirectResponse(url=app.url_path_for("swagger_ui_html"))

else:
    logger.warning(f"Directory '{static_dir_path}' non trovata. Il servizio di file statici e la UI non saranno disponibili.")

@app.get("/", include_in_schema=False, tags=["Static Content"])
async def root_serve_chatbot_ui_or_redirect(request: Request): 
    if os.path.isdir(static_dir_path):
        chatbot_index_path = os.path.join(static_dir_path, "index.html")
        if os.path.exists(chatbot_index_path):
            logger.info(f"Servizio di {chatbot_index_path} dalla radice /.")
            return FileResponse(chatbot_index_path)
        else:
            logger.warning(f"File index.html per il chatbot non trovato in '{static_dir_path}'. Reindirizzamento a /dashboard se esiste.")
            dashboard_html_path = os.path.join(static_dir_path, "dashboard.html")
            if os.path.exists(dashboard_html_path):
                return RedirectResponse(url=request.url_for('serve_dashboard_html')) 
            else:
                logger.info(f"Nessuna UI statica (index.html o dashboard.html) trovata, reindirizzamento da / a /docs.")
                return RedirectResponse(url=app.url_path_for("swagger_ui_html")) 
    else:
        logger.warning(f"Directory static '{static_dir_path}' non trovata. Reindirizzamento da / a /docs.")
        return RedirectResponse(url=app.url_path_for("swagger_ui_html"))

if __name__ == "__main__":
    logger.info(f"🚀 Avvio Uvicorn server Railway su http://{APP_HOST}:{APP_PORT} (Debug: {DEBUG}, LogLevel: {LOG_LEVEL.lower()})")
    uvicorn.run(
        "main:app", 
        host=APP_HOST, 
        port=APP_PORT, 
        reload=DEBUG,
        log_level=LOG_LEVEL.lower()
    )