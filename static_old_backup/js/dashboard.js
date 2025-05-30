// static/js/dashboard.js

class Dashboard {
    constructor() {
        this.refreshInterval = null;
        this.activityChart = null;
        this.performanceChart = null; 
        this.cacheEnabled = true; 

        this.API_BASE_URL = '/api';
        this.DASHBOARD_DATA_ENDPOINT = `${this.API_BASE_URL}/dashboard/data`;
        this.CACHE_CLEAR_ENDPOINT = `${this.API_BASE_URL}/cache/clear`;
        this.RAG_REINDEX_ENDPOINT = `${this.API_BASE_URL}/rag/reindex`; 
        this.CACHE_TOGGLE_ENDPOINT = `${this.API_BASE_URL}/cache/toggle`; 
        
        document.addEventListener('DOMContentLoaded', () => {
            this.init();
        });
    }

    async init() {
        console.log('Inizializzazione Dashboard...');
        this.setupEventListeners();
        await this.loadDashboardData(); 
        this.startAutoRefresh(30000); 
        
        document.addEventListener('visibilitychange', () => {
            if (document.hidden) {
                this.stopAutoRefresh();
            } else {
                this.loadDashboardData(); 
                this.startAutoRefresh(30000); 
            }
        });
        console.log('Dashboard inizializzata con successo!');
    }

    setupEventListeners() {
        const refreshBtn = document.getElementById('refresh-btn');
        if (refreshBtn) {
            refreshBtn.addEventListener('click', () => this.loadDashboardData());
        } else {
            console.warn("Pulsante 'refresh-btn' non trovato.");
        }

        const clearCacheBtn = document.getElementById('clear-cache-btn');
        if (clearCacheBtn) {
            clearCacheBtn.addEventListener('click', () => this.clearCache());
        } else {
            console.warn("Pulsante 'clear-cache-btn' non trovato.");
        }

        const reindexRagBtn = document.getElementById('reindex-rag-btn');
        if (reindexRagBtn) {
            reindexRagBtn.addEventListener('click', () => this.reindexRAG());
        } else {
            console.warn("Pulsante 'reindex-rag-btn' non trovato.");
        }

        const toggleCacheBtn = document.getElementById('toggle-cache-btn');
        if (toggleCacheBtn) {
            toggleCacheBtn.addEventListener('click', () => this.toggleCache());
        } else {
            console.warn("Pulsante 'toggle-cache-btn' non trovato.");
        }
    }

    async fetchData(url, options = {}) {
        const { loadingMessage = 'Caricamento...', showLoadingModal = true } = options;
        if (showLoadingModal) {
            this.showLoading(true, loadingMessage);
        }
        try {
            const response = await fetch(url, options);
            if (!response.ok) {
                let errorDetail = `HTTP error! status: ${response.status}`;
                try {
                    const errorData = await response.json();
                    errorDetail = errorData.detail || errorData.message || errorDetail;
                } catch (e) {
                    console.warn("Impossibile parsare il corpo dell'errore API come JSON.");
                }
                throw new Error(errorDetail);
            }
            const result = await response.json();
            if (result.hasOwnProperty('status') && result.status !== 'success') {
                 throw new Error(result.detail || result.message || 'Errore nella risposta API');
            }
            return result.data || result; 
        } catch (error) {
            console.error(`Errore nel fetch da ${url}:`, error);
            this.showError(error.message || 'Errore di comunicazione con il server.');
            throw error; 
        } finally {
            if (showLoadingModal) {
                this.showLoading(false);
            }
        }
    }

    async loadDashboardData() {
        try {
            const data = await this.fetchData(this.DASHBOARD_DATA_ENDPOINT, { 
                loadingMessage: 'Aggiornamento dati dashboard...',
                showLoadingModal: !this.refreshInterval 
            });
            if (data) {
                this.updateDashboard(data);
                this.updateLastRefresh();
            }
        } catch (error) {
            console.warn("loadDashboardData fallito, la dashboard potrebbe non essere aggiornata.");
        }
    }

    updateDashboard(data) {
        if (!data) {
            console.error("Nessun dato ricevuto per aggiornare la dashboard.");
            this.showError("Nessun dato ricevuto dal server.");
            return;
        }
        this.updateStatusCards(data);
        this.updateCharts(data);
        this.updateSystemHealth(data);
    }

