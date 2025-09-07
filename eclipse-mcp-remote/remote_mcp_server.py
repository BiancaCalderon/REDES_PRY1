#!/usr/bin/env python3
"""
Servidor MCP de Eclipses Remoto - Desplegable en la nube
Basado en tu eclipse_mcp_server.py existente
Funcionalidad: Cálculo de eclipses solares para ubicaciones específicas
"""

import json
import asyncio
from datetime import datetime, timedelta
from typing import Dict, Any, List
import os

# Dependencias para servidor web
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

# --- Base de Datos de Eclipses ---
ECLIPSES_DATA = {
    "2025-03-14": {
        "type": "lunar_total", 
        "description": "Total Lunar Eclipse",
        "max_duration": "01:05",
        "locations": {
            "Guatemala City": {
                "visible": True, 
                "partial": False, 
                "coverage": "100%", 
                "start_time": "04:30:00",
                "max_time": "04:58:00",
                "end_time": "05:26:00",
                "magnitude": 1.18,
                "obscuration": 1.0
            },
            "Madrid": {
                "visible": True, 
                "partial": True, 
                "coverage": "60%", 
                "start_time": "06:00:00",
                "max_time": "06:30:00",
                "end_time": "07:00:00",
                "magnitude": 0.60,
                "obscuration": 0.42
            },
            "Mexico City": {
                "visible": True, 
                "partial": False, 
                "coverage": "95%",
                "start_time": "03:45:00",
                "max_time": "04:58:00",
                "end_time": "06:11:00",
                "magnitude": 1.15,
                "obscuration": 0.95
            }
        }
    },
    "2026-02-17": {
        "type": "solar_annular", 
        "description": "Annular Solar Eclipse",
        "max_duration": "02:20",
        "locations": {
            "Guatemala City": {
                "visible": True, 
                "partial": True, 
                "coverage": "35%", 
                "start_time": "12:45:00",
                "max_time": "13:30:00",
                "end_time": "14:15:00",
                "magnitude": 0.35,
                "obscuration": 0.22
            },
            "Antigua Guatemala": {
                "visible": True,
                "partial": True,
                "coverage": "42%",
                "start_time": "12:43:00",
                "max_time": "13:28:00", 
                "end_time": "14:13:00",
                "magnitude": 0.42,
                "obscuration": 0.28
            }
        },
        "path_annularity": [
            {"lat": 14.6349, "lng": -90.5069, "duration": "01:45"},
            {"lat": 15.7835, "lng": -88.5976, "duration": "02:15"}
        ]
    },
    "2026-08-12": {
        "type": "solar_total", 
        "description": "Total Solar Eclipse",
        "max_duration": "02:18",
        "locations": {
            "Madrid": {
                "visible": True, 
                "partial": False, 
                "coverage": "100%", 
                "start_time": "18:30:00",
                "max_time": "19:30:00",
                "end_time": "20:30:00",
                "magnitude": 1.05,
                "obscuration": 1.0
            },
            "Barcelona": {
                "visible": True,
                "partial": True,
                "coverage": "85%",
                "start_time": "18:45:00",
                "max_time": "19:45:00",
                "end_time": "20:45:00",
                "magnitude": 0.85,
                "obscuration": 0.76
            }
        },
        "path_totality": [
            {"lat": 40.4168, "lng": -3.7038, "duration": "02:18"},
            {"lat": 41.3851, "lng": 2.1734, "duration": "01:55"}
        ]
    },
    "2028-07-22": {
        "type": "solar_total", 
        "description": "Total Solar Eclipse",
        "max_duration": "05:09",
        "locations": {
            "Sydney": {
                "visible": True, 
                "partial": False, 
                "coverage": "100%", 
                "start_time": "13:15:00",
                "max_time": "14:15:00",
                "end_time": "15:15:00",
                "magnitude": 1.06,
                "obscuration": 1.0
            },
            "Guatemala City": {
                "visible": False,
                "partial": False,
                "coverage": "0%",
                "reason": "Eclipse not visible from this location"
            }
        }
    },
    "2030-06-01": {
        "type": "solar_annular", 
        "description": "Annular Solar Eclipse",
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
            },
            "Quetzaltenango": {
                "visible": True,
                "partial": True,
                "coverage": "48%",
                "start_time": "11:25:00",
                "max_time": "12:47:00",
                "end_time": "14:14:00",
                "magnitude": 0.48,
                "obscuration": 0.35
            }
        }
    }
}

