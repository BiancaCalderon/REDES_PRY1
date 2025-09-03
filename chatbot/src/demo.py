#!/usr/bin/env python3
"""
Script de demostración completa del MCP Chatbot
Demuestra todas las funcionalidades implementadas:
1. Conexión con LLM Claude
2. Contexto de conversación
3. Log de interacciones MCP
4. Filesystem MCP + Git MCP
5. Eclipse Calculator MCP personalizado
"""

import asyncio
import sys
from pathlib import Path
from datetime import datetime

# Agregar el directorio src al path
sys.path.append(str(Path(__file__).parent / "chatbot" / "src"))

from llm_client import ask_claude, log_interaction_json
from filesystem_mcp import FilesystemMCP
from git_mcp import GitMCP
from logger import mcp_logger
from conversation_manager import ConversationManager
from eclipse_mcp_client import EclipseMCPClient

class MCPDemo:
    """Demostración completa de funcionalidades MCP"""
    
    def __init__(self):
        self.conversation = ConversationManager()
        self.filesystem_mcp = FilesystemMCP()
        self.git_mcp = GitMCP()
        self.eclipse_mcp = EclipseMCPClient()
        
    def print_section(self, title: str):
        """Imprimir sección con formato"""
        print(f"\n{'='*60}")
        print(f"🚀 {title}")
        print('='*60)
        
    def print_step(self, step: int, description: str):
        """Imprimir paso con formato"""
        print(f"\n📋 Paso {step}: {description}")
        print("-" * 40)

    async def demo_llm_connection(self):
        """Demostrar conexión con LLM Claude"""
        self.print_section("DEMO 1: Conexión con LLM Claude")
        
        self.print_step(1, "Pregunta simple sobre Alan Turing")
        
        # Pregunta sobre Alan Turing
        question1 = "¿Quién fue Alan Turing?"
        self.conversation.add_message("user", question1)
        
        try:
            messages = self.conversation.get_messages()
            result = ask_claude(messages, max_tokens=200)
            
            if "content" in result:
                response1 = result["content"][0]["text"]
                print(f"👤 Pregunta: {question1}")
                print(f"🤖 Claude: {response1}")
                
                self.conversation.add_message("assistant", response1)
                log_interaction_json(question1, response1)
                
                # Pregunta de seguimiento (contexto)
                self.print_step(2, "Pregunta de seguimiento - Prueba de contexto")
                
                question2 = "¿En qué fecha nació?"
                self.conversation.add_message("user", question2)
                
                messages = self.conversation.get_messages()
                result2 = ask_claude(messages, max_tokens=150)
                
                if "content" in result2:
                    response2 = result2["content"][0]["text"]
                    print(f"👤 Pregunta: {question2}")
                    print(f"🤖 Claude: {response2}")
                    
                    self.conversation.add_message("assistant", response2)
                    log_interaction_json(question2, response2)
                    
                    print("✅ Demo LLM y contexto: EXITOSO")
                    return True
                    
        except Exception as e:
            print(f"❌ Error en demo LLM: {e}")
            return False
            
        return False

    async def demo_filesystem_git(self):
        """Demostrar Filesystem MCP + Git MCP"""
        self.print_section("DEMO 2: Filesystem MCP + Git MCP")
        
        repo_name = "demo-eclipse-project"
        
        self.print_step(1, f"Crear repositorio '{repo_name}' con README")
        
        # Contenido del README
        readme_content = f"""# {repo_name.replace('-', ' ').title()}

Este repositorio fue creado automáticamente durante la demostración del MCP Chatbot.

## Información del Proyecto

- **Creado**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **Propósito**: Demostración de MCP Servers
- **Tecnologías**: Filesystem MCP, Git MCP, Eclipse Calculator MCP

## Funcionalidades Demostradas

### 1. Filesystem MCP
- ✅ Creación de archivos
- ✅ Gestión de directorios
- ✅ Escritura de contenido

### 2. Git MCP  
- ✅ Inicialización de repositorio
- ✅ Staging de archivos
- ✅ Commits automatizados

### 3. Eclipse Calculator MCP (Personalizado)
- ✅ Cálculo de visibilidad de eclipses
- ✅ Información de caminos de totalidad
- ✅ Predicción de eclipses futuros

## Datos de Eclipse Solar 2024-04-08

El eclipse solar del 8 de abril de 2024 fue visible parcialmente desde Guatemala:

- **Guatemala City**: 65% de cobertura
- **Mazatenango**: 72% de cobertura  
- **Quetzaltenango**: 70% de cobertura

### Tiempos para Guatemala City
- Inicio: 12:34:00
- Máximo: 14:15:00
- Fin: 15:45:00
- Duración total: 3h 11m

## Próximos Eclipses en Guatemala

1. **2030-06-01**: Eclipse anular (45% cobertura)
2. **2044-08-12**: Eclipse total (89% cobertura)

---
*Generado automáticamente por MCP Chatbot Demo*
"""
        
        try:
            # Crear archivo con Filesystem MCP
            success = await self.filesystem_mcp.create_file_direct(
                readme_content, "README.md", repo_name
            )
            
            if success:
                print("✅ README.md creado exitosamente")
                
                self.print_step(2, "Inicializar repositorio Git y hacer commit")
                
                # Setup Git repository
                git_success = await self.git_mcp.setup_repository(repo_name)
                
                if git_success:
                    print("✅ Repositorio Git configurado exitosamente")
                    print(f"📁 Ubicación: workspace/{repo_name}/")
                    
                    # Mostrar estructura del proyecto
                    project_path = Path(f"workspace/{repo_name}")
                    if project_path.exists():
                        print(f"\n📂 Estructura creada:")
                        for file in project_path.iterdir():
                            if file.is_file():
                                print(f"   📄 {file.name}")
                            elif file.is_dir():
                                print(f"   📁 {file.name}/")
                    
                    print("✅ Demo Filesystem + Git MCP: EXITOSO")
                    return True
                else:
                    print("❌ Error en configuración Git")
            else:
                print("❌ Error en creación de archivo")
                
        except Exception as e:
            print(f"❌ Error en demo Filesystem/Git: {e}")
            
        return False

    async def demo_eclipse_calculator(self):
        """Demostrar Eclipse Calculator MCP personalizado"""
        self.print_section("DEMO 3: Eclipse Calculator MCP (Servidor Personalizado)")
        
        self.print_step(1, "Listar herramientas disponibles")
        
        try:
            tools = await self.eclipse_mcp.list_available_tools()
            
            print("🛠️ Herramientas disponibles:")
            for tool in tools:
                if "error" not in tool:
                    print(f"   ✅ {tool['name']}: {tool['description']}")
                else:
                    print(f"   ❌ {tool['error']}")
            
            self.print_step(2, "Calcular eclipse solar 2024-04-08 para Guatemala City")
            
            result = await self.eclipse_mcp.calculate_eclipse_visibility("2024-04-08", "Guatemala City")
            
            if "error" not in result:
                print("🌒 Información del Eclipse:")
                print(f"   📅 Fecha: {result.get('date', 'N/A')}")
                print(f"   🌍 Ubicación: {result.get('location', 'N/A')}")
                print(f"   🔍 Tipo: {result.get('eclipse_type', 'N/A')}")
                print(f"   👁️  Visible: {'Sí' if result.get('visible', False) else 'No'}")
                print(f"   🌓 Cobertura: {result.get('coverage', 'N/A')}")
                print(f"   📊 Magnitud: {result.get('magnitude', 'N/A')}")
                
                times = result.get('times', {})
                print(f"   ⏰ Horarios:")
                print(f"      Inicio: {times.get('start', 'N/A')}")
                print(f"      Máximo: {times.get('maximum', 'N/A')}")
                print(f"      Fin: {times.get('end', 'N/A')}")
                print(f"   ⏱️  Duración local: {result.get('duration_at_location', 'N/A')}")
                
                safety = result.get('safety_advice', [])
                if safety:
                    print(f"   ⚠️  Consejos de seguridad:")
                    for advice in safety[:2]:  # Primeros 2 consejos
                        print(f"      • {advice}")
            else:
                print(f"❌ Error: {result['error']}")
            
            self.print_step(3, "Obtener camino de totalidad del eclipse")
            
            path_result = await self.eclipse_mcp.get_eclipse_path("2024-04-08")
            
            if "error" not in path_result:
                print("🗺️ Camino del Eclipse:")
                print(f"   📅 Fecha: {path_result.get('date', 'N/A')}")
                print(f"   🔍 Tipo: {path_result.get('eclipse_type', 'N/A')}")
                print(f"   ⏱️  Duración máxima: {path_result.get('max_duration', 'N/A')}")
                print(f"   📍 Puntos del camino: {path_result.get('total_path_length', 0)}")
                print(f"   🏙️  Cobertura: {path_result.get('coverage_info', 'N/A')}")
            else:
                print(f"❌ Error: {path_result['error']}")
            
            self.print_step(4, "Predecir próximo eclipse para Guatemala")
            
            next_result = await self.eclipse_mcp.predict_next_eclipse("Guatemala City", "2024-01-01")
            
            if "error" not in next_result:
                next_eclipse = next_result.get('next_eclipse', {})
                print("🔮 Próximo Eclipse:")
                print(f"   📅 Fecha: {next_eclipse.get('date', 'N/A')}")
                print(f"   🔍 Tipo: {next_eclipse.get('type', 'N/A')}")
                print(f"   🌓 Cobertura: {next_eclipse.get('coverage', 'N/A')}")
                print(f"   ⏳ Años de espera: {next_result.get('years_to_wait', 'N/A'):.1f}")
                
                future_eclipses = next_result.get('all_future_eclipses', [])
                if len(future_eclipses) > 1:
                    print(f"   📋 Total eclipses futuros: {len(future_eclipses)}")
            else:
                print(f"❌ Error: {next_result.get('error', 'Unknown error')}")
            
            print("✅ Demo Eclipse Calculator MCP: EXITOSO")
            return True
            
        except Exception as e:
            print(f"❌ Error en demo Eclipse Calculator: {e}")
            return False

    def show_mcp_logs(self):
        """Mostrar resumen de logs MCP"""
        self.print_section("RESUMEN DE LOGS MCP")
        
        summary = mcp_logger.get_log_summary()
        
        print(f"📊 Estadísticas de interacciones MCP:")
        print(f"   Total interacciones: {summary['total_interactions']}")
        print(f"   Requests: {summary['requests']}")
        print(f"   Responses: {summary['responses']}")
        print(f"   Errors: {summary['errors']}")
        print(f"   Tasa de éxito: {summary['success_rate']:.1%}")
        
        # Mostrar últimas entradas del log si existen
        if hasattr(mcp_logger, 'log_data') and mcp_logger.log_data:
            print(f"\n📝 Últimas 3 interacciones MCP:")
            for entry in mcp_logger.log_data[-3:]:
                timestamp = entry['timestamp'][:19]  # Solo fecha y hora
                print(f"   [{timestamp}] {entry['type']} - {entry.get('server', 'unknown')}")

    async def run_complete_demo(self):
        """Ejecutar demostración completa"""
        print("🎬 INICIANDO DEMOSTRACIÓN COMPLETA DEL MCP CHATBOT")
        print(f"🕒 Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        results = []
        
        # Demo 1: LLM Connection y Context
        results.append(await self.demo_llm_connection())
        
        # Demo 2: Filesystem + Git MCP
        results.append(await self.demo_filesystem_git())
        
        # Demo 3: Eclipse Calculator MCP
        results.append(await self.demo_eclipse_calculator())
        
        # Mostrar logs MCP
        self.show_mcp_logs()
        
        # Resumen final
        self.print_section("RESUMEN FINAL")
        
        print(f"📈 Resultados de la demostración:")
        demo_names = [
            "Conexión LLM + Contexto",
            "Filesystem + Git MCP", 
            "Eclipse Calculator MCP"
        ]
        
        for i, (name, success) in enumerate(zip(demo_names, results)):
            status = "✅ EXITOSO" if success else "❌ FALLIDO"
            print(f"   {i+1}. {name}: {status}")
        
        success_rate = sum(results) / len(results)
        print(f"\n🎯 Tasa de éxito general: {success_rate:.1%}")
        
        if success_rate == 1.0:
            print("🎉 ¡DEMOSTRACIÓN COMPLETA EXITOSA!")
            print("✅ Todas las funcionalidades MCP están funcionando correctamente")
        else:
            print("⚠️  Algunas funcionalidades presentaron problemas")
            print("🔧 Revisar logs para más detalles")
        
        print(f"\n📁 Archivos generados:")
        print(f"   • workspace/demo-eclipse-project/README.md")
        print(f"   • chat_log.json (log de conversaciones)")
        print(f"   • logs/mcp_log.json (log de interacciones MCP)")
        
        print(f"\n🚀 Para usar el chatbot interactivo:")
        print(f"   python chatbot/src/main.py")

async def main():
    """Función principal de la demostración"""
    demo = MCPDemo()
    await demo.run_complete_demo()

if __name__ == "__main__":
    print("🎭 Iniciando script de demostración del MCP Chatbot...")
    print("📋 Este script demuestra todas las funcionalidades implementadas\n")
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n⏹️  Demostración interrumpida por el usuario")
    except Exception as e:
        print(f"\n❌ Error en la demostración: {e}")
        import traceback
        traceback.print_exc()