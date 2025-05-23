#!/bin/bash
# Script per aggiornare i documenti RAG nel container Docker del backend
# e opzionalmente triggerare un re-indicizzazione del sistema RAG tramite API.

# --- Configurazione ---
BACKEND_SERVICE_NAME="backend"
RAG_DOCS_PATH_IN_CONTAINER="/app/insurance_docs"
# --- Fine Configurazione ---

if [ -z "$1" ]; then
  echo "Utilizzo: $0 <percorso_alla_directory_con_i_nuovi_documenti_sull_host> [url_endpoint_reindex_api]"
  echo "Esempio DEV (backend diretto): $0 ./nuovi_documenti http://localhost:8000/api/rag/reindex"
  echo "Esempio PROD (via Nginx):     $0 ./nuovi_documenti http://localhost:${PUBLIC_PORT:-80}/api/rag/reindex"
  exit 1
fi

SOURCE_DOCS_DIR_HOST=$1
# Se il secondo argomento non è fornito, usa un default che potrebbe puntare a Nginx
DEFAULT_REINDEX_ENDPOINT="http://localhost:${PUBLIC_PORT:-80}/api/rag/reindex"
RAG_UPDATE_API_ENDPOINT=${2:-$DEFAULT_REINDEX_ENDPOINT}


CONTAINER_ID=$(docker-compose ps -q "${BACKEND_SERVICE_NAME}")
if [ -z "$CONTAINER_ID" ]; then
    echo "Errore: Container per il servizio '${BACKEND_SERVICE_NAME}' non trovato. È in esecuzione?"
    exit 1
fi
CONTAINER_ID=$(echo "$CONTAINER_ID" | head -n 1)

if [ ! -d "$SOURCE_DOCS_DIR_HOST" ]; then
  echo "Errore: La directory sorgente specificata '$SOURCE_DOCS_DIR_HOST' non esiste."
  exit 1
fi

echo "Avvio aggiornamento documenti RAG per il container ID: ${CONTAINER_ID}..."
echo "Directory sorgente sull'host: ${SOURCE_DOCS_DIR_HOST}"

NUM_DOCS_TO_COPY=$(find "$SOURCE_DOCS_DIR_HOST" -type f | wc -l)
echo "Trovati ${NUM_DOCS_TO_COPY} file da copiare."

echo "Rimozione dei vecchi documenti RAG da '${CONTAINER_ID}:${RAG_DOCS_PATH_IN_CONTAINER}'..."
docker exec "$CONTAINER_ID" rm -rf "${RAG_DOCS_PATH_IN_CONTAINER:?}/"*

echo "Copia dei nuovi documenti in '${CONTAINER_ID}:${RAG_DOCS_PATH_IN_CONTAINER}'..."
docker cp "${SOURCE_DOCS_DIR_HOST}/." "${CONTAINER_ID}:${RAG_DOCS_PATH_IN_CONTAINER}/"
if [ $? -ne 0 ]; then
    echo "Errore: Fallimento durante la copia dei nuovi documenti RAG nel container."
    exit 1
fi
echo "Nuovi documenti RAG copiati con successo."

read -p "Vuoi tentare di triggerare un re-index del RAG tramite API a ${RAG_UPDATE_API_ENDPOINT}? (s/N): " TRIGGER_API
if [[ "$TRIGGER_API" == "s" || "$TRIGGER_API" == "S" ]]; then
    echo "Tentativo di triggerare l'aggiornamento dell'indice RAG..."
    API_RESPONSE_CODE=$(curl -s -o /dev/null -w "%{http_code}" -X POST "${RAG_UPDATE_API_ENDPOINT}")

    if [ "$API_RESPONSE_CODE" -ge 200 ] && [ "$API_RESPONSE_CODE" -lt 300 ]; then
        echo "Richiesta di aggiornamento/re-index RAG inviata con successo (HTTP $API_RESPONSE_CODE)."
    elif [ "$API_RESPONSE_CODE" -eq 000 ]; then
        echo "Attenzione: Impossibile connettersi a ${RAG_UPDATE_API_ENDPOINT}. Controllare URL e server."
    else
        echo "Attenzione: Richiesta di aggiornamento/re-index RAG fallita (HTTP $API_RESPONSE_CODE)."
    fi
    echo "Controllare i log del backend per i dettagli del processo di re-indicizzazione."
else
    echo "Aggiornamento RAG tramite API saltato. Potrebbe essere necessario un riavvio del backend."
fi

echo "Script di aggiornamento documenti RAG completato."
