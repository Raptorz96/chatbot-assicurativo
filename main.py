# main.py - Custom RAG System Integration
# Railway Compatible - Zero LangChain dependencies

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

# ===== IMPORTS CORE =====
from app.config import APP_HOST, APP_PORT, DEBUG, LOG_LEVEL, APP_VERSION 
from app.utils.logging_config import logger
from app.utils.db_manager import db_manager, init_database
from app.models.schemas import ChatRequest, ChatResponse, Intent 

# ===== CUSTOM RAG SYSTEM =====
try:
    from app.modules.rag_system import init_rag_system, CustomRAGEngine
    RAG_SYSTEM_AVAILABLE = True
    logger.info("✅ Custom RAG System disponibile")
except ImportError as e:
    logger.error(f"❌ Custom RAG System non disponibile: {e}")
    RAG_SYSTEM_AVAILABLE = False
    
    # Emergency fallback
    class CustomRAGEngine:
        def __init__(self):
            self.is_initialized = False
        
        async def get_response_async(self, query: str, **kwargs):
            return {
                "response": f"Sistema RAG non disponibile. Query: {query}",
                "sources": []
            }
        
        async def get_system_stats(self):
            return {"stats": {"base_system": {"is_initialized": False, "error": "RAG non disponibile"}}}
        
        async def force_clear_all_cache(self):
            return True
    
    async def init_rag_system():
        return CustomRAGEngine()

# ===== FALLBACK COMPONENTS =====
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
            return ""
        
        def get_direct_response(self, intent: Intent) -> Optional[str]:
            if intent.type == "saluto":
                return "Ciao! Sono il tuo assistente assicurativo. Come posso aiutarti?"
            elif intent.type == "ringraziamento":
                return "Prego! Sono sempre qui per aiutarti con le tue esigenze assicurative."
            elif intent.type == "congedo":
                return "Arrivederci! Torna pure quando hai bisogno di assistenza."
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

# ===== CONSTANTS =====
APP_START_TIME = datetime.datetime.now(timezone.utc)
DIRECT_RESPONSE_INTENTS: List[str] = ["saluto", "ringraziamento", "congedo"]
DIRECT_RESPONSE_CONFIDENCE_THRESHOLD: float = 0.8

@asynccontextmanager
async def lifespan(app: FastAPI): 
    pid = os.getpid()
    logger.info(f"[PID:{pid}] 🚀 Avvio Custom RAG Chatbot System v{APP_VERSION}")
    logger.info(f"[PID:{pid}] Componenti disponibili: RAG={RAG_SYSTEM_AVAILABLE}, Intent={INTENT_ANALYZER_AVAILABLE}")
    
    # 1. Inizializza database
    await init_database() 
    logger.info(f"[PID:{pid}] ✅ Database principale inizializzato")
    
    # 2. Performance monitor
    performance_monitor.load_metrics()
    logger.info(f"[PID:{pid}] ✅ Performance metrics caricate")
    
    # 3. Smart cache
    if hasattr(smart_cache, 'init_cache') and callable(smart_cache.init_cache):
        await smart_cache.init_cache() 
        logger.info(f"[PID:{pid}] ✅ SmartCache inizializzata")
    
    # 4. Custom RAG System
    logger.info(f"[PID:{pid}] 🧠 Inizializzazione Custom RAG System...")
    try:
        rag_system_instance = await init_rag_system()
        
        if rag_system_instance and getattr(rag_system_instance, 'is_initialized', False):
            app.state.rag_system = rag_system_instance
            logger.info(f"[PID:{pid}] ✅ Custom RAG System inizializzato correttamente")
            
            # Log statistiche
            stats = await rag_system_instance.get_system_stats()
            vector_stats = stats.get('stats', {}).get('base_system', {}).get('vector_store', {})
            total_docs = vector_stats.get('total_documents', 0)
            files_indexed = vector_stats.get('files_indexed', 0)
            logger.info(f"[PID:{pid}] 📊 RAG Stats: {total_docs} documenti, {files_indexed} file indicizzati")
            
        else:
            app.state.rag_system = rag_system_instance  # Anche se non inizializzato
            logger.warning(f"[PID:{pid}] ⚠️  Custom RAG System creato ma non inizializzato")
            
    except Exception as e:
        logger.error(f"[PID:{pid}] ❌ Errore inizializzazione Custom RAG System: {e}", exc_info=True)
        app.state.rag_system = None

    logger.info(f"[PID:{pid}] 🎯 Sistema completamente avviato e operativo")
    yield
    
    # Cleanup
    logger.info(f"[PID:{pid}] 🔄 Shutdown applicazione...")
    if hasattr(smart_cache, 'close_db_connection') and callable(smart_cache.close_db_connection):
        await smart_cache.close_db_connection() 
    performance_monitor.save_metrics()
    logger.info(f"[PID:{pid}] ✅ Shutdown completato")

