# Chatbot Assicurativo - Panoramica Progetto

## Descrizione Generale
Chatbot assicurativo avanzato basato su intelligenza artificiale che utilizza un sistema RAG (Retrieval-Augmented Generation) per fornire risposte accurate su polizze auto e casa. Il sistema combina elaborazione documenti, OCR, caching intelligente e monitoraggio performance.

## Architettura del Sistema

### Stack Tecnologico
- **Backend**: FastAPI con Python 3.10+
- **AI/ML**: OpenAI (GPT-3.5-turbo, text-embedding-ada-002)
- **Vector Database**: ChromaDB per ricerca semantica
- **OCR**: Tesseract per estrazione testo da PDF
- **NLP**: spaCy (modello italiano) per normalizzazione testo
- **Database**: SQLite per conversazioni e cache
- **Frontend**: HTML/CSS/JavaScript (dashboard e chat UI)

### Struttura del Progetto
```
chatbot-assicurativo/
├── app/                          # Core applicazione
│   ├── config.py                # Configurazioni centrali
│   ├── models/schemas.py        # Modelli Pydantic per API
│   ├── modules/                 # Moduli principali
│   │   ├── rag_system.py       # Sistema RAG con OCR
│   │   ├── intent_analyzer.py  # Analisi intenti utente
│   │   └── dialogue_manager.py # Gestione dialoghi
│   └── utils/                   # Utility
│       ├── db_manager.py       # Gestione database conversazioni
│       ├── smart_cache.py      # Sistema cache intelligente
│       ├── performance_monitor.py # Monitoraggio metriche
│       ├── text_processing.py  # Elaborazione testi
│       └── logging_config.py   # Configurazione logging
├── insurance_docs/              # Documenti assicurativi
│   ├── polizza_auto.txt        # Polizze auto
│   ├── polizza_casa.txt        # Polizze casa
│   ├── sinistri.txt           # Procedure sinistri
│   ├── faq_polizze_auto_casa.md # FAQ
│   ├── Compilazione_Modulo_CID.pdf # Modulo CID (OCR)
│   └── Condizioni_Generali_Auto.pdf # CGA (OCR)
├── static/                      # Frontend
│   ├── index.html              # Chat interface
│   ├── dashboard.html          # Dashboard monitoring
│   ├── css/style.css          # Stili chat
│   ├── css/dashboard.css      # Stili dashboard
│   └── js/                    # JavaScript
├── chroma_db_persist/          # Database vettoriale
├── data/smart_cache.db         # Cache persistente
├── logs/                       # File di log
└── main.py                     # Entry point applicazione
```

## Componenti Principali

### 1. Sistema RAG (rag_system.py)
**Responsabilità**: Core del sistema di recupero e generazione
- **Elaborazione documenti**: Carica PDF, TXT, MD, DOCX
- **OCR avanzato**: Estrae testo da PDF con immagini usando Tesseract
- **Preprocessing**: Normalizza testo con spaCy (modello italiano)
- **Embeddings**: Genera vettori semantici con OpenAI
- **Chunking**: Divide documenti in chunks ottimali (1000 char, overlap 200)
- **Retrieval**: Trova documenti rilevanti con ChromaDB
- **Generation**: Genera risposte contestuali con GPT-3.5-turbo

**Funzionalità avanzate**:
- OCR automatico su pagine PDF senza testo
- Preprocessing immagini per migliorare OCR
- Gestione metadati documenti
- Modalità MOCK per testing senza OpenAI
- Cache integrata per performance

### 2. Gestione Database (db_manager.py)
**Responsabilità**: Persistenza conversazioni e messaggi
- **Conversazioni**: Tracking utenti e sessioni
- **Messaggi**: Storage messaggi con metadati (intenti, fonti, confidence)
- **Analytics**: Statistiche utilizzo e performance
- **Schema**:
  ```sql
  conversations: id, user_id, created_at, last_activity
  messages: id, conversation_id, role, content, timestamp, metadata
  ```

