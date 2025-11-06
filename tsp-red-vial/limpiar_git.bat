@echo off
REM Script para eliminar archivos de Copilot y cache del repositorio Git
REM Este script elimina los archivos del historial de Git pero los mantiene localmente

echo ====================================================
echo Limpiando archivos de Copilot y cache de Git
echo ====================================================
echo.

cd ..

REM Eliminar archivos especificos de Copilot en .idea
echo [1/6] Eliminando archivos de Copilot...
git rm --cached .idea/copilot.data.migration.agent.xml 2>nul
git rm --cached .idea/copilot.data.migration.ask.xml 2>nul
git rm --cached .idea/copilot.data.migration.ask2agent.xml 2>nul
git rm --cached .idea/copilot.data.migration.edit.xml 2>nul
git rm --cached .idea/copilot*.xml 2>nul

REM Eliminar directorios de Copilot
git rm -r --cached .copilot 2>nul
git rm -r --cached .github/copilot 2>nul

REM Eliminar otros archivos de Copilot
git rm --cached copilot*.json 2>nul
git rm --cached *.copilot* 2>nul

echo [2/6] Eliminando archivos de IDEs...
REM Eliminar otros archivos de .idea
git rm -r --cached .idea 2>nul
git rm -r --cached .vscode 2>nul
git rm -r --cached .vs 2>nul

echo [3/6] Eliminando archivos de Python...
REM Eliminar archivos de Python
git rm -r --cached __pycache__ 2>nul
git rm --cached *.pyc 2>nul
git rm --cached *.pyo 2>nul
git rm -r --cached venv 2>nul
git rm -r --cached env 2>nul

echo [4/6] Eliminando archivos de Node...
REM Eliminar node_modules si existe
git rm -r --cached node_modules 2>nul
git rm -r --cached dist 2>nul

echo [5/6] Eliminando archivos temporales...
REM Eliminar temporales
git rm --cached *.tmp 2>nul
git rm --cached *.bak 2>nul
git rm --cached *~ 2>nul

echo [6/6] Finalizando...
echo.
echo ====================================================
echo ARCHIVOS ELIMINADOS DEL INDICE DE GIT
echo (Los archivos se mantienen en tu disco local)
echo ====================================================
echo.
echo SIGUIENTE PASO: Ejecuta estos comandos para completar:
echo.
echo   git add .gitignore
echo   git commit -m "chore: actualizar .gitignore y eliminar archivos de Copilot/cache"
echo   git push
echo.
echo ====================================================
pause

