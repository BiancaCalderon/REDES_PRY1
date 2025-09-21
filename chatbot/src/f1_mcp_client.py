# src/f1_mcp_client.py
import asyncio
import os
import json
from contextlib import AsyncExitStack
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# Ruta al archivo de configuración de peers
PEERS_CONFIG_FILE = os.path.join(os.path.dirname(__file__), "others_mcp.json")

def cargar_f1_config():
    if not os.path.exists(PEERS_CONFIG_FILE):
        return None
    with open(PEERS_CONFIG_FILE, "r", encoding="utf-8") as f:
        peers = json.load(f)
        return peers.get("f1")

class F1MCPClient:
    def __init__(self):
        f1_config = cargar_f1_config()
        if not f1_config:
            raise ValueError("No se encontró la configuración para F1 MCP en others_mcp.json")

        # CORREGIR ESTA RUTA: Apunta al directorio 'src' del proyecto de tu compañero
        # Ejemplo: "/home/bianca_cal/mcp_net/src"
        f1_config['cwd'] = "/home/bianca_cal/mcp_net/src" # ¡¡¡IMPORTANTE: AJUSTA ESTA RUTA!!!

        self.server_params = StdioServerParameters(
            command=f1_config['command'],
            args=f1_config['args'],
            cwd=f1_config['cwd']
        )
        self.stack = AsyncExitStack()
        self.session = None

    async def __aenter__(self):
        self.read, self.write = await self.stack.enter_async_context(stdio_client(self.server_params))
        self.session = await self.stack.enter_async_context(ClientSession(self.read, self.write))
        await self.session.initialize()
        return self

    async def __aexit__(self, exc_type, exc, tb):
        await self.stack.aclose()

    async def get_calendar(self, season):
        return await self.session.call_tool("get_calendar", {"season": season})

    async def get_race(self, race_id):
        return await self.session.call_tool("get_race", {"race_id": race_id})

    async def recommend_strategy(self, race_id, base_laptime_s, deg_soft_s, deg_medium_s, deg_hard_s, min_stint_laps, max_stint_laps, max_stops=2):
        return await self.session.call_tool("recommend_strategy", {
            "race_id": race_id,
            "base_laptime_s": base_laptime_s,
            "deg_soft_s": deg_soft_s,
            "deg_medium_s": deg_medium_s,
            "deg_hard_s": deg_hard_s,
            "min_stint_laps": min_stint_laps,
            "max_stint_laps": max_stint_laps,
            "max_stops": max_stops
        })

async def main():
    async with F1MCPClient() as client:
        # Ejemplo de uso
        calendar = await client.get_calendar(2024)
        print("Calendario 2024:", calendar)

        race_info = await client.get_race("monaco_2024")
        print("Información de la carrera de Mónaco 2024:", race_info)

        strategy = await client.recommend_strategy(
            race_id="monaco_2024",
            base_laptime_s=75.0,
            deg_soft_s=0.1,
            deg_medium_s=0.07,
            deg_hard_s=0.05,
            min_stint_laps=10,
            max_stint_laps=30,
            max_stops=2
        )
        print("Estrategia recomendada:", strategy)

if __name__ == "__main__":
    asyncio.run(main())