#!/bin/bash
# Script para iniciar todo el sistema en Linux/macOS

# Obtener el directorio donde se encuentra el script para usar rutas absolutas
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
BACKEND_DIR="$SCRIPT_DIR/tsp-red-vial/backend"
FRONTEND_DIR="$SCRIPT_DIR/tsp-red-vial/frontend"

echo "--- Iniciando el sistema ---"
echo "Directorio del Backend: $BACKEND_DIR"
echo "Directorio del Frontend: $FRONTEND_DIR"

# --- Backend ---
echo "[Backend] Iniciando en una nueva terminal..."
gnome-terminal --working-directory="$BACKEND_DIR" -- bash -c '
  echo "--- Configurando Backend (en `pwd`) ---"
  if [ ! -d "venv" ]; then
    echo "Creando entorno virtual (venv)..."
    python3 -m venv venv
  fi
  echo "Activando entorno virtual..."
  source venv/bin/activate
  echo "Instalando dependencias desde requerimientos.txt..."
  pip install -r requerimientos.txt
  echo "--- Iniciando Servidor Backend en http://localhost:8000 ---"
  python3 servidor.py
  echo "--- El servidor backend ha terminado. Presiona Enter para cerrar. ---"
  read
'

echo "Esperando 5 segundos para que el backend se inicie correctamente..."
sleep 5

# --- Frontend ---
echo "[Frontend] Iniciando en una nueva terminal..."
gnome-terminal --working-directory="$FRONTEND_DIR" -- bash -c '
  echo "--- Configurando Frontend (en `pwd`) ---"
  echo "Instalando dependencias de Node.js (npm install)..."
  npm install
  echo "--- Iniciando Servidor Frontend en http://localhost:5173 ---"
  npm run dev
  echo "--- El servidor frontend ha terminado. Presiona Enter para cerrar. ---"
  read
'

echo "✅ Sistema iniciado."
echo "Backend debería estar en http://localhost:8000"
echo "Frontend debería estar en http://localhost:5173"
echo "Nota: Puede que necesites dar permisos de ejecución al script con: chmod +x INICIAR_SISTEMA.sh"