    updateStatusCards(data) {
        const { system_status, conversation_stats, performance_stats } = data;

        const statusIndicator = document.getElementById('system-status');
        const statusTextEl = document.getElementById('system-status-text');
        const uptimeEl = document.getElementById('system-uptime');

        if (system_status) {
            if (statusIndicator) {
                let statusClass = system_status.status || 'unknown';
                statusIndicator.className = `fas fa-circle status-indicator ${statusClass}`;
            }
            if (statusTextEl) statusTextEl.textContent = `${(system_status.status || 'N/D').charAt(0).toUpperCase() + (system_status.status || 'N/D').slice(1)}`;
            if (uptimeEl) uptimeEl.textContent = `v${system_status.version || 'N/A'} | Uptime: ${system_status.uptime || '--'}`;
        }

        if (conversation_stats) {
            this.setTextContent('today-conversations', conversation_stats.today_conversations);
            this.setTextContent('total-conversations', conversation_stats.total_conversations);
        }
        
        if (performance_stats) {
            const avgTimeMs = performance_stats.avg_response_time_ms;
            this.setTextContent('avg-response-time', typeof avgTimeMs === 'number' && avgTimeMs >= 0 ? `${(avgTimeMs / 1000).toFixed(2)}s` : 'N/A');
            
            this.setTextContent('cache-size', performance_stats.cache_items !== undefined ? performance_stats.cache_items : 'N/A');
            const hitRate = performance_stats.cache_hit_rate;
            this.setTextContent('cache-hit-rate', typeof hitRate === 'number' ? `${hitRate.toFixed(1)}%` : 'N/A');
        }
    }

    setTextContent(elementId, text) {
        const element = document.getElementById(elementId);
        if (element) {
            element.textContent = text !== undefined && text !== null ? text.toString() : '--';
        }
    }

    updateCharts(data) {
        if (data.activity_chart && Array.isArray(data.activity_chart) && data.activity_chart.length > 0) {
            this.updateActivityChart(data.activity_chart);
        } else {
            console.warn("Dati per activity_chart mancanti, vuoti o non validi:", data.activity_chart);
            this.renderPlaceholderActivityChart(); 
        }
        
        this.renderPlaceholderPerformanceChart(); 
    }
    
