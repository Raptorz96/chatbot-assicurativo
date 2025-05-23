/**
 * Script principale per il chatbot assicurativo AssistentIA Pro
 */

let conversationId = null; 
const userId = 'user-' + Math.floor(Math.random() * 100000) + Date.now(); 
const API_URL = '/api'; 

const logger = {
    info: (message, ...optionalParams) => console.log(`[${new Date().toISOString()}] INFO:`, message, ...optionalParams),
    debug: (message, ...optionalParams) => console.debug(`[${new Date().toISOString()}] DEBUG:`, message, ...optionalParams),
    error: (message, ...optionalParams) => console.error(`[${new Date().toISOString()}] ERROR:`, message, ...optionalParams)
};

document.addEventListener('DOMContentLoaded', () => {
    logger.info("DOM completamente caricato e parsato.");

    const chatMessagesElement = document.getElementById('chat-messages');
    const userInputElement = document.getElementById('user-input');
    const sendButtonElement = document.getElementById('send-button');
    
    if (!chatMessagesElement || !userInputElement || !sendButtonElement) {
        logger.error("Elementi DOM critici del chatbot (chatMessages, userInput, sendButton) non trovati.");
    }
    
    // Chiama checkSystemStatus indipendentemente dalla pagina, 
    // la funzione stessa gestirà se gli elementi esistono.
    checkSystemStatus(); 
    setInterval(checkSystemStatus, 30000); 

    if (chatMessagesElement && userInputElement) { 
        addMessageToChat(
            "Ciao! Sono AssistentIA Pro, il tuo assistente virtuale per le polizze assicurative. Posso aiutarti con informazioni su polizze, preventivi, e gestione sinistri. Come posso esserti utile oggi?",
            'bot', 
            [],  
            [     
                {label: 'Polizze disponibili', type: 'message', payload: 'Quali polizze offrite?'},
                {label: 'Chiedi un Preventivo', type: 'message', payload: 'Vorrei un preventivo'},
                {label: 'Assistenza Sinistro', type: 'message', payload: 'Ho bisogno di assistenza per un sinistro'}
            ],
            chatMessagesElement 
        );
        userInputElement.focus(); 
    }
    
    function handleSendAction() {
        if (!userInputElement || !chatMessagesElement) return; 
        const messageText = userInputElement.value.trim();
        if (messageText) {
            sendMessage(messageText, chatMessagesElement, userInputElement);
        }
    }

    if (sendButtonElement) {
        sendButtonElement.addEventListener('click', handleSendAction);
    }
    
    if (userInputElement) {
        userInputElement.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                e.preventDefault(); 
                handleSendAction();
            }
        });
    }
});

