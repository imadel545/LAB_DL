"""
Module de gestion de ChromaDB - Stockage et indexation des vecteurs
MISE À JOUR: Configuration ChromaDB moderne (non-deprecated)
"""

import chromadb
import logging
from typing import List, Dict, Any, Tuple
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ChromaDBManager:
    """
    Gestionnaire ChromaDB moderne avec configuration à jour.
    """

    def __init__(self, db_path: str = "./emsi_knowledge_base"):
        """
        Initialise ChromaDB avec la nouvelle API.
        
        Args:
            db_path: Chemin de la base de données persistante
        """
        os.makedirs(db_path, exist_ok=True)
        
        try:
            logger.info(f"📦 Initialisation ChromaDB: {db_path}")
            
            # NOUVELLE API ChromaDB (non-deprecated)
            self.client = chromadb.PersistentClient(path=db_path)
            
            # Créer ou récupérer la collection
            self.collection = self.client.get_or_create_collection(
                name="emsi_documents",
                metadata={"hnsw:space": "cosine"}
            )
            
            logger.info(f"✅ ChromaDB OK - Collection: emsi_documents")
            
        except Exception as e:
            logger.error(f"❌ Erreur ChromaDB: {e}")
            raise

    def add_documents(
        self,
        documents: List[str],
        metadatas: List[Dict[str, Any]] = None,
        ids: List[str] = None
    ) -> None:
        """
        Ajoute des documents à la base de données.
        
        Args:
            documents: Liste des textes à ajouter
            metadatas: Métadonnées associées (source, page, date, etc.)
            ids: IDs des documents (générés auto si None)
        """
        try:
            if metadatas is None:
                metadatas = [{"source": "unknown"} for _ in documents]
            
            logger.info(f"📝 Ajout de {len(documents)} documents...")
            
            self.collection.add(
                documents=documents,
                metadatas=metadatas,
                ids=ids
            )
            
            logger.info(f"✅ {len(documents)} documents ajoutés avec succès")
            
        except Exception as e:
            logger.error(f"❌ Erreur lors de l'ajout de documents: {e}")
            raise

    def query(
        self,
        query_texts: List[str],
        n_results: int = 5
    ) -> Dict[str, Any]:
        """
        Effectue une recherche vectorielle sur la base de données.
        
        Args:
            query_texts: Requête(s) de recherche
            n_results: Nombre de résultats à retourner
            
        Returns:
            Résultats de la requête avec documents et distances
        """
        try:
            results = self.collection.query(
                query_texts=query_texts,
                n_results=n_results
            )
            
            return results
            
        except Exception as e:
            logger.error(f"❌ Erreur lors de la requête: {e}")
            raise

    def search(self, query: str, top_k: int = 5) -> List[Tuple[str, float, Dict]]:
        """
        Recherche des documents similaires à une requête.
        
        Args:
            query: Texte de la requête
            top_k: Nombre de résultats
            
        Returns:
            Liste de tuples (document, score_similarité, métadonnées)
        """
        try:
            results = self.query([query], n_results=top_k)
            
            # Formater les résultats
            formatted_results = []
            for i, doc in enumerate(results['documents'][0]):
                distance = results['distances'][0][i]
                # ChromaDB retourne les distances, les convertir en similarité
                similarity = 1 - distance  # Pour la métrique cosine
                metadata = results['metadatas'][0][i]
                
                formatted_results.append((doc, similarity, metadata))
            
            return formatted_results
            
        except Exception as e:
            logger.error(f"❌ Erreur lors de la recherche: {e}")
            raise

    def get_stats(self) -> Dict[str, Any]:
        """Retourne les statistiques de la base de données."""
        try:
            count = self.collection.count()
            return {
                "collection_name": "emsi_documents",
                "total_documents": count,
                "status": "✅ Opérationnel"
            }
        except Exception as e:
            logger.error(f"❌ Erreur lors de la récupération des stats: {e}")
            return {"error": str(e)}

    def delete_all(self) -> None:
        """Supprime tous les documents de la base de données."""
        try:
            logger.warning("⚠️ Suppression de tous les documents...")
            # Récupérer les IDs et les supprimer
            all_data = self.collection.get()
            if all_data['ids']:
                self.collection.delete(ids=all_data['ids'])
            logger.info("✅ Tous les documents supprimés")
        except Exception as e:
            logger.error(f"❌ Erreur lors de la suppression: {e}")
            raise
