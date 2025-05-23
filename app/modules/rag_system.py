import os
import asyncio
import io
from typing import List, Dict, Any, Optional, Tuple

# OCR Imports con fallback sicuro per deploy
try:
    import fitz  # PyMuPDF
    PYMUPDF_AVAILABLE = True
    print("✅ PyMuPDF disponibile - OCR PDF attivo")
except ImportError:
    print("⚠️  PyMuPDF non disponibile - PDF OCR disabilitato (modalità compatibilità)")
    PYMUPDF_AVAILABLE = False
    # Crea un fitz mock per evitare errori
    class MockFitz:
        @staticmethod
        def open(path):
            raise ImportError("PyMuPDF non disponibile")
    fitz = MockFitz()

try:
    import pytesseract
    from PIL import Image 
    TESSERACT_AVAILABLE = True
    print("✅ Tesseract disponibile - OCR immagini attivo")
except ImportError:
    print("⚠️  Tesseract non disponibile - OCR immagini disabilitato")
    TESSERACT_AVAILABLE = False

# Resto degli import (lascia tutto uguale)
from langchain_chroma import Chroma 
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains import RetrievalQA
from langchain_community.document_loaders import TextLoader, UnstructuredMarkdownLoader, UnstructuredWordDocumentLoader
from langchain_core.documents import Document
from langchain.prompts import PromptTemplate
import chromadb 

from app.config import (
    OPENAI_API_KEY, 
    EMBEDDINGS_MODEL_NAME, 
    LLM_MODEL_NAME,
    CHUNK_SIZE, 
    CHUNK_OVERLAP, 
    RETRIEVER_K,
    CHROMA_PERSIST_DIR,
    DOCS_DIRECTORY,
    USE_MOCK
)
from app import config as app_config

from app.utils.logging_config import logger
from app.utils.performance_monitor import performance_monitor, measure_performance_async
from app.utils.smart_cache import smart_cache as rag_smart_cache
from app.utils.text_processing import load_spacy_model, normalize_text, NLP_MODEL_NAME as SPACY_MODEL_FOR_NORMALIZATION

# Configurazione Tesseract con fallback
if TESSERACT_AVAILABLE:
    TESSERACT_EXECUTABLE_PATH = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
    try:
        if os.path.exists(TESSERACT_EXECUTABLE_PATH):
            pytesseract.pytesseract.tesseract_cmd = TESSERACT_EXECUTABLE_PATH
        # Test per Linux/Railway
        import subprocess
        result = subprocess.run(['tesseract', '--version'], capture_output=True, text=True)
        TESSERACT_CONFIGURED = True
        logger.info("Tesseract configurato correttamente")
    except Exception as e:
        logger.warning(f"Tesseract non configurato correttamente: {e}")
        TESSERACT_CONFIGURED = False
else:
    TESSERACT_CONFIGURED = False

DEFAULT_PROMPT_TEMPLATE = """
Sei un assistente AI per una compagnia di assicurazioni. Utilizza le seguenti informazioni di contesto per rispondere alla domanda dell'utente.
Se non conosci la risposta basandoti sul contesto, dì che non lo sai, non cercare di inventare una risposta.
Mantieni la risposta concisa e utile. Se la domanda è un saluto o una conversazione generica, rispondi in modo amichevole.

Contesto:
{context}

Domanda: {question}

Risposta utile:"""

def ocr_image(image_bytes: bytes, language: str = "ita") -> str:
    """
    Esegue OCR su un'immagine (con fallback sicuro)
    """
    if not TESSERACT_CONFIGURED:
        logger.warning("Tesseract non configurato. OCR non disponibile.")
        return ""
    
    if not TESSERACT_AVAILABLE:
        logger.warning("Tesseract non installato. OCR saltato.")
        return ""
    
    try:
        img = Image.open(io.BytesIO(image_bytes))
        
        # Test per environment Railway/Linux
        try:
            text = pytesseract.image_to_string(img, lang=language)
        except Exception as e_tesseract:
            logger.warning(f"Errore Tesseract con lingua {language}: {e_tesseract}")
            # Fallback a inglese
            try:
                text = pytesseract.image_to_string(img, lang='eng')
                logger.info("OCR fallback a inglese riuscito")
            except Exception as e_eng:
                logger.error(f"OCR fallback fallito: {e_eng}")
                return ""
        
        # Log per debug
        if text.strip():
            logger.debug(f"OCR completato: {len(text)} caratteri estratti")
        else:
            logger.debug("OCR completato ma nessun testo estratto")
            
        return text.strip()
        
    except Exception as e:
        logger.error(f"Errore generico durante l'OCR: {e}")
        return ""

