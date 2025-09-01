import asyncio
from pathlib import Path
from contextlib import AsyncExitStack
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

def content_text(resp) -> str:
    """Extract text content from MCP response"""
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

class GitMCP:
    """Manages Git operations using MCP Git server"""
    
    async def setup_repository(self, repo_name="eclipses-info"):
        """Setup and commit to Git repository"""
        try:
            git_server = StdioServerParameters(
                command="npx",
                args=["-y", "@mseep/git-mcp-server"],
                env={"MCP_LOG_LEVEL": "info"},
            )
            
            demo_dir = Path(f"workspace/{repo_name}")
            
            async with AsyncExitStack() as stack:
                read, write = await stack.enter_async_context(stdio_client(git_server))
                session = await stack.enter_async_context(ClientSession(read, write))
                await session.initialize()

                print("Setting up Git repository...")
                
                # Set working directory
                r = await session.call_tool("git_set_working_dir", {"path": str(demo_dir.resolve())})
                print("Working directory set")

                # Initialize git repository
                if not (demo_dir / ".git").exists():
                    r = await session.call_tool("git_init", {"path": str(demo_dir.resolve())})
                    print("Git repository initialized")

                # Check status
                r = await session.call_tool("git_status", {})
                print("Git status checked")

                # Add all files
                r = await session.call_tool("git_add", {"files": ["."]})
                print("Files staged")

                # Commit
                msg = "feat(astronomy): Add solar eclipses documentation"
                r = await session.call_tool("git_commit", {"message": msg})
                print("Changes committed")

                return True
        except Exception as e:
            print(f"Git operation error: {e}")
            return False

    async def commit_file(self, repo_name="eclipses-info", commit_message="Update documentation"):
        """Commit changes in existing repository"""
        try:
            git_server = StdioServerParameters(
                command="npx",
                args=["-y", "@mseep/git-mcp-server"],
                env={"MCP_LOG_LEVEL": "info"},
            )
            
            demo_dir = Path(f"workspace/{repo_name}")
            
            async with AsyncExitStack() as stack:
                read, write = await stack.enter_async_context(stdio_client(git_server))
                session = await stack.enter_async_context(ClientSession(read, write))
                await session.initialize()

                # Set working directory
                r = await session.call_tool("git_set_working_dir", {"path": str(demo_dir.resolve())})
                
                # Add and commit
                r = await session.call_tool("git_add", {"files": ["."]})
                r = await session.call_tool("git_commit", {"message": commit_message})
                
                print(f"Changes committed: {commit_message}")
                return True
        except Exception as e:
            print(f"Commit error: {e}")
            return False

# Test function
async def test_git():
    git = GitMCP()
    result = await git.setup_repository("test-repo")
    print(f"Git test result: {result}")

if __name__ == "__main__":
    asyncio.run(test_git())