async function checkSystemStatus() {
    logger.debug("Controllo stato sistema (funzione checkSystemStatus)...");
    try {
        // Tentativo di ottenere gli elementi della pagina index.html del chatbot
        const systemStatusDotChat = document.getElementById('system-status'); // ID da index.html
        const systemStatusTextChat = systemStatusDotChat ? systemStatusDotChat.parentElement.querySelector('span') : null; // Span dentro .status-indicator
        const ragStatusDotChat = document.getElementById('rag-status');          // ID da index.html
        const ragStatusTextChat = ragStatusDotChat ? ragStatusDotChat.parentElement.querySelector('span') : null;      // Span dentro .status-indicator


        // Tentativo di ottenere gli elementi della pagina dashboard.html
        const systemStatusDotDashboard = document.getElementById('system-status-dot'); // ID da dashboard.html
        const systemStatusTextDashboard = document.getElementById('system-status-text');
        const ragStatusDotDashboard = document.getElementById('rag-status-dot');
        const ragStatusTextDashboard = document.getElementById('rag-status-text');
        const dbStatusDotDashboard = document.getElementById('db-status-dot');
        const dbStatusTextDashboard = document.getElementById('db-status-text');

        // Imposta lo stato iniziale a "Verifica..." solo se gli elementi esistono
        // Gli elementi .status-item-enhanced avranno la classe healthy, warning, error, degraded
        const setPendingStatus = (dotEl, textEl, baseText) => {
            if (dotEl && textEl) {
                dotEl.className = 'status-dot pending';
                textEl.textContent = `${baseText} verifica...`;
                if (dotEl.closest('.status-item-enhanced')) {
                    dotEl.closest('.status-item-enhanced').className = 'status-item-enhanced warning';
                }
            }
        };

        setPendingStatus(systemStatusDotChat, systemStatusTextChat, 'Sistema Globale');
        setPendingStatus(ragStatusDotChat, ragStatusTextChat, 'Sistema RAG');
        
        if (systemStatusDotDashboard && systemStatusTextDashboard) {
            systemStatusDotDashboard.className = 'status-dot pending';
            systemStatusTextDashboard.textContent = 'Verifica sistema...';
        }
        if (ragStatusDotDashboard && ragStatusTextDashboard) {
            ragStatusDotDashboard.className = 'status-dot pending';
            ragStatusTextDashboard.textContent = 'Verifica RAG...';
        }
        if (dbStatusDotDashboard && dbStatusTextDashboard) {
            dbStatusDotDashboard.className = 'status-dot pending';
            dbStatusTextDashboard.textContent = 'Verifica DB...';
        }
        
        const response = await fetch(`${API_URL}/health`);
        const data = await response.json();

        if (response.ok) {
            logger.info("Dati di stato del sistema ricevuti:", data);
            
            const overallStatus = data.status || 'unknown';
            let overallStatusClass = 'offline'; // Default a rosso
            let overallItemClass = 'error'; // Default item class a error
            if (overallStatus === 'online') {
                overallStatusClass = 'online'; // Verde
                overallItemClass = 'healthy';
            } else if (overallStatus === 'degraded') {
                overallStatusClass = 'degraded'; // Giallo/Arancione
                overallItemClass = 'warning';
            }
            
            const ragComponent = data.components?.rag_system || { status: 'unknown', details: 'Non disponibile' };
            let ragStateClass = 'offline';
            let ragItemClass = 'error';
            let ragStateTextVal = ragComponent.details || 'Stato Sconosciuto';

            if (ragComponent.status === 'ready') {
                ragStateClass = 'online'; 
                ragItemClass = 'healthy';
                ragStateTextVal = ragComponent.details || 'Attivo';
            } else if (ragComponent.status === 'mock_mode') {
                ragStateClass = 'degraded'; 
                ragItemClass = 'warning';
                ragStateTextVal = ragComponent.details || 'Modalità Simulazione';
            } else if (ragComponent.status === 'not_ready' || ragComponent.status === 'error') {
                ragStateClass = 'offline';
                ragItemClass = 'error';
                ragStateTextVal = ragComponent.details || 'Non Pronto/Errore';
            }


            // Aggiorna indicatori su index.html (chatbot)
            if (systemStatusDotChat && systemStatusTextChat) {
                systemStatusDotChat.className = `status-dot ${overallStatusClass}`;
                systemStatusTextChat.textContent = `Sistema Globale ${overallStatus.charAt(0).toUpperCase() + overallStatus.slice(1)}`;
                if (systemStatusDotChat.closest('.status-item-enhanced')) {
                     systemStatusDotChat.closest('.status-item-enhanced').className = `status-item-enhanced ${overallItemClass}`;
                }
            }
            if (ragStatusDotChat && ragStatusTextChat) {
                ragStatusDotChat.className = `status-dot ${ragStateClass}`;
                ragStatusTextChat.textContent = `Sistema RAG ${ragStateTextVal}`;
                 if (ragStatusDotChat.closest('.status-item-enhanced')) {
                     ragStatusDotChat.closest('.status-item-enhanced').className = `status-item-enhanced ${ragItemClass}`;
                }
            }

            // Aggiorna indicatori su dashboard.html
            if (systemStatusDotDashboard && systemStatusTextDashboard) {
                systemStatusDotDashboard.className = `status-dot ${overallStatusClass}`;
                systemStatusTextDashboard.textContent = `Sistema ${overallStatus.charAt(0).toUpperCase() + overallStatus.slice(1)}`;
            }
            if (ragStatusDotDashboard && ragStatusTextDashboard) {
                ragStatusDotDashboard.className = `status-dot ${ragStateClass}`;
                ragStatusTextDashboard.textContent = `RAG ${ragStateTextVal}`;
            }
            if (dbStatusDotDashboard && dbStatusTextDashboard) {
                const dbComponent = data.components?.database_connection || {status: 'error', details: 'Non disponibile'};
                dbStatusDotDashboard.className = `status-dot ${dbComponent.status === 'ok' ? 'online' : 'offline'}`;
                dbStatusTextDashboard.textContent = `Database ${dbComponent.status === 'ok' ? 'Attivo' : (dbComponent.details || 'Non Attivo')}`;
            }
            
        } else {
            logger.error(`Errore HTTP nell'health check: ${response.status}`);
            const offlineMessage = 'Non Raggiungibile';
            const setErrorStatus = (dotEl, textEl, baseText) => {
                 if (dotEl && textEl) {
                    dotEl.className = 'status-dot offline';
                    textEl.textContent = `${baseText} ${offlineMessage}`;
                    if (dotEl.closest('.status-item-enhanced')) {
                        dotEl.closest('.status-item-enhanced').className = 'status-item-enhanced error';
                    }
                }
            };
            setErrorStatus(systemStatusDotChat, systemStatusTextChat, 'Sistema Globale');
            setErrorStatus(ragStatusDotChat, ragStatusTextChat, 'Sistema RAG');
            
            if (systemStatusDotDashboard && systemStatusTextDashboard) { systemStatusDotDashboard.className = 'status-dot offline'; systemStatusTextDashboard.textContent = 'Sistema non raggiungibile'; }
            if (ragStatusDotDashboard && ragStatusTextDashboard) { ragStatusDotDashboard.className = 'status-dot offline'; ragStatusTextDashboard.textContent = 'RAG non disponibile'; }
            if (dbStatusDotDashboard && dbStatusTextDashboard) { dbStatusDotDashboard.className = 'status-dot offline'; dbStatusTextDashboard.textContent = 'DB non disponibile'; }
        }
    } catch (error) {
        logger.error(`Errore durante il controllo dello stato del sistema: ${error.message}`);
        const errorMessage = 'Errore Connessione';
         const setErrorStatusCatch = (dotEl, textEl, baseText) => {
            if (dotEl && textEl) {
                dotEl.className = 'status-dot offline';
                textEl.textContent = `${baseText} ${errorMessage}`;
                if (dotEl.closest('.status-item-enhanced')) {
                    dotEl.closest('.status-item-enhanced').className = 'status-item-enhanced error';
                }
            }
        };
        setErrorStatusCatch(document.getElementById('system-status'), document.getElementById('system-status')?.parentElement.querySelector('span'), 'Sistema Globale');
        setErrorStatusCatch(document.getElementById('rag-status'), document.getElementById('rag-status')?.parentElement.querySelector('span'), 'Sistema RAG');

        // Fallback per la dashboard
        if (document.getElementById('system-status-dot') && document.getElementById('system-status-text')) {
            document.getElementById('system-status-dot').className = 'status-dot offline';
            document.getElementById('system-status-text').textContent = errorMessage;
        }
         if (document.getElementById('rag-status-dot') && document.getElementById('rag-status-text')) {
            document.getElementById('rag-status-dot').className = 'status-dot offline';
            document.getElementById('rag-status-text').textContent = errorMessage;
        }
    }
}
// Export function for demo enhancements if needed by them to update status correctly
window.updateStatusIndicators = checkSystemStatus;


