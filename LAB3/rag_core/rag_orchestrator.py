"""
Module d'orchestration RAG - Intègre tous les composants
"""

import logging
from typing import List, Dict, Tuple, Optional
from datetime import datetime
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RAGOrchestrator:
    """
    Orchestrateur principal qui coordonne tous les composants du système RAG.
    Assure l'intégration fluide de ChromaDB, embeddings, chunking et retrieval.
    """

    def __init__(
        self,
        chroma_db_path: str = "./emsi_knowledge_base",
        chunk_size: int = 500,
        chunk_overlap: int = 100,
        top_k_retrieval: int = 5
    ):
        """
        Initialise l'orchestrateur RAG.
        
        Args:
            chroma_db_path: Chemin de la base de données
            chunk_size: Taille des chunks
            chunk_overlap: Chevauchement entre chunks
            top_k_retrieval: Nombre de résultats à récupérer
        """
        logger.info("🎼 Initialisation du RAG Orchestrator...")
        
        self.chroma_db_path = chroma_db_path
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.top_k_retrieval = top_k_retrieval
        
        # Importations dépendantes (seront initialisées à la demande)
        self.chromadb_manager = None
        self.embeddings_manager = None
        self.chunker = None
        self.prompt_engineer = None
        self.ingestion_manager = None
        
        self.pipeline_stats = {
            "documents_ingested": 0,
            "chunks_created": 0,
            "queries_processed": 0,
            "last_update": None
        }

    def initialize_components(self):
        """Initialise tous les composants du pipeline."""
        try:
            logger.info("⚙️ Initialisation des composants RAG...")
            
            # Importer et initialiser les modules
            from rag_core.chromadb_manager import ChromaDBManager
            from rag_core.embeddings_manager import EmbeddingsManager
            from rag_core.chunking import IntelligentChunker
            from rag_core.prompt_engineer import AdvancedPromptEngineer
            from rag_core.pdf_ingestion import PDFIngestionManager
            
            self.chromadb_manager = ChromaDBManager(self.chroma_db_path)
            self.embeddings_manager = EmbeddingsManager()
            self.chunker = IntelligentChunker(
                chunk_size=self.chunk_size,
                chunk_overlap=self.chunk_overlap
            )
            self.prompt_engineer = AdvancedPromptEngineer()
            self.ingestion_manager = PDFIngestionManager()
            
            logger.info("✅ Tous les composants initialisés avec succès")
            
        except Exception as e:
            logger.error(f"❌ Erreur lors de l'initialisation: {e}")
            raise

    def ingest_documents(self, documents: List[Dict]) -> Dict:
        """
        Ingère des documents, les chunke, et les stocke.
        
        Args:
            documents: Liste des documents (avec 'text' et métadonnées)
            
        Returns:
            Statistiques d'ingestion
        """
        try:
            logger.info(f"📥 Ingestion de {len(documents)} documents...")
            
            # Étape 1: Chunking
            all_chunks = self.chunker.chunk_documents(documents)
            logger.info(f"   ✓ {len(all_chunks)} chunks créés")
            
            # Étape 2: Préparer les données pour ChromaDB
            chunk_texts = [chunk['content'] for chunk in all_chunks]
            chunk_metadatas = [
                {k: v for k, v in chunk.items() if k != 'content'}
                for chunk in all_chunks
            ]
            
            # Générer des IDs
            chunk_ids = [
                f"chunk_{chunk['source']}_{i}"
                for i, chunk in enumerate(all_chunks)
            ]
            
            # Étape 3: Ajouter à ChromaDB
            self.chromadb_manager.add_documents(
                documents=chunk_texts,
                metadatas=chunk_metadatas,
                ids=chunk_ids
            )
            
            # Mise à jour des statistiques
            self.pipeline_stats["documents_ingested"] += len(documents)
            self.pipeline_stats["chunks_created"] += len(all_chunks)
            self.pipeline_stats["last_update"] = datetime.now().isoformat()
            
            logger.info(f"✅ Ingestion complète: {len(all_chunks)} chunks stockés")
            
            return {
                "status": "success",
                "documents_processed": len(documents),
                "chunks_created": len(all_chunks),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Erreur lors de l'ingestion: {e}")
            return {"status": "error", "message": str(e)}

    def retrieve_context(self, query: str) -> List[Tuple[str, float, Dict]]:
        """
        Récupère les documents contextuels les plus pertinents pour une requête.
        
        Args:
            query: Requête utilisateur
            
        Returns:
            Liste de tuples (document, score_similarité, métadonnées)
        """
        try:
            logger.info(f"🔍 Recherche de contexte pour: '{query[:50]}...'")
            
            results = self.chromadb_manager.search(query, top_k=self.top_k_retrieval)
            
            logger.info(f"   ✓ {len(results)} documents trouvés")
            
            return results
            
        except Exception as e:
            logger.error(f"❌ Erreur lors de la recherche: {e}")
            return []

    def build_augmented_prompt(
        self,
        query: str,
        persona: str = "general_expert",
        include_context: bool = True
    ) -> Dict:
        """
        Construit un prompt augmenté avec contexte RAG.
        
        Args:
            query: Requête utilisateur
            persona: Type de persona pour le prompt
            include_context: Inclure le contexte récupéré
            
        Returns:
            Dictionnaire avec système prompt et user prompt
        """
        try:
            # Étape 1: Récupérer le contexte si demandé
            context_docs = []
            if include_context:
                retrieved = self.retrieve_context(query)
                context_docs = [doc[0] for doc in retrieved]
            
            # Étape 2: Construire le prompt système
            system_prompt = self.prompt_engineer.build_system_prompt(persona)
            
            # Étape 3: Construire le prompt utilisateur avec contexte
            if context_docs:
                user_prompt = self.prompt_engineer.build_context_prompt(
                    context_docs,
                    query
                )
            else:
                user_prompt = query
            
            # Mise à jour des statistiques
            self.pipeline_stats["queries_processed"] += 1
            
            return {
                "system": system_prompt,
                "user": user_prompt,
                "context_documents": context_docs,
                "context_count": len(context_docs)
            }
            
        except Exception as e:
            logger.error(f"❌ Erreur lors de la construction du prompt: {e}")
            return {
                "system": self.prompt_engineer.build_system_prompt(persona),
                "user": query,
                "context_documents": [],
                "error": str(e)
            }

    def get_stats(self) -> Dict:
        """Retourne les statistiques du pipeline RAG."""
        return {
            **self.pipeline_stats,
            "chromadb_stats": self.chromadb_manager.get_stats() if self.chromadb_manager else {},
            "top_k_retrieval": self.top_k_retrieval,
            "chunk_size": self.chunk_size
        }

    def export_pipeline_config(self, filepath: str) -> None:
        """Exporte la configuration du pipeline."""
        config = {
            "components": {
                "chromadb": {"path": self.chroma_db_path},
                "chunking": {
                    "chunk_size": self.chunk_size,
                    "chunk_overlap": self.chunk_overlap
                },
                "retrieval": {"top_k": self.top_k_retrieval}
            },
            "stats": self.get_stats()
        }
        
        with open(filepath, 'w') as f:
            json.dump(config, f, indent=2)
        
        logger.info(f"💾 Configuration exportée vers: {filepath}")
