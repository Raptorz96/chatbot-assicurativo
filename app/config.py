# app/config.py - Custom RAG System Configuration
import os
from dotenv import load_dotenv

# Carica environment variables
try:
    load_dotenv()
    print("✅ File .env caricato")
except:
    print("⚠️  File .env non trovato - uso variabili Railway")

# ===== APPLICAZIONE =====
APP_HOST = os.getenv("APP_HOST", "0.0.0.0")
APP_PORT = int(os.getenv("APP_PORT", 8000))
DEBUG = os.getenv("DEBUG", "False").lower() in ("true", "1", "t", "yes")
APP_VERSION = os.getenv("APP_VERSION", "2.0.0-custom-rag")

# ===== OPENAI CONFIGURATION =====
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Sistema intelligente per modalità
USE_MOCK_ENV = os.getenv("USE_MOCK", "").lower()
if USE_MOCK_ENV in ("true", "1", "t", "yes"):
    USE_MOCK = True
    print("🎭 Modalità MOCK forzata")
elif USE_MOCK_ENV in ("false", "0", "f", "no"):
    if not OPENAI_API_KEY:
        print("⚠️  USE_MOCK=false ma OPENAI_API_KEY mancante. Forzo MOCK.")
        USE_MOCK = True
    else:
        USE_MOCK = False
        print("✅ Modalità Custom RAG attiva")
else:
    USE_MOCK = not bool(OPENAI_API_KEY)
    if USE_MOCK:
        print("🎭 OPENAI_API_KEY mancante. Modalità MOCK attiva.")
    else:
        print("✅ OPENAI_API_KEY trovata. Custom RAG disponibile.")

# ===== CUSTOM RAG CONFIGURATION =====
# OpenAI Models
EMBEDDINGS_MODEL_NAME = os.getenv("EMBEDDINGS_MODEL_NAME", "text-embedding-ada-002")
LLM_MODEL_NAME = os.getenv("LLM_MODEL_NAME", "gpt-3.5-turbo")

# Document Processing
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", 1000))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", 200))
MAX_CONTEXT_LENGTH = int(os.getenv("MAX_CONTEXT_LENGTH", 4000))

# Vector Store Configuration
VECTOR_DB_PATH = os.getenv("VECTOR_DB_PATH", "./data/custom_vector_store.db")
SIMILARITY_THRESHOLD = float(os.getenv("SIMILARITY_THRESHOLD", 0.2))
RETRIEVER_K = int(os.getenv("RETRIEVER_K", 5))

# ===== DIRECTORY CONFIGURATION =====
DOCS_DIRECTORY = os.getenv("DOCS_DIRECTORY", "./insurance_docs")
DB_PATH = os.getenv("DB_PATH", "./chatbot_conversations.db")
SMART_CACHE_DB_PATH = os.getenv("SMART_CACHE_DB_PATH", "./data/smart_cache.db")

# Crea directories necessarie
for directory in [
    os.path.dirname(VECTOR_DB_PATH),
    os.path.dirname(SMART_CACHE_DB_PATH),
    DOCS_DIRECTORY
]:
    if directory and not os.path.exists(directory):
        os.makedirs(directory, exist_ok=True)
        print(f"📁 Creata directory: {directory}")

# Verifica documenti
if not os.path.exists(DOCS_DIRECTORY):
    print(f"⚠️  Directory documenti {DOCS_DIRECTORY} non trovata")
    os.makedirs(DOCS_DIRECTORY, exist_ok=True)
else:
    doc_files = [f for f in os.listdir(DOCS_DIRECTORY) 
                 if f.endswith(('.txt', '.md', '.pdf'))]
    print(f"📚 Trovati {len(doc_files)} documenti in {DOCS_DIRECTORY}")

# ===== LOGGING CONFIGURATION =====
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
LOG_FILE = os.getenv("LOG_FILE", "./logs/chatbot_app.log")
LOG_MAX_BYTES = int(os.getenv("LOG_MAX_BYTES", 1024 * 1024 * 5))  # 5MB
LOG_BACKUP_COUNT = int(os.getenv("LOG_BACKUP_COUNT", 3))

# Crea directory logs
log_dir = os.path.dirname(LOG_FILE)
if log_dir and not os.path.exists(log_dir):
    os.makedirs(log_dir, exist_ok=True)

# ===== RAILWAY ENVIRONMENT =====
RAILWAY_ENVIRONMENT = os.getenv("RAILWAY_ENVIRONMENT")
RAILWAY_GIT_COMMIT_SHA = os.getenv("RAILWAY_GIT_COMMIT_SHA")
RAILWAY_GIT_BRANCH = os.getenv("RAILWAY_GIT_BRANCH")

if RAILWAY_ENVIRONMENT:
    print(f"🚄 Railway Environment: {RAILWAY_ENVIRONMENT}")
    if RAILWAY_GIT_COMMIT_SHA:
        print(f"📝 Commit: {RAILWAY_GIT_COMMIT_SHA[:8]}")
    if RAILWAY_GIT_BRANCH:
        print(f"🌿 Branch: {RAILWAY_GIT_BRANCH}")

# ===== PRODUCTION/DEVELOPMENT =====
IS_DEVELOPMENT = DEBUG or RAILWAY_ENVIRONMENT == "development"
IS_PRODUCTION = not IS_DEVELOPMENT