# Crea app FastAPI
app = FastAPI(
    title="Chatbot Assicurativo Custom RAG",
    description="Sistema RAG personalizzato per assistenza assicurazioni - Railway Compatible",
    version=APP_VERSION, 
    lifespan=lifespan
)

# State initialization
if not hasattr(app, "state"):
    from starlette.datastructures import State
    app.state = State()
app.state.rag_system = None

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ===== API ENDPOINTS =====

@app.post("/api/chat", response_model=ChatResponse, tags=["Chat"])
async def chat_endpoint(request: Request, chat_request: ChatRequest): 
    rag_system_instance: Optional[CustomRAGEngine] = request.app.state.rag_system
    pid = os.getpid()
    logger.debug(f"[PID:{pid}] /api/chat: Richiesta per '{chat_request.message[:50]}...'")

    try:
        user_id = chat_request.user_id
        message_text = chat_request.message
        conversation_id = chat_request.conversation_id
        
        logger.info(f"[PID:{pid}] Chat: UserID={user_id}, ConvID={conversation_id or 'Nuova'}")
        
        # Gestione conversation_id
        if not conversation_id:
            conversation_id = await db_manager.create_conversation(user_id)
            if not conversation_id:
                logger.error(f"[PID:{pid}] Errore creazione conversazione")
                raise HTTPException(status_code=500, detail="Errore creazione conversazione")
            logger.info(f"[PID:{pid}] Nuova conversazione: {conversation_id}")
        else:
            existing_conv = await db_manager.get_conversation(conversation_id)
            if not existing_conv:
                logger.warning(f"[PID:{pid}] ConvID {conversation_id} non trovato, creo nuovo")
                conversation_id = await db_manager.create_conversation(user_id) 
                if not conversation_id:
                    raise HTTPException(status_code=500, detail="Errore creazione conversazione")

        # Salva messaggio utente
        await db_manager.add_message(conversation_id, "user", message_text)

        # Analisi intent
        intent = analyze_intent(message_text) 
        logger.info(f"[PID:{pid}] Intent: {intent.type} (conf: {intent.confidence:.2f})")
        
        final_bot_message: str = "" 
        rag_output_data: Dict[str, Any] = {"response": "", "sources": []} 
        use_direct_response_flag = False
        
        # Check per risposta diretta
        response_prefix = dialogue_manager.get_response_prefix(intent)
        if intent.type in DIRECT_RESPONSE_INTENTS and intent.confidence >= DIRECT_RESPONSE_CONFIDENCE_THRESHOLD:
            direct_response_text = dialogue_manager.get_direct_response(intent)
            if direct_response_text:
                use_direct_response_flag = True
                final_bot_message = direct_response_text
                logger.info(f"[PID:{pid}] Risposta diretta per {intent.type}")
        
        # RAG query se non risposta diretta
        if not use_direct_response_flag:
            rag_ready = rag_system_instance and getattr(rag_system_instance, 'is_initialized', False)
            if not rag_ready:
                logger.error(f"[PID:{pid}] RAG System non disponibile")
                final_bot_message = "Mi dispiace, il sistema di ricerca non è al momento disponibile. Riprova più tardi."
            else:
                logger.debug(f"[PID:{pid}] Esecuzione query RAG...")
                rag_output_data = await rag_system_instance.get_response_async(query=message_text) 
                rag_response_text = rag_output_data.get("response", "")
                logger.info(f"[PID:{pid}] Risposta RAG ottenuta ({len(rag_response_text)} caratteri)")
                final_bot_message = response_prefix + rag_response_text
        
        # Fallback se risposta vuota
        if not final_bot_message or len(final_bot_message.strip()) < 5: 
            logger.warning(f"[PID:{pid}] Risposta vuota, uso fallback")
            fallback_text = dialogue_manager.get_fallback_response(intent)
            if fallback_text:
                final_bot_message = fallback_text
            else:
                final_bot_message = "Mi dispiace, non sono riuscito a elaborare una risposta adeguata. Posso aiutarti con qualcos'altro?"

        # Suggested actions
        conversation_history = await db_manager.get_conversation_messages(conversation_id)
        suggested_actions = dialogue_manager.get_suggested_actions(intent, conversation_history)
        
        # Salva risposta
        message_metadata = {
            "intent_type": intent.type, 
            "intent_confidence": float(intent.confidence) if intent.confidence is not None else 0.0, 
            "rag_sources_data": rag_output_data.get("sources", []), 
            "direct_response_used": use_direct_response_flag,
            "custom_rag_mode": True
        }
        await db_manager.add_message(conversation_id, "assistant", final_bot_message, metadata=message_metadata)

        logger.info(f"[PID:{pid}] Risposta inviata per ConvID {conversation_id}")
        
        # Format sources per response
        response_sources = [
            {
                "source": source.get("source", "unknown") if isinstance(source, dict) else str(source),
                "content": source.get("content", "") if isinstance(source, dict) else ""
            }
            for source in rag_output_data.get("sources", [])
        ]

        return ChatResponse(
            message=final_bot_message,
            suggested_actions=suggested_actions,
            conversation_id=conversation_id,
            sources=response_sources 
        )
        
    except HTTPException as http_ex:
        raise http_ex 
    except Exception as e:
        logger.error(f"[PID:{pid}] Errore chat endpoint: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Errore interno del server")

