# app/utils/logging_config.py
import logging
import os
from logging.handlers import RotatingFileHandler
from app.config import LOG_LEVEL, LOG_FILE

# Assicurati che la directory dei log esista
os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)

def setup_logging():
    """Configura il logging dell'applicazione"""
    
    # Converte il livello di log da stringa a costante
    numeric_level = getattr(logging, LOG_LEVEL.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError(f'Livello di log non valido: {LOG_LEVEL}')
    
    # Configurazione di base
    logging.basicConfig(
        level=numeric_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            # Gestore per file con rotazione (mantiene fino a 5 file da 5MB ciascuno)
            RotatingFileHandler(
                LOG_FILE, 
                maxBytes=5*1024*1024,  # 5MB
                backupCount=5
            ),
            # Gestore per la console
            logging.StreamHandler()
        ]
    )
    
    # Riduce il livello di logging per alcune librerie troppo verbose
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    
    return logging.getLogger("chatbot")

# Crea un'istanza logger globale
logger = setup_logging()