if IS_PRODUCTION:
    print("🏭 Modalità PRODUZIONE")
    if LOG_LEVEL == "DEBUG":
        LOG_LEVEL = "INFO"
        print("📝 Log level: DEBUG → INFO (produzione)")
else:
    print("🔧 Modalità SVILUPPO")

# ===== CACHE CONFIGURATION =====
ENABLE_MEMORY_CACHE = os.getenv("ENABLE_MEMORY_CACHE", "true").lower() == "true"
ENABLE_PERSISTENT_CACHE = os.getenv("ENABLE_PERSISTENT_CACHE", "true").lower() == "true"
CACHE_TTL_SECONDS = int(os.getenv("CACHE_TTL_SECONDS", 3600))

# ===== PERFORMANCE SETTINGS =====
MAX_WORKERS = int(os.getenv("MAX_WORKERS", 4))
REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", 30))
BATCH_SIZE_EMBEDDINGS = int(os.getenv("BATCH_SIZE_EMBEDDINGS", 20))

# ===== RAG SPECIFIC SETTINGS =====
# Sistema di fallback per componenti mancanti
FALLBACK_MODE = {
    "custom_rag": USE_MOCK,
    "embeddings": not bool(OPENAI_API_KEY),
    "vector_store": False,  # SQLite sempre disponibile
    "llm": not bool(OPENAI_API_KEY)
}

# Configurazioni avanzate RAG
RAG_CONFIG = {
    "OPENAI_API_KEY": OPENAI_API_KEY,
    "EMBEDDINGS_MODEL_NAME": EMBEDDINGS_MODEL_NAME,
    "LLM_MODEL_NAME": LLM_MODEL_NAME,
    "CHUNK_SIZE": CHUNK_SIZE,
    "CHUNK_OVERLAP": CHUNK_OVERLAP,
    "MAX_CONTEXT_LENGTH": MAX_CONTEXT_LENGTH,
    "VECTOR_DB_PATH": VECTOR_DB_PATH,
    "SIMILARITY_THRESHOLD": SIMILARITY_THRESHOLD,
    "RETRIEVER_K": RETRIEVER_K,
    "DOCS_DIRECTORY": DOCS_DIRECTORY,
    "BATCH_SIZE_EMBEDDINGS": BATCH_SIZE_EMBEDDINGS,
    "ENABLE_MEMORY_CACHE": ENABLE_MEMORY_CACHE,
    "CACHE_TTL_SECONDS": CACHE_TTL_SECONDS
}

# ===== SYSTEM PROMPT CUSTOMIZATION =====
CUSTOM_SYSTEM_PROMPT = os.getenv("CUSTOM_SYSTEM_PROMPT", """
Sei un assistente esperto in assicurazioni auto e casa specializzato nel mercato italiano.

ISTRUZIONI OPERATIVE:
1. Rispondi SOLO basandoti sui documenti forniti nel contesto
2. Sii preciso, chiaro e professionale nel linguaggio assicurativo
3. Se non trovi informazioni sufficienti, dillo esplicitamente
4. Cita sempre le fonti dei documenti utilizzati
5. Per preventivi, spiega tutti i fattori che influenzano il prezzo
6. Per sinistri, fornisci procedure complete passo-passo
7. Usa terminologia tecnica appropriata ma accessibile

SPECIALIZZAZIONI:
- RCA obbligatoria e garanzie accessorie
- Polizze casa (incendio, furto, RC)
- Procedure sinistri e liquidazioni
- Normativa IVASS e codice della strada
- Sistema bonus/malus e attestati di rischio

Mantieni sempre tono professionale ma cordiale, tipico del settore assicurativo italiano.
""".strip())

# ===== CONFIGURATION SUMMARY =====
def get_config():
    """Ritorna configurazione completa per Custom RAG System"""
    return RAG_CONFIG

def print_config_summary():
    """Stampa riassunto configurazione"""
    print("=" * 60)
    print("📋 CUSTOM RAG SYSTEM - CONFIGURAZIONE")
    print("=" * 60)
    print(f"   🏠 Host:Port: {APP_HOST}:{APP_PORT}")
    print(f"   🧠 Modalità RAG: {'MOCK' if USE_MOCK else 'CUSTOM RAG ATTIVO'}")
    print(f"   🔧 Debug: {DEBUG}")
    print(f"   📊 Log Level: {LOG_LEVEL}")
    print(f"   💾 Vector DB: {VECTOR_DB_PATH}")
    print(f"   📁 Documenti: {DOCS_DIRECTORY}")
    print(f"   🎯 Chunk Size: {CHUNK_SIZE} (overlap: {CHUNK_OVERLAP})")
    print(f"   🔍 Similarity Threshold: {SIMILARITY_THRESHOLD}")
    print(f"   📊 Retriever K: {RETRIEVER_K}")
    if OPENAI_API_KEY:
        print(f"   🤖 LLM Model: {LLM_MODEL_NAME}")
        print(f"   🧮 Embeddings: {EMBEDDINGS_MODEL_NAME}")
    print(f"   🏭 Ambiente: {'Produzione' if IS_PRODUCTION else 'Sviluppo'}")
    if RAILWAY_ENVIRONMENT:
        print(f"   🚄 Railway: {RAILWAY_ENVIRONMENT}")
    print("=" * 60)

# Auto-print configuration summary
print_config_summary()