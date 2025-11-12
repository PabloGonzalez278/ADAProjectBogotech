@echo off
echo ========================================
echo   INICIANDO SERVIDOR TSP RED VIAL
echo ========================================
echo.

REM Activar entorno virtual
echo [1/3] Activando entorno virtual...
call venv\Scripts\activate.bat

REM Verificar instalacion de python-multipart
echo [2/3] Verificando dependencias...
pip show python-multipart >nul 2>&1
if errorlevel 1 (
    echo Instalando python-multipart...
    pip install python-multipart
)

REM Iniciar servidor
echo [3/3] Iniciando servidor FastAPI...
echo.
echo ========================================
echo   Servidor corriendo en:
echo   http://127.0.0.1:8000
echo   http://localhost:8000
echo
echo   Documentacion interactiva:
echo   http://localhost:8000/docs
echo ========================================
echo.
echo Presiona Ctrl+C para detener el servidor
echo.

python servidor.py

