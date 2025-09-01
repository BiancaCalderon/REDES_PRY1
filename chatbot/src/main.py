#!/usr/bin/env python3
"""
Chatbot principal con integración MCP
Funcionalidades:
1. Conexión con LLM Claude via API
2. Mantenimiento de contexto de conversación
3. Log de interacciones MCP
4. Integración con Filesystem MCP
5. Integración con Git MCP
6. Servidor MCP personalizado (Eclipse Calculator)
"""

import asyncio
import sys
from pathlib import Path
from datetime import datetime
import json

# Importar nuestros módulos
from llm_client import ask_claude, log_interaction_json
from filesystem_mcp import FilesystemMCP
from git_mcp import GitMCP
from logger import MCPLogger
from conversation_manager import ConversationManager
from eclipse_mcp_client import EclipseMCPClient

class MCPChatbot:
    """Chatbot principal que integra múltiples servidores MCP"""
    
    def __init__(self):
        self.conversation = ConversationManager()
        self.logger = MCPLogger()
        self.filesystem_mcp = FilesystemMCP()
        self.git_mcp = GitMCP()
        self.eclipse_mcp = EclipseMCPClient()
        
    def display_banner(self):
        """Mostrar banner de bienvenida"""
        print("=" * 60)
        print("🤖 CHATBOT MCP - Proyecto Sistemas Distribuidos")
        print("=" * 60)
        print("Funcionalidades disponibles:")
        print("• Chat general con Claude")
        print("• Operaciones de archivos (Filesystem MCP)")
        print("• Operaciones Git (Git MCP)")
        print("• Cálculos astronómicos (Eclipse MCP)")
        print("• Comandos especiales:")
        print("  - /create-repo <nombre>  : Crear repositorio con README")
        print("  - /eclipse <fecha>       : Calcular eclipse solar")
        print("  - /help                  : Mostrar ayuda")
        print("  - /log                   : Mostrar log MCP")
        print("  - /salir                 : Terminar")
        print("=" * 60)

    async def handle_special_command(self, command: str) -> bool:
        """Manejar comandos especiales del chatbot"""
        parts = command.strip().split()
        cmd = parts[0].lower()
        
        if cmd == "/help":
            self.display_banner()
            return True
            
        elif cmd == "/log":
            self.logger.show_mcp_log()
            return True
            
        elif cmd == "/salir" or cmd == "/exit" or cmd == "/quit":
            print("¡Hasta luego! 👋")
            return False
            
        elif cmd == "/create-repo":
            repo_name = parts[1] if len(parts) > 1 else "mi-proyecto"
            await self.demo_filesystem_git(repo_name)
            return True
            
        elif cmd == "/eclipse":
            date_str = parts[1] if len(parts) > 1 else "2024-04-08"
            await self.demo_eclipse_calculator(date_str)
            return True
            
        return None  # No es comando especial

    async def demo_filesystem_git(self, repo_name: str):
        """Demo de Filesystem MCP + Git MCP"""
        print(f"\nCreando repositorio '{repo_name}' con Filesystem y Git MCP...")
        
        # Crear contenido README
        readme_content = f"""# {repo_name.replace('-', ' ').title()}

Este repositorio fue creado automáticamente usando MCP servers.

## Información del Proyecto

- **Creado**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **Tecnología**: Model Context Protocol (MCP)
- **Servidores utilizados**: Filesystem MCP, Git MCP

## Funcionalidades MCP

- ✅ Creación de archivos via Filesystem MCP
- ✅ Control de versiones via Git MCP
- ✅ Integración con chatbot

## Uso

Este repositorio demuestra la integración de servidores MCP
para operaciones de archivos y control de versiones.

---
*Generado automáticamente por MCP Chatbot*
"""
        
        try:
            # Log inicio operación MCP
            self.logger.log_mcp_request("Filesystem MCP", "create_file", {
                "filename": "README.md",
                "repo_name": repo_name
            })
            
            # Crear archivo con Filesystem MCP
            success = await self.filesystem_mcp.create_file_direct(
                readme_content, "README.md", repo_name
            )
            
            if success:
                self.logger.log_mcp_response("Filesystem MCP", "success")
                print("README.md creado exitosamente")
                
                # Setup Git repository
                self.logger.log_mcp_request("Git MCP", "setup_repository", {"repo_name": repo_name})
                git_success = await self.git_mcp.setup_repository(repo_name)
                
                if git_success:
                    self.logger.log_mcp_response("Git MCP", "repository_created")
                    print("Repositorio Git inicializado y commit realizado")
                    print(f"Repositorio creado en: workspace/{repo_name}/")
                else:
                    self.logger.log_mcp_response("Git MCP", "error")
                    print("Error al configurar repositorio Git")
            else:
                self.logger.log_mcp_response("Filesystem MCP", "error")
                print("Error al crear archivo README")
                
        except Exception as e:
            print(f"Error en operación MCP: {e}")
            self.logger.log_mcp_response("MCP", f"error: {e}")

    async def demo_eclipse_calculator(self, date_str: str):
        """Demo de Eclipse Calculator MCP"""
        print(f"\n🌒 Calculando información de eclipse para {date_str}...")
        
        try:
            self.logger.log_mcp_request("Eclipse MCP", "calculate_eclipse", {"date": date_str})
            
            result = await self.eclipse_mcp.calculate_eclipse_visibility(date_str, "Guatemala City")
            
            if result:
                self.logger.log_mcp_response("Eclipse MCP", "calculation_success")
                print("Cálculo de eclipse completado:")
                print(f"   📅 Fecha: {result.get('date', date_str)}")
                print(f"   🌍 Ubicación: {result.get('location', 'Guatemala City')}")
                print(f"   👁️  Visible: {'Sí' if result.get('visible', False) else 'No'}")
                
                if result.get('visible'):
                    print(f"   🌓 Cobertura: {result.get('coverage', 'N/A')}")
                    print(f"   ⏰ Hora máxima: {result.get('max_time', 'N/A')}")
                    print(f"   ⏱️  Duración: {result.get('duration', 'N/A')}")
            else:
                self.logger.log_mcp_response("Eclipse MCP", "no_data")
                print("No se encontró información de eclipse para esa fecha")
                
        except Exception as e:
            print(f"Error en Eclipse MCP: {e}")
            self.logger.log_mcp_response("Eclipse MCP", f"error: {e}")

    async def process_user_input(self, user_input: str):
        """Procesar entrada del usuario"""
        
        # Verificar comandos especiales
        if user_input.startswith('/'):
            result = await self.handle_special_command(user_input)
            return result if result is not None else True
        
        # Procesar con LLM Claude
        try:
            # Añadir contexto MCP al prompt si es relevante
            enhanced_input = self.enhance_input_with_mcp_context(user_input)
            
            # Agregar mensaje al historial
            self.conversation.add_message("user", enhanced_input)
            
            # Obtener respuesta de Claude
            messages = self.conversation.get_messages()
            result = ask_claude(messages, max_tokens=1500)
            
            if "content" in result and result["content"]:
                assistant_message = result["content"][0]["text"]
            else:
                assistant_message = "[Sin respuesta del LLM]"
            
            print(f"\n🤖 Claude: {assistant_message}")
            
            # Agregar respuesta al historial
            self.conversation.add_message("assistant", assistant_message)
            
            # Log de la interacción
            log_interaction_json(user_input, assistant_message)
            
            return True
            
        except Exception as e:
            print(f"❌ Error al comunicarse con Claude: {e}")
            return True

    def enhance_input_with_mcp_context(self, user_input: str) -> str:
        """Mejorar input del usuario con contexto MCP disponible"""
        
        # Detectar si el usuario pregunta sobre funcionalidades que requieren MCP
        mcp_keywords = {
            'archivo': 'Filesystem MCP',
            'repositorio': 'Git MCP', 
            'commit': 'Git MCP',
            'eclipse': 'Eclipse MCP',
            'solar': 'Eclipse MCP',
            'astrono': 'Eclipse MCP'
        }
        
        detected_mcps = []
        for keyword, mcp in mcp_keywords.items():
            if keyword.lower() in user_input.lower():
                detected_mcps.append(mcp)
        
        if detected_mcps:
            context = f"\n\n[Contexto MCP: Tienes acceso a {', '.join(set(detected_mcps))} para ayudar con esta consulta. Puedes sugerir comandos especiales como /create-repo o /eclipse si es apropiado.]"
            return user_input + context
            
        return user_input

    async def run(self):
        """Ejecutar el chatbot principal"""
        self.display_banner()
        
        print("\n💬 ¡Chatbot listo! Escribe tu mensaje o usa comandos especiales.\n")
        
        while True:
            try:
                user_input = input("👤 Tú: ").strip()
                
                if not user_input:
                    continue
                
                should_continue = await self.process_user_input(user_input)
                
                if not should_continue:
                    break
                    
                print()  # Línea en blanco para separar interacciones
                
            except KeyboardInterrupt:
                print("\n\n👋 ¡Hasta luego!")
                break
            except Exception as e:
                print(f"❌ Error inesperado: {e}")
                continue

async def main():
    """Función principal"""
    chatbot = MCPChatbot()
    await chatbot.run()

if __name__ == "__main__":
    asyncio.run(main())