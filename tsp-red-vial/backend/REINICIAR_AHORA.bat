@echo off
echo ========================================
echo REINICIANDO SERVIDOR BACKEND
echo ========================================
echo.

cd /d "%~dp0"

echo [1/3] Buscando procesos en puerto 8000...
FOR /F "tokens=5" %%P IN ('netstat -ano ^| findstr :8000') DO (
    echo Terminando proceso %%P
    taskkill /F /PID %%P >nul 2>&1
)

timeout /t 2 /nobreak >nul

echo [2/3] Activando entorno virtual...
if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
) else (
    echo ERROR: No se encontro el entorno virtual
    echo Ejecuta primero: python -m venv venv
    pause
    exit /b 1
)

echo [3/3] Iniciando servidor...
echo.
echo Servidor estara disponible en: http://localhost:8000
echo Documentacion API: http://localhost:8000/docs
echo.
echo Presiona Ctrl+C para detener el servidor
echo.

python servidor.py

pause

