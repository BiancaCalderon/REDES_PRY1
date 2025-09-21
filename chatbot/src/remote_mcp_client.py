import httpx
import json
from typing import Dict, Any

class RemoteMcpClient:
    """Cliente para conectar con el servidor Eclipse MCP remoto"""
    
    def __init__(self, config):
        self.name = "eclipse-remote"
        self.description = "Interactúa con un servidor MCP de eclipses remoto."
        self.url = config.get("REMOTE_MCP_URL", "").rstrip('/')
        self.commands = {
            "status": "Verifica el estado del servidor remoto",
            "list_eclipses_by_year": "Lista eclipses para un año dado",
            "calculate_eclipse_visibility": "Calcula la visibilidad de un eclipse",
            "predict_next_eclipse": "Predice el próximo eclipse visible",
            "get_eclipse_path": "Obtiene la ruta de un eclipse",
            "get_safety_advice": "Obtiene consejos de seguridad para un eclipse"
        }
        self.timeout = 10.0

    def handle_command(self, command: str, params: dict = None) -> dict:
        """Maneja comandos hacia el servidor MCP remoto"""
        if not self.url:
            return {
                "status": "error", 
                "message": "La URL del servidor remoto no está configurada en config.json"
            }

        try:
            payload = {
                "command": command, 
                "params": params or {}
            }
            
            print("--- CLIENT: Enviando Petición JSON --->")
            print(json.dumps(payload, indent=2))

            print(f"🌐 Conectando a servidor remoto: {self.url}")
            
            with httpx.Client(timeout=self.timeout) as client:
                response = client.post(f"{self.url}/mcp", json=payload)
                response.raise_for_status()
            
            result = response.json()

            print("<--- SERVIDOR: Recibiendo Respuesta JSON ---")
            print(json.dumps(result, indent=2))
            
            result["response_time"] = response.elapsed.total_seconds()
            result["server_url"] = self.url
            
            return result
            
        except httpx.TimeoutException:
            return {
                "status": "error", 
                "message": f"Timeout: El servidor en {self.url} no respondió en {self.timeout}s"
            }
        except httpx.ConnectError:
            return {
                "status": "error", 
                "message": f"Error de conexión: No se puede alcanzar {self.url}. ¿Está el servidor en línea?"
            }
        except httpx.HTTPStatusError as e:
            return {
                "status": "error", 
                "message": f"Error HTTP {e.response.status_code}: {e.response.text}"
            }
        except json.JSONDecodeError:
            return {
                "status": "error", 
                "message": "La respuesta del servidor no es JSON válido"
            }
        except Exception as e:
            return {
                "status": "error", 
                "message": f"Error inesperado: {str(e)}"
            }

    def check_server_status(self) -> dict:
        """Verifica el estado del servidor remoto"""
        return self.handle_command("status")

    def list_eclipses_by_year(self, year: int) -> dict:
        return self.handle_command("list_eclipses_by_year", {"year": year})

    def calculate_eclipse_visibility(self, date: str, location: str) -> dict:
        return self.handle_command("calculate_eclipse_visibility", {"date": date, "location": location})

    def predict_next_eclipse(self, location: str) -> dict:
        return self.handle_command("predict_next_eclipse", {"location": location})

    def get_eclipse_path(self, date: str) -> dict:
        return self.handle_command("get_eclipse_path", {"date": date})

    def get_safety_advice(self, date: str) -> dict:
        return self.handle_command("get_safety_advice", {"date": date})
