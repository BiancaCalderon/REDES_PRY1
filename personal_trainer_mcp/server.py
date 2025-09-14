from mcp.server.fastmcp.server import FastMCP
import planner

# Create a FastMCP server instance
server = FastMCP(name="Personal Trainer")

# Register the tools from the planner module
server.add_tool(planner.compute_metrics)
server.add_tool(planner.recommend_exercises)
server.add_tool(planner.build_routine_tool)
server.add_tool(planner.recommend_by_metrics_tool)

if __name__ == "__main__":
    # Run the server
    server.run()