### 3. Cache Intelligente (smart_cache.py)
**Responsabilità**: Ottimizzazione performance
- **Cache memoria**: LRU cache per risposte frequenti
- **Cache persistente**: SQLite per persistenza tra sessioni
- **TTL**: Gestione scadenza automatica (default 1 ora)
- **Statistiche**: Hit rate, performance metrics
- **API**: get/set/clear asincrono

### 4. Analisi Intenti (intent_analyzer.py)
**Responsabilità**: Classificazione richieste utente
- **Intenti supportati**: saluto, ringraziamento, congedo, domanda_assicurazione
- **Pattern matching**: Regex e keyword-based
- **Confidence scoring**: Calcolo affidabilità classificazione
- **Estrazione entità**: Identificazione elementi chiave

### 5. Gestione Dialoghi (dialogue_manager.py)
**Responsabilità**: Logica conversazionale
- **Response templates**: Risposte predefinite per intenti comuni
- **Context awareness**: Gestione contesto conversazione
- **Suggested actions**: Azioni suggerite per l'utente
- **Fallback handling**: Gestione risposte quando RAG fallisce

### 6. Monitoraggio Performance (performance_monitor.py)
**Responsabilità**: Metriche e monitoring
- **Metriche RAG**: Tempo risposta, cache hit/miss
- **Metriche sistema**: Memoria, CPU, uptime
- **Persistenza**: Salvataggio automatico metriche
- **API**: Esposizione dati per dashboard

## API Endpoints

### Chat Endpoints
- `POST /api/chat`: Invio messaggi al chatbot
  - Input: `{message, user_id, conversation_id?}`
  - Output: `{message, sources, suggested_actions, conversation_id}`

### System Endpoints
- `GET /api/health`: Status sistema (DB, RAG, cache)
- `GET /api/dashboard/data`: Dati per dashboard monitoring
- `POST /api/cache/clear`: Pulizia cache sistema

### Static Content
- `GET /`: Chat interface (index.html)
- `GET /dashboard`: Dashboard monitoring
- `GET /static/*`: File statici (CSS, JS, immagini)

## Documenti Assicurativi

### Contenuti Disponibili
1. **Polizze Auto** (polizza_auto.txt):
   - Coperture RCA (€6M massimale)
   - Garanzie opzionali (Kasko, Furto, Eventi naturali)
   - Franchigie e scoperti
   - Procedura preventivi

2. **Procedure Sinistri** (sinistri.txt):
   - Denuncia sinistri auto/casa
   - Numeri verde assistenza
   - Tempi liquidazione
   - Assistenza stradale 24/7

3. **FAQ** (faq_polizze_auto_casa.md):
   - RCA e coperture
   - Validità territoriale
   - Sistema Bonus/Malus
   - Procedure post-incidente

4. **Moduli PDF** (con OCR):
   - Modulo CID (Constatazione Amichevole)
   - Condizioni Generali Assicurazione Auto

## Configurazione

### Variabili Ambiente (.env)
```env
# OpenAI
OPENAI_API_KEY=sk-...

# Applicazione
APP_HOST=0.0.0.0
APP_PORT=8000
DEBUG=True

# RAG
CHROMA_PERSIST_DIR=./chroma_db_persist
DOCS_DIRECTORY=./insurance_docs
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
RETRIEVER_K=3

# Database
DB_PATH=./chatbot_conversations.db
SMART_CACHE_DB_PATH=./data/smart_cache.db

# Logging
LOG_LEVEL=INFO
LOG_FILE=./logs/chatbot_app.log
```

### Setup Tesseract (Windows)
- Path: `C:\Program Files\Tesseract-OCR\tesseract.exe`
- Linguaggio: Italiano (ita)
- Tessdata: Configurazione automatica

## Deployment

### Requisiti Sistema
- Python 3.10+
- Tesseract OCR installato
- Modello spaCy italiano: `python -m spacy download it_core_news_sm`
- Chiave API OpenAI valida

