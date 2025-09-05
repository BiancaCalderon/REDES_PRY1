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

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt
from rich.theme import Theme

console = Console(theme=Theme({
    "menu": "bold cyan",
    "option": "bold yellow",
    "input": "bold green",
    "error": "bold red",
    "success": "bold green",
    "title": "bold magenta",
    "highlight": "bold white on blue"
}))

PEERS_CONFIG_FILE = os.path.join(os.path.dirname(__file__), "others_mcp.json")

def cargar_peers():
    if not os.path.exists(PEERS_CONFIG_FILE):
        return {}
    with open(PEERS_CONFIG_FILE, "r", encoding="utf-8") as f:
        return _json.load(f)

MENU_OPTIONS = [
    ("Chat General (LLM)", "chat_general"),
    ("Astronomía (Eclipse MCP)", "astronomia"),
    ("F1 Strategy (F1 MCP)", "f1"),
    ("MCP de Compañero 1", "mcp1"),
    ("MCP de Compañero 2", "mcp2"),
    ("MCP Remoto", "mcp_remoto"),
    ("Ver logs", "logs"),
    ("Salir", "salir")
]

def mostrar_menu():
    console.clear()
    console.print(Panel("[title]🤖 [bold]MCP Chatbot - Menú Principal[/bold]", style="title"))
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Opción", style="option", width=8)
    table.add_column("Descripción", style="menu")
    for idx, (desc, _) in enumerate(MENU_OPTIONS, 1):
        table.add_row(str(idx), desc)
    console.print(table)

def seleccionar_opcion():
    while True:
        try:
            opcion = Prompt.ask("[input]Selecciona una opción (1-8)", default="1")
            idx = int(opcion)
            if 1 <= idx <= len(MENU_OPTIONS):
                return MENU_OPTIONS[idx-1][1]
            else:
                console.print("[error]Opción fuera de rango. Intenta de nuevo.")
        except ValueError:
            console.print("[error]Entrada inválida. Ingresa un número.")

async def f1_mcp_loop():
    """Bucle para interactuar con el MCP de F1."""
    console.clear()
    console.print(Panel("[title]🏎️ [bold]Menú F1 Strategy (MCP)[/bold]", style="title"))
    console.print("Interactúa con el servidor F1 MCP de tu compañero.")
    console.print("Comandos disponibles:")
    console.print("  - [bold]/f1_calendar <año>[/bold]")
    console.print("  - [bold]/f1_race <race_id>[/bold]")
    console.print("  - [bold]/f1_plan <...args...>[/bold]")
    console.print("  - [bold]volver[/bold] (para regresar al menú principal)")
    
    chatbot = MCPChatbot()

    while True:
        try:
            command = Prompt.ask("[input]Comando F1[/input]").strip()
            if command.lower() in ["volver", "salir", "exit"]:
                break
            if not command.startswith("/f1"):
                console.print("[error]Comando inválido. Debe empezar con /f1")
                continue
            
            await chatbot.handle_special_command(command)
        except Exception as e:
            console.print(f"[error]Error: {e}")

