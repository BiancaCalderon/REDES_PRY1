# conversation_manager.py
"""
Gestor de conversación que mantiene el contexto de la sesión
Funcionalidad requerida: Mantener contexto entre preguntas
"""

from datetime import datetime
import json
from typing import List, Dict, Any

class ConversationManager:
    """Maneja el historial y contexto de la conversación"""
    
    def __init__(self, max_messages: int = 50):
        """
        Inicializar el gestor de conversación
        
        Args:
            max_messages: Número máximo de mensajes a mantener en memoria
        """
        self.messages = []
        self.max_messages = max_messages
        self.session_start = datetime.now()
        
        # Mensaje del sistema para establecer contexto
        system_message = {
            "role": "system",
            "content": """Eres un chatbot que utiliza servidores MCP (Model Context Protocol). 

Tienes acceso a las siguientes funcionalidades MCP:
- Filesystem MCP: Crear y gestionar archivos
- Git MCP: Operaciones de control de versiones
- Eclipse MCP: Cálculos astronómicos de eclipses solares

Características importantes:
- Mantén el contexto de la conversación
- Si el usuario pregunta sobre crear repositorios, archivos o commits, puedes sugerir comandos MCP
- Para consultas astronómicas sobre eclipses, puedes sugerir el comando /eclipse
- Siempre responde de manera útil y contextual

Recuerda que puedes acceder a información específica sobre eclipses solares, especialmente para Guatemala."""
        }
        
        # No agregamos el mensaje del sistema a self.messages ya que Claude maneja esto internamente
        
    def add_message(self, role: str, content: str) -> None:
        """
        Agregar un mensaje al historial de conversación
        
        Args:
            role: 'user' o 'assistant'
            content: Contenido del mensaje
        """
        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        }
        
        self.messages.append(message)
        
        # Mantener solo los últimos max_messages mensajes para evitar exceder límites de tokens
        if len(self.messages) > self.max_messages:
            # Mantener los primeros mensajes importantes y los más recientes
            important_messages = self.messages[:2]  # Primeros mensajes del contexto
            recent_messages = self.messages[-(self.max_messages-2):]
            self.messages = important_messages + recent_messages
    
    def get_messages(self) -> List[Dict[str, str]]:
        """
        Obtener mensajes formateados para Claude API
        
        Returns:
            Lista de mensajes en formato requerido por Claude
        """
        # Convertir al formato requerido por Claude (sin timestamps)
        formatted_messages = []
        
        for msg in self.messages:
            formatted_messages.append({
                "role": msg["role"],
                "content": msg["content"]
            })
        
        return formatted_messages
    
    def get_context(self) -> str:
        """
        Obtener contexto textual de la conversación
        
        Returns:
            Resumen del contexto actual
        """
        if not self.messages:
            return "Conversación iniciada"
        
        # Contar mensajes por rol
        user_msgs = len([m for m in self.messages if m["role"] == "user"])
        assistant_msgs = len([m for m in self.messages if m["role"] == "assistant"])
        
        # Obtener los últimos temas mencionados
        recent_content = []
        for msg in self.messages[-6:]:  # Últimos 6 mensajes
            content_preview = msg["content"][:50] + "..." if len(msg["content"]) > 50 else msg["content"]
            recent_content.append(f"{msg['role']}: {content_preview}")
        
        context_info = {
            "session_duration": str(datetime.now() - self.session_start),
            "total_exchanges": min(user_msgs, assistant_msgs),
            "recent_topics": recent_content
        }
        
        return json.dumps(context_info, indent=2, ensure_ascii=False)
    
    def search_context(self, keyword: str) -> List[Dict]:
        """
        Buscar mensajes que contengan una palabra clave
        
        Args:
            keyword: Palabra clave a buscar
            
        Returns:
            Lista de mensajes que contienen la palabra clave
        """
        matching_messages = []
        
        for msg in self.messages:
            if keyword.lower() in msg["content"].lower():
                matching_messages.append(msg)
        
        return matching_messages
    
    def get_last_user_message(self) -> str:
        """Obtener el último mensaje del usuario"""
        for msg in reversed(self.messages):
            if msg["role"] == "user":
                return msg["content"]
        return ""
    
    def get_last_assistant_message(self) -> str:
        """Obtener la última respuesta del asistente"""
        for msg in reversed(self.messages):
            if msg["role"] == "assistant":
                return msg["content"]
        return ""
    
    def clear_conversation(self):
        """Limpiar el historial de conversación"""
        self.messages = []
        self.session_start = datetime.now()
    
    def export_conversation(self, filename: str = None) -> str:
        """
        Exportar la conversación completa a un archivo JSON
        
        Args:
            filename: Nombre del archivo (opcional)
            
        Returns:
            Ruta del archivo creado
        """
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"conversation_{timestamp}.json"
        
        export_data = {
            "session_info": {
                "start_time": self.session_start.isoformat(),
                "export_time": datetime.now().isoformat(),
                "total_messages": len(self.messages)
            },
            "messages": self.messages
        }
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            return filename
        except Exception as e:
            print(f"Error al exportar conversación: {e}")
            return None
    
    def get_conversation_stats(self) -> Dict[str, Any]:
        """Obtener estadísticas de la conversación"""
        user_messages = [m for m in self.messages if m["role"] == "user"]
        assistant_messages = [m for m in self.messages if m["role"] == "assistant"]
        
        stats = {
            "total_messages": len(self.messages),
            "user_messages": len(user_messages),
            "assistant_messages": len(assistant_messages),
            "session_duration": str(datetime.now() - self.session_start),
            "avg_user_message_length": sum(len(m["content"]) for m in user_messages) / len(user_messages) if user_messages else 0,
            "avg_assistant_message_length": sum(len(m["content"]) for m in assistant_messages) / len(assistant_messages) if assistant_messages else 0
        }
        
        return stats
    
    def has_context_about(self, topic: str) -> bool:
        """
        Verificar si existe contexto previo sobre un tema
        
        Args:
            topic: Tema a verificar
            
        Returns:
            True si hay contexto previo sobre el tema
        """
        for msg in self.messages:
            if topic.lower() in msg["content"].lower():
                return True
        return False