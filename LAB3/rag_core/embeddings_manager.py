"""
Module de gestion des embeddings - Utilise sentence-transformers pour une qualité optimale
OPTIMISÉ: Lazy Loading pour éviter le blocage au démarrage
"""

from typing import List, Union, Optional
import numpy as np
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EmbeddingsManager:
    """
    Gestionnaire des embeddings avec LAZY LOADING.
    Le modèle n'est chargé qu'au premier appel (évite blocage démarrage).
    """

    def __init__(self, model_name: str = "sentence-transformers/distiluse-base-multilingual-cased-v2"):
        """
        Initialise le gestionnaire (sans charger le modèle immédiatement).
        
        Args:
            model_name: Modèle de sentence-transformers à utiliser
        """
        self.model_name = model_name
        self._model: Optional[any] = None
        self._embedding_dim: Optional[int] = None
        logger.info(f"🎯 EmbeddingsManager créé (chargement différé: {model_name})")

    def _ensure_model_loaded(self):
        """Charge le modèle seulement si nécessaire (lazy loading)."""
        if self._model is None:
            try:
                from sentence_transformers import SentenceTransformer
                logger.info(f"🔄 Chargement lazy du modèle: {self.model_name}")
                self._model = SentenceTransformer(self.model_name)
                self._embedding_dim = self._model.get_sentence_embedding_dimension()
                logger.info(f"✅ Modèle chargé (dim: {self._embedding_dim})")
            except Exception as e:
                logger.error(f"❌ Erreur chargement modèle: {e}")
                raise

    @property
    def model(self):
        """Accès au modèle (charge automatiquement si besoin)."""
        self._ensure_model_loaded()
        return self._model

    @property
    def embedding_dim(self):
        """Dimension des embeddings (charge le modèle si nécessaire)."""
        self._ensure_model_loaded()
        return self._embedding_dim

    def embed_text(self, text: Union[str, List[str]]) -> np.ndarray:
        """
        Génère les embeddings pour un texte ou une liste de textes.
        
        Args:
            text: Texte ou liste de textes à encoder
            
        Returns:
            Embeddings numpy array de forme (n, embedding_dim)
        """
        try:
            if isinstance(text, str):
                text = [text]
            
            embeddings = self.model.encode(text, show_progress_bar=False)
            return embeddings
        except Exception as e:
            logger.error(f"❌ Erreur lors de l'encodage: {e}")
            raise

    def embed_query(self, query: str) -> np.ndarray:
        """
        Génère l'embedding d'une requête de recherche.
        
        Args:
            query: La requête
            
        Returns:
            Embedding numpy array
        """
        return self.embed_text(query)

    def embed_documents(self, documents: List[str]) -> List[np.ndarray]:
        """
        Génère les embeddings pour une liste de documents.
        
        Args:
            documents: Liste de documents texte
            
        Returns:
            Liste d'embeddings
        """
        embeddings = self.embed_text(documents)
        return [emb for emb in embeddings]

    def similarity_search(self, query: str, candidates: List[str], top_k: int = 5) -> List[tuple]:
        """
        Recherche les documents les plus similaires à une requête.
        
        Args:
            query: Requête de recherche
            candidates: Liste des documents candidats
            top_k: Nombre de résultats à retourner
            
        Returns:
            Liste de (document, score) triée par score décroissant
        """
        query_embedding = self.embed_query(query)
        candidate_embeddings = self.embed_documents(candidates)
        
        # Calcul des similarités cosinus
        from sklearn.metrics.pairwise import cosine_similarity
        similarities = cosine_similarity([query_embedding], candidate_embeddings)[0]
        
        # Tri et sélection top-k
        top_indices = np.argsort(similarities)[::-1][:top_k]
        
        return [(candidates[i], float(similarities[i])) for i in top_indices]
