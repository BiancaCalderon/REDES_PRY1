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
7. Integración dinámica con servidores MCP de otros estudiantes
"""

import asyncio
import sys
import json
from datetime import datetime
import os
import json as _json

# Importar nuestros módulos
from llm_client import ask_claude, log_interaction_json
from filesystem_mcp import FilesystemMCP
from git_mcp import GitMCP
from logger import MCPLogger
from conversation_manager import ConversationManager
from eclipse_mcp_client import EclipseMCPClient
from external_mcp_client import ExternalMCPClient
from f1_mcp_client import F1MCPClient
from remote_mcp_client import RemoteMcpClient

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt
from rich.theme import Theme
from rich.live import Live
from rich.spinner import Spinner

console = Console(theme=Theme({
    "menu": "bold cyan",
    "option": "bold yellow",
    "input": "bold green",
    "error": "bold red",
    "success": "bold green",
    "title": "bold magenta",
    "highlight": "bold white on blue",
    "info": "dim cyan",
    "tool_code": "bold yellow",
}))

class MCPChatbot:
    """Chatbot agente que integra múltiples servidores MCP como herramientas."""

    def __init__(self):
        self.conversation = ConversationManager()
        self.logger = MCPLogger()
        # Inicializar clientes para las herramientas
        self.eclipse_mcp = EclipseMCPClient()
        self.f1_mcp = F1MCPClient()
        self.filesystem_mcp = FilesystemMCP()
        self.git_mcp = GitMCP()
        trainer_server_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'personal_trainer_mcp', 'server.py'))
        self.personal_trainer_mcp = ExternalMCPClient(trainer_server_path)
        # Definir herramientas DESPUÉS de inicializar los clientes
        self.tools = self._define_tools()

    def _define_tools(self):
        """Define la lista de herramientas disponibles para el LLM."""
        return [
            {
                "name": "create_repository",
                "description": "Crea un nuevo directorio, lo inicializa como un repositorio de Git, crea un archivo README.md con contenido y realiza el primer commit. Todo en un solo paso.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "repo_name": {"type": "string", "description": "El nombre del nuevo repositorio a crear. Por ejemplo: 'mi-nuevo-proyecto'."},
                        "readme_content": {"type": "string", "description": "El contenido de texto que se escribirá en el archivo README.md."}
                    },
                    "required": ["repo_name", "readme_content"]
                }
            },
            {
                "name": "predict_next_eclipse",
                "description": "Predice el próximo eclipse solar o lunar visible desde una ubicación específica. Devuelve la fecha, tipo y descripción del próximo eclipse.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "location": {
                            "type": "string",
                            "description": "La ciudad o ubicación desde donde se quiere observar. Ejemplo: 'Guatemala City', 'Madrid'."
                        }
                    },
                    "required": ["location"]
                }
            },
            {
                "name": "calculate_eclipse_visibility",
                "description": "Calcula si un eclipse específico es visible en una fecha y ubicación dadas. Proporciona detalles como cobertura, hora máxima, etc.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "date": {"type": "string", "description": "La fecha del eclipse en formato YYYY-MM-DD."},
                        "location": {"type": "string", "description": "La ciudad para verificar la visibilidad."}
                    },
                    "required": ["date", "location"]
                }
            },
            {
                "name": "get_f1_calendar",
                "description": "Obtiene el calendario de carreras de la Fórmula 1 para una temporada (año) específica.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "season": {"type": "integer", "description": "El año de la temporada de F1. Ejemplo: 2024."}
                    },
                    "required": ["season"]
                }
            },
            {
                "name": "compute_metrics",
                "description": "Calcula el Índice de Masa Corporal (IMC) y la Tasa Metabólica Basal (TMB) de una persona.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "sexo": {"type": "string", "description": "Sexo de la persona ('male' o 'female')."},
                        "edad": {"type": "integer", "description": "Edad de la persona en años."},
                        "altura_cm": {"type": "integer", "description": "Altura de la persona en centímetros."},
                        "peso_kg": {"type": "integer", "description": "Peso de la persona en kilogramos."}
                    },
                    "required": ["sexo", "edad", "altura_cm", "peso_kg"]
                }
            },
            {
                "name": "build_routine_tool",
                "description": "Construye una rutina de ejercicios semanal basada en un objetivo, disponibilidad y nivel de experiencia.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "objetivo": {"type": "string", "description": "El objetivo de la rutina, ej: 'perder peso', 'ganar músculo'."},
                        "dias_por_semana": {"type": "integer", "description": "Número de días disponibles para entrenar."},
                        "minutos_por_sesion": {"type": "integer", "description": "Duración en minutos de cada sesión de entrenamiento."},
                        "experiencia": {"type": "string", "description": "Nivel de experiencia, ej: 'principiante', 'intermedio', 'avanzado'."}
                    },
                    "required": ["objetivo", "dias_por_semana", "minutos_por_sesion", "experiencia"]
                }
            }
        ]

    async def execute_tool(self, tool_name: str, tool_args: dict):
        """Ejecuta la herramienta seleccionada y devuelve el resultado."""
        try:
            if tool_name == "create_repository":
                repo_name = tool_args.get("repo_name")
                content = tool_args.get("readme_content")
                file_success = await self.filesystem_mcp.create_file_direct(
                    content, "README.md", repo_name
                )
                if not file_success:
                    return {"error": f"Fallo al crear el archivo README en el repositorio {repo_name}."}
                git_success = await self.git_mcp.setup_repository(repo_name)
                if not git_success:
                    return {"error": f"Fallo al inicializar el repositorio Git para {repo_name}."}
                return {"status": "success", "message": f"Repositorio '{repo_name}' creado exitosamente con README.md y commit inicial."}
            
            elif tool_name == "predict_next_eclipse":
                async with self.eclipse_mcp as client:
                    return await client.predict_next_eclipse(tool_args.get("location"))
            elif tool_name == "calculate_eclipse_visibility":
                async with self.eclipse_mcp as client:
                    return await client.calculate_eclipse_visibility(tool_args.get("date"), tool_args.get("location"))
            elif tool_name == "get_f1_calendar":
                async with self.f1_mcp as client:
                    return await client.get_calendar(tool_args.get("season"))
            elif tool_name == "compute_metrics":
                async with self.personal_trainer_mcp as client:
                    return await client.call_tool("compute_metrics", {"args": tool_args})
            elif tool_name == "build_routine_tool":
                async with self.personal_trainer_mcp as client:
                    return await client.call_tool("build_routine_tool", {"args": tool_args})
            else:
                return {"error": f"Herramienta '{tool_name}' desconocida."}
        except Exception as e:
            self.logger.log_mcp_error("Agent", tool_name, str(e))
            return {"error": f"Error al ejecutar la herramienta '{tool_name}': {e}"}

    def display_help(self):
        """Muestra la ayuda de comandos especiales."""
        console.print(Panel("[title]🤖 [bold]MCP Chatbot - Ayuda[/bold]", style="title"))
        console.print("Este es un chatbot agente. Puedes hacerle preguntas directamente en lenguaje natural.\n")
        console.print("El chatbot puede usar las siguientes herramientas:", style="info")
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Herramienta", style="option")
        table.add_column("Descripción", style="menu")
        for tool in self.tools:
            table.add_row(f"[tool_code]{tool['name']}[/tool_code]", tool['description'])
        console.print(table)
        console.print("\nComandos especiales disponibles:", style="info")
        console.print("  [bold]/help[/bold]  - Muestra esta ayuda.")
        console.print("  [bold]/log[/bold]   - Muestra el log de interacciones MCP.")
        console.print("  [bold]/reset[/bold] - Reinicia la conversación actual.")
        console.print("  [bold]/exit[/bold]  - Termina el chatbot.")

    async def handle_special_command(self, command: str):
        """Maneja comandos especiales que no van al LLM."""
        if command == "/help":
            self.display_help()
            return True
        if command == "/log":
            self.logger.show_logs(console)
            return True
        if command == "/reset":
            self.conversation.reset()
            console.print("[success]La conversación ha sido reiniciada.[/success]")
            return True
        if command in ["/exit", "/quit", "/salir"]:
            return False
        return None

    async def run(self):
        """Bucle principal del chatbot agente."""
        self.display_help()
        console.print("\n[info]Escribe tu mensaje o usa [bold]/help[/bold] para ver los comandos.[/info]")

        while True:
            try:
                user_input = Prompt.ask("👤 Tú").strip()
                if not user_input:
                    continue

                # Manejar comandos especiales
                should_continue = await self.handle_special_command(user_input.lower())
                if should_continue is not None:
                    if not should_continue:
                        break
                    continue

                self.conversation.add_message("user", user_input)
                
                with Live(Spinner("dots", text=" Pensando..."), console=console, transient=True) as live:
                    # Primer llamado al LLM para ver si usa una herramienta
                    response = ask_claude(
                        self.conversation.get_messages(),
                        tools=self.tools
                    )

                    if response.get("type") == "error":
                        console.print(f"[error]Error de API: {response.get('error', {}).get('message', 'Desconocido')}[/error]")
                        self.conversation.reset()
                        console.print("[info]La conversación se ha reiniciado debido a un error de API.[/info]")
                        continue

                    self.conversation.add_message("assistant", response['content'])

                    # Bucle de herramientas: si el LLM quiere usar herramientas, se ejecuta este bloque
                    while response.get("stop_reason") == "tool_use":
                        tool_results = []
                        for tool_call in response.get("content", []):
                            if tool_call.get("type") == "tool_use":
                                tool_name = tool_call["name"]
                                tool_args = tool_call["input"]
                                live.update(Spinner("dots", text=f" Usando la herramienta [tool_code]{tool_name}[/tool_code]..."))
                                
                                # Ejecutar la herramienta
                                tool_result_data = await self.execute_tool(tool_name, tool_args)
                                
                                tool_results.append({
                                    "type": "tool_result",
                                    "tool_use_id": tool_call["id"],
                                    "content": json.dumps(str(tool_result_data))
                                })

                        # Añadir el resultado de la herramienta a la conversación
                        self.conversation.add_message("user", tool_results)
                        
                        live.update(Spinner("dots", text=" Pensando..."))
                        
                        # Volver a llamar al LLM con el resultado de la herramienta
                        response = ask_claude(
                            self.conversation.get_messages(),
                            tools=self.tools
                        )
                        self.conversation.add_message("assistant", response['content'])

                # Imprimir la respuesta final del asistente
                final_response_text = ""
                for content_block in response.get("content", []):
                    if content_block.get("type") == "text":
                        final_response_text += content_block["text"]
                
                console.print(f"🤖 [bold]Claude:[/bold] {final_response_text}")

            except (KeyboardInterrupt, EOFError):
                break
            except Exception as e:
                console.print(f"[error]Ocurrió un error inesperado: {e}[/error]")
        
        console.print("\n[success]¡Hasta luego! 👋[/success]")


async def main():
    """Función principal para ejecutar el chatbot."""
    chatbot = MCPChatbot()
    await chatbot.run()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        console.print("\n\n[success]¡Hasta luego! 👋[/success]")
