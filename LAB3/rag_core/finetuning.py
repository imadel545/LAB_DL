"""
Module de Fine-tuning du Modèle Llama sur les données EMSI
"""

import json
import logging
from typing import List, Dict, Tuple
from datetime import datetime
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LlamaFineTuner:
    """
    Gestionnaire du fine-tuning de Llama sur les données EMSI.
    Crée des datasets optimisés et coordonne l'entraînement.
    """

    def __init__(self, model_name: str = "llama3.2:1b"):
        """
        Initialise le fine-tuner.
        
        Args:
            model_name: Nom du modèle Llama à fine-tuner
        """
        self.model_name = model_name
        self.dataset_path = None
        logger.info(f"🎓 Fine-Tuner Llama initialisé pour: {model_name}")

    def create_training_dataset(
        self,
        documents: List[Dict],
        output_path: str = "./training_data.jsonl"
    ) -> str:
        """
        Crée un dataset JSONL pour le fine-tuning.
        
        Args:
            documents: Documents d'entraînement
            output_path: Chemin du fichier de sortie
            
        Returns:
            Chemin du fichier généré
        """
        try:
            logger.info(f"📝 Création du dataset d'entraînement...")
            
            training_examples = []
            
            # Convertir les documents en exemples d'entraînement
            for doc in documents:
                content = doc.get('content') or doc.get('text', '')
                source = doc.get('source', 'unknown')
                
                # Créer des exemples format QA
                if len(content) > 100:
                    # Exemple 1: Complétion
                    example1 = {
                        "messages": [
                            {
                                "role": "system",
                                "content": "Tu es un expert EMSI répondant sur l'école, les programmes et opportunités."
                            },
                            {
                                "role": "user",
                                "content": f"Parle-moi de: {content[:100]}..."
                            },
                            {
                                "role": "assistant",
                                "content": content
                            }
                        ]
                    }
                    training_examples.append(example1)
                    
                    # Exemple 2: Extraction
                    if 'EMSI' in content or 'école' in content.lower():
                        example2 = {
                            "messages": [
                                {
                                    "role": "system",
                                    "content": "Tu es expert EMSI."
                                },
                                {
                                    "role": "user",
                                    "content": "Résume les informations principales"
                                },
                                {
                                    "role": "assistant",
                                    "content": content[:200]
                                }
                            ]
                        }
                        training_examples.append(example2)
            
            # Sauvegarder en JSONL
            os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                for example in training_examples:
                    f.write(json.dumps(example, ensure_ascii=False) + '\n')
            
            logger.info(f"✅ Dataset créé: {len(training_examples)} exemples")
            logger.info(f"   Sauvegardé à: {output_path}")
            
            self.dataset_path = output_path
            return output_path
            
        except Exception as e:
            logger.error(f"❌ Erreur lors de la création du dataset: {e}")
            raise

    def generate_training_config(
        self,
        output_path: str = "./finetune_config.json"
    ) -> Dict:
        """
        Génère un fichier de configuration pour le fine-tuning.
        
        Args:
            output_path: Chemin du fichier de configuration
            
        Returns:
            Configuration générée
        """
        config = {
            "model": self.model_name,
            "training": {
                "learning_rate": 2e-5,
                "num_train_epochs": 3,
                "batch_size": 4,
                "warmup_steps": 100,
                "weight_decay": 0.01
            },
            "parameters": {
                "temperature": 0.7,
                "top_p": 0.9,
                "top_k": 40,
                "max_tokens": 512
            },
            "dataset": self.dataset_path,
            "domain": "EMSI_Academic_Domain",
            "created_at": datetime.now().isoformat()
        }
        
        os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
        
        with open(output_path, 'w') as f:
            json.dump(config, f, indent=2)
        
        logger.info(f"📋 Configuration sauvegardée: {output_path}")
        
        return config

    def suggest_fine_tuning_strategy(self) -> Dict:
        """
        Suggère une stratégie de fine-tuning optimale.
        
        Returns:
            Stratégie recommandée
        """
        strategy = {
            "approach": "Instruction Fine-Tuning",
            "phases": [
                {
                    "phase": 1,
                    "name": "Domain Adaptation",
                    "description": "Adapter le modèle au domaine académique EMSI",
                    "duration": "5-10 heures",
                    "focus": "Base de connaissances EMSI"
                },
                {
                    "phase": 2,
                    "name": "Task Specialization",
                    "description": "Spécialiser pour tâches EMSI-spécifiques",
                    "duration": "3-5 heures",
                    "focus": "QA, admissions, orientations"
                },
                {
                    "phase": 3,
                    "name": "Safety & Quality",
                    "description": "Assurer cohérence et qualité",
                    "duration": "2-3 heures",
                    "focus": "Fact-checking, fact-alignment"
                }
            ],
            "resources": {
                "gpu_memory": "8GB+ VRAM recommandé",
                "ram": "16GB+ RAM",
                "storage": "20GB+ disque libre"
            },
            "expected_improvements": [
                "✓ Réponses plus pertinentes au contexte EMSI",
                "✓ Meilleure compréhension des termes académiques",
                "✓ Ton et style aligné avec EMSI",
                "✓ Accuracy +30-40% sur domaine EMSI"
            ]
        }
        
        return strategy

    def create_evaluation_dataset(self, output_path: str = "./eval_data.json") -> str:
        """
        Crée un dataset d'évaluation pour valider le fine-tuning.
        
        Args:
            output_path: Chemin du fichier d'évaluation
            
        Returns:
            Chemin du fichier
        """
        eval_dataset = {
            "metadata": {
                "created_at": datetime.now().isoformat(),
                "domain": "EMSI",
                "purpose": "Evaluation du fine-tuning Llama"
            },
            "test_cases": [
                {
                    "id": 1,
                    "question": "Quels sont les programmes majeurs offerts par l'EMSI?",
                    "expected_keywords": ["ingénierie", "informatique", "cycle", "mastères"],
                    "domain": "programs"
                },
                {
                    "id": 2,
                    "question": "Comment candidater à l'EMSI?",
                    "expected_keywords": ["candidature", "admission", "dossier", "test"],
                    "domain": "admissions"
                },
                {
                    "id": 3,
                    "question": "Quels sont les débouchés après l'EMSI?",
                    "expected_keywords": ["emploi", "startup", "carrière", "alumni"],
                    "domain": "career"
                },
                {
                    "id": 4,
                    "question": "Y a-t-il des bourses à l'EMSI?",
                    "expected_keywords": ["bourse", "financement", "aide", "support"],
                    "domain": "support"
                },
                {
                    "id": 5,
                    "question": "Quel est le campus de l'EMSI?",
                    "expected_keywords": ["localisation", "infrastructure", "facilités"],
                    "domain": "facilities"
                }
            ]
        }
        
        os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(eval_dataset, f, indent=2, ensure_ascii=False)
        
        logger.info(f"✅ Dataset d'évaluation créé: {output_path}")
        
        return output_path


