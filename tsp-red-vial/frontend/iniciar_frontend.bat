@echo off
echo ========================================
echo Iniciando Frontend TSP Red Vial
echo ========================================
echo.

cd /d "%~dp0"

echo [1/3] Verificando instalacion de Node.js...
where node >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Node.js no esta instalado
    echo Descargalo desde: https://nodejs.org/
    pause
    exit /b 1
)

echo [2/3] Verificando dependencias...
if not exist "node_modules\" (
    echo Instalando dependencias por primera vez...
    call npm install
)

echo [3/3] Iniciando servidor de desarrollo...
echo.
echo Frontend estara disponible en: http://localhost:5173
echo Backend debe estar en: http://localhost:8000
echo.
echo Presiona Ctrl+C para detener el servidor
echo.

npm run dev

pause

