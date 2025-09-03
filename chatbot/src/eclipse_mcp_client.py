# eclipse_mcp_client.py
"""
Cliente MCP para conectar con el servidor Eclipse Calculator
"""

import asyncio
import json
import sys
from pathlib import Path
from contextlib import AsyncExitStack
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

def content_text(resp) -> str:
    """Extraer contenido de texto de respuesta MCP"""
    out = []
    parts = getattr(resp, "content", []) or []
    for p in parts:
        if isinstance(p, dict):
            if p.get("type") == "text":
                out.append(p.get("text", ""))
        else:
            if getattr(p, "type", None) == "text":
                out.append(getattr(p, "text", ""))
    return "\n".join(out).strip()

class EclipseMCPClient:
    """Cliente para el servidor Eclipse Calculator MCP"""
    
    def __init__(self):
        self.server_path = Path(__file__).parent / "eclipse_mcp_server.py"
    
    async def calculate_eclipse_visibility(self, date: str, location: str) -> dict:
        """
        Calcular visibilidad de eclipse usando el servidor MCP
        
        Args:
            date: Fecha en formato YYYY-MM-DD
            location: Ubicación (ej: "Guatemala City")
            
        Returns:
            Información del eclipse o None si hay error
        """
        try:
            # Configurar parámetros del servidor
            server_params = StdioServerParameters(
                command=sys.executable,
                args=[str(self.server_path)],
                env={"PYTHONPATH": str(Path(__file__).parent)}
            )
            
            async with AsyncExitStack() as stack:
                # Conectar al servidor
                read, write = await stack.enter_async_context(stdio_client(server_params))
                session = await stack.enter_async_context(ClientSession(read, write))
                await session.initialize()
                
                # Llamar a la herramienta
                result = await session.call_tool(
                    "calculate_eclipse_visibility",
                    {
                        "date": date,
                        "location": location
                    }
                )
                
                # Extraer y parsear respuesta
                response_text = content_text(result)
                
                if response_text:
                    try:
                        return json.loads(response_text)
                    except json.JSONDecodeError:
                        return {"error": "Invalid JSON response", "raw_response": response_text}
                else:
                    return {"error": "Empty response from server"}
                    
        except Exception as e:
            return {"error": f"Failed to connect to Eclipse MCP server: {str(e)}"}
    
    async def get_eclipse_path(self, date: str) -> dict:
        """
        Obtener camino de eclipse usando el servidor MCP
        
        Args:
            date: Fecha en formato YYYY-MM-DD
            
        Returns:
            Información del camino o None si hay error
        """
        try:
            server_params = StdioServerParameters(
                command=sys.executable,
                args=[str(self.server_path)],
                env={"PYTHONPATH": str(Path(__file__).parent)}
            )
            
            async with AsyncExitStack() as stack:
                read, write = await stack.enter_async_context(stdio_client(server_params))
                session = await stack.enter_async_context(ClientSession(read, write))
                await session.initialize()
                
                result = await session.call_tool("get_eclipse_path", {"date": date})
                response_text = content_text(result)
                
                if response_text:
                    try:
                        return json.loads(response_text)
                    except json.JSONDecodeError:
                        return {"error": "Invalid JSON response", "raw_response": response_text}
                else:
                    return {"error": "Empty response from server"}
                    
        except Exception as e:
            return {"error": f"Failed to get eclipse path: {str(e)}"}
    
    async def predict_next_eclipse(self, location: str, after_date: str = None) -> dict:
        """
        Predecir próximo eclipse usando el servidor MCP
        
        Args:
            location: Ubicación
            after_date: Fecha después de la cual buscar (opcional)
            
        Returns:
            Información del próximo eclipse o None si hay error
        """
        try:
            server_params = StdioServerParameters(
                command=sys.executable,
                args=[str(self.server_path)],
                env={"PYTHONPATH": str(Path(__file__).parent)}
            )
            
            params = {"location": location}
            if after_date:
                params["after_date"] = after_date
            
            async with AsyncExitStack() as stack:
                read, write = await stack.enter_async_context(stdio_client(server_params))
                session = await stack.enter_async_context(ClientSession(read, write))
                await session.initialize()
                
                result = await session.call_tool("predict_next_eclipse", params)
                response_text = content_text(result)
                
                if response_text:
                    try:
                        return json.loads(response_text)
                    except json.JSONDecodeError:
                        return {"error": "Invalid JSON response", "raw_response": response_text}
                else:
                    return {"error": "Empty response from server"}
                    
        except Exception as e:
            return {"error": f"Failed to predict eclipse: {str(e)}"}
    
    async def list_available_tools(self) -> list:
        """
        Listar herramientas disponibles en el servidor
        
        Returns:
            Lista de herramientas disponibles
        """
        try:
            server_params = StdioServerParameters(
                command=sys.executable,
                args=[str(self.server_path)],
                env={"PYTHONPATH": str(Path(__file__).parent)}
            )
            
            async with AsyncExitStack() as stack:
                read, write = await stack.enter_async_context(stdio_client(server_params))
                session = await stack.enter_async_context(ClientSession(read, write))
                await session.initialize()
                
                # Listar herramientas
                tools = await session.list_tools()
                
                return [
                    {
                        "name": tool.name,
                        "description": tool.description,
                        "input_schema": tool.inputSchema
                    }
                    for tool in tools.tools
                ]
                
        except Exception as e:
            return [{"error": f"Failed to list tools: {str(e)}"}]

# Función de prueba
async def test_eclipse_client():
    """Función de prueba del cliente Eclipse MCP"""
    client = EclipseMCPClient()
    
    print("Probando Eclipse Calculator MCP Client...")
    
    # Probar lista de herramientas
    print("\n1. Listando herramientas disponibles:")
    tools = await client.list_available_tools()
    for tool in tools:
        if "error" in tool:
            print(f"   {tool['error']}")
        else:
            print(f"   {tool['name']}: {tool['description']}")
    
    # Probar cálculo de eclipse
    print("\n2. Calculando eclipse para Guatemala City el 2024-04-08:")
    result = await client.calculate_eclipse_visibility("2024-04-08", "Guatemala City")
    
    if "error" in result:
        print(f"   Error: {result['error']}")
    else:
        print(f"   Eclipse visible: {result.get('visible', False)}")
        print(f"    Cobertura: {result.get('coverage', 'N/A')}")
        print(f"   Hora máxima: {result.get('times', {}).get('maximum', 'N/A')}")
    
    # Probar camino de eclipse
    print("\n3. Obteniendo camino de eclipse para 2024-04-08:")
    path_result = await client.get_eclipse_path("2024-04-08")
    
    if "error" in path_result:
        print(f"    Error: {path_result['error']}")
    else:
        print(f" Tipo: {path_result.get('eclipse_type', 'N/A')}")
        print(f" Duración máxima: {path_result.get('max_duration', 'N/A')}")
    
    print("\n Pruebas del cliente Eclipse MCP completadas!")

if __name__ == "__main__":
    asyncio.run(test_eclipse_client())