# app/utils/db_manager.py
import aiosqlite
import json
import uuid
from datetime import datetime, timezone
from typing import Optional, Dict, List, Any, Union # Aggiunto Union
from app.utils.logging_config import logger
from app.config import DB_PATH 
import os 

class DatabaseManager:
    """Gestione asincrona del database SQLite per il chatbot assicurativo"""
    
    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path or DB_PATH # Permette override per test
        if self.db_path != ":memory:":
             os.makedirs(os.path.dirname(self.db_path), exist_ok=True)

    async def get_connection(self) -> aiosqlite.Connection:
        """
        Crea e restituisce una connessione ATTIVA al database.
        Il chiamante è responsabile della chiusura di questa connessione.
        """
        try:
            # Abilita WAL mode per migliori performance concorrenti, se non è in memoria
            conn_params = {}
            if self.db_path != ":memory:":
                conn_params["journal_mode"] = "WAL" # Non standard per aiosqlite, ma per sqlite3 sì
            
            conn = await aiosqlite.connect(self.db_path)
            if self.db_path != ":memory:": # WAL mode è persistente
                await conn.executescript("PRAGMA journal_mode=WAL; PRAGMA busy_timeout = 5000;")
            await conn.execute("PRAGMA foreign_keys = ON;") # Abilita foreign keys per sessione
            return conn
        except Exception as e:
            logger.error(f"Errore fatale nella connessione al DB ({self.db_path}): {e}", exc_info=True)
            raise # Rilancia per indicare un problema serio

    async def init_db(self):
        """Inizializza il database con le tabelle necessarie."""
        conn: Optional[aiosqlite.Connection] = None
        try:
            conn = await self.get_connection()
            await conn.execute('''
            CREATE TABLE IF NOT EXISTS conversations (
                conversation_id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                created_at TEXT NOT NULL, -- Memorizza come ISO8601 UTC
                last_updated TEXT NOT NULL -- Memorizza come ISO8601 UTC
            )
            ''')
            await conn.execute('''
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                conversation_id TEXT NOT NULL,
                role TEXT NOT NULL CHECK(role IN ('user', 'assistant', 'system')),
                content TEXT NOT NULL,
                metadata TEXT, -- JSON string
                timestamp TEXT NOT NULL, -- Memorizza come ISO8601 UTC
                FOREIGN KEY (conversation_id) REFERENCES conversations (conversation_id) ON DELETE CASCADE
            )
            ''')
            # Indici per migliorare le performance delle query comuni
            await conn.execute("CREATE INDEX IF NOT EXISTS idx_messages_conversation_id ON messages (conversation_id);")
            await conn.execute("CREATE INDEX IF NOT EXISTS idx_messages_timestamp ON messages (timestamp);")
            await conn.execute("CREATE INDEX IF NOT EXISTS idx_conversations_last_updated ON conversations (last_updated);")
            
            await conn.commit()
            logger.info(f"Database ({self.db_path}) inizializzato/verificato con successo.")
        except Exception as e:
            logger.error(f"Errore nell'inizializzazione del database ({self.db_path}): {e}", exc_info=True)
            if conn: await conn.rollback() # Tenta rollback se possibile
            raise
        finally:
            if conn:
                await conn.close()

    async def create_conversation(self, user_id: str) -> Optional[str]:
        conn: Optional[aiosqlite.Connection] = None
        try:
            conversation_id = str(uuid.uuid4())
            conn = await self.get_connection()
            current_time_iso = datetime.now(timezone.utc).isoformat()
            await conn.execute(
                "INSERT INTO conversations (conversation_id, user_id, created_at, last_updated) VALUES (?, ?, ?, ?)",
                (conversation_id, user_id, current_time_iso, current_time_iso)
            )
            await conn.commit()
            logger.info(f"Creata nuova conversazione: {conversation_id} per UserID: {user_id}")
            return conversation_id
        except Exception as e:
            logger.error(f"Errore nella creazione della conversazione per UserID {user_id}: {e}", exc_info=True)
            return None
        finally:
            if conn: await conn.close()
    
    async def get_conversation(self, conversation_id: str) -> Optional[Dict[str, Any]]:
        conn: Optional[aiosqlite.Connection] = None
        try:
            conn = await self.get_connection()
            conn.row_factory = aiosqlite.Row
            async with conn.execute(
                "SELECT * FROM conversations WHERE conversation_id = ?",
                (conversation_id,)
            ) as cursor:
                row = await cursor.fetchone()
                return dict(row) if row else None
        except Exception as e:
            logger.error(f"Errore nel recupero della conversazione {conversation_id}: {e}", exc_info=True)
            return None
        finally:
            if conn: await conn.close()
            
    async def add_message(self, conversation_id: str, role: str, content: str, metadata: Optional[Dict[str, Any]] = None) -> bool:
        conn: Optional[aiosqlite.Connection] = None
        try:
            conn = await self.get_connection()
            await conn.execute("BEGIN IMMEDIATE TRANSACTION") 
            
            async with conn.execute("SELECT 1 FROM conversations WHERE conversation_id = ?", (conversation_id,)) as cursor:
                if not await cursor.fetchone():
                    logger.warning(f"Tentativo di aggiungere messaggio a conversazione inesistente: {conversation_id}. Rollback.")
                    await conn.rollback()
                    return False
            
            metadata_json_str = json.dumps(metadata) if metadata else None
            current_time_iso = datetime.now(timezone.utc).isoformat()
            
            await conn.execute(
                "INSERT INTO messages (conversation_id, role, content, metadata, timestamp) VALUES (?, ?, ?, ?, ?)",
                (conversation_id, role, content, metadata_json_str, current_time_iso)
            )
            await conn.execute(
                "UPDATE conversations SET last_updated = ? WHERE conversation_id = ?",
                (current_time_iso, conversation_id)
            )
            await conn.commit()
            logger.debug(f"Messaggio aggiunto a ConvID {conversation_id} (Ruolo: {role})")
            return True
        except Exception as e:
            logger.error(f"Errore nell'aggiunta del messaggio a ConvID {conversation_id}: {e}", exc_info=True)
            if conn:
                try: await conn.rollback()
                except Exception as rb_err: logger.error(f"Errore durante il rollback (add_message): {rb_err}", exc_info=True)
            return False
        finally:
            if conn: await conn.close()
            
    async def get_conversation_messages(self, conversation_id: str, limit: Optional[int] = None, offset: Optional[int] = 0) -> List[Dict[str, Any]]:
        conn: Optional[aiosqlite.Connection] = None
        try:
            conn = await self.get_connection()
            conn.row_factory = aiosqlite.Row
            
            query = "SELECT * FROM messages WHERE conversation_id = ? ORDER BY timestamp ASC"
            params: List[Any] = [conversation_id]
            if limit is not None:
                query += " LIMIT ?"
                params.append(limit)
                if offset is not None and offset > 0 : # Offset ha senso solo con limit
                    query += " OFFSET ?"
                    params.append(offset)

            async with conn.execute(query, tuple(params)) as cursor:
                messages = []
                async for row in cursor:
                    message_dict = dict(row)
                    if message_dict.get('metadata'):
                        try:
                            message_dict['metadata'] = json.loads(message_dict['metadata'])
                        except json.JSONDecodeError as json_err:
                            logger.warning(f"Errore decodifica JSON metadata per MsgID {message_dict.get('id')} in ConvID {conversation_id}: {json_err}. Metadata: {message_dict['metadata']}")
                            message_dict['metadata'] = {} 
                    messages.append(message_dict)
                return messages
        except Exception as e:
            logger.error(f"Errore nel recupero dei messaggi per ConvID {conversation_id}: {e}", exc_info=True)
            return []
        finally:
            if conn: await conn.close()

    async def get_recent_conversations(self, limit: int = 10) -> List[Dict[str, Any]]:
        conn: Optional[aiosqlite.Connection] = None
        try:
            conn = await self.get_connection()
            conn.row_factory = aiosqlite.Row
            async with conn.execute(
                "SELECT * FROM conversations ORDER BY last_updated DESC LIMIT ?",
                (limit,)
            ) as cursor:
                return [dict(row) async for row in cursor]
        except Exception as e:
            logger.error(f"Errore nel recupero delle conversazioni recenti: {e}", exc_info=True)
            return []
        finally:
            if conn: await conn.close()

    async def delete_conversation(self, conversation_id: str) -> bool:
        conn: Optional[aiosqlite.Connection] = None
        try:
            conn = await self.get_connection()
            await conn.execute("BEGIN TRANSACTION") 
            cursor = await conn.execute(
                "DELETE FROM conversations WHERE conversation_id = ?",
                (conversation_id,)
            )
            await conn.commit()
            if cursor.rowcount > 0: 
                logger.info(f"Conversazione {conversation_id} e relativi messaggi eliminati.")
                return True
            else:
                logger.warning(f"Nessuna conversazione trovata con ID {conversation_id} per l'eliminazione.")
                return False
        except Exception as e:
            logger.error(f"Errore nell'eliminazione della conversazione {conversation_id}: {e}", exc_info=True)
            if conn:
                try: await conn.rollback()
                except Exception as rb_err: logger.error(f"Errore durante il rollback (delete_conversation): {rb_err}", exc_info=True)
            return False
        finally:
            if conn: await conn.close()

    async def search_conversations(self, search_term: str, limit: int = 10) -> List[Dict[str, Any]]:
        conn: Optional[aiosqlite.Connection] = None
        try:
            conn = await self.get_connection()
            conn.row_factory = aiosqlite.Row
            query = """
            SELECT DISTINCT c.* FROM conversations c
            JOIN messages m ON c.conversation_id = m.conversation_id
            WHERE m.content LIKE ?
            ORDER BY c.last_updated DESC
            LIMIT ?
            """
            search_pattern = f"%{search_term}%"
            async with conn.execute(query, (search_pattern, limit)) as cursor:
                return [dict(row) async for row in cursor]
        except Exception as e:
            logger.error(f"Errore nella ricerca delle conversazioni per termine '{search_term}': {e}", exc_info=True)
            return []
        finally:
            if conn: await conn.close()

    async def test_connection(self) -> bool:
        conn: Optional[aiosqlite.Connection] = None
        try:
            conn = await self.get_connection() # get_connection ora include PRAGMA foreign_keys=ON
            # conn.row_factory = aiosqlite.Row # Non necessario se get_connection non la imposta globalmente
            async with conn.execute("SELECT 1 AS result") as cursor:
                row = await cursor.fetchone() # fetchone() restituisce una tupla o None
                return bool(row and row[0] == 1) # Accedi per indice se row_factory non è aiosqlite.Row
        except Exception as e:
            logger.error(f"Test connessione al database ({self.db_path}) fallito: {e}", exc_info=False) 
            return False
        finally:
            if conn: await conn.close()

    async def execute_query(self, query: str, params: Optional[tuple] = None, fetch_one: bool = False) -> Optional[Union[List[Dict[str, Any]], Dict[str, Any]]]:
        conn: Optional[aiosqlite.Connection] = None
        try:
            conn = await self.get_connection()
            conn.row_factory = aiosqlite.Row 
            async with conn.execute(query, params or ()) as cursor:
                if fetch_one:
                    row = await cursor.fetchone()
                    return dict(row) if row else None
                else:
                    rows = await cursor.fetchall()
                    return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"Errore durante l'esecuzione della query '{query[:100]}...': {e}", exc_info=True)
            return None 
        finally:
            if conn: await conn.close()

    async def get_database_info(self) -> Dict[str, Any]: # Modificato per restituire sempre un dict
        """Restituisce informazioni sul database, o un dizionario di errore."""
        db_path_resolved = os.path.abspath(self.db_path) if self.db_path != ":memory:" else ":memory:"
        
        base_info = {
            "connected": False,
            "error_message": None,
            "database_path": db_path_resolved,
            "tables": [],
            "record_counts": {},
            "db_size_bytes": 0
        }

        try:
            if not await self.test_connection():
                logger.warning(f"get_database_info: Test di connessione fallito per {db_path_resolved}.")
                base_info["error_message"] = "Connessione al database fallita."
                return base_info
            
            base_info["connected"] = True
            
            tables_info_raw = await self.execute_query(
                "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
            )
            table_names = [table['name'] for table in tables_info_raw] if tables_info_raw else []
            base_info["tables"] = table_names

            counts = {}
            tables_to_count = ['conversations', 'messages']
            if 'users' in table_names: 
                 tables_to_count.append('users')
            
            for table_name in tables_to_count:
                if table_name not in table_names: # Salta se la tabella non esiste
                    counts[table_name] = 0 
                    logger.debug(f"Tabella '{table_name}' non trovata per il conteggio in get_database_info.")
                    continue
                try:
                    result = await self.execute_query(f"SELECT COUNT(*) as count FROM {table_name}", fetch_one=True)
                    counts[table_name] = result['count'] if result and 'count' in result else 0
                except Exception as e: 
                    logger.error(f"Errore nel conteggio dei record per la tabella '{table_name}': {e}", exc_info=True)
                    counts[table_name] = -1 # Indica un errore nel conteggio
            base_info["record_counts"] = counts
            
            if db_path_resolved != ':memory:':
                base_info["db_size_bytes"] = await self._get_db_size_bytes(db_path_resolved)
            
            return base_info
        except Exception as e: 
            logger.error(f"Errore generale nel recupero delle info del database ({db_path_resolved}): {e}", exc_info=True)
            base_info["error_message"] = str(e)
            base_info["connected"] = False # Assicura che sia False in caso di eccezione generale
            return base_info

    async def _get_db_size_bytes(self, db_file_path: str) -> int:
        """Helper per ottenere la dimensione del file del database."""
        try:
            if os.path.exists(db_file_path):
                return os.path.getsize(db_file_path)
        except Exception as e: 
            logger.warning(f"Impossibile ottenere la dimensione del file DB '{db_file_path}': {e}")
        return 0

db_manager = DatabaseManager() # Istanza globale

async def init_database():
    """Inizializza lo schema del database se necessario."""
    # Questa funzione è chiamata da lifespan in main.py
    await db_manager.init_db()
