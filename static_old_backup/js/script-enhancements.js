// === SCRIPT UI ENHANCEMENTS === //
// File: script-enhancements.js
// Da includere DOPO il tuo script.js esistente
// Ruolo: Migliorare aspetti UI preesistenti, senza alterare la logica del chatbot.

class UIEnhancements {
    constructor() {
        // Non c'è più this.demoMode o this.demoResponses

        this.domElements = {
            // Rimuovi elementi DOM legati alla vecchia demo mode
            // demoToggleBtn: document.getElementById('demo-toggle'), // Rimosso
            // demoBanner: document.getElementById('demo-banner'),     // Rimosso
            quickActionBtns: document.querySelectorAll('.quick-action-btn'), // Mantenuto se il pannello esiste in HTML
            userInput: document.getElementById('user-input'),
            charCounter: document.getElementById('char-counter'),         // Mantenuto se il div esiste in HTML
            chatMessagesEl: document.getElementById('chat-messages'),
            // Rimuovi elementi DOM per statistiche simulate
            // responseTimeDisplay: document.getElementById('response-time'),
            // accuracyDisplay: document.getElementById('accuracy'),    
            // avgResponseFooter: document.getElementById('avg-response'),
            // liveResponseTimePerfIndicator: document.getElementById('live-response-time'),
            // perfIndicator: document.getElementById('perf-indicator'),  
            // uptimeDisplay: document.getElementById('uptime'),          
            // footerDemoBadge: document.getElementById('footer-demo-badge'),
            chatHeaderStatus: document.getElementById('chat-header-status') // Può essere aggiornato da script.js
            // Gli indicatori di stato (systemStatusDot, etc.) sono gestiti da script.js
        };

        // Store original functions that might be overridden for enhancement
        this.originalAddMessageToChat = window.addMessageToChat;
        // Non si fa più override di sendMessage, showTypingIndicator, hideTypingIndicator, updateStatusIndicators

        this.init();
    }

    init() {
        logger.info('[UIEnhancements] Inizializzazione migliorie UI...');
        if (!this.domElements.userInput) {
            logger.warn('[UIEnhancements] User input non trovato. Alcune funzionalità UI potrebbero non attivarsi.');
        }
        
        // Mantenuti:
        this.setupQuickActions();        // Se il pannello Quick Actions è ancora in index.html
        this.setupCharacterCounter();    // Se il div per il contatore è ancora in index.html
        this.enhanceAddMessageStyling(); // Modifica addMessageToChat per aggiungere classi CSS
        this.showWelcomeSuggestion();    // Messaggio di benvenuto modificato

        // Rimossi:
        // this.setupDemoControls();
        // this.startMetricsUpdater();
        // this.updateDemoModeVisuals(); 
        // this.updateStatusIndicatorsInDemoContext();

        logger.info('[UIEnhancements] Migliorie UI inizializzate!');
    }

    // Rimosso: setupDemoControls
    // Rimosso: toggleDemoMode
    // Rimosso: updateDemoModeVisuals
    // Rimosso: updateStatusIndicatorsInDemoContext

    setupQuickActions() {
        if (!this.domElements.quickActionBtns || this.domElements.quickActionBtns.length === 0) {
            // logger.debug('[UIEnhancements] Nessun pulsante Quick Action trovato.');
            return;
        }
        this.domElements.quickActionBtns.forEach(btn => {
            btn.addEventListener('click', () => {
                const message = btn.dataset.message;
                if (message) {
                    this.sendQuickMessage(message);
                }
            });
        });
        logger.debug('[UIEnhancements] Pulsanti Quick Action configurati.');
    }

    async sendQuickMessage(message) { // Invia il messaggio usando la funzione sendMessage reale
        if (!this.domElements.userInput || !this.domElements.chatMessagesEl) return;
        
        this.domElements.userInput.value = message;
        if (this.domElements.charCounter) this.updateCharacterCounter(); // Aggiorna contatore se presente
        
        await this.sleep(50); // Breve pausa per UI

        if (typeof window.sendMessage === 'function') {
             window.sendMessage(message, this.domElements.chatMessagesEl, this.domElements.userInput);
        } else {
            logger.error("[UIEnhancements] Funzione window.sendMessage non definita.");
        }
    }

    setupCharacterCounter() {
        if (!this.domElements.userInput || !this.domElements.charCounter) {
            // logger.debug('[UIEnhancements] Input utente o contatore caratteri non trovato. Funzionalità non attiva.');
            return;
        }
        this.domElements.userInput.maxLength = 300;
        this.domElements.userInput.addEventListener('input', () => {
            this.updateCharacterCounter();
        });
        this.updateCharacterCounter(); // Chiamata iniziale
        logger.debug('[UIEnhancements] Contatore caratteri configurato.');
    }

    updateCharacterCounter() {
        if (!this.domElements.userInput || !this.domElements.charCounter) return;
        const length = this.domElements.userInput.value.length;
        const maxLength = this.domElements.userInput.maxLength || 300;

        this.domElements.charCounter.textContent = `${length}/${maxLength}`;
        this.domElements.charCounter.className = 'character-counter'; 

        if (length > maxLength * 0.95) { 
            this.domElements.charCounter.classList.add('danger');
        } else if (length > maxLength * 0.8) { 
            this.domElements.charCounter.classList.add('warning');
        }
    }

