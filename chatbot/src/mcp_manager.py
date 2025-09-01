import asyncio
import anthropic
from contextlib import AsyncExitStack
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

class AstronomyMCPChatbot:
    def __init__(self, anthropic_key):
        self.anthropic = anthropic.Anthropic(api_key=anthropic_key)
        self.conversation = []
        self.mcp_sessions = {}

    async def setup_mcp_servers(self):
        """Connect to MCP Filesystem server using stdio."""
        fs_server = StdioServerParameters(
            command="npx",
            args=["-y", "@modelcontextprotocol/server-filesystem", "workspace"]
        )
        async with AsyncExitStack() as stack:
            (read, write) = await stack.enter_async_context(stdio_client(fs_server))
            self.mcp_sessions['fs'] = await stack.enter_async_context(
                ClientSession(read, write)
            )
            await self.mcp_sessions['fs'].initialize()
            print("Filesystem MCP connected.")

    async def chat(self, message):
        """Chat with context and MCP Filesystem integration."""
        self.conversation.append({"role": "user", "content": message})

        # Example: if the user asks to create a file, use MCP Filesystem
        if "create file" in message.lower() or "crear archivo" in message.lower():
            await self.mcp_sessions['fs'].call_tool("write_file", {
                "path": "workspace/README.md",
                "content": "# Astronomy Project\nCreated with MCP!"
            })
            response = "File created using MCP Filesystem."
        else:
            # Otherwise, use Claude for a normal response
            claude_response = self.anthropic.messages.create(
                model="claude-3-sonnet-20240229",
                messages=self.conversation,
                max_tokens=500
            )
            response = claude_response.content[0].text

        self.conversation.append({"role": "assistant", "content": response})
        return response

# Usage example
async def main():
    # Replace with your real API key
    chatbot = AstronomyMCPChatbot("your_anthropic_api_key")
    await chatbot.setup_mcp_servers()
    response = await chatbot.chat("Create file README for astronomy project")
    print(f"Assistant: {response}")

if __name__ == "__main__":
    asyncio.run(main())