# app/utils/performance_monitor.py
import time
import functools
import logging
from typing import Dict, Any, List, Optional, Callable, Coroutine 
from collections import defaultdict
import json
from datetime import datetime, timedelta 
import os
import asyncio 

try:
    from app.utils.logging_config import logger as app_logger
    logger = app_logger.getChild(__name__) 
except ImportError:
    logger = logging.getLogger(__name__)
    if not logger.hasHandlers(): 
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

class PerformanceMonitor:
    def __init__(self, metrics_filepath: str = "logs/performance_metrics.json"):
        self.metrics: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
        self.metrics_filepath: str = metrics_filepath
        # Assicura che la directory per il file di metriche esista
        metrics_dir = os.path.dirname(self.metrics_filepath)
        if metrics_dir and not os.path.exists(metrics_dir):
            try:
                os.makedirs(metrics_dir, exist_ok=True)
            except OSError as e:
                logger.error(f"Errore durante la creazione della directory per le metriche {metrics_dir}: {e}")
        self.load_metrics()

    def record_metric_entry(self, func_name: str, execution_time: float, success: bool, error_message: Optional[str] = None):
        entry: Dict[str, Any] = {
            'timestamp': datetime.now().isoformat(),
            'execution_time': execution_time,
            'success': success
        }
        if error_message:
            entry['error'] = error_message
        
        self.metrics[func_name].append(entry)

    def get_metrics_summary(self, specific_metrics: Optional[List[str]] = None) -> Dict[str, Any]: # MODIFICATO: Accetta specific_metrics
        summary = {}
        now = datetime.now()

        # Se specific_metrics è fornito, usa quelli, altrimenti tutte le chiavi in self.metrics
        metrics_to_process = specific_metrics if specific_metrics is not None else list(self.metrics.keys())

        for func_name in metrics_to_process:
            func_metrics = self.metrics.get(func_name, []) # Usa .get() per sicurezza
            
            if not func_metrics: 
                summary[func_name] = {
                    'total_calls': 0, 'successful_calls': 0, 'failed_calls': 0, 'success_rate_percent': 0.0,
                    'avg_time_ms_all': 0.0, 'min_time_ms_all': 0.0, 'max_time_ms_all': 0.0,
                    'avg_time_ms_successful': 0.0, 'min_time_ms_successful': 0.0, 'max_time_ms_successful': 0.0,
                    'last_24h_total_calls': 0, 'last_24h_successful_calls': 0, 'last_24h_failed_calls': 0,
                }
                if func_name.endswith("_counter"): # Gestione contatori semplici
                    summary[func_name] = {'count': 0}
                continue

            # Gestione speciale per i contatori (es. rag_cache_hits_counter)
            if func_name.endswith("_counter"):
                # Per i contatori, sommiamo i valori di 'execution_time' che usiamo come 'count'
                total_count = sum(m.get('execution_time', 0) for m in func_metrics if m.get('success')) # Assumendo che il conteggio sia in execution_time
                summary[func_name] = {'count': total_count}
                continue

            all_execution_times_ms = [m['execution_time'] * 1000 for m in func_metrics]
            
            successful_metrics = [m for m in func_metrics if m.get('success', False)]
            successful_execution_times_ms = [m['execution_time'] * 1000 for m in successful_metrics]
            
            failed_metrics_count = len(func_metrics) - len(successful_metrics)

            calls_last_24h = [
                m for m in func_metrics
                if now - datetime.fromisoformat(m['timestamp']) <= timedelta(hours=24)
            ]
            successful_calls_last_24h = [m for m in calls_last_24h if m.get('success', False)]
            failed_calls_last_24h_count = len(calls_last_24h) - len(successful_calls_last_24h)

            summary[func_name] = {
                'total_calls': len(func_metrics),
                'successful_calls': len(successful_metrics),
                'failed_calls': failed_metrics_count,
                'success_rate_percent': round((len(successful_metrics) / len(func_metrics) * 100),1) if func_metrics else 0.0,
                
                'avg_time_ms_all': round(sum(all_execution_times_ms) / len(all_execution_times_ms), 2) if all_execution_times_ms else 0.0,
                'min_time_ms_all': round(min(all_execution_times_ms), 2) if all_execution_times_ms else 0.0,
                'max_time_ms_all': round(max(all_execution_times_ms), 2) if all_execution_times_ms else 0.0,
                
                'avg_time_ms_successful': round(sum(successful_execution_times_ms) / len(successful_execution_times_ms), 2) if successful_execution_times_ms else 0.0,
                'min_time_ms_successful': round(min(successful_execution_times_ms), 2) if successful_execution_times_ms else 0.0,
                'max_time_ms_successful': round(max(successful_execution_times_ms), 2) if successful_execution_times_ms else 0.0,
                
                'last_24h_total_calls': len(calls_last_24h),
                'last_24h_successful_calls': len(successful_calls_last_24h),
                'last_24h_failed_calls': failed_calls_last_24h_count,
            }
        return summary

    def save_metrics(self):
        try:
            metrics_dir = os.path.dirname(self.metrics_filepath)
            if metrics_dir and not os.path.exists(metrics_dir):
                 os.makedirs(metrics_dir, exist_ok=True)
            with open(self.metrics_filepath, 'w') as f:
                json.dump(dict(self.metrics), f, indent=4) 
            logger.info(f"Performance metrics salvate con successo in {self.metrics_filepath}")
        except IOError as e:
            logger.error(f"Errore durante il salvataggio delle metriche in {self.metrics_filepath}: {e}")
        except Exception as e:
            logger.error(f"Errore imprevisto durante il salvataggio delle metriche: {e}", exc_info=True)

    def load_metrics(self):
        if not os.path.exists(self.metrics_filepath):
            logger.info(f"File metriche {self.metrics_filepath} non trovato. Avvio con metriche vuote.")
            self.metrics = defaultdict(list)
            return

        try:
            with open(self.metrics_filepath, 'r') as f:
                data = json.load(f)
                self.metrics = defaultdict(list)
                if isinstance(data, dict): 
                    for key, value in data.items():
                        if isinstance(value, list): 
                            self.metrics[key] = value
                        else:
                            logger.warning(f"Valore non valido per la chiave '{key}' nel file metriche. Attesa lista, ricevuto {type(value)}. Ignoro.")
                else:
                    logger.warning(f"Formato dati non valido nel file metriche {self.metrics_filepath}. Atteso dizionario, ricevuto {type(data)}. Avvio con metriche vuote.")
                    self.metrics = defaultdict(list) 
            logger.info(f"Performance metrics caricate con successo da {self.metrics_filepath}")
        except json.JSONDecodeError as e:
            logger.error(f"Errore di decodifica JSON da {self.metrics_filepath}. Avvio con metriche vuote. Errore: {e}")
            self.metrics = defaultdict(list)
        except Exception as e:
            logger.error(f"Errore imprevisto durante il caricamento delle metriche da {self.metrics_filepath}. Avvio con metriche vuote. Errore: {e}", exc_info=True)
            self.metrics = defaultdict(list)
            
    def clear_metrics_for_function(self, func_name: str):
        if func_name in self.metrics:
            del self.metrics[func_name] 
            logger.info(f"Metriche azzerate per la funzione: {func_name}")
        else:
            logger.warning(f"Nessuna metrica trovata da azzerare per la funzione: {func_name}")

    def clear_all_metrics(self):
        self.metrics.clear()
        logger.info("Tutte le performance metrics sono state azzerate.")

