# 🤖 Chatbot Assicurativo AI

Un chatbot intelligente per il settore assicurativo che utilizza RAG (Retrieval-Augmented Generation) per fornire risposte accurate su polizze auto e casa, procedure sinistri e servizi assicurativi.

## ✨ Caratteristiche Principali

- 🧠 **AI-Powered**: Integrazione OpenAI (GPT-3.5-turbo) per risposte naturali
- 📄 **Elaborazione Documenti**: OCR automatico per PDF con Tesseract
- 🔍 **Ricerca Semantica**: ChromaDB per recupero documenti contestuale
- ⚡ **Cache Intelligente**: Sistema cache multi-livello per performance ottimali
- 📊 **Monitoring**: Dashboard real-time per metriche e statistiche
- 🌐 **API REST**: Interfacce complete per integrazioni
- 🎯 **Analisi Intenti**: Classificazione automatica richieste utenti

## 🏗️ Architettura

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   FastAPI       │    │   RAG System    │
│   Dashboard     │◄──►│   Backend       │◄──►│   + ChromaDB    │
│   Chat UI       │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                       ┌────────▼────────┐
                       │   SmartCache    │
                       │   + SQLite      │
                       └─────────────────┘
```

## 🚀 Quick Start

### Prerequisiti

- Python 3.10+
- [Tesseract OCR](https://github.com/tesseract-ocr/tesseract) installato
- Chiave API OpenAI

### Installazione

1. **Clone del repository**
   ```bash
   git clone https://github.com/yourusername/chatbot-assicurativo.git
   cd chatbot-assicurativo
   ```

2. **Setup ambiente virtuale**
   ```bash
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # Linux/Mac
   source venv/bin/activate
   ```

3. **Installazione dipendenze**
   ```bash
   pip install -r requirements.txt
   
   # Download modello spaCy italiano
   python -m spacy download it_core_news_sm
   ```

4. **Configurazione environment**
   ```bash
   # Copia il file di esempio
   cp .env.example .env
   
   # Modifica .env con le tue configurazioni
   nano .env
   ```

5. **Configurazione Tesseract (Windows)**
   - Installa Tesseract da: https://github.com/UB-Mannheim/tesseract/wiki
   - Verifica path: `C:\Program Files\Tesseract-OCR\tesseract.exe`

### Avvio

```bash
python main.py
```

Il server sarà disponibile su:
- **Chat Interface**: http://localhost:8000
- **Dashboard**: http://localhost:8000/dashboard
- **API Docs**: http://localhost:8000/docs

## 📁 Struttura Progetto

```
chatbot-assicurativo/
├── app/                          # Core applicazione
│   ├── config.py                # Configurazioni
│   ├── models/                  # Modelli dati
│   ├── modules/                 # Moduli principali
│   │   ├── rag_system.py       # Sistema RAG + OCR
│   │   ├── intent_analyzer.py  # Analisi intenti
│   │   └── dialogue_manager.py # Gestione dialoghi
│   └── utils/                   # Utility
│       ├── db_manager.py       # Database manager
│       ├── smart_cache.py      # Sistema cache
│       └── performance_monitor.py
├── insurance_docs/              # Documenti assicurativi
├── static/                      # Frontend (HTML/CSS/JS)
├── tests/                       # Test suite
└── main.py                     # Entry point
```

## 🔧 Configurazione

### File .env

```env
# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here

# Application Settings
APP_HOST=0.0.0.0
APP_PORT=8000
DEBUG=True

# RAG System
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

## 📚 Documenti Supportati

Il sistema elabora automaticamente:

- **📄 PDF**: Con OCR automatico per estrazione testo
- **📝 Markdown**: File .md con formattazione
- **📃 Testo**: File .txt semplici
- **📋 Word**: Documenti .docx

### Documenti Inclusi

