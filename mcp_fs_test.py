import asyncio
from contextlib import AsyncExitStack
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def main():
    # Configura el servidor MCP Filesystem usando npx
    fs_server = StdioServerParameters(
        command="npx",
        args=["-y", "@modelcontextprotocol/server-filesystem", "workspace"]
    )
    async with AsyncExitStack() as stack:
        (read, write) = await stack.enter_async_context(stdio_client(fs_server))
        fs_session = await stack.enter_async_context(ClientSession(read, write))
        await fs_session.initialize()
        print("Filesystem MCP connected.")

        # Prueba: crear un archivo README.md en la carpeta workspace
        result = await fs_session.call_tool("write_file", {
            "path": "workspace/README.md",
            "content": "# Astronomy Project\nCreated with MCP!"
        })
        print("write_file result:", result)

if __name__ == "__main__":
    asyncio.run(main())