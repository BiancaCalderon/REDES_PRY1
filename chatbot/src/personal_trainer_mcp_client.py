import asyncio
import os
import json
from contextlib import AsyncExitStack
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

PEERS_CONFIG_FILE = os.path.join(os.path.dirname(__file__), "others_mcp.json")

def cargar_personal_trainer_config():
    if not os.path.exists(PEERS_CONFIG_FILE):
        return None
    with open(PEERS_CONFIG_FILE, "r", encoding="utf-8") as f:
        peers = json.load(f)
        return peers.get("personal_trainer")

class PersonalTrainerMCPClient:
    def __init__(self):
        pt_config = cargar_personal_trainer_config()
        if not pt_config:
            raise ValueError("No se encontró la configuración para Personal Trainer MCP en others_mcp.json")

        # This path needs to be adjusted to the actual location of the personal trainer project
        pt_config['cwd'] = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'personal_trainer_mcp'))

        self.server_params = StdioServerParameters(
            command=pt_config['command'],
            args=pt_config['args'],
            cwd=pt_config['cwd']
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

    async def compute_metrics(self, sexo: str, edad: int, altura_cm: int, peso_kg: int):
        return await self.session.call_tool("compute_metrics", {
            "sexo": sexo,
            "edad": edad,
            "altura_cm": altura_cm,
            "peso_kg": peso_kg
        })

    async def recommend_exercises(self, objetivo: str, deporte: str, limite: int):
        return await self.session.call_tool("recommend_exercises", {
            "objetivo": objetivo,
            "deporte": deporte,
            "limite": limite
        })

    async def build_routine_tool(self, objetivo: str, dias_por_semana: int, minutos_por_sesion: int, experiencia: str):
        return await self.session.call_tool("build_routine_tool", {
            "objetivo": objetivo,
            "dias_por_semana": dias_por_semana,
            "minutos_por_sesion": minutos_por_sesion,
            "experiencia": experiencia
        })

    async def recommend_by_metrics_tool(self, sexo: str, edad: int, altura_cm: int, peso_kg: int, objetivo: str, limite: int):
        return await self.session.call_tool("recommend_by_metrics_tool", {
            "sexo": sexo,
            "edad": edad,
            "altura_cm": altura_cm,
            "peso_kg": peso_kg,
            "objetivo": objetivo,
            "limite": limite
        })

async def main():
    # Example usage
    async with PersonalTrainerMCPClient() as client:
        metrics = await client.compute_metrics("male", 28, 175, 78)
        print("Metrics:", metrics)

        exercises = await client.recommend_exercises("gain muscle mass", "calisthenics", 10)
        print("Exercises:", exercises)

if __name__ == "__main__":
    # This requires adding the personal_trainer config to others_mcp.json first
    # asyncio.run(main())
    print("To run this example, first add the personal_trainer config to others_mcp.json")
