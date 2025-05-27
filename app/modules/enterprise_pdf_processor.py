# app/modules/enterprise_pdf_processor.py
"""
Enterprise PDF Processing System
Handles ALL types of PDFs: text-based, scanned, complex layouts
Multi-library approach with OCR fallback
"""

import asyncio
import aiosqlite
import json
import numpy as np
import openai
import os
import logging
import time
import hashlib
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from pathlib import Path
import io
import base64

# Multi-library PDF support with comprehensive fallbacks
PDF_LIBRARIES = {}
OCR_AVAILABLE = False

# Try all PDF processing libraries
try:
    import fitz  # pymupdf - most robust
    PDF_LIBRARIES["fitz"] = fitz
    print("✅ PyMuPDF (fitz) disponibile - PDF processing robusto")
except ImportError:
    print("⚠️  PyMuPDF non disponibile")

try:
    import pdfplumber
    PDF_LIBRARIES["pdfplumber"] = pdfplumber
    print("✅ pdfplumber disponibile - layout-aware processing")
except ImportError:
    print("⚠️  pdfplumber non disponibile")

try:
    import PyPDF2
    PDF_LIBRARIES["PyPDF2"] = PyPDF2
    print("✅ PyPDF2 disponibile - fast text extraction")
except ImportError:
    print("⚠️  PyPDF2 non disponibile")

try:
    import pypdf
    PDF_LIBRARIES["pypdf"] = pypdf
    print("✅ pypdf disponibile - modern PyPDF2 alternative")
except ImportError:
    print("⚠️  pypdf non disponibile")

# OCR capabilities for scanned PDFs
try:
    import pytesseract
    from PIL import Image
    OCR_AVAILABLE = True
    print("✅ OCR disponibile - Tesseract + PIL")
    
    # Try to configure Tesseract path
    import platform
    if platform.system() == "Windows":
        tesseract_paths = [
            r'C:\Program Files\Tesseract-OCR\tesseract.exe',
            r'C:\Program Files (x86)\Tesseract-OCR\tesseract.exe'
        ]
        for path in tesseract_paths:
            if os.path.exists(path):
                pytesseract.pytesseract.tesseract_cmd = path
                print(f"✅ Tesseract configurato: {path}")
                break
    
except ImportError:
    print("⚠️  OCR non disponibile - pytesseract/PIL mancanti")

# Setup logging
logger = logging.getLogger(__name__)

@dataclass
class PDFProcessingResult:
    """Risultato elaborazione PDF"""
    success: bool
    text: str
    pages_processed: int
    method_used: str
    ocr_pages: int = 0
    error_message: str = ""
    metadata: Dict[str, Any] = None

