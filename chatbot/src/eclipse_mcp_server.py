#!/usr/bin/env python3
"""
Servidor MCP personalizado para cálculo de eclipses solares
Ubicación correcta: chatbot/src/eclipse_mcp_server.py

Este archivo debe estar en la misma ubicación que eclipse_mcp_client.py
para que el cliente pueda encontrarlo correctamente.
"""

import asyncio
import json
import sys
from datetime import datetime, timedelta
from typing import Any, Sequence
from pathlib import Path

# Importaciones MCP
from mcp import types
from mcp.server import NotificationOptions, Server
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server

# Datos de eclipses (base de datos astronómica simplificada)
ECLIPSES_DATA = {
    "2024-04-08": {
        "type": "solar_total",
        "date": "2024-04-08",
        "max_duration": "04:28",
        "locations": {
            "Guatemala City": {
                "visible": True,
                "partial": True,
                "coverage": "65%",
                "start_time": "12:34:00",
                "max_time": "14:15:00",
                "end_time": "15:45:00",
                "magnitude": 0.65,
                "obscuration": 0.52
            },
            "Mazatenango": {
                "visible": True,
                "partial": True,
                "coverage": "72%",
                "start_time": "12:32:00",
                "max_time": "14:13:00",
                "end_time": "15:43:00",
                "magnitude": 0.72,
                "obscuration": 0.61
            },
            "Quetzaltenango": {
                "visible": True,
                "partial": True,
                "coverage": "70%",
                "start_time": "12:35:00",
                "max_time": "14:16:00",
                "end_time": "15:46:00",
                "magnitude": 0.70,
                "obscuration": 0.58
            }
        },
        "path_totality": [
            {"lat": 25.295, "lng": -109.077, "duration": "04:20"},
            {"lat": 25.776, "lng": -108.567, "duration": "04:25"},
            {"lat": 32.749, "lng": -103.793, "duration": "04:13"}
        ]
    },
    "2030-06-01": {
        "type": "solar_annular",
        "date": "2030-06-01",
        "max_duration": "05:21",
        "locations": {
            "Guatemala City": {
                "visible": True,
                "partial": True,
                "coverage": "45%",
                "start_time": "11:23:00",
                "max_time": "12:45:00",
                "end_time": "14:12:00",
                "magnitude": 0.45,
                "obscuration": 0.32
            }
        }
    },
    "2044-08-12": {
        "type": "solar_total",
        "date": "2044-08-12",
        "max_duration": "04:09",
        "locations": {
            "Guatemala City": {
                "visible": True,
                "partial": True,
                "coverage": "89%",
                "start_time": "15:45:00",
                "max_time": "17:23:00",
                "end_time": "18:54:00",
                "magnitude": 0.89,
                "obscuration": 0.82
            }
        }
    }
}

