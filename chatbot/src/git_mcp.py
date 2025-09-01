# chatbot/src/git_mcp.py
import asyncio
from pathlib import Path
from contextlib import AsyncExitStack
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from logger import mcp_logger

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
            
            # Log repository setup request
            mcp_logger.log_mcp_request("git", "setup_repository", {
                "repo_name": repo_name,
                "path": str(demo_dir)
            })
            
            async with AsyncExitStack() as stack:
                read, write = await stack.enter_async_context(stdio_client(git_server))
                session = await stack.enter_async_context(ClientSession(read, write))
                await session.initialize()

                print("Setting up Git repository...")
                
                # Set working directory
                r = await session.call_tool("git_set_working_dir", {"path": str(demo_dir.resolve())})
                mcp_logger.log_mcp_response("git", "git_set_working_dir", content_text(r), success=True)
                print("Working directory set")

                # Initialize git repository
                if not (demo_dir / ".git").exists():
                    r = await session.call_tool("git_init", {"path": str(demo_dir.resolve())})
                    mcp_logger.log_mcp_response("git", "git_init", content_text(r), success=True)
                    print("Git repository initialized")

                # Check status
                r = await session.call_tool("git_status", {})
                mcp_logger.log_mcp_response("git", "git_status", content_text(r), success=True)
                print("Git status checked")

                # Add all files
                r = await session.call_tool("git_add", {"files": ["."]})
                mcp_logger.log_mcp_response("git", "git_add", content_text(r), success=True)
                print("Files staged")

                # Commit
                msg = "feat(astronomy): Add solar eclipses documentation"
                r = await session.call_tool("git_commit", {"message": msg})
                mcp_logger.log_mcp_response("git", "git_commit", content_text(r), success=True)
                print("Changes committed")

                # Log successful repository setup
                mcp_logger.log_mcp_response("git", "setup_repository", {
                    "repo_name": repo_name,
                    "status": "completed"
                }, success=True)

                return True
        except Exception as e:
            mcp_logger.log_mcp_error("git", "setup_repository", str(e))
            print(f"Git operation error: {e}")
            return False

# Test function
async def test_git():
    git = GitMCP()
    result = await git.setup_repository("test-repo")
    print(f"Git test result: {result}")
    
    # Show log summary
    summary = mcp_logger.get_log_summary()
    print(f"Log summary: {summary}")

if __name__ == "__main__":
    asyncio.run(test_git())