async def astronomia_mcp_loop():
    """Bucle para interactuar con el MCP de Astronomía (DB Version)."""
    async with EclipseMCPClient() as client:
        while True:
            console.clear()
            console.print(Panel("[title]🔭 [bold]Menú de Astronomía (Base de Datos Interna)[/bold]", style="title"))
            
            astro_menu = Table(show_header=False, box=None)
            astro_menu.add_row("[option]1[/option]", "Listar eclipses por año")
            astro_menu.add_row("[option]2[/option]", "Verificar visibilidad de eclipse")
            astro_menu.add_row("[option]3[/option]", "Predecir próximo eclipse visible")
            astro_menu.add_row("[option]4[/option]", "Volver al menú principal")
            console.print(astro_menu)

            choice = Prompt.ask("\n[input]Elige una opción[/input]", choices=["1", "2", "3", "4"], default="4")

            if choice == '1':
                year_str = Prompt.ask("[input]Ingresa el año (YYYY)[/input]")
                try:
                    year = int(year_str)
                    console.print("\n[highlight]Buscando...[/highlight]")
                    result = await client.list_eclipses_by_year(year)
                    if result and not result.get("error"):
                        eclipses = result.get('eclipses', [])
                        table = Table(title=f"Eclipses en {year}")
                        table.add_column("Fecha", style="bold green")
                        table.add_column("Tipo", style="cyan")
                        table.add_column("Descripción", style="magenta")
                        table.add_column("Visible en", style="yellow")
                        if eclipses:
                            for e in eclipses:
                                locations = ", ".join(e.get('visible_in', [])) or "N/A"
                                table.add_row(e.get('date'), e.get('type'), e.get('description'), locations)
                        else:
                            table.add_row(f"No hay datos para {year}", "", "", "")
                        console.print(table)
                    else:
                        console.print(Panel(f"Error: {result.get('error', 'Desconocido')}", title="[error]Error[/error]"))
                except ValueError:
                    console.print(Panel("Año inválido.", title="[error]Error[/error]"))
                Prompt.ask("\n[input]Presiona Enter para continuar...[/input]")

            elif choice == '2':
                date = Prompt.ask("[input]Ingresa la fecha (YYYY-MM-DD)[/input]")
                location = Prompt.ask("[input]Ingresa la ubicación (ej: Guatemala City)[/input]")
                console.print("\n[highlight]Calculando...[/highlight]")
                result = await client.calculate_eclipse_visibility(date, location)
                if result and not result.get("error"):
                    panel_content = f"[bold]Fecha:[/bold] {result.get('date', 'N/A')}\n"
                    panel_content += f"[bold]Ubicación:[/bold] {result.get('location', 'N/A')}\n"
                    panel_content += f"[bold]Visible:[/bold] {'Sí' if result.get('visible') else 'No'}\n"
                    if result.get('visible'):
                        panel_content += f"[bold]Cobertura:[/bold] {result.get('coverage', 'N/A')}\n"
                        panel_content += f"[bold]Hora Máxima:[/bold] {result.get('max_time', 'N/A')}"
                    console.print(Panel(panel_content, title="[success]Resultado de Visibilidad[/success]"))
                else:
                    console.print(Panel(f"Error: {result.get('error', 'Desconocido')}", title="[error]Error[/error]"))
                Prompt.ask("\n[input]Presiona Enter para continuar...[/input]")

            elif choice == '3':
                location = Prompt.ask("[input]Ingresa la ubicación (ej: Guatemala City)[/input]")
                console.print("\n[highlight]Buscando...[/highlight]")
                result = await client.predict_next_eclipse(location)
                if result and not result.get("error"):
                    next_eclipse = result.get('next_eclipse', {})
                    panel_content = f"[bold]Fecha:[/bold] {next_eclipse.get('date', 'N/A')}\n"
                    panel_content += f"[bold]Tipo:[/bold] {next_eclipse.get('type', 'N/A')}\n"
                    panel_content += f"[bold]Descripción:[/bold] {next_eclipse.get('description', 'N/A')}"
                    console.print(Panel(panel_content, title=f"[success]Próximo Eclipse en {location}[/success]"))
                else:
                    console.print(Panel(f"Error: {result.get('error', 'Desconocido')}", title="[error]Error[/error]"))
                Prompt.ask("\n[input]Presiona Enter para continuar...[/input]")

            elif choice == '4':
                break




async def main_menu_loop():
    """Bucle del menú principal mejorado."""
    while True:
        mostrar_menu()
        seleccion = seleccionar_opcion()
        if seleccion == "astronomia":
            await astronomia_mcp_loop()
        elif seleccion == "f1":
            await f1_mcp_loop()
        elif seleccion == "salir":
            console.print("[success]¡Hasta luego! 👋")
            break
        else:
            console.print(Panel(f"[highlight]Opción '{seleccion}' - Próximamente...[/highlight]"))
            Prompt.ask("[input]Presiona Enter para volver al menú...")




