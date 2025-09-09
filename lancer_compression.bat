@echo off
echo Demarrage d'UltraCompression...
echo.

REM Verifier si Python est installe
python --version >nul 2>&1
if errorlevel 1 (
    echo ERREUR: Python n'est pas installe ou pas dans le PATH
    echo Veuillez installer Python depuis https://python.org
    pause
    exit /b 1
)

REM Verifier si 7zip est installe
7z >nul 2>&1
if errorlevel 1 (
    echo ERREUR: 7zip n'est pas installe ou pas dans le PATH
    echo Veuillez installer 7zip depuis https://7-zip.org
    pause
    exit /b 1
)

REM Installer les dependances si necessaire
if not exist "venv\" (
    echo Creation de l'environnement virtuel...
    python -m venv venv
)

echo Activation de l'environnement virtuel...
call venv\Scripts\activate.bat

echo Installation des dependances...
pip install -r requirements.txt

echo Lancement d'UltraCompression...
echo.
python ultra_compression.py

pause
