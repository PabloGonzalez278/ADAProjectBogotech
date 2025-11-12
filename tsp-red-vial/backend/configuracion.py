"""
Configuración del proyecto TSP
"""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Configuracion(BaseSettings):
    """Configuración de la aplicación"""

    # API
    API_TITULO: str = "TSP en Redes Viales API"
    API_VERSION: str = "1.0.0"
    API_DESCRIPCION: str = "API para resolver el Travelling Salesman Problem sobre redes viales"

    # CORS
    CORS_ORIGENES: list[str] = ["http://localhost:5173", "http://127.0.0.1:5173"]

    # Límites
    MAX_PUNTOS_FUERZA_BRUTA: int = 11  # Máximo para fuerza bruta
    MAX_PUNTOS_HELD_KARP: int = 20      # Máximo para Held-Karp

    # Rutas de archivos temporales
    DIRECTORIO_TEMPORAL: str = "temp"

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True
    )


# Instancia global de configuración
config = Configuracion()