class EnterprisePDFProcessor:
    """
    Enterprise-grade PDF processor
    Handles all PDF types with multiple fallback strategies
    """
    
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.processing_stats = {
            "total_pdfs": 0,
            "successful_pdfs": 0,
            "failed_pdfs": 0,
            "ocr_pdfs": 0,
            "methods_used": {}
        }
    
    async def process_pdf_comprehensive(self, file_path: str) -> PDFProcessingResult:
        """
        Comprehensive PDF processing with multiple strategies
        
        Strategy order:
        1. PyMuPDF (fitz) - Most robust for complex PDFs
        2. pdfplumber - Best for layout-aware extraction
        3. PyPDF2/pypdf - Fast for simple text PDFs
        4. OCR fallback - For scanned/image PDFs
        """
        
        self.processing_stats["total_pdfs"] += 1
        logger.info(f"🔍 Processing PDF: {file_path}")
        
        # Strategy 1: PyMuPDF (fitz) - Most comprehensive
        if "fitz" in PDF_LIBRARIES:
            result = await self._process_with_fitz(file_path)
            if result.success and result.text.strip():
                self.processing_stats["successful_pdfs"] += 1
                self.processing_stats["methods_used"]["fitz"] = self.processing_stats["methods_used"].get("fitz", 0) + 1
                return result
        
        # Strategy 2: pdfplumber - Layout-aware
        if "pdfplumber" in PDF_LIBRARIES:
            result = await self._process_with_pdfplumber(file_path)
            if result.success and result.text.strip():
                self.processing_stats["successful_pdfs"] += 1
                self.processing_stats["methods_used"]["pdfplumber"] = self.processing_stats["methods_used"].get("pdfplumber", 0) + 1
                return result
        
        # Strategy 3: PyPDF2/pypdf - Fast extraction
        for lib_name in ["PyPDF2", "pypdf"]:
            if lib_name in PDF_LIBRARIES:
                result = await self._process_with_pypdf(file_path, lib_name)
                if result.success and result.text.strip():
                    self.processing_stats["successful_pdfs"] += 1
                    self.processing_stats["methods_used"][lib_name] = self.processing_stats["methods_used"].get(lib_name, 0) + 1
                    return result
        
        # Strategy 4: OCR fallback for scanned PDFs
        if OCR_AVAILABLE and "fitz" in PDF_LIBRARIES:
            logger.info(f"📸 Tentativo OCR per PDF: {file_path}")
            result = await self._process_with_ocr(file_path)
            if result.success and result.text.strip():
                self.processing_stats["successful_pdfs"] += 1
                self.processing_stats["ocr_pdfs"] += 1
                self.processing_stats["methods_used"]["ocr"] = self.processing_stats["methods_used"].get("ocr", 0) + 1
                return result
        
        # All strategies failed
        self.processing_stats["failed_pdfs"] += 1
        logger.error(f"❌ Tutte le strategie fallite per: {file_path}")
        return PDFProcessingResult(
            success=False,
            text="",
            pages_processed=0,
            method_used="none",
            error_message="Tutte le strategie di estrazione fallite"
        )
    
    async def _process_with_fitz(self, file_path: str) -> PDFProcessingResult:
        """Process PDF with PyMuPDF (fitz) - most robust"""
        try:
            fitz = PDF_LIBRARIES["fitz"]
            doc = fitz.open(file_path)
            
            text = ""
            pages_processed = 0
            total_pages = len(doc)
            
            for page_num in range(total_pages):
                try:
                    page = doc.load_page(page_num)
                    
                    # Try multiple text extraction methods
                    page_text = page.get_text()
                    
                    # If no text, try different extraction modes
                    if not page_text.strip():
                        page_text = page.get_text("text")
                    
                    if not page_text.strip():
                        try:
                            page_text_dict = page.get_text("dict")
                            if isinstance(page_text_dict, dict):
                                page_text = self._extract_text_from_dict(page_text_dict)
                        except Exception as dict_e:
                            logger.debug(f"Dict extraction failed for page {page_num}: {dict_e}")
                    
                    if page_text and page_text.strip():
                        text += page_text + "\n"
                        pages_processed += 1
                    
                except Exception as page_e:
                    logger.warning(f"Error processing page {page_num}: {page_e}")
                    continue
            
            doc.close()
            
            return PDFProcessingResult(
                success=bool(text.strip()),
                text=text,
                pages_processed=pages_processed,
                method_used="fitz",
                metadata={"total_pages": total_pages}
            )
            
        except Exception as e:
            logger.error(f"Errore fitz processing: {e}")
            return PDFProcessingResult(
                success=False,
                text="",
                pages_processed=0,
                method_used="fitz",
                error_message=str(e)
            )
    
    async def _process_with_pdfplumber(self, file_path: str) -> PDFProcessingResult:
        """Process PDF with pdfplumber - layout-aware"""
        try:
            pdfplumber = PDF_LIBRARIES["pdfplumber"]
            
            text = ""
            pages_processed = 0
            
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    # Try different extraction strategies
                    page_text = page.extract_text()
                    
                    # If no text, try with different settings
                    if not page_text or not page_text.strip():
                        page_text = page.extract_text(
                            x_tolerance=3,
                            y_tolerance=3,
                            layout=True
                        )
                    
                    # Try extracting from tables
                    if not page_text or not page_text.strip():
                        tables = page.extract_tables()
                        if tables:
                            table_text = ""
                            for table in tables:
                                for row in table:
                                    if row:
                                        table_text += " ".join([cell or "" for cell in row]) + "\n"
                            page_text = table_text
                    
                    if page_text and page_text.strip():
                        text += page_text + "\n"
                        pages_processed += 1
            
            return PDFProcessingResult(
                success=bool(text.strip()),
                text=text,
                pages_processed=pages_processed,
                method_used="pdfplumber",
                metadata={"total_pages": len(pdf.pages)}
            )
            
        except Exception as e:
            logger.error(f"Errore pdfplumber processing: {e}")
            return PDFProcessingResult(
                success=False,
                text="",
                pages_processed=0,
                method_used="pdfplumber",
                error_message=str(e)
            )
    
    async def _process_with_pypdf(self, file_path: str, lib_name: str) -> PDFProcessingResult:
        """Process PDF with PyPDF2 or pypdf"""
        try:
            pdf_lib = PDF_LIBRARIES[lib_name]
            
            text = ""
            pages_processed = 0
            
            with open(file_path, 'rb') as file:
                pdf_reader = pdf_lib.PdfReader(file)
                
                for page in pdf_reader.pages:
                    page_text = page.extract_text()
                    
                    if page_text and page_text.strip():
                        text += page_text + "\n"
                        pages_processed += 1
            
            return PDFProcessingResult(
                success=bool(text.strip()),
                text=text,
                pages_processed=pages_processed,
                method_used=lib_name,
                metadata={"total_pages": len(pdf_reader.pages)}
            )
            
        except Exception as e:
            logger.error(f"Errore {lib_name} processing: {e}")
            return PDFProcessingResult(
                success=False,
                text="",
                pages_processed=0,
                method_used=lib_name,
                error_message=str(e)
            )
    
    async def _process_with_ocr(self, file_path: str) -> PDFProcessingResult:
        """Process PDF with OCR for scanned documents"""
        if not OCR_AVAILABLE or "fitz" not in PDF_LIBRARIES:
            return PDFProcessingResult(
                success=False,
                text="",
                pages_processed=0,
                method_used="ocr",
                error_message="OCR non disponibile"
            )
        
        try:
            fitz = PDF_LIBRARIES["fitz"]
            doc = fitz.open(file_path)
            
            text = ""
            pages_processed = 0
            ocr_pages = 0
            total_pages = len(doc)
            
            for page_num in range(total_pages):
                try:
                    page = doc.load_page(page_num)
                    
                    # Convert page to image
                    mat = fitz.Matrix(2.0, 2.0)  # 2x resolution for better OCR
                    pix = page.get_pixmap(matrix=mat)
                    img_data = pix.tobytes("png")
                    
                    # OCR the image
                    image = Image.open(io.BytesIO(img_data))
                    
                    # Try multiple OCR configurations
                    ocr_text = ""
                    
                    # Try with different language configurations
                    for lang_config in ['ita+eng', 'eng', None]:
                        try:
                            if lang_config:
                                ocr_text = pytesseract.image_to_string(image, lang=lang_config)
                            else:
                                ocr_text = pytesseract.image_to_string(image)
                            
                            if ocr_text and ocr_text.strip():
                                break  # Success, exit lang loop
                                
                        except Exception as ocr_e:
                            logger.debug(f"OCR tentativo {lang_config} fallito: {ocr_e}")
                            continue
                    
                    if ocr_text and ocr_text.strip():
                        text += f"\n--- Pagina {page_num+1} (OCR) ---\n{ocr_text}\n"
                        pages_processed += 1
                        ocr_pages += 1
                    
                    pix = None  # Free memory
                    
                except Exception as page_e:
                    logger.warning(f"OCR fallito per pagina {page_num+1}: {page_e}")
                    continue
            
            doc.close()
            
            return PDFProcessingResult(
                success=bool(text.strip()),
                text=text,
                pages_processed=pages_processed,
                method_used="ocr",
                ocr_pages=ocr_pages,
                metadata={"total_pages": total_pages, "ocr_pages": ocr_pages}
            )
            
        except Exception as e:
            logger.error(f"Errore OCR processing: {e}")
            return PDFProcessingResult(
                success=False,
                text="",
                pages_processed=0,
                method_used="ocr",
                error_message=str(e)
            )
    
    def _extract_text_from_dict(self, text_dict: Dict) -> str:
        """Extract text from fitz text dictionary format"""
        text = ""
        if "blocks" in text_dict:
            for block in text_dict["blocks"]:
                if "lines" in block:
                    for line in block["lines"]:
                        if "spans" in line:
                            for span in line["spans"]:
                                if "text" in span:
                                    text += span["text"] + " "
                    text += "\n"
        return text
    
    def get_processing_stats(self) -> Dict[str, Any]:
        """Get processing statistics"""
        success_rate = (self.processing_stats["successful_pdfs"] / 
                       max(self.processing_stats["total_pdfs"], 1)) * 100
        
        return {
            **self.processing_stats,
            "success_rate_percent": round(success_rate, 2),
            "available_libraries": list(PDF_LIBRARIES.keys()),
            "ocr_available": OCR_AVAILABLE
        }