@app.get("/api/health", summary="Health check del sistema", tags=["System"])
async def health_check_endpoint(request: Request): 
    rag_system_instance: Optional[CustomRAGEngine] = request.app.state.rag_system
    pid = os.getpid()
    logger.debug(f"[PID:{pid}] /api/health: Health check richiesto")
    
    # Test database
    db_ok = False
    try:
        db_ok = await db_manager.test_connection()
    except Exception: 
        db_ok = False 
        logger.error(f"[PID:{pid}] Errore test connessione database", exc_info=True)
    
    # Test RAG system
    rag_is_initialized = False
    rag_details_log = "RAG system non definito"

    if rag_system_instance: 
        rag_is_initialized = getattr(rag_system_instance, 'is_initialized', False)
        rag_details_log = f"RAG system presente, inizializzato: {rag_is_initialized}"
    
    logger.debug(f"[PID:{pid}] Health check: DB={db_ok}, RAG={rag_details_log}")

    # Determina status generale
    overall_status = "online"
    details_db = "Connessione riuscita" if db_ok else "Connessione fallita"
    details_rag = "Custom RAG inizializzato" if rag_is_initialized else "Custom RAG non inizializzato"
    
    if not db_ok:
        overall_status = "degraded"
        logger.warning(f"[PID:{pid}] Sistema DEGRADED (Database)")
    elif not rag_is_initialized: 
        overall_status = "degraded"
        logger.warning(f"[PID:{pid}] Sistema DEGRADED (RAG non inizializzato)")
    else:
        logger.info(f"[PID:{pid}] Sistema ONLINE")
        
    return {
        "status": overall_status,
        "timestamp": datetime.datetime.now(timezone.utc).isoformat(),
        "deployment": "Railway - Custom RAG",
        "components": {
            "database_connection": {"status": "ok" if db_ok else "error", "details": details_db},
            "rag_system": {"status": "ready" if rag_is_initialized else "not_ready", 
                           "details": details_rag}
        },
        "version": APP_VERSION
    }