def preprocess_image_for_ocr(image_bytes: bytes) -> bytes:
    """
    Preprocessa un'immagine per migliorare i risultati OCR (con fallback)
    """
    if not TESSERACT_AVAILABLE:
        logger.debug("PIL non disponibile per preprocessing - ritorno immagine originale")
        return image_bytes
        
    try:
        img = Image.open(io.BytesIO(image_bytes))
        
        # Converti in scala di grigi
        if img.mode != 'L':
            img = img.convert('L')
        
        # Aumenta la risoluzione se troppo bassa
        width, height = img.size
        min_dimension = 300
        if width < min_dimension or height < min_dimension:
            scale = max(min_dimension/width, min_dimension/height, 2.0)
            new_size = (int(width * scale), int(height * scale))
            img = img.resize(new_size, Image.Resampling.LANCZOS)
            logger.debug(f"Immagine ridimensionata da {width}x{height} a {new_size[0]}x{new_size[1]}")
        
        # Aumenta il contrasto
        from PIL import ImageEnhance
        enhancer = ImageEnhance.Contrast(img)
        img = enhancer.enhance(1.5)
        
        # Converti di nuovo in bytes
        img_buffer = io.BytesIO()
        img.save(img_buffer, format='PNG')
        return img_buffer.getvalue()
        
    except Exception as e:
        logger.warning(f"Errore nel preprocessing dell'immagine: {e}")
        return image_bytes

def parse_pdf_enhanced(pdf_path: str) -> Tuple[str, List[Dict[str, Any]], Dict[str, Any]]:
    """
    Parsing avanzato di PDF con OCR migliorato (con fallback per deploy)
    """
    if not PYMUPDF_AVAILABLE:
        logger.warning(f"PyMuPDF non disponibile - saltando elaborazione PDF: {pdf_path}")
        return "", [], {"error": "PyMuPDF non disponibile", "file_path": pdf_path}
    
    full_text = ""
    images_data = []
    pdf_metadata = {}
    
    try:
        doc = fitz.open(pdf_path)
    except Exception as e:
        logger.error(f"Errore nell'apertura del file PDF '{pdf_path}': {e}")
        return "", [], {"error": str(e), "file_path": pdf_path}

    # Estrai metadata
    doc_meta = doc.metadata
    if doc_meta:
        pdf_metadata = {
            "title": doc_meta.get("title", None), 
            "author": doc_meta.get("author", None),
            "subject": doc_meta.get("subject", None), 
            "keywords": doc_meta.get("keywords", None),
            "creator": doc_meta.get("creator", None), 
            "producer": doc_meta.get("producer", None),
            "creationDate": doc_meta.get("creationDate", None), 
            "modDate": doc_meta.get("modDate", None),
            "format": doc_meta.get("format", "PDF"), 
            "encryption": doc_meta.get("encryption", None)
        }
    pdf_metadata["page_count"] = len(doc)

    # Processa ogni pagina
    for page_num in range(len(doc)):
        try:
            page = doc.load_page(page_num)
            
            # Estrai testo normale
            page_text = page.get_text("text")
            full_text += page_text + "\n"
            
            # Se la pagina ha poco testo E l'OCR è disponibile, usa OCR
            if len(page_text.strip()) < 50 and TESSERACT_CONFIGURED:
                logger.debug(f"Pagina {page_num + 1} ha poco testo ({len(page_text.strip())} caratteri), applicando OCR all'intera pagina")
                
                # Converti l'intera pagina in immagine ad alta risoluzione
                mat = fitz.Matrix(2.0, 2.0)  # 2x risoluzione per migliorare OCR
                pix = page.get_pixmap(matrix=mat)
                img_data = pix.tobytes("png")
                pix = None
                
                # Aggiungi questa pagina per OCR
                images_data.append({
                    "page_number": page_num + 1,
                    "image_index_on_page": 0,
                    "image_bytes": img_data,
                    "image_format": "PNG",
                    "xref": -1,  # Indica che è l'intera pagina
                    "bbox": None,
                    "page_has_text": False,
                    "is_full_page": True
                })
                continue  # Salta l'estrazione dei frammenti
            elif len(page_text.strip()) < 50:
                logger.debug(f"Pagina {page_num + 1} ha poco testo ma OCR non disponibile - saltando")
            
            # Estrai immagini (solo se la pagina ha già testo E OCR è disponibile)
            if TESSERACT_CONFIGURED:
                image_list = page.get_images(full=True)
                
                for img_index, img_info_tuple in enumerate(image_list):
                    xref = img_info_tuple[0]
                    
                    try:
                        pix = fitz.Pixmap(doc, xref)
                        image_bytes = pix.tobytes("png")
                        pix = None  # Libera memoria
                        
                        if image_bytes:
                            # Preprocessa l'immagine per OCR
                            processed_bytes = preprocess_image_for_ocr(image_bytes) if TESSERACT_AVAILABLE else image_bytes
                            
                            # Info sul bounding box
                            bbox_info = None 
                            try:
                                img_rects = page.get_image_rects(img_info_tuple)
                                if img_rects and isinstance(img_rects[0], fitz.Rect):
                                    bbox_info = img_rects[0].irect
                            except Exception as e_bbox:
                                logger.debug(f"Impossibile ottenere bbox per immagine: {e_bbox}")
                            
                            images_data.append({
                                "page_number": page_num + 1,
                                "image_index_on_page": img_index,
                                "image_bytes": processed_bytes,
                                "image_format": "PNG",
                                "xref": xref,
                                "bbox": bbox_info,
                                "page_has_text": len(page_text.strip()) > 50
                            })
                    except Exception as e_img:
                        logger.error(f"Errore nell'estrazione immagine xref {xref}: {e_img}")
                        continue
                        
        except Exception as e_page:
            logger.error(f"Errore nella pagina {page_num + 1}: {e_page}")
            continue
    
    try:
        doc.close()
    except Exception as e:
        logger.warning(f"Errore nella chiusura del PDF: {e}")
    
    return full_text, images_data, pdf_metadata