    renderPlaceholderActivityChart(message = 'Dati attività non disponibili') {
        const canvasElement = document.getElementById('activity-chart');
        if (!canvasElement) {
            console.error("Canvas 'activity-chart' non trovato per il placeholder.");
            return;
        }
        const ctx = canvasElement.getContext('2d');
        if (!ctx) {
            console.error("Contesto 2D non disponibile per 'activity-chart' (placeholder).");
            return;
        }

        if (this.activityChart) {
            this.activityChart.destroy();
            this.activityChart = null;
        }
        this.activityChart = new Chart(ctx, {
            type: 'line',
            data: { 
                labels: ['Nessun dato'], 
                datasets: [{ 
                    label: 'Attività', 
                    data: [0], 
                    borderColor: '#bdc3c7',
                    backgroundColor: 'rgba(189, 195, 199, 0.1)',
                    borderWidth: 1,
                    fill: true
                }] 
            },
            options: { 
                responsive: true, 
                maintainAspectRatio: true, 
                plugins: { 
                    title: { display: true, text: message, font: {size: 14}, color: '#7f8c8d' },
                    legend: { display: false }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        min: 0, 
                        suggestedMax: 1, 
                        ticks: { display: false } 
                    },
                    x: {
                        ticks: { display: false } 
                    }
                }
            }
        });
    }


    updateActivityChart(activityData) {
        const canvasElement = document.getElementById('activity-chart');
        if (!canvasElement) {
            console.error("Canvas 'activity-chart' non trovato nel DOM.");
            this.renderPlaceholderActivityChart("Errore: Canvas non trovato");
            return;
        }
        const ctx = canvasElement.getContext('2d');
        if (!ctx) {
            console.error("Impossibile ottenere il contesto 2D per 'activity-chart'.");
            this.renderPlaceholderActivityChart("Errore: Contesto grafico non disponibile");
            return;
        }
        
        if (this.activityChart) {
            this.activityChart.destroy();
            this.activityChart = null; 
        }

        if (!activityData || activityData.length === 0) {
            this.renderPlaceholderActivityChart();
            return;
        }

        const labels = activityData.map(item => {
            const date = new Date(item.hour); 
            return date.toLocaleTimeString('it-IT', { hour: '2-digit', minute: '2-digit', timeZone: 'UTC' }) + ' UTC';
        });
        const counts = activityData.map(item => item.count);
        
        const maxCount = counts.length > 0 ? Math.max(...counts) : 0;
        const stepSizeY = Math.max(1, Math.ceil(maxCount / 10));

        this.activityChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Messaggi per Ora (UTC)',
                    data: counts,
                    borderColor: '#3498db',
                    backgroundColor: 'rgba(52, 152, 219, 0.1)',
                    borderWidth: 2,
                    fill: true,
                    tension: 0.3
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: true, 
                scales: {
                    y: {
                        beginAtZero: true,
                        min: 0, 
                        ticks: {
                            stepSize: stepSizeY,
                            precision: 0 
                        }
                    },
                    x: {
                        display: true,
                        ticks: {
                            maxTicksLimit: 12, 
                            autoSkip: true,
                        }
                    }
                },
                plugins: {
                    legend: {
                        display: true, 
                        position: 'top',
                    },
                    title: { 
                        display: false 
                    }
                }
            }
        });
    }
    
    renderPlaceholderPerformanceChart() {
        const canvasElement = document.getElementById('performance-chart');
         if (!canvasElement) {
            console.error("Canvas 'performance-chart' non trovato nel DOM.");
            return;
        }
        const ctx = canvasElement.getContext('2d');
        if (!ctx) {
            console.error("Impossibile ottenere il contesto 2D per 'performance-chart'.");
            return;
        }

        if (this.performanceChart) {
            this.performanceChart.destroy();
            this.performanceChart = null; 
        }
        
        this.performanceChart = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: ['Metrica A (Placeholder)', 'Metrica B (Placeholder)', 'Metrica C (Placeholder)'],
                datasets: [{
                    label: 'Performance (Placeholder)',
                    data: [30, 50, 20], 
                    backgroundColor: ['rgba(52, 152, 219, 0.8)', 'rgba(46, 204, 113, 0.8)', 'rgba(230, 126, 34, 0.8)'],
                    borderWidth: 2, 
                    borderColor: '#fff' 
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false, 
                plugins: {
                    legend: { 
                        position: 'bottom',
                        labels: {
                            padding: 10, 
                            boxWidth: 12, 
                            font: {
                                size: 10 
                            }
                        }
                    },
                    title: { 
                        display: true, 
                        text: 'Performance Sistema (Placeholder)', 
                        padding: {
                            top: 5, 
                            bottom: 5 
                        },
                        font: {
                            size: 14 
                        }
                    }
                },
                cutout: '60%',
                layout: { 
                    padding: {
                        top: 5, // Aggiunto un piccolo padding sopra
                        bottom: 20, // <<<< MODIFICATO: Aumentato il padding in basso
                        left: 5,
                        right: 5
                    }
                }
            }
        });
    }

    updateSystemHealth(data) {
        const healthComps = data.system_health_components;
        if (!healthComps) {
            this.updateHealthIcon('health-database', false);
            this.updateHealthIcon('health-rag', false);
            this.updateHealthIcon('health-cache', false);
            return;
        }

        this.updateHealthIcon('health-database', healthComps.database_status === 'ok');
        
        const ragIsHealthy = healthComps.rag_status === 'initialized' || healthComps.rag_status === 'ready' || healthComps.rag_in_mock_mode === true;
        this.updateHealthIcon('health-rag', ragIsHealthy);
        
        this.updateHealthIcon('health-cache', healthComps.cache_status === 'ok');
    }

    updateHealthIcon(elementId, isHealthy) {
        const element = document.getElementById(elementId);
        if (element) {
            element.innerHTML = isHealthy 
                ? '<i class="fas fa-check-circle" style="color: #2ecc71;"></i>'  
                : '<i class="fas fa-times-circle" style="color: #e74c3c;"></i>';
        }
    }

    async clearCache() {
        if (!confirm("Sei sicuro di voler pulire la cache?")) return;
        try {
            const result = await this.fetchData(this.CACHE_CLEAR_ENDPOINT, { 
                method: 'POST',
                loadingMessage: 'Pulizia cache in corso...'
            });
            if (result) {
                this.showSuccess(result.message || 'Cache pulita con successo.');
                setTimeout(() => this.loadDashboardData(), 1000); 
            }
        } catch (error) {
            // Errore già gestito e mostrato da fetchData
        }
    }

    async reindexRAG() {
        this.showNotification("La reindicizzazione RAG non è ancora implementata nel backend.", "info");
    }

    async toggleCache() {
        this.showNotification("Il toggle della cache non è ancora implementato nel backend.", "info");
    }

    updateCacheToggleButton() {
        const button = document.getElementById('toggle-cache-btn');
        if (button) {
            if (this.cacheEnabled) {
                button.className = 'btn btn-secondary'; 
                button.innerHTML = '<i class="fas fa-toggle-on"></i> <span id="cache-toggle-text">Disabilita Cache</span>';
            } else {
                button.className = 'btn btn-warning'; 
                button.innerHTML = '<i class="fas fa-toggle-off"></i> <span id="cache-toggle-text">Abilita Cache</span>';
            }
        }
    }

    startAutoRefresh(interval = 30000) {
        this.stopAutoRefresh(); 
        this.refreshInterval = setInterval(() => {
            if (!document.hidden) { 
                this.loadDashboardData();
            }
        }, interval);
        console.log(`Auto-refresh attivato (ogni ${interval / 1000} secondi)`);
    }

    stopAutoRefresh() {
        if (this.refreshInterval) {
            clearInterval(this.refreshInterval);
            this.refreshInterval = null;
            console.log('Auto-refresh disattivato');
        }
    }

    updateLastRefresh() {
        const now = new Date();
        const timeString = now.toLocaleTimeString('it-IT', { hour: '2-digit', minute: '2-digit', second: '2-digit' });
        this.setTextContent('last-update', `Ultimo aggiornamento: ${timeString}`);
    }

    showLoading(show, message = 'Caricamento...') {
        const modal = document.getElementById('loading-modal');
        if (!modal) return;
        const modalText = modal.querySelector('p');
        
        if (show) {
            if(modalText) modalText.textContent = message;
            modal.classList.add('show'); 
        } else {
            modal.classList.remove('show');
        }
    }

    showNotification(message, type = 'info', duration = 5000) {
        const container = document.getElementById('notification-container') || this.createNotificationContainer();
        
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        let iconClass = 'fa-info-circle';
        if (type === 'success') iconClass = 'fa-check-circle';
        if (type === 'error') iconClass = 'fa-exclamation-circle';

        notification.innerHTML = `
            <i class="fas ${iconClass}"></i>
            <span>${message}</span>
            <button class="notification-close-btn" aria-label="Chiudi notifica">&times;</button>
        `;
        
        container.appendChild(notification);

        notification.querySelector('.notification-close-btn').addEventListener('click', () => {
            notification.classList.add('notification-fade-out');
            setTimeout(() => notification.remove(), 300); 
        });

        if (duration > 0) { 
            setTimeout(() => {
                if (notification.parentElement) {
                    notification.classList.add('notification-fade-out');
                    setTimeout(() => notification.remove(), 300);
                }
            }, duration);
        }
    }
    
    createNotificationContainer() {
        let container = document.getElementById('notification-container');
        if (!container) {
            container = document.createElement('div');
            container.id = 'notification-container';
            document.body.appendChild(container);

            if (!this.areNotificationStylesInCSS()) {
                 const styles = document.createElement('style');
                 styles.id = 'dynamic-notification-styles'; 
                 styles.textContent = `
                    #notification-container {
                        position: fixed; top: 20px; right: 20px; z-index: 1001;
                        display: flex; flex-direction: column; gap: 10px;
                    }
                    .notification {
                        padding: 15px 20px; border-radius: 8px; color: white;
                        display: flex; align-items: center; gap: 10px;
                        min-width: 300px; max-width: 400px;
                        box-shadow: 0 2px 10px rgba(0,0,0,0.2);
                        animation: notification-slideIn 0.3s ease-out;
                        transition: opacity 0.3s ease, transform 0.3s ease;
                    }
                    .notification-success { background: #27ae60; }
                    .notification-error { background: #e74c3c; }
                    .notification-info { background: #3498db; }
                    .notification span { flex-grow: 1; }
                    .notification-close-btn {
                        background: none; border: none; color: white;
                        cursor: pointer; padding: 0 5px; font-size: 20px;
                        line-height: 1; opacity: 0.7; margin-left: auto;
                    }
                    .notification-close-btn:hover { opacity: 1; }
                    .notification-fade-out { opacity: 0; transform: translateX(20px); }
                    @keyframes notification-slideIn {
                        from { transform: translateX(100%); opacity: 0; }
                        to { transform: translateX(0); opacity: 1; }
                    }
                 `;
                 document.head.appendChild(styles);
            }
        }
        return container;
    }

    areNotificationStylesInCSS() {
        const testEl = document.createElement('div');
        testEl.className = 'notification'; 
        document.body.appendChild(testEl); 
        const styles = window.getComputedStyle(testEl);
        const hasStyles = styles.getPropertyValue('padding-left') === '20px' || styles.getPropertyValue('padding') === '15px 20px';
        document.body.removeChild(testEl);
        return hasStyles;
    }

    showSuccess(message) { this.showNotification(message, 'success'); }
    showError(message) { this.showNotification(message, 'error'); }
}

// Inizializza la dashboard
const dashboard = new Dashboard();