@app.get("/api/dashboard/data", summary="Dati dashboard monitoring", tags=["Dashboard"])
async def get_dashboard_data_endpoint(request: Request): 
    rag_system_instance: Optional[CustomRAGEngine] = request.app.state.rag_system
    pid = os.getpid()
    logger.debug(f"[PID:{pid}] /api/dashboard/data: Richiesta dati dashboard")
    
    try:
        current_time = datetime.datetime.now(timezone.utc)
        today_start_utc = current_time.replace(hour=0, minute=0, second=0, microsecond=0)

        # Stats RAG system
        rag_stats_data = {}
        if rag_system_instance and hasattr(rag_system_instance, "get_system_stats"):
            rag_stats_data = await rag_system_instance.get_system_stats() 
        
        # Query database async
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
        
        db_results = await asyncio.gather(*db_query_futures, return_exceptions=True)

        # Parse results
        today_conv_res = db_results[0] if not isinstance(db_results[0], Exception) else None
        total_conv_res = db_results[1] if not isinstance(db_results[1], Exception) else None
        total_msg_res = db_results[2] if not isinstance(db_results[2], Exception) else None
        last_24h_msg_res = db_results[3] if not isinstance(db_results[3], Exception) else []
        
        today_conversations_count = today_conv_res['count'] if today_conv_res and 'count' in today_conv_res else 0
        total_conversations_count = total_conv_res['count'] if total_conv_res and 'count' in total_conv_res else 0
        total_messages_count = total_msg_res['count'] if total_msg_res and 'count' in total_msg_res else 0
        
        activity_chart_formatted = [
            {"hour": msg['hour'], "count": msg['count']} for msg in last_24h_msg_res 
            if isinstance(msg, dict) and 'hour' in msg and 'count' in msg
        ]
        
        # Extract stats da RAG
        stats_section = rag_stats_data.get('stats', {}) if isinstance(rag_stats_data, dict) else {}
        base_system_info = stats_section.get('base_system', {}) 
        performance_metrics = stats_section.get('performance', {})
        cache_info = stats_section.get('cache', {}) 

        rag_initialized_val = base_system_info.get('is_initialized', False)
        
        # Cache metrics
        cache_hits = cache_info.get('memory_cache_stats', {}).get('hits', 0)
        cache_misses = cache_info.get('memory_cache_stats', {}).get('misses', 0)
        cache_hit_rate = cache_info.get('memory_cache_stats', {}).get('hit_rate_percent', 0.0)
        cache_items_count = cache_info.get('memory_cache_entry_count', 0)

        # Sistema info
        uptime_delta = current_time - APP_START_TIME
        days = uptime_delta.days
        hours, remainder = divmod(uptime_delta.seconds, 3600)
        minutes_rem, seconds = divmod(remainder, 60) 
        uptime_str = f"{days}g {hours:02d}:{minutes_rem:02d}:{seconds:02d}"

        current_process = psutil.Process(os.getpid())
        memory_rss_mb = round(current_process.memory_info().rss / (1024 * 1024), 1)

        # Vector store info
        vector_stats = base_system_info.get('vector_store', {})
        total_docs = vector_stats.get('total_documents', 0)
        files_indexed = vector_stats.get('files_indexed', 0)

        dashboard_payload = {
            "timestamp": current_time.isoformat(),
            "system_status": {
                "status": "online" if rag_initialized_val else "degraded",
                "uptime": uptime_str,
                "version": APP_VERSION,
                "deployment": "Railway - Custom RAG"
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
                "cache_hit_rate": cache_hit_rate,
                "avg_response_time_ms": performance_metrics.get('rag_get_response', {}).get('avg_time_ms_successful', 2500.0), 
                "total_queries_processed": performance_metrics.get('rag_get_response', {}).get('total_calls', total_docs)
            },
            "activity_chart": activity_chart_formatted,
            "system_health_components": { 
                "database_status": "ok",
                "rag_status": "initialized" if rag_initialized_val else "not_initialized", 
                "cache_status": "ok", 
                "memory_usage_mb": memory_rss_mb,
                "documents_indexed": total_docs,
                "files_indexed": files_indexed
            }
        }
        
        return { "status": "success", "data": dashboard_payload }
        
    except Exception as e:
        logger.error(f"[PID:{pid}] Errore dashboard data: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Errore dati dashboard: {str(e)}")