class OptimizedRAGSystem:
    def __init__(self, config_override: Optional[Dict] = None):
        self.config = { 
            "OPENAI_API_KEY": OPENAI_API_KEY,
            "EMBEDDINGS_MODEL_NAME": EMBEDDINGS_MODEL_NAME,
            "LLM_MODEL_NAME": LLM_MODEL_NAME,
            "CHUNK_SIZE": CHUNK_SIZE,
            "CHUNK_OVERLAP": CHUNK_OVERLAP,
            "RETRIEVER_K": RETRIEVER_K,
            "CHROMA_PERSIST_DIR": CHROMA_PERSIST_DIR,
            "DOCS_DIRECTORY": DOCS_DIRECTORY,
            "USE_MOCK": USE_MOCK,
            "PROMPT_TEMPLATE": DEFAULT_PROMPT_TEMPLATE,
            "TESSERACT_LANG": getattr(app_config, 'TESSERACT_LANG', 'ita'),
            "SPACY_MODEL_NAME": SPACY_MODEL_FOR_NORMALIZATION
        }
        if config_override:
            self.config.update(config_override)

        self.embeddings: Optional[OpenAIEmbeddings] = None
        self.llm: Optional[ChatOpenAI] = None
        self.vectorstore: Optional[Chroma] = None
        self.qa_chain: Optional[RetrievalQA] = None
        self.nlp_processor: Optional[Any] = None
        
        self.is_initialized: bool = False 
        self.use_mock: bool = self.config["USE_MOCK"]
        self.collection_name: str = os.getenv("CHROMA_COLLECTION_NAME", "assicurazioni_docs_prod_lc_v7")
        self.chroma_persist_directory: str = self.config["CHROMA_PERSIST_DIR"]
        os.makedirs(self.chroma_persist_directory, exist_ok=True)

        logger.info(f"Istanza OptimizedRAGSystem creata. Mock: {self.use_mock}, Collection: {self.collection_name}")
        logger.debug(f"Configurazione RAG: {self.config}")
        
        # Log dello stato di Tesseract
        if TESSERACT_AVAILABLE and TESSERACT_CONFIGURED:
            logger.info("Tesseract OCR disponibile e configurato")
        else:
            logger.warning("Tesseract OCR non disponibile - L'estrazione testo da immagini sara disabilitata")

    @measure_performance_async("rag_setup_optimized")
    async def setup_rag_system_async(self):
        pid = os.getpid()
        logger.info(f"[PID:{pid}] RAG_CLASS.setup: Avvio setup OptimizedRAGSystem (Mock: {self.use_mock})...")
        try:
            if not self.use_mock:
                logger.info(f"[PID:{pid}] RAG_CLASS.setup: Caricamento modello spaCy '{self.config['SPACY_MODEL_NAME']}' per normalizzazione...")
                self.nlp_processor = await asyncio.to_thread(load_spacy_model, self.config['SPACY_MODEL_NAME'])
                if not self.nlp_processor:
                    logger.error(f"[PID:{pid}] RAG_CLASS.setup: Fallimento caricamento modello spaCy.")
                else:
                    logger.info(f"[PID:{pid}] RAG_CLASS.setup: Modello spaCy '{self.config['SPACY_MODEL_NAME']}' caricato.")

            if self.use_mock:
                logger.info(f"[PID:{pid}] RAG_CLASS.setup: Setup RAG in MODALITÀ MOCK.")
                self.is_initialized = True 
                return 

            logger.info(f"[PID:{pid}] RAG_CLASS.setup: Inizializzazione Embeddings '{self.config['EMBEDDINGS_MODEL_NAME']}'...")
            self.embeddings = OpenAIEmbeddings(
                openai_api_key=self.config["OPENAI_API_KEY"],
                model=self.config["EMBEDDINGS_MODEL_NAME"]
            )
            logger.info(f"[PID:{pid}] RAG_CLASS.setup: Embeddings inizializzati.")

            logger.info(f"[PID:{pid}] RAG_CLASS.setup: Caricamento, normalizzazione e splitting documenti...")
            documents_to_add = await self._load_and_split_documents_async()
            
            if not documents_to_add and not os.path.exists(os.path.join(self.chroma_persist_directory, "chroma.sqlite3")):
                logger.warning(f"[PID:{pid}] RAG_CLASS.setup: Nessun documento da processare e nessun DB Chroma preesistente. RAG potrebbe essere vuoto.")

            logger.info(f"[PID:{pid}] RAG_CLASS.setup: Controllo o creazione vectorstore...")
            self.vectorstore = await self._create_or_load_vectorstore_async(documents_to_add)

            if not self.vectorstore: 
                logger.error(f"[PID:{pid}] RAG_CLASS.setup: Fallimento Vectorstore. RAG non inizializzato.")
                self.is_initialized = False 
                return 

            logger.info(f"[PID:{pid}] RAG_CLASS.setup: Inizializzazione LLM '{self.config['LLM_MODEL_NAME']}'...")
            self.llm = ChatOpenAI(
                openai_api_key=self.config["OPENAI_API_KEY"],
                model_name=self.config["LLM_MODEL_NAME"],
                temperature=0.2 
            )
            logger.info(f"[PID:{pid}] RAG_CLASS.setup: LLM inizializzato.")

            logger.info(f"[PID:{pid}] RAG_CLASS.setup: Configurazione RetrievalQA chain...")
            retriever = self.vectorstore.as_retriever(search_kwargs={"k": self.config["RETRIEVER_K"]})
            prompt = PromptTemplate(
                template=self.config["PROMPT_TEMPLATE"],
                input_variables=["context", "question"]
            )
            chain_type_kwargs = {"prompt": prompt}
            self.qa_chain = RetrievalQA.from_chain_type(
                llm=self.llm, chain_type="stuff", retriever=retriever,
                chain_type_kwargs=chain_type_kwargs, return_source_documents=True 
            )
            logger.info(f"[PID:{pid}] RAG_CLASS.setup: RetrievalQA chain configurata.")
            self.is_initialized = True 
            logger.info(f"[PID:{pid}] RAG_CLASS.setup: OptimizedRAGSystem inizializzato. is_initialized: {self.is_initialized}")

        except Exception as e:
            logger.error(f"[PID:{pid}] RAG_CLASS.setup: Errore critico: {e}", exc_info=True)
            self.is_initialized = False
    
    @measure_performance_async("rag_document_loading_splitting")
    async def _load_and_split_documents_async(self) -> List[Document]:
        docs_path = self.config["DOCS_DIRECTORY"]
        pid = os.getpid()
        logger.info(f"[PID:{pid}] RAG_CLASS._load_split: Scansione documenti in '{docs_path}'...")
        all_langchain_documents = []
        
        supported_loaders = {
            ".txt": TextLoader, 
            ".md": UnstructuredMarkdownLoader, 
            ".docx": UnstructuredWordDocumentLoader,
        }

        if not os.path.exists(docs_path) or not os.path.isdir(docs_path):
            logger.warning(f"[PID:{pid}] RAG_CLASS._load_split: Directory documenti '{docs_path}' non trovata.")
            return []

        doc_files = [f for f in os.listdir(docs_path) if os.path.isfile(os.path.join(docs_path, f))]
        
        if not doc_files:
            logger.info(f"[PID:{pid}] RAG_CLASS._load_split: Nessun file in '{docs_path}'.")
            return []
        logger.info(f"[PID:{pid}] RAG_CLASS._load_split: Trovati {len(doc_files)} file da processare.")

        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.config["CHUNK_SIZE"],
            chunk_overlap=self.config["CHUNK_OVERLAP"]
        )

        for doc_file in doc_files:
            file_path = os.path.join(docs_path, doc_file)
            ext = os.path.splitext(doc_file)[1].lower()
            
            file_text_content = ""
            current_file_metadata = {
                "source": file_path, 
                "file_name": doc_file,
                "file_type": ext.replace(".", "").upper()
            }

            if ext == ".pdf":
                logger.debug(f"[PID:{pid}] RAG_CLASS._load_split: Parsing PDF: {file_path}")
                try:
                    pdf_text, images_data, extracted_pdf_metadata = await asyncio.to_thread(
                        parse_pdf_enhanced, file_path
                    )
                    file_text_content = pdf_text
                    current_file_metadata.update(extracted_pdf_metadata)
                    
                    if images_data and TESSERACT_AVAILABLE and TESSERACT_CONFIGURED:
                        logger.info(f"[PID:{pid}] RAG_CLASS._load_split: Trovate {len(images_data)} immagini in '{doc_file}'. Esecuzione OCR...")
                        ocr_texts_for_doc = []
                        
                        # Filtra immagini e limita il numero massimo per evitare tempi eccessivi
                        images_to_process = [img for img in images_data if len(img.get('image_bytes', b'')) >= 5000]
                        max_images = min(50, len(images_to_process))  # Massimo 50 immagini
                        
                        if len(images_to_process) > max_images:
                            logger.info(f"[PID:{pid}] RAG_CLASS._load_split: Limitato OCR a {max_images}/{len(images_to_process)} immagini per prestazioni")
                        
                        for idx, i_data in enumerate(images_to_process[:max_images]):
                            # OCR solo se la pagina non ha già molto testo
                            page_has_text = i_data.get('page_has_text', False)
                            if not page_has_text:
                                logger.debug(f"Esecuzione OCR su immagine {idx + 1}/{len(images_data)} dalla pagina {i_data['page_number']}")
                                ocr_text = await asyncio.to_thread(
                                    ocr_image, 
                                    i_data['image_bytes'], 
                                    language=self.config.get("TESSERACT_LANG", "ita")
                                )
                                if ocr_text:
                                    ocr_texts_for_doc.append(
                                        f"\n\n--- OCR Pagina {i_data['page_number']} (Immagine {i_data['image_index_on_page']+1}) ---\n"
                                        f"{ocr_text}\n"
                                        f"--- Fine OCR ---"
                                    )
                                    logger.debug(f"OCR completato, estratti {len(ocr_text)} caratteri")
                            else:
                                logger.debug(f"Saltato OCR per immagine a pagina {i_data['page_number']} (pagina ha già testo)")
                        
                        if ocr_texts_for_doc:
                            file_text_content += "\n\n" + "\n".join(ocr_texts_for_doc)
                            logger.info(f"[PID:{pid}] RAG_CLASS._load_split: Aggiunto testo OCR da {len(ocr_texts_for_doc)} immagini per '{doc_file}'.")
                    elif images_data and not (TESSERACT_AVAILABLE and TESSERACT_CONFIGURED):
                        logger.warning(f"[PID:{pid}] RAG_CLASS._load_split: {len(images_data)} immagini trovate ma OCR non disponibile")
                        
                except Exception as e:
                    logger.error(f"[PID:{pid}] RAG_CLASS._load_split: Errore PDF/OCR {file_path}: {e}", exc_info=True)
                    continue
            else:
                loader_class = supported_loaders.get(ext)
                if loader_class:
                    logger.debug(f"[PID:{pid}] RAG_CLASS._load_split: Caricamento {file_path} con {loader_class.__name__}")
                    try:
                        loader = loader_class(file_path)
                        loaded_docs_list = await asyncio.to_thread(loader.load) 
                        if loaded_docs_list:
                            file_text_content = "\n\n".join([d.page_content for d in loaded_docs_list if d.page_content])
                            for doc_obj in loaded_docs_list:
                                if doc_obj.metadata:
                                    current_file_metadata.update(doc_obj.metadata)
                    except Exception as e:
                        logger.error(f"[PID:{pid}] RAG_CLASS._load_split: Errore caricamento {file_path}: {e}", exc_info=True)
                        continue
                else:
                    logger.warning(f"[PID:{pid}] RAG_CLASS._load_split: No loader per '{ext}' ({doc_file}). Saltato.")
                    continue

            if file_text_content:
                normalized_content = file_text_content
                if self.nlp_processor:
                    logger.debug(f"[PID:{pid}] RAG_CLASS._load_split: Normalizzazione testo per '{doc_file}'...")
                    try:
                        normalized_content = await asyncio.to_thread(normalize_text, file_text_content, self.nlp_processor)
                        if not normalized_content:
                            logger.warning(f"[PID:{pid}] RAG_CLASS._load_split: Testo normalizzato vuoto per '{doc_file}', uso testo originale.")
                            normalized_content = file_text_content
                    except Exception as e_norm:
                         logger.error(f"[PID:{pid}] RAG_CLASS._load_split: Errore normalizzazione per '{doc_file}': {e_norm}. Uso testo originale.", exc_info=True)
                         normalized_content = file_text_content
                else:
                     logger.warning(f"[PID:{pid}] RAG_CLASS._load_split: Processore NLP non disponibile. Uso testo grezzo per '{doc_file}'.")
                
                langchain_doc = Document(page_content=normalized_content, metadata=current_file_metadata)
                split_docs = text_splitter.split_documents([langchain_doc])
                all_langchain_documents.extend(split_docs)
                logger.debug(f"[PID:{pid}] RAG_CLASS._load_split: '{doc_file}' processato e splittato in {len(split_docs)} chunks.")
                if len(split_docs) > 0:
                    logger.debug(f"Metadati per il primo chunk di '{doc_file}': {split_docs[0].metadata}")
            else:
                logger.warning(f"[PID:{pid}] RAG_CLASS._load_split: Nessun contenuto testuale per '{doc_file}'.")

        logger.info(f"[PID:{pid}] RAG_CLASS._load_split: Processati {len(doc_files)} file, risultanti in {len(all_langchain_documents)} chunks totali.")
        return all_langchain_documents

    @measure_performance_async("rag_vectorstore_creation_loading")
    async def _create_or_load_vectorstore_async(self, documents_for_vectorstore: Optional[List[Document]] = None):
        pid = os.getpid()
        logger.info(f"[PID:{pid}] RAG_CLASS._vectorstore: Controllo o creazione vectorstore ChromaDB in: '{self.chroma_persist_directory}' con collezione '{self.collection_name}'")
        vectorstore_instance: Optional[Chroma] = None
        try:
            chroma_client = await asyncio.to_thread(
                chromadb.PersistentClient, 
                path=self.chroma_persist_directory,
                settings=chromadb.Settings(anonymized_telemetry=False, allow_reset=True) 
            )
            logger.info(f"[PID:{pid}] RAG_CLASS._vectorstore: ChromaDB PersistentClient creato/caricato.")
            collection_exists = False
            try:
                await asyncio.to_thread(chroma_client.get_collection, name=self.collection_name)
                collection_exists = True
                logger.info(f"[PID:{pid}] RAG_CLASS._vectorstore: Collezione '{self.collection_name}' esistente.")
            except Exception:
                logger.info(f"[PID:{pid}] RAG_CLASS._vectorstore: Collezione '{self.collection_name}' non trovata.")

            if documents_for_vectorstore and len(documents_for_vectorstore) > 0:
                logger.info(f"[PID:{pid}] RAG_CLASS._vectorstore: Creazione/Aggiornamento vectorstore con {len(documents_for_vectorstore)} chunks...")
                if collection_exists:
                     logger.warning(f"[PID:{pid}] RAG_CLASS._vectorstore: Collezione '{self.collection_name}' esistente. Verrà sovrascritta/aggiornata.")
                vectorstore_instance = await asyncio.to_thread(
                    Chroma.from_documents, 
                    client=chroma_client, documents=documents_for_vectorstore,
                    embedding=self.embeddings, collection_name=self.collection_name,
                    persist_directory=self.chroma_persist_directory
                )
                logger.info(f"[PID:{pid}] RAG_CLASS._vectorstore: Vectorstore creato/aggiornato.")
            elif collection_exists:
                logger.info(f"[PID:{pid}] RAG_CLASS._vectorstore: Nessun nuovo documento. Caricamento vectorstore esistente.")
                vectorstore_instance = await asyncio.to_thread(
                    Chroma, client=chroma_client, collection_name=self.collection_name,
                    embedding_function=self.embeddings, persist_directory=self.chroma_persist_directory
                )
                if vectorstore_instance:
                    count = await asyncio.to_thread(vectorstore_instance._collection.count)
                    logger.info(f"[PID:{pid}] RAG_CLASS._vectorstore: Vectorstore caricato. Collezione '{self.collection_name}' ha {count} elementi.")
                    if count == 0: logger.warning(f"[PID:{pid}] RAG_CLASS._vectorstore: Collezione '{self.collection_name}' è vuota.")
                else: logger.error(f"[PID:{pid}] RAG_CLASS._vectorstore: Fallimento caricamento Chroma esistente.")
            else:
                 logger.error(f"[PID:{pid}] RAG_CLASS._vectorstore: Nessun documento e collezione non esistente. Vectorstore non creato.")
                 return None
            if vectorstore_instance: logger.info(f"[PID:{pid}] RAG_CLASS._vectorstore: Vectorstore ChromaDB inizializzato.")
            else: logger.error(f"[PID:{pid}] RAG_CLASS._vectorstore: Fallimento ottenimento istanza Vectorstore ChromaDB.")
            return vectorstore_instance
        except Exception as e:
            logger.error(f"[PID:{pid}] RAG_CLASS._vectorstore: Errore CRITICO vectorstore: {e}", exc_info=True)
            return None
    
    @measure_performance_async("rag_get_response")
    async def get_response_async(self, query: str) -> Dict[str, Any]:
        default_response = {"response": "Non sono riuscito a trovare una risposta.", "sources": []}
        pid = os.getpid()
        if self.use_mock:
            logger.info(f"[PID:{pid}] RAG MOCK: query '{query}'")
            mock_text = f"Risposta MOCK per '{query}'."
            await rag_smart_cache.set(query, {"response": mock_text, "sources": [{"source": "mock.txt"}]})
            return {"response": mock_text, "sources": [{"source": "mock.txt"}]}
        if not self.is_initialized or not self.qa_chain:
            logger.error(f"[PID:{pid}] RAG non inizializzato. Query: '{query}'")
            return default_response
        cached_response = await rag_smart_cache.get(query)
        if cached_response:
            logger.info(f"[PID:{pid}] Cache HIT per query: '{query}'")
            performance_monitor.record_metric_entry("rag_cache_hits_counter", 0, True) 
            return cached_response
        performance_monitor.record_metric_entry("rag_cache_misses_counter", 0, True)
        logger.info(f"[PID:{pid}] Cache MISS. Esecuzione QA per: '{query}'")
        try:
            result = await self.qa_chain.ainvoke({"query": query}) if hasattr(self.qa_chain, "ainvoke") else await asyncio.to_thread(self.qa_chain, {"query": query})
            answer = result.get("result", "Nessuna risposta dalla catena QA.")
            sources_metadata = [{"source": doc.metadata.get("source", "Sconosciuto"), 
                                 "file_name": doc.metadata.get("file_name", "N/D"),
                                 "title": doc.metadata.get("title", "N/D"),
                                 "page_count": doc.metadata.get("page_count", "N/D"),
                                 "content_preview": doc.page_content[:200] + "..."} 
                                for doc in result.get("source_documents", [])]
            response_payload = {"response": answer, "sources": sources_metadata}
            await rag_smart_cache.set(query, response_payload) 
            return response_payload
        except Exception as e:
            logger.error(f"[PID:{pid}] Errore QA chain per '{query}': {e}", exc_info=True)
            return default_response

    async def get_system_stats(self) -> Dict[str, Any]:
        cache_stats = await rag_smart_cache.get_cache_stats() if rag_smart_cache and hasattr(rag_smart_cache, 'get_cache_stats') else {"error": "Cache stats non disponibili"}
        stats = {
            "base_system": {
                "is_initialized": self.is_initialized, 
                "use_mock": self.use_mock,
                "llm_model": self.config["LLM_MODEL_NAME"] if not self.use_mock and self.llm else "N/A",
                "embeddings_model": self.config["EMBEDDINGS_MODEL_NAME"] if not self.use_mock and self.embeddings else "N/A",
                "docs_directory": self.config["DOCS_DIRECTORY"],
                "chroma_persist_directory": self.chroma_persist_directory,
                "collection_name": self.collection_name,
                "ocr_available": TESSERACT_AVAILABLE and TESSERACT_CONFIGURED,
                "ocr_language": self.config.get("TESSERACT_LANG", "ita") if (TESSERACT_AVAILABLE and TESSERACT_CONFIGURED) else "N/A"
            },
            "cache": cache_stats, 
            "vectorstore": {"status": "Non disponibile", "collection_count": 0}
        }
        if self.is_initialized and self.vectorstore and not self.use_mock:
            try:
                count = 0
                if hasattr(self.vectorstore, '_collection') and self.vectorstore._collection:
                    count = await asyncio.to_thread(self.vectorstore._collection.count)
                elif hasattr(self.vectorstore, 'client'):
                    collection = await asyncio.to_thread(self.vectorstore.client.get_collection, name=self.collection_name)
                    count = await asyncio.to_thread(collection.count)
                stats["vectorstore"]["status"] = "Operativo"
                stats["vectorstore"]["collection_count"] = count
            except Exception as e:
                logger.warning(f"Impossibile ottenere conteggio vectorstore: {e}", exc_info=False)
                stats["vectorstore"]["status"] = f"Errore stats: {str(e)[:50]}"
        elif self.use_mock:
            stats["vectorstore"]["status"] = "Mock"
        stats["performance"] = performance_monitor.get_metrics_summary(["rag_get_response", "rag_cache_hits_counter", "rag_cache_misses_counter" ])
        return {"stats": stats}

    async def force_clear_all_cache(self):
        logger.info("Pulizia completa cache RAG...")
        if rag_smart_cache and hasattr(rag_smart_cache, 'clear_all_cache'):
            await rag_smart_cache.clear_all_cache()
            logger.info("SmartCache RAG pulita.")
        else:
            logger.warning("Metodo clear_all_cache non trovato su rag_smart_cache.")

async def init_rag_system() -> Optional[OptimizedRAGSystem]:
    instance = OptimizedRAGSystem() 
    pid = os.getpid()
    logger.info(f"[PID:{pid}] RAG_INIT: Creata istanza OptimizedRAGSystem id={id(instance)}")
    await instance.setup_rag_system_async()
    if not instance.is_initialized:
        logger.error(f"[PID:{pid}] RAG_INIT: Fallimento inizializzazione RAG id={id(instance)}. Restituisco istanza non inizializzata.")
    else:
        logger.info(f"[PID:{pid}] RAG_INIT: RAG inizializzato con successo id={id(instance)}.")
    return instance

# Test rapido all'importazione
if TESSERACT_AVAILABLE and TESSERACT_CONFIGURED:
    logger.info("Modulo OCR pronto per l'uso")
else:
    logger.warning("Modulo OCR non disponibile - verificare installazione Tesseract e PyMuPDF")