class FineTuningOrchestrator:
    """
    Orchestre l'ensemble du processus de fine-tuning.
    """

    def __init__(self):
        """Initialise l'orchestrateur."""
        self.fine_tuner = LlamaFineTuner()
        logger.info("🎼 Orchestrateur Fine-Tuning initialisé")

    def prepare_finetune_pipeline(self, documents: List[Dict]) -> Dict:
        """
        Prépare le pipeline complet de fine-tuning.
        
        Args:
            documents: Documents d'entraînement
            
        Returns:
            Informations du pipeline préparé
        """
        try:
            logger.info("🚀 Préparation du pipeline fine-tuning...")
            
            # Étape 1: Créer le dataset
            dataset_path = self.fine_tuner.create_training_dataset(documents)
            
            # Étape 2: Générer la configuration
            config = self.fine_tuner.generate_training_config()
            
            # Étape 3: Créer le dataset d'évaluation
            eval_path = self.fine_tuner.create_evaluation_dataset()
            
            # Étape 4: Suggérer la stratégie
            strategy = self.fine_tuner.suggest_fine_tuning_strategy()
            
            return {
                "status": "ready",
                "dataset_path": dataset_path,
                "config_path": "./finetune_config.json",
                "eval_dataset_path": eval_path,
                "strategy": strategy,
                "next_steps": [
                    "1. Examiner la stratégie de fine-tuning",
                    "2. Ajuster les paramètres si nécessaire",
                    "3. Lancer l'entraînement",
                    "4. Évaluer et valider les résultats"
                ]
            }
            
        except Exception as e:
            logger.error(f"❌ Erreur lors de la préparation: {e}")
            return {"status": "error", "message": str(e)}
