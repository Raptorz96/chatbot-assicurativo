# app/config.py - Railway Compatible Version
import os
from dotenv import load_dotenv

# Carica le variabili d'ambiente dal file .env se esiste
# Railway fornisce variabili via environment, .env è opzionale
try:
    load_dotenv()
    print("✅ File .env caricato")
except:
    print("⚠️  File .env non trovato - uso variabili environment Railway")

# ===== CONFIGURAZIONI APPLICAZIONE =====
APP_HOST = os.getenv("APP_HOST", "0.0.0.0")
APP_PORT = int(os.getenv("APP_PORT", 8000))
DEBUG = os.getenv("DEBUG", "False").lower() in ("true", "1", "t", "yes")
APP_VERSION = os.getenv("APP_VERSION", "1.0.3-railway") # Aggiornato per Railway

# ===== CONFIGURAZIONI OPENAI (MODALITÀ INTELLIGENTE) =====
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Sistema intelligente per gestire modalità MOCK
# Railway può funzionare senza OpenAI key (modalità demo)
USE_MOCK_ENV = os.getenv("USE_MOCK", "").lower()
if USE_MOCK_ENV in ("true", "1", "t", "yes"):
    # Modalità MOCK forzata via environment
    USE_MOCK = True
    print("🎭 Modalità MOCK forzata via environment variable USE_MOCK=true")
elif USE_MOCK_ENV in ("false", "0", "f", "no"):
    # Modalità produzione forzata ma controlla se chiave è disponibile
    if not OPENAI_API_KEY:
        print("⚠️  USE_MOCK=false ma OPENAI_API_KEY non trovata. Forzo modalità MOCK.")
        USE_MOCK = True
    else:
        USE_MOCK = False
        print("✅ Modalità produzione con OpenAI attiva")
else:
    # Auto-detect basato su presenza della chiave
    USE_MOCK = not bool(OPENAI_API_KEY)
    if USE_MOCK:
        print("🎭 OPENAI_API_KEY non trovata. Sistema opererà in modalità MOCK.")
    else:
        print("✅ OPENAI_API_KEY trovata. Modalità produzione disponibile.")

# ===== CONFIGURAZIONI RAG (CON FALLBACK) =====
CHROMA_PERSIST_DIR = os.getenv("CHROMA_PERSIST_DIR", "./chroma_db_persist")
EMBEDDINGS_MODEL_NAME = os.getenv("EMBEDDINGS_MODEL_NAME", "text-embedding-ada-002")
LLM_MODEL_NAME = os.getenv("LLM_MODEL_NAME", "gpt-3.5-turbo")
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", 1000))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", 200))
RETRIEVER_K = int(os.getenv("RETRIEVER_K", 3))

# ===== CONFIGURAZIONI DATABASE =====
DB_PATH = os.getenv("DB_PATH", "./chatbot_conversations.db")
SMART_CACHE_DB_PATH = os.getenv("SMART_CACHE_DB_PATH", "./data/smart_cache.db")

# ===== DIRECTORY DOCUMENTI =====
DOCS_DIRECTORY = os.getenv("DOCS_DIRECTORY", "./insurance_docs")

# Verifica esistenza directory documenti
if not os.path.exists(DOCS_DIRECTORY):
    print(f"⚠️  Directory documenti {DOCS_DIRECTORY} non trovata. Creazione directory vuota.")
    os.makedirs(DOCS_DIRECTORY, exist_ok=True)

# ===== CONFIGURAZIONI OCR (OPZIONALI) =====
TESSERACT_LANG = os.getenv("TESSERACT_LANG", "ita")

# ===== CONFIGURAZIONI LOGGING =====
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
LOG_FILE = os.getenv("LOG_FILE", "./logs/chatbot_app.log")
LOG_MAX_BYTES = int(os.getenv("LOG_MAX_BYTES", 1024 * 1024 * 5))  # 5MB
LOG_BACKUP_COUNT = int(os.getenv("LOG_BACKUP_COUNT", 3))

# Verifica che la directory dei log esista
os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)

# ===== CONFIGURAZIONI RAILWAY SPECIFICHE =====
# Railway-specific environment variables
RAILWAY_ENVIRONMENT = os.getenv("RAILWAY_ENVIRONMENT")
RAILWAY_GIT_COMMIT_SHA = os.getenv("RAILWAY_GIT_COMMIT_SHA")
RAILWAY_GIT_BRANCH = os.getenv("RAILWAY_GIT_BRANCH")

if RAILWAY_ENVIRONMENT:
    print(f"🚄 Running on Railway - Environment: {RAILWAY_ENVIRONMENT}")
    if RAILWAY_GIT_COMMIT_SHA:
        print(f"📝 Git Commit: {RAILWAY_GIT_COMMIT_SHA[:8]}")
    if RAILWAY_GIT_BRANCH:
        print(f"🌿 Git Branch: {RAILWAY_GIT_BRANCH}")

# ===== MODALITÀ SVILUPPO VS PRODUZIONE =====
IS_DEVELOPMENT = DEBUG or RAILWAY_ENVIRONMENT == "development"
IS_PRODUCTION = not IS_DEVELOPMENT

if IS_PRODUCTION:
    print("🏭 Modalità PRODUZIONE")
    # In produzione, disabilita alcuni log verbose
    if LOG_LEVEL == "DEBUG":
        LOG_LEVEL = "INFO"
        print("📝 Log level cambiato da DEBUG a INFO in produzione")
else:
    print("🔧 Modalità SVILUPPO")

# ===== CONFIGURAZIONI FALLBACK =====
# Impostazioni per quando librerie mancano
FALLBACK_MODE = {
    "rag_system": not bool(OPENAI_API_KEY),
    "ocr_processing": True,  # Sempre fallback su Railway per OCR
    "nlp_processing": True,  # Sempre fallback su Railway per spaCy
    "vector_store": not bool(OPENAI_API_KEY)
}

# ===== CONFIGURAZIONI CACHE =====
ENABLE_MEMORY_CACHE = os.getenv("ENABLE_MEMORY_CACHE", "true").lower() == "true"
ENABLE_PERSISTENT_CACHE = os.getenv("ENABLE_PERSISTENT_CACHE", "true").lower() == "true"
CACHE_TTL_SECONDS = int(os.getenv("CACHE_TTL_SECONDS", 3600))  # 1 ora default

# ===== PERFORMANCE SETTINGS =====
MAX_WORKERS = int(os.getenv("MAX_WORKERS", 4))
REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", 30))

# ===== SUMMARY CONFIG =====
print("=" * 50)
print("📋 CONFIGURAZIONE ATTUALE:")
print(f"   🏠 Host: {APP_HOST}:{APP_PORT}")
print(f"   🎭 Modalità MOCK: {USE_MOCK}")
print(f"   🔧 Debug: {DEBUG}")
print(f"   📊 Log Level: {LOG_LEVEL}")
print(f"   💾 Database: {DB_PATH}")
print(f"   📁 Documenti: {DOCS_DIRECTORY}")
print(f"   🏭 Ambiente: {'Produzione' if IS_PRODUCTION else 'Sviluppo'}")
if RAILWAY_ENVIRONMENT:
    print(f"   🚄 Railway Env: {RAILWAY_ENVIRONMENT}")
print("=" * 50)