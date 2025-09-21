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
    ("Personal Trainer MCP", "personal_trainer"),
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
            opcion = Prompt.ask(f"[input]Selecciona una opción (1-{len(MENU_OPTIONS)})", default="1")
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

async def personal_trainer_mcp_loop(logger: MCPLogger):
    """Bucle para interactuar con el MCP de Personal Trainer."""
    console.clear()
    console.print(Panel("[title]🏋️ [bold]Menú Personal Trainer (MCP)[/bold]", style="title"))
    console.print("Comandos disponibles:")
    console.print("  - /metrics <sexo> <edad> <altura_cm> <peso_kg>")
    console.print("  - /recommend <objetivo> <deporte> <limite>")
    console.print("  - /routine <objetivo> <dias> <minutos> <experiencia>")
    console.print("  - /recommend_metrics <sexo> <edad> <altura_cm> <peso_kg> <objetivo> <limite>")
    console.print("  - volver")

    server_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'personal_trainer_mcp', 'server.py'))
    
    while True:
        try:
            command = Prompt.ask("[input]Comando[/input]").strip()
            if command.lower() == "volver":
                break

            parts = command.split()
            cmd = parts[0]
            
            async with ExternalMCPClient(server_path) as client:
                if cmd == "/metrics":
                    if len(parts) != 5:
                        console.print("[error]Uso: /metrics <sexo> <edad> <altura_cm> <peso_kg>")
                        continue
                    sexo = parts[1]
                    edad = int(parts[2])
                    altura_cm = int(parts[3])
                    peso_kg = int(parts[4])
                    result = await client.call_tool("compute_metrics", {"args": {"sexo": sexo, "edad": edad, "altura_cm": altura_cm, "peso_kg": peso_kg}})
                    console.print(Panel(json.dumps(result, indent=2), title="[success]Métricas Calculadas[/success]"))
                
                elif cmd == "/recommend":
                    if len(parts) != 4:
                        console.print("[error]Uso: /recommend <objetivo> <deporte> <limite>")
                        continue
                    objetivo = parts[1]
                    deporte = parts[2]
                    limite = int(parts[3])
                    result = await client.call_tool("recommend_exercises", {"args": {"objetivo": objetivo, "deporte": deporte, "limite": limite}})
                    console.print(Panel(json.dumps(result, indent=2), title="[success]Ejercicios Recomendados[/success]"))

                elif cmd == "/routine":
                    if len(parts) != 5:
                        console.print("[error]Uso: /routine <objetivo> <dias> <minutos> <experiencia>")
                        continue
                    objetivo = parts[1]
                    dias = int(parts[2])
                    minutos = int(parts[3])
                    exp = parts[4]
                    result = await client.call_tool("build_routine_tool", {"args": {"objetivo": objetivo, "dias_por_semana": dias, "minutos_por_sesion": minutos, "experiencia": exp}})
                    console.print(Panel(json.dumps(result, indent=2), title="[success]Rutina Semanal[/success]"))

                elif cmd == "/recommend_metrics":
                    if len(parts) != 7:
                        console.print("[error]Uso: /recommend_metrics <sexo> <edad> <altura_cm> <peso_kg> <objetivo> <limite>")
                        continue
                    sexo = parts[1]
                    edad = int(parts[2])
                    altura_cm = int(parts[3])
                    peso_kg = int(parts[4])
                    objetivo = parts[5]
                    limite = int(parts[6])
                    result = await client.call_tool("recommend_by_metrics_tool", {"args": {"sexo": sexo, "edad": edad, "altura_cm": altura_cm, "peso_kg": peso_kg, "objetivo": objetivo, "limite": limite}})
                    console.print(Panel(json.dumps(result, indent=2), title="[success]Recomendaciones por Métricas[/success]"))

                else:
                    console.print("[error]Comando no válido.")

        except Exception as e:
            console.print(f"[error]Error: {e}")



