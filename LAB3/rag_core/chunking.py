"""
Module de chunking intelligent - Segmentation des documents en chunks optimisés
"""

import logging
from typing import List, Dict, Tuple
import re

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class IntelligentChunker:
    """
    Segmente intelligemment les documents en chunks cohérents
    en respectant les limites de sections et paragraphes.
    """

    def __init__(
        self,
        chunk_size: int = 500,
        chunk_overlap: int = 100,
        separator: str = "\n\n"
    ):
        """
        Initialise le chunker.
        
        Args:
            chunk_size: Taille cible des chunks en caractères
            chunk_overlap: Chevauchement entre chunks pour maintenir la cohérence
            separator: Séparateur principal (par défaut: paragraphes)
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.separator = separator
        logger.info(f"🔪 ChunkerIntelligent: size={chunk_size}, overlap={chunk_overlap}")

    def chunk_text(self, text: str, metadata: Dict = None) -> List[Dict]:
        """
        Divise un texte en chunks intelligents.
        
        Args:
            text: Texte à découper
            metadata: Métadonnées à attacher à chaque chunk
            
        Returns:
            Liste de chunks avec métadonnées
        """
        if metadata is None:
            metadata = {}

        # Étape 1: Découper par paragraphes
        paragraphs = text.split(self.separator)
        
        # Étape 2: Fusion des paragraphes en chunks cohérents
        chunks = []
        current_chunk = ""
        
        for paragraph in paragraphs:
            # Si le paragraphe seul dépasse chunk_size, le diviser davantage
            if len(paragraph) > self.chunk_size:
                paragraph = self._split_large_paragraph(paragraph)
            else:
                paragraph = [paragraph]
            
            for para_part in paragraph:
                # Vérifier si ajouter ce paragraphe dépasserait la limite
                if len(current_chunk) + len(para_part) > self.chunk_size:
                    if current_chunk:  # Sauvegarder le chunk actuel
                        chunks.append(current_chunk.strip())
                    
                    # Commencer un nouveau chunk avec chevauchement
                    current_chunk = current_chunk[-self.chunk_overlap:] + "\n" + para_part
                else:
                    current_chunk += "\n" + para_part if current_chunk else para_part
        
        # Ajouter le dernier chunk
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        logger.info(f"✅ Texte découpé en {len(chunks)} chunks")
        
        # Étape 3: Attacher les métadonnées
        result_chunks = []
        for i, chunk in enumerate(chunks):
            result_chunks.append({
                "content": chunk,
                "chunk_id": i,
                "char_count": len(chunk),
                "word_count": len(chunk.split()),
                **metadata
            })
        
        return result_chunks

    def _split_large_paragraph(self, paragraph: str) -> List[str]:
        """
        Divise un paragraphe trop grand en sous-segments.
        
        Args:
            paragraph: Paragraphe à diviser
            
        Returns:
            Liste de segments
        """
        # Chercher les points finaux de phrases
        sentences = re.split(r'(?<=[.!?])\s+', paragraph)
        
        segments = []
        current_segment = ""
        
        for sentence in sentences:
            if len(current_segment) + len(sentence) > self.chunk_size:
                if current_segment:
                    segments.append(current_segment.strip())
                current_segment = sentence
            else:
                current_segment += " " + sentence if current_segment else sentence
        
        if current_segment:
            segments.append(current_segment.strip())
        
        return segments

    def chunk_documents(
        self,
        documents: List[Dict]
    ) -> List[Dict]:
        """
        Applique le chunking à une liste de documents.
        
        Args:
            documents: Liste de documents avec clé 'text' ou 'content'
            
        Returns:
            Liste de chunks avec métadonnées enrichies
        """
        all_chunks = []
        
        for doc in documents:
            text = doc.get('text') or doc.get('content', '')
            
            # Créer les métadonnées pour ce document
            doc_metadata = {
                k: v for k, v in doc.items() 
                if k not in ['text', 'content']
            }
            
            # Chunker le texte
            chunks = self.chunk_text(text, doc_metadata)
            all_chunks.extend(chunks)
        
        logger.info(f"✅ {len(all_chunks)} chunks créés au total")
        return all_chunks

    @staticmethod
    def extract_key_phrases(text: str, top_k: int = 5) -> List[str]:
        """
        Extrait les phrases-clés d'un texte.
        
        Args:
            text: Texte d'entrée
            top_k: Nombre de phrases-clés à extraire
            
        Returns:
            Liste de phrases-clés
        """
        # Extraire les capitalisés et les mots technique
        words = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', text)
        
        # Compter les occurrences
        from collections import Counter
        freq = Counter(words)
        
        # Retourner les plus fréquents
        return [phrase for phrase, count in freq.most_common(top_k)]
