# external_mcp_client.py
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

class ExternalMCPClient:
    """Cliente genérico para servidores MCP externos"""
    
    def __init__(self, server_path: str):
        self.server_path = Path(server_path)
        self.session = None
        self.stack = None

    async def __aenter__(self):
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc, tb):
        await self.close()
    
    async def connect(self):
        """Conectar al servidor MCP"""
        server_params = StdioServerParameters(
            command=sys.executable,
            args=[str(self.server_path)]
        )
        self.stack = AsyncExitStack()
        read, write = await self.stack.enter_async_context(stdio_client(server_params))
        self.session = await self.stack.enter_async_context(ClientSession(read, write))
        await self.session.initialize()
    
    async def list_tools(self):
        """Listar herramientas del servidor"""
        tools = await self.session.list_tools()
        return [
            {
                "name": t.name,
                "description": t.description,
                "schema": t.inputSchema
            }
            for t in tools.tools
        ]
    
    async def call_tool(self, name: str, arguments: dict):
        """Ejecutar una herramienta"""
        result = await self.session.call_tool(name, arguments)
        text = content_text(result)
        try:
            return json.loads(text)
        except:
            return {"raw_response": text}
    
    async def close(self):
        """Cerrar conexión"""
        if self.stack:
            await self.stack.aclose()
