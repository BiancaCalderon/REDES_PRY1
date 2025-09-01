# chatbot/src/logger.py
import json
from datetime import datetime
from pathlib import Path

class MCPLogger:
    def __init__(self, log_file="logs/mcp_log.json"):
        self.log_file = Path(log_file)
        self.log_file.parent.mkdir(parents=True, exist_ok=True)
        self._load_log()
    
    def _load_log(self):
        """Load existing log or create new one"""
        if self.log_file.exists():
            try:
                with open(self.log_file, 'r', encoding='utf-8') as f:
                    self.log_data = json.load(f)
            except json.JSONDecodeError:
                self.log_data = []
        else:
            self.log_data = []
    
    def _save_log(self):
        """Save log to file"""
        with open(self.log_file, 'w', encoding='utf-8') as f:
            json.dump(self.log_data, f, indent=2, ensure_ascii=False)
    
    def log_mcp_request(self, server, method, params):
        """Log MCP server request"""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "type": "mcp_request",
            "server": server,
            "method": method,
            "params": params
        }
        self.log_data.append(entry)
        self._save_log()
        print(f"Logged MCP request: {server}.{method}")
    
    def log_mcp_response(self, server, method, response, success=True):
        """Log MCP server response"""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "type": "mcp_response",
            "server": server,
            "method": method,
            "success": success,
            "response": str(response) if response else None
        }
        self.log_data.append(entry)
        self._save_log()
        print(f"Logged MCP response: {server}.{method} ({'✅' if success else '❌'})")
    
    def log_mcp_error(self, server, method, error):
        """Log MCP server error"""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "type": "mcp_error",
            "server": server,
            "method": method,
            "error": str(error)
        }
        self.log_data.append(entry)
        self._save_log()
        print(f"📝 Logged MCP error: {server}.{method} - {error}")
    
    def get_log_summary(self):
        """Get summary of MCP interactions"""
        requests = [e for e in self.log_data if e["type"] == "mcp_request"]
        responses = [e for e in self.log_data if e["type"] == "mcp_response"]
        errors = [e for e in self.log_data if e["type"] == "mcp_error"]
        
        return {
            "total_interactions": len(self.log_data),
            "requests": len(requests),
            "responses": len(responses),
            "errors": len(errors),
            "success_rate": len([r for r in responses if r.get("success", False)]) / len(responses) if responses else 0
        }

# Global logger instance
mcp_logger = MCPLogger()