# Integration with existing document processor
class EnhancedDocumentProcessor:
    """Enhanced document processor with enterprise PDF support"""
    
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.pdf_processor = EnterprisePDFProcessor(chunk_size, chunk_overlap)
    
    async def process_file(self, file_path: str) -> List['Document']:
        """Process any file type with enhanced PDF support"""
        path = Path(file_path)
        
        if not path.exists():
            logger.warning(f"File non trovato: {file_path}")
            return []
        
        try:
            text = ""
            processing_metadata = {}
            
            if path.suffix.lower() == '.pdf':
                # Use enterprise PDF processor
                pdf_result = await self.pdf_processor.process_pdf_comprehensive(file_path)
                
                if pdf_result.success:
                    text = pdf_result.text
                    processing_metadata = {
                        "pdf_processing_method": pdf_result.method_used,
                        "pdf_pages_processed": pdf_result.pages_processed,
                        "pdf_ocr_pages": pdf_result.ocr_pages,
                        "pdf_metadata": pdf_result.metadata or {}
                    }
                    logger.info(f"✅ PDF processed with {pdf_result.method_used}: {len(text)} chars")
                else:
                    logger.error(f"❌ PDF processing failed: {pdf_result.error_message}")
                    return []
                    
            elif path.suffix.lower() in ['.txt', '.md']:
                text = await self._extract_text_file(file_path)
            else:
                logger.warning(f"Tipo file non supportato: {path.suffix}")
                return []
            
            if not text.strip():
                logger.warning(f"File vuoto: {file_path}")
                return []
            
            # Chunk del testo
            chunks = self._chunk_text(text)
            
            # Crea documenti
            documents = []
            for i, chunk in enumerate(chunks):
                from app.modules.rag_system import Document  # Import from existing module
                doc = Document(
                    id=f"{path.stem}_{i}",
                    content=self._clean_text(chunk),
                    metadata={
                        "source_file": path.name,
                        "chunk_index": i,
                        "total_chunks": len(chunks),
                        "file_path": str(path),
                        **processing_metadata
                    }
                )
                documents.append(doc)
            
            logger.info(f"✅ Processato {file_path}: {len(documents)} chunks")
            return documents
            
        except Exception as e:
            logger.error(f"Errore processando {file_path}: {e}")
            return []
    
    async def _extract_text_file(self, file_path: str) -> str:
        """Estrae testo da file di testo"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except UnicodeDecodeError:
            with open(file_path, 'r', encoding='latin-1') as f:
                return f.read()
    
    def _chunk_text(self, text: str) -> List[str]:
        """Divide il testo in chunks con overlap"""
        if len(text) <= self.chunk_size:
            return [text]
        
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + self.chunk_size
            
            if end < len(text):
                boundary = max(
                    text.rfind(' ', start, end),
                    text.rfind('.', start, end),
                    text.rfind('\n', start, end)
                )
                if boundary > start:
                    end = boundary + 1
            
            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)
            
            start = end - self.chunk_overlap
            if start >= len(text):
                break
        
        return chunks
    
    def _clean_text(self, text: str) -> str:
        """Pulisce e normalizza il testo"""
        text = ' '.join(text.split())
        text = ''.join(char for char in text if ord(char) >= 32 or char in '\n\t')
        return text.strip()
    
    def get_processing_stats(self) -> Dict[str, Any]:
        """Get comprehensive processing statistics"""
        return self.pdf_processor.get_processing_stats()