async def astronomia_mcp_loop(logger: MCPLogger):
    """Bucle para interactuar con el MCP de Astronomía (DB Version)."""
    try:
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
                        params = {"year": year}
                        logger.log_mcp_request("Eclipse MCP", "list_eclipses_by_year", params)
                        result = await client.list_eclipses_by_year(year)
                        logger.log_mcp_response("Eclipse MCP", "list_eclipses_by_year", result, success=not result.get("error"))
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
                            logger.log_mcp_error("Eclipse MCP", "list_eclipses_by_year", result.get('error', 'Desconocido'))
                            console.print(Panel(f"Error: {result.get('error', 'Desconocido')}", title="[error]Error[/error]"))
                    except ValueError:
                        console.print(Panel("Año inválido.", title="[error]Error[/error]"))
                    Prompt.ask("\n[input]Presiona Enter para continuar...[/input]")

                elif choice == '2':
                    date = Prompt.ask("[input]Ingresa la fecha (YYYY-MM-DD)[/input]")
                    location = Prompt.ask("[input]Ingresa la ubicación (ej: Guatemala City)[/input]")
                    console.print("\n[highlight]Calculando...[/highlight]")
                    params = {"date": date, "location": location}
                    logger.log_mcp_request("Eclipse MCP", "calculate_eclipse_visibility", params)
                    result = await client.calculate_eclipse_visibility(date, location)
                    logger.log_mcp_response("Eclipse MCP", "calculate_eclipse_visibility", result, success=not result.get("error"))
                    if result and not result.get("error"):
                        panel_content = f"[bold]Fecha:[/bold] {result.get('date', 'N/A')}\n"
                        panel_content += f"[bold]Ubicación:[/bold] {result.get('location', 'N/A')}\n"
                        panel_content += f"[bold]Visible:[/bold] {'Sí' if result.get('visible') else 'No'}\n"
                        if result.get('visible'):
                            panel_content += f"[bold]Cobertura:[/bold] {result.get('coverage', 'N/A')}\n"
                            panel_content += f"[bold]Hora Máxima:[/bold] {result.get('max_time', 'N/A')}"
                        console.print(Panel(panel_content, title="[success]Resultado de Visibilidad[/success]"))
                    else:
                        logger.log_mcp_error("Eclipse MCP", "calculate_eclipse_visibility", result.get('error', 'Desconocido'))
                        console.print(Panel(f"Error: {result.get('error', 'Desconocido')}", title="[error]Error[/error]"))
                    Prompt.ask("\n[input]Presiona Enter para continuar...[/input]")

                elif choice == '3':
                    location = Prompt.ask("[input]Ingresa la ubicación (ej: Guatemala City)[/input]")
                    console.print("\n[highlight]Buscando...[/highlight]")
                    params = {"location": location}
                    logger.log_mcp_request("Eclipse MCP", "predict_next_eclipse", params)
                    result = await client.predict_next_eclipse(location)
                    logger.log_mcp_response("Eclipse MCP", "predict_next_eclipse", result, success=not result.get("error"))
                    if result and not result.get("error"):
                        next_eclipse = result.get('next_eclipse', {})
                        panel_content = f"[bold]Fecha:[/bold] {next_eclipse.get('date', 'N/A')}\n"
                        panel_content += f"[bold]Tipo:[/bold] {next_eclipse.get('type', 'N/A')}\n"
                        panel_content += f"[bold]Descripción:[/bold] {next_eclipse.get('description', 'N/A')}"
                        console.print(Panel(panel_content, title=f"[success]Próximo Eclipse en {location}[/success]"))
                    else:
                        logger.log_mcp_error("Eclipse MCP", "predict_next_eclipse", result.get('error', 'Desconocido'))
                        console.print(Panel(f"Error: {result.get('error', 'Desconocido')}", title="[error]Error[/error]"))
                    Prompt.ask("\n[input]Presiona Enter para continuar...[/input]")

                elif choice == '4':
                    break
    except Exception as e:
        logger.log_mcp_error("Eclipse MCP", "connection_error", str(e))
        console.print(f"[error]Error al conectar con Eclipse MCP: {e}")
        Prompt.ask("\n[input]Presiona Enter para continuar...[/input]")



