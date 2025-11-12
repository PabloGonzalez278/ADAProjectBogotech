@echo off
echo ========================================
echo   LIMPIAR Y REINICIAR SERVIDOR
echo ========================================
echo.

REM Buscar procesos Python corriendo
echo [1/4] Buscando procesos Python en puerto 8000...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8000') do (
    echo Cerrando proceso %%a...
    taskkill /F /PID %%a 2>nul
)

REM Esperar un momento
echo [2/4] Esperando que se libere el puerto...
timeout /t 2 /nobreak >nul

REM Activar entorno virtual
echo [3/4] Activando entorno virtual...
call venv\Scripts\activate.bat

REM Verificar python-multipart
echo [4/4] Verificando dependencias...
pip show python-multipart >nul 2>&1
if errorlevel 1 (
    echo Instalando python-multipart...
    pip install python-multipart
)

echo.
echo ========================================
echo   INICIANDO SERVIDOR EN PUERTO 8000
echo ========================================
echo.
echo Presiona Ctrl+C para detener
echo.

python servidor.py

