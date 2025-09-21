import asyncio
from eclipse_mcp_client import EclipseMCPClient

async def main():
    client = EclipseMCPClient()
    await client.connect()

    print("=== Test: Eclipses en 2025 ===")
    print(await client.list_eclipses_by_year(2025))

    print("\n=== Test: Visibilidad Guatemala City 2025-03-14 ===")
    print(await client.calculate_eclipse_visibility("2025-03-14", "Guatemala City"))

    print("\n=== Test: Próximo eclipse Guatemala City ===")
    print(await client.predict_next_eclipse("Guatemala City"))

    await client.disconnect()

asyncio.run(main())
