import asyncio
from pathlib import Path
from contextlib import AsyncExitStack
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

class FilesystemMCP:
    """Manages file operations using MCP Filesystem server"""
    
    async def create_file_with_mcp(self, content, filename="README.md", directory="workspace"):
        """Create file using MCP Filesystem server"""
        try:
            fs_server = StdioServerParameters(
                command="npx",
                args=["-y", "@modelcontextprotocol/server-filesystem", directory]
            )
            
            async with AsyncExitStack() as stack:
                (read, write) = await stack.enter_async_context(stdio_client(fs_server))
                fs_session = await stack.enter_async_context(ClientSession(read, write))
                await fs_session.initialize()
                
                result = await fs_session.call_tool("write_file", {
                    "path": f"{directory}/{filename}",
                    "content": content
                })
                
                print(f"File created via MCP Filesystem: {filename}")
                return result
        except Exception as e:
            print(f"MCP Filesystem Error: {e}")
            return None

    async def create_file_direct(self, content, filename="README.md", repo_name="eclipses-info"):
        """Create file directly in filesystem (fallback method)"""
        try:
            repo_dir = Path(f"workspace/{repo_name}")
            repo_dir.mkdir(parents=True, exist_ok=True)
            
            file_path = repo_dir / filename
            file_path.write_text(content, encoding="utf-8")
            print(f"File created directly: {file_path}")
            return True
        except Exception as e:
            print(f"Error creating file: {e}")
            return False

# Test function
async def test_filesystem():
    fs = FilesystemMCP()
    result = await fs.create_file_direct("# Test File\nCreated with FilesystemMCP", "test.md", "test-repo")
    print(f"Test result: {result}")

if __name__ == "__main__":
    asyncio.run(test_filesystem())