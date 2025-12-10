"""
rag_core - Package principal pour le système RAG EMSI
Contient tous les composants du système d'augmentation contextuelle
"""

__version__ = "1.0.0"
__author__ = "EMSI Development Team"
__description__ = "Advanced RAG System for EMSI Chatbot powered by LLaMA"

from .rag_orchestrator import RAGOrchestrator
from .chromadb_manager import ChromaDBManager
from .embeddings_manager import EmbeddingsManager
from .chunking import IntelligentChunker
from .prompt_engineer import AdvancedPromptEngineer
from .pdf_ingestion import PDFIngestionManager
from .finetuning import LlamaFineTuner, FineTuningOrchestrator

__all__ = [
    'RAGOrchestrator',
    'ChromaDBManager',
    'EmbeddingsManager',
    'IntelligentChunker',
    'AdvancedPromptEngineer',
    'PDFIngestionManager',
    'LlamaFineTuner',
    'FineTuningOrchestrator'
]