    enhanceAddMessageStyling() {
        if (this.originalAddMessageToChat) {
            window.addMessageToChat = (text, sender, sources, suggestedActions, chatMessagesEl) => {
                this.originalAddMessageToChat(text, sender, sources, suggestedActions, chatMessagesEl);
                
                const lastMessage = chatMessagesEl.lastElementChild;
                if (lastMessage && lastMessage.classList.contains('message')) {
                    lastMessage.classList.add('message-enhanced'); // Classe generica per animazioni/transizioni
                    if (sender === 'bot') {
                        lastMessage.classList.add('bot-message-enhanced'); // Stili specifici bot
                    } else {
                        lastMessage.classList.add('user-message-enhanced'); // Stili specifici utente
                    }
                }
            };
            logger.debug('[UIEnhancements] Funzione addMessageToChat estesa per stili migliorati.');
        } else {
            logger.warn("[UIEnhancements] Funzione addMessageToChat originale non trovata. Styling migliorato dei messaggi non applicato.");
        }
    }

    // Rimosso: demoSendMessage
    // Rimosso: generateDemoResponse e tutti i get...Response
    // Rimosso: generateDemoSources
    // Rimosso: generateDemoActions
    // Rimosso: recordResponseTime
    // Rimosso: updateResponseTimeDisplay
    // Rimosso: getAverageResponseTime
    // Rimosso: updateDisplayMetrics
    // Rimosso: startMetricsUpdater

    showWelcomeSuggestion() { // Nome e contenuto modificati
        setTimeout(() => {
            const firstBotMessage = this.domElements.chatMessagesEl ? this.domElements.chatMessagesEl.querySelector('.bot-message:first-child') : null;

            if (firstBotMessage && !firstBotMessage.querySelector('.tech-demo-suggestion')) { // Usa una classe diversa per il nuovo suggerimento
                const suggestionContainer = document.createElement('div');
                suggestionContainer.className = 'tech-demo-suggestion'; // Nuova classe per evitare conflitti e per styling
                suggestionContainer.style.marginTop = '12px';
                suggestionContainer.style.padding = '10px';
                suggestionContainer.style.background = 'var(--primary-light, #e6f2ff)'; // Usa variabile CSS o fallback
                suggestionContainer.style.border = '1px solid var(--accent-color, #0088cc)';
                suggestionContainer.style.borderRadius = '8px';
                suggestionContainer.style.fontSize = '0.9em';
                
                const icon = document.createElement('i');
                icon.className = 'fas fa-tools'; // Icona più tecnica
                icon.style.marginRight = '8px';
                suggestionContainer.appendChild(icon);

                const strongText = document.createElement('strong');
                strongText.textContent = ' Esplora le Capacità: ';
                suggestionContainer.appendChild(strongText);
                
                suggestionContainer.append('Utilizza i controlli "Demo Tecnica" (che appariranno nell\'header) per testare funzionalità specifiche del sistema.');
                
                firstBotMessage.appendChild(suggestionContainer);
                logger.debug('[UIEnhancements] Suggerimento Demo Tecnica aggiunto al messaggio di benvenuto.');
            }
        }, 2200); 
    }

    showNotification(message, type = 'info', duration = 5000) { // Mantenuta come utility
        const existingNotification = document.body.querySelector('.notification');
        if (existingNotification) {
            existingNotification.remove();
        }

        const notification = document.createElement('div');
        notification.className = `notification ${type}`; 

        const content = document.createElement('div');
        content.className = 'notification-content';
        content.textContent = message;

        const closeBtn = document.createElement('button');
        closeBtn.className = 'notification-close-btn';
        closeBtn.innerHTML = '&times;';
        closeBtn.setAttribute('aria-label', 'Chiudi notifica');
        closeBtn.onclick = () => {
            notification.classList.remove('show');
            setTimeout(() => { if (notification.parentElement) notification.remove(); }, 400);
        };
        
        notification.appendChild(content); 
        notification.appendChild(closeBtn);
        document.body.appendChild(notification);

        void notification.offsetWidth; 
        setTimeout(() => notification.classList.add('show'), 50);

        if (duration > 0) {
            setTimeout(() => {
                if (notification.parentElement) {
                    notification.classList.remove('show');
                    setTimeout(() => { if (notification.parentElement) notification.remove(); }, 400);
                }
            }, duration);
        }
    }

    sleep(ms) { // Mantenuta come utility
        return new Promise(resolve => setTimeout(resolve, ms));
    }
}

// Initialize UI enhancements when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    setTimeout(() => { 
        if (!window.UIEnhancementsInstance) { // Usa un nome diverso per l'istanza
             window.UIEnhancementsInstance = new UIEnhancements();
             // logger.info('[UIEnhancements] Istanza UIEnhancements creata.'); // logger è in script.js
             console.log('[UIEnhancements] Istanza UIEnhancements creata e inizializzata.');
        }
    }, 350); 
});

// Rimuovi le funzioni globali legate alla vecchia demo mode
// window.sendQuickDemoMessage = ...
// window.toggleDemoModeGlobally = ...