async function sendMessage(messageText, chatMessagesEl, userInputEl) {
    if (!chatMessagesEl || !userInputEl) {
        logger.error("Elementi DOM chatMessages o userInput non forniti a sendMessage.");
        return;
    }

    addMessageToChat(messageText, 'user', [], [], chatMessagesEl); 
    userInputEl.value = ''; 
    
    showTypingIndicator(chatMessagesEl); 
    
    try {
        const payload = {
            user_id: userId,
            message: messageText,
            conversation_id: conversationId
        };
        logger.debug("Invio messaggio a /api/chat:", payload);

        const response = await fetch(`${API_URL}/chat`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        
        hideTypingIndicator();

        if (response.ok) {
            const data = await response.json();
            logger.debug("Risposta ricevuta da /api/chat:", data);
            conversationId = data.conversation_id;
            
            addMessageToChat(
                data.message,
                'bot',
                data.sources || [],
                data.suggested_actions || [],
                chatMessagesEl 
            );
        } else {
            const errorData = await response.json().catch(() => ({ detail: `Errore server (${response.status})` }));
            const errorMessage = errorData.detail || `Errore HTTP: ${response.status}`;
            logger.error(`Errore API Chat: ${errorMessage}`, errorData);
            addMessageToChat(
                `Mi dispiace, si è verificato un errore (${response.status}). Riprova. Dettagli: ${errorMessage}`,
                'bot', [], [], chatMessagesEl 
            );
        }
    } catch (error) {
        hideTypingIndicator();
        logger.error(`Errore di rete/JS in sendMessage: ${error.message}`, error);
        addMessageToChat(
            "Connessione al server fallita. Controlla la tua connessione e riprova.",
            'bot', [], [], chatMessagesEl 
        );
    }
}

function addMessageToChat(text, sender, sources = [], suggestedActions = [], chatMessagesEl) {
    if (!chatMessagesEl) {
        logger.error("Elemento 'chat-messages' non fornito a addMessageToChat.");
        return;
    }
    
    const messageDiv = document.createElement('div');
    messageDiv.classList.add('message', sender === 'user' ? 'user-message' : 'bot-message');
    
    const formattedHtml = formatMessageText(text);
    messageDiv.innerHTML = formattedHtml;
    
    if (sender === 'bot' && sources && sources.length > 0) {
        logger.debug("Processando fonti ricevute:", JSON.stringify(sources)); 
        const sourcesContainer = document.createElement('div');
        sourcesContainer.classList.add('message-sources');
        
        const title = document.createElement('strong');
        title.textContent = 'Fonti: ';
        sourcesContainer.appendChild(title);

        const sourcesList = document.createElement('ul');
        sources.forEach((sourceObj, index) => { 
            logger.debug(`Processando sourceObj [${index}]:`, sourceObj); 
            const listItem = document.createElement('li');
            
            if (sourceObj && typeof sourceObj.source === 'string') {
                 const sourcePath = sourceObj.source; 
                 const fileName = sourcePath.split(/[\\/]/).pop(); 
                 listItem.textContent = fileName;
                 listItem.title = sourceObj.content_preview || sourcePath;
            } else {
                 listItem.textContent = "Fonte non valida/malformata";
                 logger.error(`Ricevuto oggetto source non valido all'indice ${index}:`, sourceObj);
            }
            sourcesList.appendChild(listItem);
        });
        sourcesContainer.appendChild(sourcesList);
        messageDiv.appendChild(sourcesContainer);
    }
    
    if (sender === 'bot' && suggestedActions && suggestedActions.length > 0) {
        const actionsContainer = document.createElement('div');
        actionsContainer.classList.add('suggested-actions-container'); // Modificato da 'suggested-actions'
        
        suggestedActions.forEach(action => {
            if (!action || typeof action.label !== 'string' || typeof action.type !== 'string' || typeof action.payload !== 'string') {
                logger.error("Azione suggerita non valida ricevuta:", action);
                return; 
            }

            const button = document.createElement('button');
            button.classList.add('action-button');
            
            let iconHtml = '';
            if (action.icon) { // Se un'icona è specificata (es. 'fas fa-car')
                 iconHtml = `<i class="${action.icon}"></i>`;
            } else { // Fallback per icone di default
                if (action.type === 'link') iconHtml = '<i class="fas fa-external-link-alt"></i>';
                else if (action.type === 'contact') iconHtml = '<i class="fas fa-phone"></i>';
                else if (action.type === 'message') iconHtml = '<i class="fas fa-comment-dots"></i>';
            }
            
            button.innerHTML = `${iconHtml} ${action.label}`.trim(); 
            
            button.addEventListener('click', () => {
                const currentChatMessagesEl = document.getElementById('chat-messages');
                const currentUserInputEl = document.getElementById('user-input');
                if (!currentChatMessagesEl || !currentUserInputEl) {
                    logger.error("Elementi DOM mancanti nel gestore click dell'azione suggerita.");
                    return;
                }

                logger.debug(`Azione suggerita cliccata: Tipo='${action.type}', Payload='${action.payload}'`);
                if (action.type === 'message') {
                    // Per le azioni suggerite, invia il payload come messaggio
                    sendMessage(action.payload, currentChatMessagesEl, currentUserInputEl); 
                } else if (action.type === 'link') {
                    window.open(action.payload, '_blank', 'noopener,noreferrer'); 
                } else if (action.type === 'contact') {
                    // Potrebbe aprire un modale di contatto o inviare un messaggio specifico
                    sendMessage(`Vorrei essere contattato riguardo: ${action.label} (Rif: ${action.payload})`, currentChatMessagesEl, currentUserInputEl);
                }
            });
            actionsContainer.appendChild(button);
        });
        messageDiv.appendChild(actionsContainer);
    }
    
    chatMessagesEl.appendChild(messageDiv);
    scrollToBottom(chatMessagesEl); 
}

function formatMessageText(text) {
    if (typeof text !== 'string') return '';
    let html = text;
    // Escape HTML special characters
    html = html.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');

    // Markdown-like formatting
    // Bold: **text** or __text__
    html = html.replace(/\*\*(.*?)\*\*|__(.*?)__/g, (match, p1, p2) => `<strong>${p1 || p2}</strong>`);
    // Italic: *text* or _text_
    html = html.replace(/\*(.*?)\*|_(.*?)_/g, (match, p1, p2) => `<em>${p1 || p2}</em>`);
    // Strikethrough: ~~text~~
    html = html.replace(/~~(.*?)~~/g, '<del>$1</del>');
    // Inline code: `code`
    html = html.replace(/`(.*?)`/g, '<code>$1</code>');
    // Links: [text](url "title")
    html = html.replace(/\[([^\]]+)\]\(([^)]+?)(?: "(.+)")?\)/g, '<a href="$2" target="_blank" rel="noopener noreferrer" title="$3">$1</a>');
    
    // Lists (simple unordered)
    // html = html.replace(/^\s*-\s+(.*)/gm, '<li>$1</li>'); // Requires pre-wrapping in <ul>
    // html = html.replace(/<\/li>\n<li>/g, '</li><li>'); // Clean up newlines between list items

    // For lists, it's better to detect blocks and wrap them. This is a simplified newline to <br>
    // More complex list handling would require more advanced parsing.
    html = html.replace(/\n/g, '<br>'); // Convert newlines to <br>
    
    return html;
}


function showTypingIndicator(chatMessagesEl) {
    if (!chatMessagesEl) return;
    hideTypingIndicator(); // Rimuove indicatori esistenti

    const typingDiv = document.createElement('div');
    typingDiv.classList.add('message', 'bot-message'); // Stessi stili di un messaggio bot
    typingDiv.id = 'typing-indicator-message'; // ID per rimuoverlo facilmente
    
    const indicator = document.createElement('div');
    indicator.classList.add('typing-indicator');
    indicator.innerHTML = '<span></span><span></span><span></span>'; // 3 pallini per l'animazione
    
    typingDiv.appendChild(indicator);
    chatMessagesEl.appendChild(typingDiv);
    scrollToBottom(chatMessagesEl);
}

function hideTypingIndicator() {
    const typingIndicator = document.getElementById('typing-indicator-message');
    if (typingIndicator) {
        typingIndicator.remove();
    }
}

function scrollToBottom(chatMessagesEl) {
    if (chatMessagesEl) {
        chatMessagesEl.scrollTop = chatMessagesEl.scrollHeight;
    }
}