- `polizza_auto.txt` - Informazioni polizze auto
- `polizza_casa.txt` - Informazioni polizze casa  
- `sinistri.txt` - Procedure gestione sinistri
- `faq_polizze_auto_casa.md` - Domande frequenti
- `Modulo_CID.pdf` - Modulo constatazione amichevole
- `Condizioni_Generali_Auto.pdf` - CGA polizze auto

## 🔌 API Endpoints

### Chat

```http
POST /api/chat
Content-Type: application/json

{
  "message": "Cosa copre la garanzia RCA?",
  "user_id": "user123",
  "conversation_id": "optional"
}
```

### Sistema

```http
GET /api/health              # Status sistema
GET /api/dashboard/data      # Dati dashboard
POST /api/cache/clear        # Pulizia cache
```

## 🧪 Testing

```bash
# Test sistema RAG
python test_rag_simple.py

# Test recupero documenti
python test_document_retrieval.py

# Test completo con domande predefinite
python quick_test.py
```

## 📊 Monitoring e Dashboard

La dashboard fornisce:

- **Statistiche conversazioni**: Totali giornalieri/mensili
- **Performance metrics**: Tempi risposta, cache hit rate
- **Stato sistema**: Health check componenti
- **Grafici attività**: Utilizzo nel tempo
- **Gestione cache**: Statistiche e controlli

## 🔒 Sicurezza

- **Environment variables**: Chiavi API protette
- **Input validation**: Validazione richieste
- **Rate limiting**: Controllo traffico API
- **Error handling**: Gestione errori sicura
- **Logging**: Tracciamento accessi senza PII

## 🚀 Deployment

### Docker (Raccomandato)

```dockerfile
# Dockerfile incluso per deployment containerizzato
docker build -t chatbot-assicurativo .
docker run -p 8000:8000 --env-file .env chatbot-assicurativo
```

### Cloud Platforms

- **AWS**: EC2, ECS, Lambda
- **Google Cloud**: Cloud Run, Compute Engine
- **Azure**: Container Instances, App Service
- **Railway/Render**: Deploy diretto da GitHub

## 🤝 Contribuire

1. Fork del repository
2. Crea feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push branch (`git push origin feature/amazing-feature`)
5. Apri Pull Request

### Linee Guida

- Segui PEP 8 per Python code style
- Aggiungi test per nuove funzionalità
- Aggiorna documentazione quando necessario
- Usa commit messages descrittivi

## 📋 Roadmap

### v2.0
- [ ] Supporto multi-lingua
- [ ] Integration Telegram/WhatsApp
- [ ] Advanced analytics
- [ ] Voice interface

### v3.0
- [ ] Multi-tenancy
- [ ] Enterprise authentication
- [ ] API rate limiting avanzato
- [ ] Machine learning insights

## 🐛 Troubleshooting

### Problemi Comuni

**Tesseract non trovato**
```bash
# Windows: Verifica installazione
tesseract --version

# Linux: Installa via package manager
sudo apt-get install tesseract-ocr tesseract-ocr-ita
```

**Modello spaCy mancante**
```bash
python -m spacy download it_core_news_sm
```

**Errori OpenAI API**
- Verifica validità chiave API
- Controlla limiti rate/quota
- Verifica connessione internet

## 📝 License

Questo progetto è rilasciato sotto licenza MIT. Vedi `LICENSE` per dettagli.

## 👨‍💻 Autore

**Marco Mantovani**
- GitHub: [@marcomantovani](https://github.com/marcomantovani)
- Email: marco@example.com

## 🙏 Ringraziamenti

- [OpenAI](https://openai.com) per i modelli AI
- [LangChain](https://langchain.com) per il framework RAG
- [ChromaDB](https://www.trychroma.com) per il vector database
- [FastAPI](https://fastapi.tiangolo.com) per il web framework
- [Tesseract](https://github.com/tesseract-ocr/tesseract) per OCR

---

⭐ **Se questo progetto ti è utile, lascia una stella!** ⭐