# Modelos Pydantic para validación
class MCPRequest(BaseModel):
    command: str
    params: Dict[str, Any] = {}

class MCPResponse(BaseModel):
    status: str
    message: str
    data: Dict[str, Any] = {}
    timestamp: str

# Crear aplicación FastAPI
app = FastAPI(
    title="Eclipse Calculator MCP Server",
    description="Servidor MCP remoto para cálculos de eclipses solares y lunares",
    version="2.1.0"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class EclipseCalculatorServer:
    """Servidor MCP remoto para cálculo de eclipses"""
    
    def __init__(self):
        self.name = "eclipse-calculator-remote"
        self.version = "2.1.0"
        self.capabilities = {
            "list_eclipses_by_year": "Lista todos los eclipses conocidos para un año dado",
            "calculate_eclipse_visibility": "Calcula visibilidad de eclipse para fecha y ubicación",
            "predict_next_eclipse": "Predice próximo eclipse visible desde una ubicación",
            "get_eclipse_path": "Obtiene información del camino de totalidad/anularidad",
            "get_safety_advice": "Proporciona consejos de seguridad para observación"
        }

    def list_eclipses_by_year(self, year: int) -> Dict[str, Any]:
        """Lista eclipses por año"""
        eclipses_in_year = []
        for date, data in ECLIPSES_DATA.items():
            if date.startswith(str(year)):
                visible_locations = [loc for loc, loc_data in data.get("locations", {}).items() 
                                   if loc_data.get("visible")]
                eclipses_in_year.append({
                    "date": date, 
                    "type": data.get("type"), 
                    "description": data.get("description", "N/A"),
                    "max_duration": data.get("max_duration", "N/A"),
                    "visible_in": visible_locations,
                    "total_locations": len(data.get("locations", {}))
                })
        
        return {
            "year": year, 
            "eclipses": eclipses_in_year,
            "total_eclipses": len(eclipses_in_year),
            "status": "success"
        }

    def calculate_eclipse_visibility(self, date: str, location: str) -> Dict[str, Any]:
        """Calcula visibilidad de eclipse para fecha y ubicación"""
        eclipse_data = ECLIPSES_DATA.get(date)
        if not eclipse_data:
            available_dates = list(ECLIPSES_DATA.keys())
            return {
                "error": f"No hay datos de eclipse para la fecha {date}",
                "available_dates": available_dates,
                "suggestion": f"Prueba con: {', '.join(available_dates[:3])}"
            }
        
        location_data = eclipse_data["locations"].get(location)
        if not location_data:
            available_locations = list(eclipse_data["locations"].keys())
            return {
                "error": f"Ubicación '{location}' no disponible para este eclipse",
                "available_locations": available_locations,
                "suggestion": f"Prueba con: {', '.join(available_locations)}"
            }
        
        # Calcular duración si está visible
        duration = "N/A"
        if location_data.get("visible") and location_data.get("start_time") and location_data.get("end_time"):
            duration = self._calculate_duration(location_data["start_time"], location_data["end_time"])
        
        result = {
            "date": date,
            "location": location,
            "eclipse_type": eclipse_data["type"],
            "description": eclipse_data.get("description", ""),
            "visible": location_data.get("visible", False),
            "partial": location_data.get("partial", False),
            "coverage": location_data.get("coverage", "0%"),
            "magnitude": location_data.get("magnitude", 0),
            "obscuration": location_data.get("obscuration", 0),
            "times": {
                "start": location_data.get("start_time", "N/A"),
                "maximum": location_data.get("max_time", "N/A"),
                "end": location_data.get("end_time", "N/A")
            },
            "duration_at_location": duration,
            "max_duration_global": eclipse_data.get("max_duration", "N/A"),
            "safety_advice": self._get_safety_advice(eclipse_data["type"]),
            "status": "success"
        }
        
        if not location_data.get("visible"):
            result["reason"] = location_data.get("reason", "Eclipse no visible desde esta ubicación")
        
        return result

    def predict_next_eclipse(self, location: str, after_date: str = None) -> Dict[str, Any]:
        """Predice próximo eclipse visible desde una ubicación"""
        if not after_date:
            after_date = datetime.now().strftime("%Y-%m-%d")
        
        future_eclipses = []
        for date, eclipse_data in ECLIPSES_DATA.items():
            if date > after_date:
                if location in eclipse_data["locations"] and eclipse_data["locations"][location].get("visible"):
                    location_data = eclipse_data["locations"][location]
                    future_eclipses.append({
                        "date": date,
                        "type": eclipse_data.get("type"),
                        "description": eclipse_data.get("description", "N/A"),
                        "coverage": location_data.get("coverage", "0%"),
                        "magnitude": location_data.get("magnitude", 0),
                        "max_time": location_data.get("max_time", "N/A"),
                        "years_from_now": round((datetime.strptime(date, "%Y-%m-%d") - datetime.now()).days / 365.25, 1)
                    })
        
        if not future_eclipses:
            # Buscar ubicaciones disponibles
            available_locations = set()
            for eclipse_data in ECLIPSES_DATA.values():
                available_locations.update(eclipse_data.get("locations", {}).keys())
            
            return {
                "error": f"No se encontraron eclipses futuros para {location}",
                "available_locations": list(available_locations),
                "suggestion": "Prueba con Guatemala City, Madrid o Mexico City"
            }
        
        future_eclipses.sort(key=lambda x: x["date"])
        next_eclipse = future_eclipses[0]
        
        return {
            "location": location,
            "next_eclipse": next_eclipse,
            "years_to_wait": next_eclipse["years_from_now"],
            "total_future_eclipses": len(future_eclipses),
            "all_future_eclipses": future_eclipses[:5],  # Máximo 5 para no sobrecargar
            "status": "success"
        }

    def get_eclipse_path(self, date: str) -> Dict[str, Any]:
        """Obtiene información del camino de totalidad/anularidad"""
        eclipse_data = ECLIPSES_DATA.get(date)
        if not eclipse_data:
            return {
                "error": f"No hay datos de eclipse para {date}",
                "available_dates": list(ECLIPSES_DATA.keys())
            }
        
        eclipse_type = eclipse_data.get("type", "")
        path_key = "path_totality" if "total" in eclipse_type else "path_annularity"
        path_data = eclipse_data.get(path_key, [])
        
        return {
            "date": date,
            "eclipse_type": eclipse_type,
            "description": eclipse_data.get("description", ""),
            "max_duration": eclipse_data.get("max_duration", "N/A"),
            "path_points": path_data,
            "path_length": len(path_data),
            "cities_covered": len(eclipse_data.get("locations", {})),
            "visible_locations": list(eclipse_data.get("locations", {}).keys()),
            "status": "success"
        }

    def get_safety_advice(self, eclipse_type: str = "solar") -> Dict[str, Any]:
        """Proporciona consejos de seguridad para observación de eclipses"""
        advice = self._get_safety_advice(eclipse_type)
        
        return {
            "eclipse_type": eclipse_type,
            "safety_advice": advice,
            "critical_warnings": [
                "NUNCA mire directamente al Sol sin protección adecuada",
                "Los lentes de sol comunes NO son suficientes",
                "Use filtros solares certificados ISO 12312-2"
            ],
            "emergency_info": "Si experimenta dolor ocular después de observar un eclipse, consulte inmediatamente a un oftalmólogo",
            "status": "success"
        }

    def _calculate_duration(self, start_time: str, end_time: str) -> str:
        """Calcula duración del eclipse en la ubicación"""
        if not start_time or not end_time:
            return "N/A"
        
        try:
            start = datetime.strptime(start_time, "%H:%M:%S")
            end = datetime.strptime(end_time, "%H:%M:%S")
            
            # Manejar casos donde el eclipse cruza medianoche
            if end < start:
                end = end + timedelta(days=1)
            
            duration = end - start
            hours = duration.seconds // 3600
            minutes = (duration.seconds % 3600) // 60
            
            return f"{hours:02d}:{minutes:02d}"
        except:
            return "N/A"
    
    def _get_safety_advice(self, eclipse_type: str) -> List[str]:
        """Obtener consejos de seguridad para observación"""
        base_advice = [
            "NUNCA mire directamente al Sol sin protección adecuada",
            "Use filtros solares certificados ISO 12312-2",
            "Los lentes de sol comunes NO son suficientes",
            "Supervise siempre a los niños durante la observación",
            "Use métodos de proyección indirecta como alternativa segura"
        ]
        
        if "total" in eclipse_type.lower():
            base_advice.extend([
                "Durante la totalidad es seguro mirar sin filtro POR UNOS SEGUNDOS",
                "Vuelva a usar filtros INMEDIATAMENTE cuando termine la totalidad",
                "La corona solar solo es visible durante la totalidad completa"
            ])
        elif "lunar" in eclipse_type.lower():
            base_advice = [
                "Los eclipses lunares son completamente seguros de observar",
                "No se necesita protección especial para los ojos",
                "Use binoculares o telescopio para mejor vista",
                "La Luna puede verse rojiza durante la totalidad"
            ]
        
        return base_advice

# Instancia del servidor MCP
eclipse_server = EclipseCalculatorServer()

@app.get("/")
async def root():
    """Endpoint de información del servidor"""
    return {
        "name": eclipse_server.name,
        "version": eclipse_server.version,
        "description": "Servidor MCP remoto para cálculos de eclipses solares y lunares",
        "capabilities": eclipse_server.capabilities,
        "total_eclipses": len(ECLIPSES_DATA),
        "available_years": sorted(list(set(date[:4] for date in ECLIPSES_DATA.keys()))),
        "status": "online",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/health")
async def health_check():
    """Endpoint de health check para servicios de nube"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "server": eclipse_server.name,
        "version": eclipse_server.version,
        "eclipses_loaded": len(ECLIPSES_DATA)
    }

@app.post("/mcp", response_model=MCPResponse)
async def handle_mcp_request(request: MCPRequest):
    """Endpoint principal para manejar peticiones MCP"""
    try:
        command = request.command.lower()
        params = request.params
        
        if command == "status":
            return MCPResponse(
                status="success",
                message="Servidor Eclipse Calculator MCP operativo",
                data={
                    "server_name": eclipse_server.name,
                    "version": eclipse_server.version,
                    "capabilities": list(eclipse_server.capabilities.keys()),
                    "total_eclipses": len(ECLIPSES_DATA),
                    "available_locations": list(set().union(*[d.get("locations", {}).keys() for d in ECLIPSES_DATA.values()]))
                },
                timestamp=datetime.now().isoformat()
            )
        
        elif command == "list_eclipses_by_year":
            year = params.get("year", datetime.now().year)
            result = eclipse_server.list_eclipses_by_year(year)
            
            return MCPResponse(
                status="success",
                message=f"Eclipses listados para el año {year}",
                data=result,
                timestamp=datetime.now().isoformat()
            )
        
        elif command == "calculate_eclipse_visibility":
            date = params.get("date")
            location = params.get("location")
            
            if not date or not location:
                return MCPResponse(
                    status="error",
                    message="Se requieren los parámetros 'date' y 'location'",
                    data={"example": {"date": "2026-02-17", "location": "Guatemala City"}},
                    timestamp=datetime.now().isoformat()
                )
            
            result = eclipse_server.calculate_eclipse_visibility(date, location)
            
            if "error" in result:
                return MCPResponse(
                    status="error",
                    message=result["error"],
                    data=result,
                    timestamp=datetime.now().isoformat()
                )
            
            return MCPResponse(
                status="success",
                message=f"Visibilidad calculada para {location} el {date}",
                data=result,
                timestamp=datetime.now().isoformat()
            )
        
        elif command == "predict_next_eclipse":
            location = params.get("location")
            after_date = params.get("after_date")
            
            if not location:
                return MCPResponse(
                    status="error",
                    message="Se requiere el parámetro 'location'",
                    data={"example": {"location": "Guatemala City"}},
                    timestamp=datetime.now().isoformat()
                )
            
            result = eclipse_server.predict_next_eclipse(location, after_date)
            
            if "error" in result:
                return MCPResponse(
                    status="error",
                    message=result["error"],
                    data=result,
                    timestamp=datetime.now().isoformat()
                )
            
            return MCPResponse(
                status="success",
                message=f"Próximo eclipse predicho para {location}",
                data=result,
                timestamp=datetime.now().isoformat()
            )
        
        elif command == "get_eclipse_path":
            date = params.get("date")
            
            if not date:
                return MCPResponse(
                    status="error",
                    message="Se requiere el parámetro 'date'",
                    data={"example": {"date": "2026-08-12"}},
                    timestamp=datetime.now().isoformat()
                )
            
            result = eclipse_server.get_eclipse_path(date)
            
            if "error" in result:
                return MCPResponse(
                    status="error",
                    message=result["error"],
                    data=result,
                    timestamp=datetime.now().isoformat()
                )
            
            return MCPResponse(
                status="success",
                message=f"Información de camino obtenida para eclipse del {date}",
                data=result,
                timestamp=datetime.now().isoformat()
            )
        
        elif command == "get_safety_advice":
            eclipse_type = params.get("eclipse_type", "solar")
            result = eclipse_server.get_safety_advice(eclipse_type)
            
            return MCPResponse(
                status="success",
                message=f"Consejos de seguridad para eclipse {eclipse_type}",
                data=result,
                timestamp=datetime.now().isoformat()
            )
        
        else:
            available_commands = list(eclipse_server.capabilities.keys()) + ["status", "get_safety_advice"]
            return MCPResponse(
                status="error",
                message=f"Comando '{command}' no reconocido",
                data={
                    "available_commands": available_commands,
                    "example_usage": {
                        "list_eclipses_by_year": {"year": 2026},
                        "calculate_eclipse_visibility": {"date": "2026-02-17", "location": "Guatemala City"},
                        "predict_next_eclipse": {"location": "Guatemala City"},
                        "get_eclipse_path": {"date": "2026-08-12"},
                        "get_safety_advice": {"eclipse_type": "solar"}
                    }
                },
                timestamp=datetime.now().isoformat()
            )
    
    except Exception as e:
        return MCPResponse(
            status="error",
            message=f"Error interno del servidor: {str(e)}",
            data={},
            timestamp=datetime.now().isoformat()
        )

if __name__ == "__main__":
    # Configuración para desarrollo local y despliegue
    port = int(os.environ.get("PORT", 8000))
    host = os.environ.get("HOST", "0.0.0.0")
    
    print(f"🌒 Iniciando Eclipse Calculator MCP Server en {host}:{port}")
    print(f"📡 Endpoints disponibles:")
    print(f"   GET  / - Información del servidor")
    print(f"   GET  /health - Health check")
    print(f"   POST /mcp - Endpoint MCP principal")
    print(f"🌍 Eclipses disponibles: {len(ECLIPSES_DATA)} eventos")
    print(f"🚀 Listo para desplegar en la nube!")
    
    uvicorn.run(
        "remote_eclipse_mcp:app",
        host=host,
        port=port,
        reload=True if os.environ.get("ENV") == "development" else False
    )