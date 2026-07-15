@echo off

cd /d "%~dp0"

python catalog_generator.py

echo.
echo ==========================================
echo   CATALOG GENERATION FINISHED
echo ==========================================
pause