@app.post("/api/cache/clear", summary="Pulisce cache sistema", tags=["System"])
async def clear_system_cache_endpoint(request: Request): 
    rag_system_instance: Optional[CustomRAGEngine] = request.app.state.rag_system
    messages = []

    # RAG cache
    if rag_system_instance and hasattr(rag_system_instance, "force_clear_all_cache"):
        try:
            await rag_system_instance.force_clear_all_cache()
            messages.append("Cache Custom RAG System pulita")
            logger.info("Cache Custom RAG pulita")
        except Exception as e:
            logger.error(f"Errore pulizia cache RAG: {e}")
            messages.append(f"Errore pulizia cache RAG: {str(e)[:50]}")
    else:
        messages.append("Custom RAG System non disponibile per pulizia cache")

    # Smart cache
    if smart_cache and hasattr(smart_cache, 'clear_all_cache'):
        try:
            await smart_cache.clear_all_cache()
            messages.append("SmartCache globale pulita")
            logger.info("SmartCache pulita")
        except Exception as e:
            logger.error(f"Errore pulizia SmartCache: {e}")
            messages.append(f"Errore SmartCache: {str(e)[:50]}")
    else:
        messages.append("SmartCache non disponibile")

    return {
        "status": "success",
        "timestamp": datetime.datetime.now(timezone.utc).isoformat(),
        "message": " | ".join(messages),
        "deployment": "Railway - Custom RAG"
    }

# ===== STATIC FILES =====
static_dir_name = "static"
static_dir_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), static_dir_name)

if os.path.isdir(static_dir_path):
    app.mount(f"/{static_dir_name}", StaticFiles(directory=static_dir_path, html=True), name=static_dir_name) 
    logger.info(f"File statici serviti da: {static_dir_path}")
    
    @app.get("/dashboard", include_in_schema=False, tags=["Static Content"])
    async def serve_dashboard_html(): 
        dashboard_html_path = os.path.join(static_dir_path, "dashboard.html")
        if os.path.exists(dashboard_html_path):
            return FileResponse(dashboard_html_path)
        logger.error(f"Dashboard non trovata: {static_dir_path}")
        return RedirectResponse(url="/docs")

@app.get("/", include_in_schema=False, tags=["Static Content"])
async def root_serve_chatbot_ui(): 
    if os.path.isdir(static_dir_path):
        chatbot_index_path = os.path.join(static_dir_path, "index.html")
        if os.path.exists(chatbot_index_path):
            return FileResponse(chatbot_index_path)
        dashboard_html_path = os.path.join(static_dir_path, "dashboard.html")
        if os.path.exists(dashboard_html_path):
            return RedirectResponse(url="/dashboard") 
    return RedirectResponse(url="/docs")

if __name__ == "__main__":
    # Record start time
    app.state.start_time = time.time()
    
    logger.info(f"🚀 Avvio Custom RAG Chatbot su http://{APP_HOST}:{APP_PORT}")
    logger.info(f"Debug: {DEBUG}, LogLevel: {LOG_LEVEL}")
    
    uvicorn.run(
        "main:app", 
        host=APP_HOST, 
        port=APP_PORT, 
        reload=DEBUG,
        log_level=LOG_LEVEL.lower()
    )