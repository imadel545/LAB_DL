"""
🤖 MCP Client pour EMSI-Bot - Agentic AI Integration
Permet au chatbot d'accéder à des outils via Model Context Protocol
"""

import asyncio
import json
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import subprocess
import logging

try:
    from mcp_tools_advanced import ADVANCED_TOOLS
    ADVANCED_TOOLS_AVAILABLE = True
except ImportError:
    ADVANCED_TOOLS_AVAILABLE = False
    ADVANCED_TOOLS = {}

logger = logging.getLogger(__name__)

logger = logging.getLogger(__name__)


@dataclass
class MCPTool:
    """Représente un outil MCP disponible"""
    name: str
    description: str
    parameters: Dict[str, Any]
    server: str


class MCPClient:
    """Client MCP pour interaction avec les serveurs"""
    
    def __init__(self, config_path: str = "mcp_config.json"):
        self.config_path = config_path
        self.servers: Dict[str, Any] = {}
        self.available_tools: List[MCPTool] = []
        self._initialized = False
        
    async def initialize(self):
        """Initialise la connexion aux serveurs MCP"""
        if self._initialized:
            return
            
        try:
            with open(self.config_path, 'r') as f:
                config = json.load(f)
            
            self.servers = config.get('mcpServers', {})
            
            # Simuler la découverte des outils (en production, on interrogerait vraiment les serveurs)
            self._discover_tools()
            
            self._initialized = True
            logger.info(f"✅ MCP Client initialized with {len(self.available_tools)} tools")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize MCP client: {e}")
            
    def _discover_tools(self):
        """Découvre les outils disponibles depuis les serveurs configurés"""
        
        # Filesystem tools
        if 'filesystem' in self.servers:
            self.available_tools.extend([
                MCPTool(
                    name="read_file",
                    description="Lit le contenu d'un fichier dans emsi_knowledge_base",
                    parameters={"file_path": "string"},
                    server="filesystem"
                ),
                MCPTool(
                    name="list_directory",
                    description="Liste les fichiers dans emsi_knowledge_base",
                    parameters={"path": "string"},
                    server="filesystem"
                ),
                MCPTool(
                    name="search_files",
                    description="Recherche dans les fichiers de la base de connaissances",
                    parameters={"query": "string"},
                    server="filesystem"
                )
            ])
        
        # Brave Search tools
        if 'brave-search' in self.servers:
            self.available_tools.append(
                MCPTool(
                    name="web_search",
                    description="Recherche sur le web avec Brave Search",
                    parameters={"query": "string", "count": "integer"},
                    server="brave-search"
                )
            )
        
        # Memory tools
        if 'memory' in self.servers:
            self.available_tools.extend([
                MCPTool(
                    name="store_memory",
                    description="Stocke une information en mémoire",
                    parameters={"key": "string", "value": "string"},
                    server="memory"
                ),
                MCPTool(
                    name="recall_memory",
                    description="Récupère une information depuis la mémoire",
                    parameters={"key": "string"},
                    server="memory"
                )
            ])
        
        # Advanced tools (WhatsApp, Email, Météo, etc.)
        if ADVANCED_TOOLS_AVAILABLE:
            self.available_tools.extend([
                MCPTool(
                    name="whatsapp_send",
                    description="📱 Envoie un message WhatsApp",
                    parameters={"phone": "string", "message": "string"},
                    server="advanced"
                ),
                MCPTool(
                    name="email_send",
                    description="📧 Envoie un email",
                    parameters={"to": "string", "subject": "string", "body": "string"},
                    server="advanced"
                ),
                MCPTool(
                    name="weather_current",
                    description="🌤️ Obtient la météo actuelle d'une ville",
                    parameters={"city": "string", "country": "string"},
                    server="advanced"
                ),
                MCPTool(
                    name="weather_forecast",
                    description="📅 Prévisions météo sur plusieurs jours",
                    parameters={"city": "string", "days": "integer"},
                    server="advanced"
                ),
                MCPTool(
                    name="calendar_create",
                    description="📅 Crée un événement dans le calendrier",
                    parameters={"title": "string", "date": "string", "time": "string"},
                    server="advanced"
                ),
                MCPTool(
                    name="translate",
                    description="🌍 Traduit un texte entre deux langues",
                    parameters={"text": "string", "from_lang": "string", "to_lang": "string"},
                    server="advanced"
                ),
                MCPTool(
                    name="notify",
                    description="🔔 Envoie une notification push",
                    parameters={"title": "string", "message": "string"},
                    server="advanced"
                ),
                MCPTool(
                    name="pdf_extract",
                    description="📄 Extrait le texte d'un fichier PDF",
                    parameters={"pdf_path": "string"},
                    server="advanced"
                ),
                MCPTool(
                    name="tts",
                    description="🔊 Convertit du texte en audio (Text-to-Speech)",
                    parameters={"text": "string", "language": "string"},
                    server="advanced"
                ),
                MCPTool(
                    name="stt",
                    description="🎤 Convertit de l'audio en texte (Speech-to-Text)",
                    parameters={"audio_path": "string"},
                    server="advanced"
                )
            ])
    
    def get_tools_description(self) -> str:
        """Retourne une description textuelle des outils pour le LLM"""
        if not self._initialized:
            return "MCP tools not initialized"
        
        tools_desc = "🛠️ **Outils disponibles via MCP:**\n\n"
        for tool in self.available_tools:
            params = ", ".join([f"{k}: {v}" for k, v in tool.parameters.items()])
            tools_desc += f"- **{tool.name}** ({tool.server}): {tool.description}\n  Paramètres: {params}\n"
        
        return tools_desc
    
    async def call_tool(self, tool_name: str, **kwargs) -> Dict[str, Any]:
        """Exécute un outil MCP"""
        tool = next((t for t in self.available_tools if t.name == tool_name), None)
        
        if not tool:
            return {"error": f"Tool {tool_name} not found"}
        
        try:
            # Simulation d'appel (en production, on appellerait vraiment le serveur MCP)
            result = await self._simulate_tool_call(tool, kwargs)
            logger.info(f"✅ Tool {tool_name} executed successfully")
            return result
            
        except Exception as e:
            logger.error(f"❌ Tool {tool_name} failed: {e}")
            return {"error": str(e)}
    
    async def _simulate_tool_call(self, tool: MCPTool, params: Dict) -> Dict[str, Any]:
        """Simule l'appel d'un outil (à remplacer par vrais appels MCP)"""
        
        if tool.name == "read_file":
            # Simulation lecture fichier
            file_path = params.get('file_path', '')
            knowledge_base = "/Users/imad/Desktop/Lab_DL/LAB3/emsi_knowledge_base"
            
            # Construire le chemin correct (éviter la duplication)
            if file_path.startswith('emsi_knowledge_base'):
                full_path = f"/Users/imad/Desktop/Lab_DL/LAB3/{file_path}"
            else:
                full_path = f"{knowledge_base}/{file_path}"
            
            try:
                with open(full_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                return {"success": True, "content": content}
            except Exception as e:
                return {"success": False, "error": str(e)}
        
        elif tool.name == "list_directory":
            # Simulation listage
            import os
            path = params.get('path', '')
            knowledge_base = "/Users/imad/Desktop/Lab_DL/LAB3/emsi_knowledge_base"
            
            # Construire le chemin correct (éviter la duplication)
            if path.startswith('emsi_knowledge_base'):
                full_path = f"/Users/imad/Desktop/Lab_DL/LAB3/{path}"
            elif path == '' or path == '.':
                full_path = knowledge_base
            else:
                full_path = f"{knowledge_base}/{path}"
            
            try:
                files = os.listdir(full_path)
                return {"success": True, "files": files}
            except Exception as e:
                return {"success": False, "error": str(e)}
        
        elif tool.name == "search_files":
            # Simulation recherche
            query = params.get('query', '')
            return {
                "success": True,
                "results": [
                    {"file": "example.txt", "relevance": 0.9},
                    {"file": "cours.md", "relevance": 0.7}
                ],
                "message": f"Recherche simulée pour: {query}"
            }
        
        elif tool.name == "web_search":
            query = params.get('query', '')
            return {
                "success": True,
                "results": f"Résultats web simulés pour: {query}",
                "message": "⚠️ Brave API key needed for real search"
            }
        
        elif tool.name == "store_memory":
            # Simulation mémoire
            key = params.get('key', '')
            value = params.get('value', '')
            return {"success": True, "message": f"Stored {key}={value}"}
        
        elif tool.name == "recall_memory":
            key = params.get('key', '')
            return {"success": True, "value": f"Recalled value for {key}"}
        
        # Advanced tools
        elif tool.name in ADVANCED_TOOLS:
            tool_func = ADVANCED_TOOLS[tool.name]
            result = await tool_func(**params)
            return result
        
        return {"success": False, "error": "Unknown tool"}


# Instance globale
mcp_client = MCPClient()