performance_monitor = PerformanceMonitor()

def measure_performance(name: str) -> Callable:
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            start_time = time.perf_counter()
            success = False
            error_msg = None
            try:
                result = func(*args, **kwargs)
                success = True
                return result
            except Exception as e:
                error_msg = str(e)
                logger.error(f"Function '{name}' (from {func.__name__}) failed: {type(e).__name__} - {e}")
                raise 
            finally:
                execution_time = time.perf_counter() - start_time
                performance_monitor.record_metric_entry(name, execution_time, success, error_msg)
                if success:
                    logger.info(f"Function '{name}' (from {func.__name__}) executed in {execution_time:.4f}s")
        return wrapper
    return decorator

def measure_performance_async(func_name: str) -> Callable[[Callable[..., Coroutine]], Callable[..., Coroutine]]:
    if not isinstance(func_name, str) or not func_name:
        effective_func_name = "unknown_async_function_metric"
        logger.warning(f"func_name non valido fornito a measure_performance_async. Uso '{effective_func_name}'.")
    else:
        effective_func_name = func_name
            
    def decorator(func: Callable[..., Coroutine]) -> Callable[..., Coroutine]:
        if not asyncio.iscoroutinefunction(func):
            logger.warning(
                f"Il decoratore 'measure_performance_async' è progettato per funzioni asincrone. "
                f"Applicato a una funzione sincrona '{getattr(func, '__name__', 'N/A')}' con metrica '{effective_func_name}'. "
            )

        @functools.wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            start_time = time.perf_counter()
            success = False
            error_msg = None
            try:
                result = await func(*args, **kwargs)
                success = True
                return result
            except Exception as e:
                error_msg = str(e)
                logger.error(f"Async Function '{effective_func_name}' (from {func.__name__}) failed: {type(e).__name__} - {e}")
                raise 
            finally:
                execution_time = time.perf_counter() - start_time
                performance_monitor.record_metric_entry(effective_func_name, execution_time, success, error_msg)
                if success:
                    logger.info(f"Async Function '{effective_func_name}' (from {func.__name__}) executed in {execution_time:.4f}s")
        return wrapper
    return decorator
