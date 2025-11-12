"""
Configuración de pytest para las pruebas.
Configura el path para que pytest pueda encontrar el módulo dominio.
"""

import sys
from pathlib import Path

# Agregar el directorio backend al path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))
