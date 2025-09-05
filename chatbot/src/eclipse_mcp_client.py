# eclipse_mcp_client.py
"""
Cliente MCP para conectar con el servidor Eclipse Calculator (DB Version)
"""

import asyncio
import json
import sys
from pathlib import Path
from contextlib import AsyncExitStack
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

def content_text(resp) -> str:
    return resp.content[0].text if resp.content and resp.content[0].type == "text" else "{}"

class EclipseMCPClient:
    def __init__(self):
        self.server_path = Path(__file__).parent / "eclipse_mcp_server.py"
        self.server_params = StdioServerParameters(command=sys.executable, args=[str(self.server_path)])
        self.stack = AsyncExitStack()
        self.session = None

    async def __aenter__(self):
        read, write = await self.stack.enter_async_context(stdio_client(self.server_params))
        self.session = await self.stack.enter_async_context(ClientSession(read, write))
        await self.session.initialize()
        return self

    async def __aexit__(self, exc_type, exc, tb):
        await self.stack.aclose()

    async def _call_tool(self, tool_name: str, params: dict) -> dict:
        if not self.session:
            raise ConnectionError("Session not initialized. Use 'async with' context manager.")
        try:
            result = await self.session.call_tool(tool_name, params)
            return json.loads(content_text(result))
        except Exception as e:
            return {"error": str(e)}

    async def list_eclipses_by_year(self, year: int) -> dict:
        return await self._call_tool("list_eclipses_by_year", {"year": year})

    async def calculate_eclipse_visibility(self, date: str, location: str) -> dict:
        return await self._call_tool("calculate_eclipse_visibility", {"date": date, "location": location})

    async def predict_next_eclipse(self, location: str) -> dict:
        return await self._call_tool("predict_next_eclipse", {"location": location})