class MCPChatbot:
    """Chatbot principal que integra múltiples servidores MCP"""

    def __init__(self):
        self.conversation = ConversationManager()
        self.logger = MCPLogger()
        self.filesystem_mcp = FilesystemMCP()
        self.git_mcp = GitMCP()
        self.eclipse_mcp = EclipseMCPClient()
        self.external_servers = {}  # Servidores MCP de compañeros

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
        print("• Integración con servidores MCP de compañeros")
        print("• Comandos especiales:")
        print("  - /create-repo <nombre>       : Crear repositorio con README")
        print("  - /eclipse <fecha>            : Calcular eclipse solar")
        print("  - /f1_calendar <año>          : Calendario F1 MCP")
        print("  - /f1_race <race_id>          : Info carrera F1 MCP")
        print("  - /f1_plan <race_id> <base_laptime> <deg_soft> <deg_medium> <deg_hard> <min_stint> <max_stint> <max_stops> : Estrategia F1")
        print("  - /use-server <ruta>          : Registrar servidor MCP externo")
        print("  - /call <ruta> <tool> {json}  : Invocar herramienta de servidor externo")
        print("  - /help                       : Mostrar ayuda")
        print("  - /log                        : Mostrar log MCP")
        print("  - /salir                      : Terminar")
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

        elif cmd in ["/salir", "/exit", "/quit"]:
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

        # --- INICIO: Comandos F1 MCP ---
        elif cmd == "/f1_calendar":
            if len(parts) < 2:
                print("Uso: /f1_calendar <año>")
                return True
            season = int(parts[1])
            try:
                async with F1MCPClient() as f1:
                    result = await f1.get_calendar(season)
                    print("\n📅 Calendario F1:")
                    print(result)
                    self.logger.log_mcp_request("F1 MCP", "get_calendar", {"season": season})
                    self.logger.log_mcp_response("F1 MCP", "get_calendar", result)
            except Exception as e:
                print(f"Error F1 MCP: {e}")
                self.logger.log_mcp_error("F1 MCP", "get_calendar", str(e))
            return True

        elif cmd == "/f1_race":
            if len(parts) < 2:
                print("Uso: /f1_race <race_id>")
                return True
            race_id = parts[1]
            try:
                async with F1MCPClient() as f1:
                    result = await f1.get_race(race_id)
                    print("\n🏁 Info carrera F1:")
                    print(result)
                    self.logger.log_mcp_request("F1 MCP", "get_race", {"race_id": race_id})
                    self.logger.log_mcp_response("F1 MCP", "get_race", result)
            except Exception as e:
                print(f"Error F1 MCP: {e}")
                self.logger.log_mcp_error("F1 MCP", "get_race", str(e))
            return True

        elif cmd == "/f1_plan":
            if len(parts) < 9:
                print("Uso: /f1_plan <race_id> <base_laptime> <deg_soft> <deg_medium> <deg_hard> <min_stint> <max_stint> <max_stops>")
                return True
            race_id = parts[1]
            try:
                base_laptime = float(parts[2])
                deg_soft = float(parts[3])
                deg_medium = float(parts[4])
                deg_hard = float(parts[5])
                min_stint = int(parts[6])
                max_stint = int(parts[7])
                max_stops = int(parts[8])
                async with F1MCPClient() as f1:
                    result = await f1.recommend_strategy(race_id, base_laptime, deg_soft, deg_medium, deg_hard, min_stint, max_stint, max_stops)
                    print("\n📝 Estrategia F1 recomendada:")
                    print(result)
                    self.logger.log_mcp_request("F1 MCP", "recommend_strategy", {
                        "race_id": race_id,
                        "base_laptime": base_laptime,
                        "deg_soft": deg_soft,
                        "deg_medium": deg_medium,
                        "deg_hard": deg_hard,
                        "min_stint": min_stint,
                        "max_stint": max_stint,
                        "max_stops": max_stops
                    })
                    self.logger.log_mcp_response("F1 MCP", "recommend_strategy", result)
            except Exception as e:
                print(f"Error F1 MCP: {e}")
                self.logger.log_mcp_error("F1 MCP", "recommend_strategy", str(e))
            return True
        # --- FIN: Comandos F1 MCP ---

        elif cmd == "/use-server":
            if len(parts) < 2:
                print("Uso: /use-server <ruta_al_server.py>")
                return True
            server_path = parts[1]
            try:
                client = ExternalMCPClient(server_path)
                await client.connect()
                tools = await client.list_tools()
                self.external_servers[server_path] = client
                print(f"Servidor {server_path} registrado con {len(tools)} herramientas:")
                for t in tools:
                    print(f" - {t['name']}: {t['description']}")
            except Exception as e:
                print(f"Error al registrar servidor: {e}")
            return True

        elif cmd == "/call":
            if len(parts) < 3:
                print("Uso: /call <ruta_al_server.py> <tool> {args_json}")
                return True
            server_path = parts[1]
            tool_name = parts[2]
            args_json = " ".join(parts[3:])
            try:
                args = json.loads(args_json) if args_json else {}
            except:
                args = {}

            if server_path not in self.external_servers:
                print("Ese servidor no está registrado. Usa /use-server primero.")
                return True

            try:
                result = await self.external_servers[server_path].call_tool(tool_name, args)
                print("📡 Resultado:", json.dumps(result, indent=2, ensure_ascii=False))
            except Exception as e:
                print(f"Error al llamar herramienta: {e}")
            return True

        return None  # No es comando especial

    async def demo_filesystem_git(self, repo_name: str):
        """Demo de Filesystem MCP + Git MCP"""
        print(f"\nCreando repositorio '{repo_name}' con Filesystem y Git MCP...")

        readme_content = f"""# {repo_name.replace('-', ' ').title()}

Este repositorio fue creado automáticamente usando MCP servers.

## Información del Proyecto

- **Creado**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **Tecnología**: Model Context Protocol (MCP)
- **Servidores utilizados**: Filesystem MCP, Git MCP

## Funcionalidades MCP

- Creación de archivos via Filesystem MCP
- Control de versiones via Git MCP
- Integración con chatbot

---
*Generado automáticamente por MCP Chatbot*
"""
        try:
            self.logger.log_mcp_request("Filesystem MCP", "create_file", {
                "filename": "README.md",
                "repo_name": repo_name
            })
            success = await self.filesystem_mcp.create_file_direct(
                readme_content, "README.md", repo_name
            )
            if success:
                self.logger.log_mcp_response("Filesystem MCP", "success")
                print("README.md creado exitosamente")

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
                print(f"   👁️ Visible: {'Sí' if result.get('visible', False) else 'No'}")
                if result.get('visible'):
                    print(f"   🌓 Cobertura: {result.get('coverage', 'N/A')}")
                    print(f"   ⏰ Hora máxima: {result.get('max_time', 'N/A')}")
                    print(f"   ⏱️ Duración: {result.get('duration', 'N/A')}")
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
            enhanced_input = self.enhance_input_with_mcp_context(user_input)
            self.conversation.add_message("user", enhanced_input)
            messages = self.conversation.get_messages()
            result = ask_claude(messages, max_tokens=1500)

            if "content" in result and result["content"]:
                assistant_message = result["content"][0]["text"]
            else:
                assistant_message = "[Sin respuesta del LLM]"

            print(f"\n🤖 Claude: {assistant_message}")
            self.conversation.add_message("assistant", assistant_message)
            log_interaction_json(user_input, assistant_message)
            return True

        except Exception as e:
            print(f"Error al comunicarse con Claude: {e}")
            return True

    def enhance_input_with_mcp_context(self, user_input: str) -> str:
        """Mejorar input del usuario con contexto MCP disponible"""
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
                print()
            except KeyboardInterrupt:
                print("\n\n👋 ¡Hasta luego!")
                break
            except Exception as e:
                print(f"Error inesperado: {e}")
                continue


async def main():
    chatbot = MCPChatbot()
    await chatbot.run()


if __name__ == "__main__":
    try:
        asyncio.run(main_menu_loop())
    except KeyboardInterrupt:
        print("\n\n👋 ¡Hasta luego!")
