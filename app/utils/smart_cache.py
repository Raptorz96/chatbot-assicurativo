# app/utils/smart_cache.py
import hashlib
import json
import time
from typing import Any, Optional, Dict, Tuple # Tuple non usato, ma Any, Optional, Dict sì
import aiosqlite
import asyncio
import os # Aggiunto per os.path e os.makedirs
import logging # Aggiunto per il logger

# Configurazione del logger
logger = logging.getLogger(__name__)
if not logger.hasHandlers():
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

class SmartCache:
    def __init__(self, db_path: str = "data/cache.db", default_ttl: int = 3600):
        self.db_path = db_path
        # Assicura che il percorso sia assoluto o relativo alla directory corretta
        if not os.path.isabs(self.db_path):
            # Questo esempio lo rende relativo alla directory dello script, 
            # ma potresti volerlo relativo alla root del progetto.
            # Adatta questo se necessario in base a dove viene istanziato SmartCache
            # o passa un percorso assoluto.
            # Per un'app FastAPI, è comune avere percorsi definiti in un file di configurazione.
            # base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) # Esempio per root/data/
            # self.db_path = os.path.join(base_dir, db_path)
            pass # Lasciamo che sia l'utente a gestire il path corretto per ora

        self.default_ttl = default_ttl
        self.memory_cache: Dict[str, Dict[str, Any]] = {} # Più specifico sulla struttura interna
        logger.info(f"SmartCache inizializzato. DB path: {os.path.abspath(self.db_path)}, Default TTL: {self.default_ttl}s")

    async def _ensure_db_directory_exists(self):
        """Assicura che la directory per il file SQLite esista."""
        db_dir = os.path.dirname(self.db_path)
        if db_dir and not os.path.exists(db_dir):
            try:
                os.makedirs(db_dir, exist_ok=True)
                logger.info(f"Directory della cache creata: {db_dir}")
            except OSError as e:
                logger.error(f"Errore durante la creazione della directory della cache {db_dir}: {e}")
                raise # Rilancia l'errore se la directory non può essere creata

    async def init_cache(self):
        """Inizializza il database della cache e la directory se necessario."""
        await self._ensure_db_directory_exists()
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute('''
                    CREATE TABLE IF NOT EXISTS cache (
                        key TEXT PRIMARY KEY,
                        value TEXT NOT NULL,
                        timestamp REAL NOT NULL,
                        ttl INTEGER NOT NULL
                    )
                ''')
                await db.execute('CREATE INDEX IF NOT EXISTS idx_cache_timestamp_ttl ON cache (timestamp, ttl)') # Indice per clear_expired
                await db.commit()
            logger.info("Tabella cache SQLite inizializzata/verificata con successo.")
        except Exception as e:
            logger.error(f"Errore durante l'inizializzazione del database della cache SQLite: {e}", exc_info=True)
            raise

    def _generate_key(self, query: str, context: Optional[Dict[str, Any]] = None) -> str:
        """Genera una chiave univoca per la query e il contesto."""
        # Assicura che il contesto sia sempre un dizionario per json.dumps
        effective_context = context if context is not None else {}
        # Ordinare le chiavi del contesto assicura che lo stesso contesto produca la stessa stringa JSON
        combined = f"{query}_{json.dumps(effective_context, sort_keys=True, ensure_ascii=False)}"
        return hashlib.md5(combined.encode('utf-8')).hexdigest()

    async def get(self, query: str, context: Optional[Dict[str, Any]] = None) -> Optional[Any]:
        """Recupera un valore dalla cache (memoria o DB), controllando il TTL."""
        key = self._generate_key(query, context)
        current_time = time.time()

        # 1. Controlla la cache in memoria
        if key in self.memory_cache:
            item = self.memory_cache[key]
            if current_time - item['timestamp'] < item['ttl']:
                logger.debug(f"Cache HIT (memory) per la chiave: {key}")
                return item['value']  # Valore già deserializzato
            else:
                logger.debug(f"Cache EXPIRED (memory) per la chiave: {key}")
                del self.memory_cache[key]
                # Considera di eliminare anche dal DB qui se vuoi essere proattivo,
                # ma clear_expired o il prossimo accesso al DB lo faranno.

        # 2. Controlla la cache persistente (SQLite)
        try:
            async with aiosqlite.connect(self.db_path) as db:
                async with db.execute('SELECT value, timestamp, ttl FROM cache WHERE key = ?', (key,)) as cursor:
                    row = await cursor.fetchone()

                if row:
                    value_json, timestamp_db, ttl_db = row
                    if current_time - timestamp_db < ttl_db:
                        logger.debug(f"Cache HIT (DB) per la chiave: {key}")
                        try:
                            value = json.loads(value_json)
                        except json.JSONDecodeError as e:
                            logger.error(f"Errore di decodifica JSON per la chiave {key} dal DB: {e}. Rimuovo elemento corrotto.")
                            await db.execute('DELETE FROM cache WHERE key = ?', (key,))
                            await db.commit()
                            return None
                        
                        # Aggiorna la cache in memoria (write-through on read)
                        self.memory_cache[key] = {
                            'value': value,        # Valore deserializzato
                            'timestamp': timestamp_db,
                            'ttl': ttl_db
                        }
                        return value
                    else:
                        logger.debug(f"Cache EXPIRED (DB) per la chiave: {key}")
                        # Rimuovi elemento scaduto dal DB
                        await db.execute('DELETE FROM cache WHERE key = ?', (key,))
                        await db.commit()
                        logger.info(f"Elemento scaduto rimosso dal DB per la chiave: {key}")
        except Exception as e:
            logger.error(f"Errore durante l'accesso alla cache DB per la chiave {key}: {e}", exc_info=True)
            # Non rilanciare l'errore per permettere all'applicazione di procedere (cache miss)
            # ma loggarlo è importante.

        logger.debug(f"Cache MISS per la chiave: {key}")
        return None

    async def set(self, query: str, value: Any, context: Optional[Dict[str, Any]] = None, ttl: Optional[int] = None):
        """Salva un valore nella cache (memoria e DB) con un TTL."""
        key = self._generate_key(query, context)
        effective_ttl = ttl if ttl is not None else self.default_ttl
        current_timestamp = time.time()
        
        try:
            value_json = json.dumps(value)
        except TypeError as e:
            logger.error(f"Errore di serializzazione JSON per la chiave {key} (query: '{query}'). Il valore non verrà messo in cache. Errore: {e}")
            return

        # Salva/Aggiorna in memoria (con valore Python originale)
        self.memory_cache[key] = {
            'value': value, # Salva l'oggetto Python originale, non la stringa JSON
            'timestamp': current_timestamp,
            'ttl': effective_ttl
        }

        # Salva/Aggiorna in database (con valore JSON)
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute(
                    'INSERT OR REPLACE INTO cache (key, value, timestamp, ttl) VALUES (?, ?, ?, ?)',
                    (key, value_json, current_timestamp, effective_ttl)
                )
                await db.commit()
            logger.debug(f"Elemento salvato/aggiornato in cache (memoria & DB) per la chiave: {key}, TTL: {effective_ttl}s")
        except Exception as e:
            logger.error(f"Errore durante il salvataggio nella cache DB per la chiave {key}: {e}", exc_info=True)
            # L'elemento è ancora nella cache in memoria, ma il salvataggio persistente è fallito.

    async def clear_expired(self):
        """Rimuove tutti gli elementi scaduti dalla cache in memoria e dal database."""
        current_time = time.time()
        cleaned_memory_count = 0
        cleaned_db_count = 0

        # Pulizia cache in memoria
        # È più sicuro iterare su una copia delle chiavi se si modifica il dizionario
        expired_memory_keys = [
            key for key, item in list(self.memory_cache.items()) # list() crea una copia
            if current_time - item['timestamp'] >= item['ttl']
        ]
        for key in expired_memory_keys:
            try:
                del self.memory_cache[key]
                cleaned_memory_count += 1
            except KeyError:
                pass # Già rimosso da un altro task, va bene
        if cleaned_memory_count > 0:
            logger.info(f"{cleaned_memory_count} elementi scaduti rimossi dalla cache in memoria.")

        # Pulizia database
        try:
            async with aiosqlite.connect(self.db_path) as db:
                cursor = await db.execute(
                    'DELETE FROM cache WHERE timestamp + ttl < ?',
                    (current_time,)
                )
                await db.commit()
                cleaned_db_count = cursor.rowcount # Numero di righe eliminate
                if cleaned_db_count > 0:
                     logger.info(f"{cleaned_db_count} elementi scaduti rimossi dalla cache DB.")
        except Exception as e:
            logger.error(f"Errore durante la pulizia degli elementi scaduti dal DB: {e}", exc_info=True)
        
        if cleaned_memory_count == 0 and cleaned_db_count == 0:
            logger.info("Nessun elemento scaduto trovato durante la pulizia della cache.")


    async def get_cache_stats(self) -> Dict[str, Any]:
        """Restituisce statistiche sulla cache (numero di elementi)."""
        db_entry_count = 0
        try:
            async with aiosqlite.connect(self.db_path) as db:
                async with db.execute('SELECT COUNT(*) FROM cache') as cursor:
                    result = await cursor.fetchone()
                    if result:
                        db_entry_count = result[0]
        except Exception as e:
            logger.error(f"Errore durante il recupero delle statistiche dalla cache DB: {e}", exc_info=True)
            # db_entry_count rimane 0

        memory_entry_count = len(self.memory_cache)
        
        # "total_entries" qui significherebbe il numero di chiavi uniche se la cache di memoria
        # fosse sempre un sottoinsieme del DB. Dato che possono divergere leggermente
        # (es. errore scrittura DB), presentiamo i conteggi separati.
        return {
            'memory_cache_entry_count': memory_entry_count,
            'db_cache_entry_count': db_entry_count,
            # 'approx_total_unique_entries': db_entry_count se memory è un sottoinsieme,
            # altrimenti un calcolo più complesso servirebbe se le chiavi potessero divergere molto.
            # Per ora, questi due conteggi sono i più chiari.
        }

    async def clear_all_memory_cache(self):
        """Svuota completamente la cache in memoria."""
        count = len(self.memory_cache)
        self.memory_cache.clear()
        logger.info(f"Cache in memoria svuotata completamente ({count} elementi rimossi).")

    async def clear_all_persistent_cache(self):
        """Svuota completamente la cache persistente (database)."""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                cursor = await db.execute('DELETE FROM cache')
                await db.commit()
                logger.info(f"Cache persistente (DB) svuotata completamente ({cursor.rowcount} elementi rimossi).")
        except Exception as e:
            logger.error(f"Errore durante lo svuotamento completo della cache DB: {e}", exc_info=True)

    async def clear_all_cache(self):
        """Svuota sia la cache in memoria che quella persistente."""
        await self.clear_all_memory_cache()
        await self.clear_all_persistent_cache()
        logger.info("Tutta la cache (memoria e persistente) è stata svuotata.")


# Istanza globale, il percorso del DB può essere configurato tramite variabili d'ambiente o config
# DB_CACHE_PATH = os.getenv("DB_CACHE_PATH", "data/smart_cache.db")
# smart_cache = SmartCache(db_path=DB_CACHE_PATH)
smart_cache = SmartCache(db_path="data/smart_cache.db") # Default semplice