async def remote_mcp_loop():
    """Bucle para interactuar con el MCP Remoto."""
    console.clear()
    console.print(Panel("[title]📡 [bold]Menú MCP Remoto (Eclipse Calculator)[/bold]", style="title"))

    # Cargar configuración para obtener la URL
    config = {}
    try:
        with open(os.path.join(os.path.dirname(__file__), '..', 'config', 'config.json')) as f:
            config = json.load(f)
    except FileNotFoundError:
        console.print("[error]Archivo de configuración no encontrado.[/error]")
        Prompt.ask("[input]Presiona Enter para continuar...[/input]")
        return
    
    if "REMOTE_MCP_URL" not in config or not config["REMOTE_MCP_URL"]:
        console.print("[error]La URL para 'REMOTE_MCP_URL' no está definida en el archivo de configuración.[/error]")
        Prompt.ask("[input]Presiona Enter para continuar...[/input]")
        return

    client = RemoteMcpClient(config)

    while True:
        console.clear()
        console.print(Panel("[title]📡 [bold]Menú MCP Remoto (Eclipse Calculator)[/bold]", style="title"))
        
        remote_menu = Table(show_header=False, box=None)
        remote_menu.add_row("[option]1[/option]", "Verificar Conexión (status)")
        remote_menu.add_row("[option]2[/option]", "Listar eclipses por año")
        remote_menu.add_row("[option]3[/option]", "Calcular visibilidad de eclipse")
        remote_menu.add_row("[option]4[/option]", "Predecir próximo eclipse")
        remote_menu.add_row("[option]5[/option]", "Obtener ruta de eclipse")
        remote_menu.add_row("[option]6[/option]", "Obtener consejos de seguridad")
        remote_menu.add_row("[option]7[/option]", "Volver al menú principal")
        console.print(remote_menu)

        choice = Prompt.ask("\n[input]Elige una opción[/input]", choices=["1", "2", "3", "4", "5", "6", "7"], default="7")

        if choice == '1':
            result = client.check_server_status()
            console.print(Panel(json.dumps(result, indent=2), title="[success]Estado del Servidor[/success]"))
            Prompt.ask("\n[input]Presiona Enter para continuar...[/input]")

        elif choice == '2':
            year = int(Prompt.ask("[input]Ingresa el año[/input]"))
            result = client.list_eclipses_by_year(year)
            console.print(Panel(json.dumps(result, indent=2), title=f"[success]Eclipses en {year}[/success]"))
            Prompt.ask("\n[input]Presiona Enter para continuar...[/input]")
        
        elif choice == '3':
            date = Prompt.ask("[input]Ingresa la fecha (YYYY-MM-DD)[/input]")
            location = Prompt.ask("[input]Ingresa la ubicación[/input]")
            result = client.calculate_eclipse_visibility(date, location)
            console.print(Panel(json.dumps(result, indent=2), title="[success]Visibilidad de Eclipse[/success]"))
            Prompt.ask("\n[input]Presiona Enter para continuar...[/input]")

        elif choice == '4':
            location = Prompt.ask("[input]Ingresa la ubicación[/input]")
            result = client.predict_next_eclipse(location)
            console.print(Panel(json.dumps(result, indent=2), title="[success]Próximo Eclipse[/success]"))
            Prompt.ask("\n[input]Presiona Enter para continuar...[/input]")

        elif choice == '5':
            date = Prompt.ask("[input]Ingresa la fecha (YYYY-MM-DD)[/input]")
            result = client.get_eclipse_path(date)
            console.print(Panel(json.dumps(result, indent=2), title="[success]Ruta del Eclipse[/success]"))
            Prompt.ask("\n[input]Presiona Enter para continuar...[/input]")

        elif choice == '6':
            date = Prompt.ask("[input]Ingresa la fecha (YYYY-MM-DD)[/input]")
            result = client.get_safety_advice(date)
            console.print(Panel(json.dumps(result, indent=2), title="[success]Consejos de Seguridad[/success]"))
            Prompt.ask("\n[input]Presiona Enter para continuar...[/input]")
        
        elif choice == '7':
            break



