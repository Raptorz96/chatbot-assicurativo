# app/config.py
import os
from dotenv import load_dotenv

# Carica le variabili d'ambiente dal file .env
# Assicurati che il file .env sia nella root del progetto, NON dentro la cartella 'app'
# Se main.py è nella root, load_dotenv() senza argomenti funziona.
# Se main.py è in una sottocartella, potresti dover specificare il percorso:
# dotenv_path = os.path.join(os.path.dirname(__file__), '..', '.env') # Se config.py è in app/ e .env è nella root
# load_dotenv(dotenv_path=dotenv_path)
load_dotenv() 

# Configurazioni dell'applicazione
APP_HOST = os.getenv("APP_HOST", "0.0.0.0")
APP_PORT = int(os.getenv("APP_PORT", 8000))
DEBUG = os.getenv("DEBUG", "False").lower() in ("true", "1", "t", "yes")
APP_VERSION = os.getenv("APP_VERSION", "1.0.2") # Aggiornato per riflettere le modifiche

# Configurazioni OpenAI
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY") # Rimosso default "" per rendere esplicita la sua assenza
# Se OPENAI_API_KEY è None (non impostato in .env), allora USE_MOCK sarà True.
USE_MOCK = not bool(OPENAI_API_KEY) 
if USE_MOCK:
    print("ATTENZIONE: OPENAI_API_KEY non trovata. Il sistema RAG opererà in modalità MOCK.")

# Configurazioni RAG
CHROMA_PERSIST_DIR = os.getenv("CHROMA_PERSIST_DIR", "./chroma_db_persist") # Modificato per coerenza con log iniziale
EMBEDDINGS_MODEL_NAME = os.getenv("EMBEDDINGS_MODEL_NAME", "text-embedding-ada-002") # Rinominato per chiarezza
LLM_MODEL_NAME = os.getenv("LLM_MODEL_NAME", "gpt-3.5-turbo") # Rinominato per chiarezza
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", 1000))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", 200))
RETRIEVER_K = int(os.getenv("RETRIEVER_K", 3))

# Configurazioni database conversazioni
DB_PATH = os.getenv("DB_PATH", "./chatbot_conversations.db") # Nome più specifico

# Configurazioni SmartCache (se usi un DB separato per la cache persistente di SmartCache)
SMART_CACHE_DB_PATH = os.getenv("SMART_CACHE_DB_PATH", "./smart_cache.db")

# Directory documenti per RAG
DOCS_DIRECTORY = os.getenv("DOCS_DIRECTORY", "./insurance_docs_sample") # Esempio

# Configurazioni di logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper() # Assicura che sia maiuscolo
LOG_FILE = os.getenv("LOG_FILE", "./logs/chatbot_app.log") # Nome file log
LOG_MAX_BYTES = int(os.getenv("LOG_MAX_BYTES", 1024 * 1024 * 5)) # 5MB
LOG_BACKUP_COUNT = int(os.getenv("LOG_BACKUP_COUNT", 3))

# Verifica che la directory dei log esista
os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
# app/config.py
import os
from dotenv import load_dotenv

# Carica le variabili d'ambiente dal file .env
# Assicurati che il file .env sia nella root del progetto, NON dentro la cartella 'app'
# Se main.py è nella root, load_dotenv() senza argomenti funziona.
# Se main.py è in una sottocartella, potresti dover specificare il percorso:
# dotenv_path = os.path.join(os.path.dirname(__file__), '..', '.env') # Se config.py è in app/ e .env è nella root
# load_dotenv(dotenv_path=dotenv_path)
load_dotenv() 

# Configurazioni dell'applicazione
APP_HOST = os.getenv("APP_HOST", "0.0.0.0")
APP_PORT = int(os.getenv("APP_PORT", 8000))
DEBUG = os.getenv("DEBUG", "False").lower() in ("true", "1", "t", "yes")
APP_VERSION = os.getenv("APP_VERSION", "1.0.2") # Aggiornato per riflettere le modifiche

# Configurazioni OpenAI
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY") # Rimosso default "" per rendere esplicita la sua assenza
# Se OPENAI_API_KEY è None (non impostato in .env), allora USE_MOCK sarà True.
USE_MOCK = not bool(OPENAI_API_KEY) 
if USE_MOCK:
    print("ATTENZIONE: OPENAI_API_KEY non trovata. Il sistema RAG opererà in modalità MOCK.")

# Configurazioni RAG
CHROMA_PERSIST_DIR = os.getenv("CHROMA_PERSIST_DIR", "./chroma_db_persist") # Modificato per coerenza con log iniziale
EMBEDDINGS_MODEL_NAME = os.getenv("EMBEDDINGS_MODEL_NAME", "text-embedding-ada-002") # Rinominato per chiarezza
LLM_MODEL_NAME = os.getenv("LLM_MODEL_NAME", "gpt-3.5-turbo") # Rinominato per chiarezza
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", 1000))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", 200))
RETRIEVER_K = int(os.getenv("RETRIEVER_K", 3))

# Configurazioni database conversazioni
DB_PATH = os.getenv("DB_PATH", "./chatbot_conversations.db") # Nome più specifico

# Configurazioni SmartCache (se usi un DB separato per la cache persistente di SmartCache)
SMART_CACHE_DB_PATH = os.getenv("SMART_CACHE_DB_PATH", "./smart_cache.db")

# Directory documenti per RAG
DOCS_DIRECTORY = os.getenv("DOCS_DIRECTORY", "./insurance_docs") # Esempio

# Configurazione OCR con Tesseract
TESSERACT_LANG = os.getenv("TESSERACT_LANG", "ita") # Lingua di default per OCR

# Configurazioni di logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper() # Assicura che sia maiuscolo
LOG_FILE = os.getenv("LOG_FILE", "./logs/chatbot_app.log") # Nome file log
LOG_MAX_BYTES = int(os.getenv("LOG_MAX_BYTES", 1024 * 1024 * 5)) # 5MB
LOG_BACKUP_COUNT = int(os.getenv("LOG_BACKUP_COUNT", 3))

# Verifica che la directory dei log esista
os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