### Avvio Applicazione
```bash
# Ambiente virtuale
python -m venv venv
source venv/bin/activate  # Linux/Mac
# o venv\Scripts\activate  # Windows

# Dipendenze
pip install -r requirements.txt

# Download modello spaCy
python -m spacy download it_core_news_sm

# Avvio server
python main.py
```

### Struttura Startup
1. **Inizializzazione DB**: Setup tabelle conversazioni
2. **Cache loading**: Caricamento metriche e cache
3. **RAG setup**: Inizializzazione sistema RAG
   - Caricamento modello spaCy
   - Setup OpenAI embeddings
   - Elaborazione documenti con OCR
   - Creazione/caricamento vectorstore ChromaDB
   - Setup catena QA LangChain
4. **Server start**: Avvio Uvicorn FastAPI

## Funzionalità Chiave

### Elaborazione Documenti Intelligente
- **Auto-OCR**: Rileva PDF senza testo e applica OCR automaticamente
- **Preprocessing immagini**: Migliora qualità per OCR (scala grigi, contrasto, ridimensionamento)
- **Chunking adattivo**: Divide documenti mantenendo coerenza semantica
- **Metadati ricchi**: Conserva informazioni fonte per tracciabilità

### Cache Multi-Livello
- **L1 (Memoria)**: Cache LRU per risposte immediate
- **L2 (Disco)**: Persistenza SQLite per riavvii
- **TTL dinamico**: Scadenza basata su tipo contenuto
- **Statistics**: Monitoraggio hit rate e performance

### Monitoring Completo
- **Performance**: Tempi risposta, throughput, errori
- **Sistema**: Memoria, uptime, stato componenti
- **Business**: Conversazioni, utenti attivi, argomenti frequenti
- **Dashboard**: Visualizzazione real-time con grafici

### Error Handling Robusto
- **Graceful degradation**: Fallback quando componenti non disponibili
- **Retry logic**: Tentativi automatici per operazioni critiche
- **Logging strutturato**: Tracciamento dettagliato per debug
- **Health checks**: Monitoraggio continuo stato sistema

## Testing e Qualità

### Test Coverage
- **Unit tests**: Componenti individuali
- **Integration tests**: Flussi end-to-end
- **Performance tests**: Carico e stress
- **Document retrieval tests**: Qualità recupero informazioni

### Metriche Qualità
- **Retrieval accuracy**: Precisione documenti recuperati
- **Response relevance**: Pertinenza risposte generate
- **Response time**: Latenza media < 3 secondi
- **Cache hit rate**: Target > 60% per query ripetute

## Roadmap e Estensioni

### Miglioramenti Pianificati
- **Multi-tenancy**: Supporto multiple compagnie assicurative
- **Advanced analytics**: ML-driven insights su comportamento utenti
- **Voice integration**: Supporto input/output vocale
- **Mobile app**: App nativa iOS/Android
- **API enterprise**: Rate limiting, authentication, billing

### Scalabilità
- **Database**: Migrazione PostgreSQL per volumi enterprise
- **Vector DB**: Upgrade Pinecone/Weaviate per performance
- **Caching**: Redis cluster per cache distribuita
- **Load balancing**: Nginx per gestione traffico
- **Containerization**: Docker + Kubernetes deployment

## Sicurezza e Compliance

### Data Protection
- **PII handling**: Anonimizzazione dati sensibili
- **Encryption**: Cifratura dati a riposo e in transito
- **Access control**: Autenticazione e autorizzazione
- **Audit logging**: Tracciamento accessi e modifiche

### Compliance Assicurativo
- **GDPR**: Gestione consensi e diritto oblio
- **Normative IVASS**: Conformità regolamentazione italiana
- **Data retention**: Politiche conservazione dati
- **Privacy by design**: Principi privacy integrati

Questo progetto rappresenta una soluzione completa per automatizzare il customer service assicurativo, combinando AI avanzata, elaborazione documenti intelligente e monitoring enterprise-grade.