"""
Module d'ingestion des PDFs et prétraitement des documents EMSI
"""

import PyPDF2
import logging
from typing import List, Dict, Tuple
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PDFIngestionManager:
    """
    Gestionnaire pour l'ingestion et l'extraction de texte depuis les PDFs EMSI.
    """

    def __init__(self):
        """Initialise le gestionnaire d'ingestion PDF."""
        logger.info("📄 Initialisation du gestionnaire d'ingestion PDF")

    @staticmethod
    def extract_text_from_pdf(pdf_path: str) -> Dict[str, any]:
        """
        Extrait le texte d'un fichier PDF.
        
        Args:
            pdf_path: Chemin vers le fichier PDF
            
        Returns:
            Dictionnaire contenant le texte et les métadonnées
        """
        try:
            logger.info(f"📖 Lecture du PDF: {os.path.basename(pdf_path)}")
            
            with open(pdf_path, 'rb') as pdf_file:
                pdf_reader = PyPDF2.PdfReader(pdf_file)
                
                num_pages = len(pdf_reader.pages)
                logger.info(f"   - Nombre de pages: {num_pages}")
                
                text_content = ""
                page_content = {}
                
                # Extraire le texte page par page
                for page_num, page in enumerate(pdf_reader.pages, 1):
                    page_text = page.extract_text()
                    text_content += page_text + "\n"
                    page_content[page_num] = page_text
                
                logger.info(f"✅ Extraction complète: {len(text_content)} caractères")
                
                return {
                    "text": text_content,
                    "pages": page_content,
                    "num_pages": num_pages,
                    "source": os.path.basename(pdf_path),
                    "path": pdf_path
                }
                
        except Exception as e:
            logger.error(f"❌ Erreur lors de la lecture du PDF: {e}")
            raise

    @staticmethod
    def extract_from_multiple_pdfs(pdf_directory: str) -> List[Dict]:
        """
        Extrait le texte de tous les PDFs dans un répertoire.
        
        Args:
            pdf_directory: Chemin vers le répertoire contenant les PDFs
            
        Returns:
            Liste des documents extraits
        """
        documents = []
        
        try:
            logger.info(f"📂 Scan du répertoire: {pdf_directory}")
            
            if not os.path.exists(pdf_directory):
                logger.error(f"❌ Répertoire non trouvé: {pdf_directory}")
                return documents
            
            pdf_files = [f for f in os.listdir(pdf_directory) if f.endswith('.pdf')]
            logger.info(f"   - {len(pdf_files)} fichiers PDF trouvés")
            
            for pdf_file in pdf_files:
                pdf_path = os.path.join(pdf_directory, pdf_file)
                try:
                    doc = PDFIngestionManager.extract_text_from_pdf(pdf_path)
                    documents.append(doc)
                except Exception as e:
                    logger.warning(f"⚠️ Impossible de lire {pdf_file}: {e}")
                    continue
            
            logger.info(f"✅ {len(documents)} documents extraits avec succès")
            return documents
            
        except Exception as e:
            logger.error(f"❌ Erreur lors de l'extraction: {e}")
            raise

    @staticmethod
    def clean_text(text: str) -> str:
        """
        Nettoie le texte extrait.
        
        Args:
            text: Texte brut
            
        Returns:
            Texte nettoyé
        """
        import re
        
        # Supprimer les espaces multiples
        text = re.sub(r'\s+', ' ', text)
        
        # Supprimer les caractères spéciaux inutiles
        text = re.sub(r'[^\w\s\.\,\!\?\:;()éèêêàâäùûüôöñ-]', '', text)
        
        return text.strip()