class EclipseCalculatorServer:
    """Servidor MCP para cálculo de eclipses solares"""
    
    def __init__(self):
        self.server = Server("eclipse-calculator")
    
    async def calculate_eclipse_visibility(self, date: str, location: str) -> dict:
        """
        Calcular visibilidad de eclipse para una fecha y ubicación
        
        Args:
            date: Fecha en formato YYYY-MM-DD
            location: Nombre de la ubicación
            
        Returns:
            Información detallada del eclipse
        """
        # Buscar datos del eclipse
        eclipse_data = ECLIPSES_DATA.get(date)
        
        if not eclipse_data:
            return {
                "date": date,
                "location": location,
                "visible": False,
                "reason": "No eclipse data available for this date",
                "suggestion": f"Try dates: {', '.join(ECLIPSES_DATA.keys())}"
            }
        
        # Buscar ubicación
        location_data = eclipse_data["locations"].get(location)
        
        if not location_data:
            available_locations = list(eclipse_data["locations"].keys())
            return {
                "date": date,
                "location": location,
                "visible": False,
                "reason": "Location not in database",
                "available_locations": available_locations,
                "suggestion": f"Try: {', '.join(available_locations)}"
            }
        
        # Calcular información adicional
        result = {
            "date": date,
            "location": location,
            "eclipse_type": eclipse_data["type"],
            "visible": location_data["visible"],
            "is_partial": location_data.get("partial", False),
            "coverage": location_data.get("coverage"),
            "magnitude": location_data.get("magnitude"),
            "obscuration": location_data.get("obscuration"),
            "times": {
                "start": location_data.get("start_time"),
                "maximum": location_data.get("max_time"),
                "end": location_data.get("end_time")
            },
            "duration_at_location": self._calculate_duration(
                location_data.get("start_time"),
                location_data.get("end_time")
            ),
            "max_duration_global": eclipse_data.get("max_duration"),
            "safety_advice": self._get_safety_advice(eclipse_data["type"])
        }
        
        return result
    
    def _calculate_duration(self, start_time: str, end_time: str) -> str:
        """Calcular duración del eclipse en la ubicación"""
        if not start_time or not end_time:
            return "N/A"
        
        try:
            start = datetime.strptime(start_time, "%H:%M:%S")
            end = datetime.strptime(end_time, "%H:%M:%S")
            duration = end - start
            
            hours = duration.seconds // 3600
            minutes = (duration.seconds % 3600) // 60
            
            return f"{hours:02d}:{minutes:02d}"
        except:
            return "N/A"
    
    def _get_safety_advice(self, eclipse_type: str) -> list:
        """Obtener consejos de seguridad para observación"""
        base_advice = [
            "NUNCA mire directamente al Sol sin protección adecuada",
            "Use filtros solares certificados ISO 12312-2",
            "Los lentes de sol comunes NO son suficientes",
            "Supervise siempre a los niños durante la observación"
        ]
        
        if "total" in eclipse_type:
            base_advice.append("Durante la totalidad es seguro mirar sin filtro POR UNOS SEGUNDOS")
            base_advice.append("Vuelva a usar filtros cuando termine la totalidad")
        
        return base_advice
    
    async def get_eclipse_path(self, date: str) -> dict:
        """
        Obtener información del camino de totalidad/anularidad
        
        Args:
            date: Fecha del eclipse
            
        Returns:
            Información del camino del eclipse
        """
        eclipse_data = ECLIPSES_DATA.get(date)
        
        if not eclipse_data:
            return {
                "date": date,
                "error": "Eclipse data not available",
                "available_dates": list(ECLIPSES_DATA.keys())
            }
        
        return {
            "date": date,
            "eclipse_type": eclipse_data["type"],
            "max_duration": eclipse_data.get("max_duration"),
            "path_points": eclipse_data.get("path_totality", []),
            "total_path_length": len(eclipse_data.get("path_totality", [])),
            "coverage_info": f"Path covers {len(eclipse_data.get('locations', {}))} major cities"
        }
    
    async def predict_next_eclipse(self, location: str, after_date: str = None) -> dict:
        """
        Predecir el próximo eclipse visible desde una ubicación
        
        Args:
            location: Ubicación de interés
            after_date: Fecha después de la cual buscar (opcional)
            
        Returns:
            Información del próximo eclipse
        """
        if not after_date:
            after_date = datetime.now().strftime("%Y-%m-%d")
        
        # Buscar eclipses futuros para la ubicación
        future_eclipses = []
        
        for date, eclipse_data in ECLIPSES_DATA.items():
            if date > after_date:
                location_data = eclipse_data["locations"].get(location)
                if location_data and location_data.get("visible"):
                    future_eclipses.append({
                        "date": date,
                        "type": eclipse_data["type"],
                        "coverage": location_data.get("coverage"),
                        "magnitude": location_data.get("magnitude")
                    })
        
        if not future_eclipses:
            return {
                "location": location,
                "message": "No upcoming eclipses found in database",
                "suggestion": "Check back later or try a different location"
            }
        
        # Ordenar por fecha y tomar el primero
        future_eclipses.sort(key=lambda x: x["date"])
        next_eclipse = future_eclipses[0]
        
        return {
            "location": location,
            "next_eclipse": next_eclipse,
            "years_to_wait": (datetime.strptime(next_eclipse["date"], "%Y-%m-%d") - 
                            datetime.strptime(after_date, "%Y-%m-%d")).days / 365.25,
            "all_future_eclipses": future_eclipses
        }
    
    def setup_handlers(self):
        """Configurar los handlers MCP"""
        
        @self.server.list_tools()
        async def handle_list_tools() -> list[types.Tool]:
            """Listar herramientas disponibles"""
            return [
                types.Tool(
                    name="calculate_eclipse_visibility",
                    description="Calculate solar eclipse visibility for a specific date and location",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "date": {
                                "type": "string",
                                "description": "Date in YYYY-MM-DD format",
                                "pattern": r"^\d{4}-\d{2}-\d{2}$"
                            },
                            "location": {
                                "type": "string",
                                "description": "Location name (e.g., 'Guatemala City')"
                            }
                        },
                        "required": ["date", "location"]
                    }
                ),
                types.Tool(
                    name="get_eclipse_path",
                    description="Get eclipse path information including totality/annularity track",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "date": {
                                "type": "string",
                                "description": "Date in YYYY-MM-DD format",
                                "pattern": r"^\d{4}-\d{2}-\d{2}$"
                            }
                        },
                        "required": ["date"]
                    }
                ),
                types.Tool(
                    name="predict_next_eclipse",
                    description="Predict next visible eclipse for a location",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "location": {
                                "type": "string",
                                "description": "Location name"
                            },
                            "after_date": {
                                "type": "string",
                                "description": "Find eclipses after this date (optional, defaults to today)",
                                "pattern": r"^\d{4}-\d{2}-\d{2}$"
                            }
                        },
                        "required": ["location"]
                    }
                )
            ]
        
        @self.server.call_tool()
        async def handle_call_tool(name: str, arguments: dict) -> list[types.TextContent]:
            """Manejar llamadas a herramientas"""
            
            if name == "calculate_eclipse_visibility":
                date = arguments.get("date")
                location = arguments.get("location")
                
                if not date or not location:
                    return [types.TextContent(
                        type="text",
                        text="Error: Both date and location are required"
                    )]
                
                result = await self.calculate_eclipse_visibility(date, location)
                
                return [types.TextContent(
                    type="text",
                    text=json.dumps(result, indent=2, ensure_ascii=False)
                )]
            
            elif name == "get_eclipse_path":
                date = arguments.get("date")
                
                if not date:
                    return [types.TextContent(
                        type="text",
                        text="Error: Date is required"
                    )]
                
                result = await self.get_eclipse_path(date)
                
                return [types.TextContent(
                    type="text",
                    text=json.dumps(result, indent=2, ensure_ascii=False)
                )]
            
            elif name == "predict_next_eclipse":
                location = arguments.get("location")
                after_date = arguments.get("after_date")
                
                if not location:
                    return [types.TextContent(
                        type="text",
                        text="Error: Location is required"
                    )]
                
                result = await self.predict_next_eclipse(location, after_date)
                
                return [types.TextContent(
                    type="text",
                    text=json.dumps(result, indent=2, ensure_ascii=False)
                )]
            
            else:
                return [types.TextContent(
                    type="text",
                    text=f"Error: Unknown tool '{name}'"
                )]

async def main():
    """Función principal del servidor"""
    server_instance = EclipseCalculatorServer()
    server_instance.setup_handlers()
    
    # Opciones de inicialización
    init_options = InitializationOptions(
        server_name="eclipse-calculator",
        server_version="1.0.0",
        capabilities=server_instance.server.get_capabilities(
            notification_options=NotificationOptions(),
            experimental_capabilities={},
        ),
    )
    
    # Ejecutar servidor stdio
    async with stdio_server() as (read_stream, write_stream):
        await server_instance.server.run(
            read_stream,
            write_stream,
            init_options
        )

if __name__ == "__main__":
    print("🌒 Starting Eclipse Calculator MCP Server...", file=sys.stderr)
    asyncio.run(main())