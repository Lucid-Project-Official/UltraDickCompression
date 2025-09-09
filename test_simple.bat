@echo off
echo Test simple d'UltraCompression
echo.

echo Test 1: Version Python
python --version
if errorlevel 1 (
    echo ERREUR: Python non trouve
    pause
    exit /b 1
)

echo.
echo Test 2: Installation psutil
pip install psutil
if errorlevel 1 (
    echo ERREUR: Impossible d'installer psutil
    pause
    exit /b 1
)

echo.
echo Test 3: Test d'import basique
python -c "import tkinter; import os; import sys; print('Imports de base OK')"
if errorlevel 1 (
    echo ERREUR: Probleme avec les imports de base
    pause
    exit /b 1
)

echo.
echo Test 4: Test des modules personnalises
python -c "from compression_optimizer import CompressionOptimizer; import config; print('Modules personnalises OK')"
if errorlevel 1 (
    echo ERREUR: Probleme avec les modules personnalises
    pause
    exit /b 1
)

echo.
echo ✅ Tous les tests de base sont passes!
echo L'application devrait fonctionner correctement.
echo.
echo Pour lancer l'application:
echo   python ultra_compression.py
echo.
pause
