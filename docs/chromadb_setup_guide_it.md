# Guida all'Installazione e Risoluzione Problemi di ChromaDB

Questa documentazione spiega come configurare correttamente ChromaDB per l'archiviazione locale di vettori nel sistema RAG del chatbot assicurativo, insieme ai problemi comuni e alle loro soluzioni.

## Problema: Errore "HTTP-only Client Mode" di ChromaDB

Durante l'inizializzazione di `PersistentClient` di ChromaDB, potresti incontrare il seguente errore:

```
RuntimeError: Chroma is running in http-only client mode, and can only be run with 'chromadb.api.fastapi.FastAPI' as the chroma_api_impl.
```

## Causa Principale

Questo errore si verifica tipicamente per una di queste ragioni:

1. **Conflitto tra Pacchetti**: Avere sia il pacchetto `chromadb` che `chromadb-client` installati contemporaneamente. Il pacchetto client forza ChromaDB a funzionare in modalità HTTP-only, impedendo la persistenza locale.

2. **Variabili d'Ambiente**: Variabili d'ambiente come `CHROMA_SERVER_HOST` impostate, che forzano ChromaDB in modalità client.

3. **Versioni Incompatibili**: Utilizzo di versioni di ChromaDB incompatibili con le sue dipendenze (NumPy, langchain, ecc.).

## Soluzione

La soluzione che abbiamo implementato ha coinvolto:

1. **Rimozione dei Pacchetti in Conflitto**:
   ```bash
   pip uninstall -y chromadb chromadb-client
   ```

2. **Installazione di una Versione Compatibile Specifica**:
   ```bash
   pip install chromadb==0.4.22
   ```

3. **Utilizzo di un'Inizializzazione Semplice**:
   ```python
   import chromadb
   chroma_client = chromadb.PersistentClient(path=persist_directory)
   ```

## Note di Compatibilità

- ChromaDB 0.4.x funziona bene con la persistenza locale e LangChain
- Evita di installare contemporaneamente i pacchetti `chromadb` e `chromadb-client`
- Con le versioni più recenti di LangChain, è consigliato utilizzare il pacchetto `langchain_chroma`

## Dipendenze

La nostra configurazione funzionante utilizza questi pacchetti:

- `chromadb==0.4.22`
- `numpy==1.26.4`
- `langchain==0.3.25`
- `langchain-community==0.3.24`
- `langchain-openai==0.3.17`

## Test

Per verificare che la configurazione di ChromaDB funzioni correttamente, esegui gli script di test forniti:

```bash
python test_chromadb_init.py  # Testa la funzionalità base di ChromaDB
python test_rag_system.py     # Testa il sistema RAG completo
```

## Avvisi e Note di Deprecazione

Potresti vedere avvisi di deprecazione riguardanti:

1. La classe `Chroma` di LangChain:
   ```
   LangChainDeprecationWarning: The class `Chroma` was deprecated in LangChain 0.2.9 and will be removed in 1.0.
   ```
   
   Soluzione futura: Sostituire con `from langchain_chroma import Chroma`

2. Il metodo `Chain.__call__`:
   ```
   LangChainDeprecationWarning: The method `Chain.__call__` was deprecated in langchain 0.1.0 and will be removed in 1.0.
   ```
   
   Soluzione futura: Utilizzare `.invoke()` invece della sintassi di chiamata

Questi avvisi possono essere ignorati per ora, ma dovrebbero essere affrontati in aggiornamenti futuri.

## Risoluzione dei Problemi

Se incontri problemi:

1. Verifica che non siano impostate variabili d'ambiente correlate a ChromaDB
2. Controlla eventuali conflitti tra pacchetti con `pip list | grep chroma`
3. Assicurati che la tua versione di NumPy sia compatibile con le tue dipendenze
4. Utilizza il `PersistentClient` con parametri minimi (solo il percorso)

## Risorse Aggiuntive

- [Documentazione ChromaDB](https://docs.trychroma.com/)
- [Integrazione LangChain con Chroma](https://python.langchain.com/docs/integrations/vectorstores/chroma)