async def main_menu_loop():
    """Bucle del menú principal mejorado."""
    chatbot = MCPChatbot() # Instanciar una vez

    while True:
        mostrar_menu()
        seleccion = seleccionar_opcion()
        
        if seleccion == "chat_general":
            await chat_general_loop(chatbot)
        elif seleccion == "astronomia":
            await astronomia_mcp_loop(chatbot.logger)
        elif seleccion == "f1":
            await f1_mcp_loop()
        elif seleccion == "personal_trainer":
            await personal_trainer_mcp_loop(chatbot.logger)
        elif seleccion == "mcp_remoto":
            await remote_mcp_loop()
        elif seleccion == "logs":
            await view_logs_loop()
        elif seleccion == "salir":
            console.print("[success]¡Hasta luego! 👋")
            break

async def chat_general_loop(chatbot: 'MCPChatbot'):
    """Bucle para el chat general con el LLM."""
    console.clear()
    console.print(Panel("[title]💬 [bold]Chat General (LLM)[/bold]", style="title"))
    console.print("Escribe tu mensaje o usa [bold]/help[/bold] para ver los comandos. Escribe [bold]volver[/bold] para regresar.")
    
    while True:
        try:
            user_input = Prompt.ask("👤 Tú").strip()
            if user_input.lower() == "volver":
                break
            if not await chatbot.process_user_input(user_input):
                break # Salir si el comando lo indica
        except (KeyboardInterrupt, EOFError):
            break
    console.print()

async def view_logs_loop():
    """Muestra los logs de MCP y espera para volver al menú."""
    console.clear()
    console.print(Panel("[title]📄 [bold]Visor de Logs MCP[/bold]", style="title"))
    logger = MCPLogger()
    summary = logger.get_log_summary()

    table = Table(title="Resumen de Interacciones MCP")
    table.add_column("Métrica", style="cyan")
    table.add_column("Valor", style="magenta")
    table.add_row("Total de Interacciones", str(summary['total_interactions']))
    table.add_row("Peticiones (Requests)", str(summary['requests']))
    table.add_row("Respuestas (Responses)", str(summary['responses']))
    table.add_row("Errores", str(summary['errors']))
    table.add_row("Tasa de Éxito", f"{summary['success_rate']:.1%}")
    console.print(table)

    if hasattr(logger, 'log_data') and logger.log_data:
        console.print("\n[bold]Últimas 10 entradas del log:[/bold]")
        log_table = Table(show_header=True, header_style="bold yellow")
        log_table.add_column("Timestamp", width=20)
        log_table.add_column("Tipo")
        log_table.add_column("Servidor")
        log_table.add_column("Detalle")
        
        for entry in logger.log_data[-10:]:
            timestamp = entry.get('timestamp', '')[:19].replace("T", " ")
            log_type = entry.get('type', '')
            server = entry.get('server', 'N/A')
            detail = ""
            if log_type == "mcp_request":
                detail = f"Método: {entry.get('method')}"
            elif log_type == "mcp_response":
                detail = f"Método: {entry.get('method')}, Éxito: {'✅' if entry.get('success') else '❌'}"
            elif log_type == "mcp_error":
                detail = f"Error: {entry.get('error')}"

            log_table.add_row(timestamp, log_type, server, detail)
        console.print(log_table)
    else:
        console.print("\nNo hay entradas en el log.")

    Prompt.ask("\n[input]Presiona Enter para volver al menú...[/input]")




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
            self.logger.show_logs(console)
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
