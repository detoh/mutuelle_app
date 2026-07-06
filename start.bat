@echo off
echo ========================================
echo   MUTUELLE SOLIDAIRE - Démarrage
echo ========================================

cd /d C:\mutuelle_app
call venv\Scripts\activate

if not exist .env (
    echo ERREUR: Fichier .env manquant!
    pause
    exit /b 1
)

if not exist logs mkdir logs
if not exist instance mkdir instance
if not exist static\uploads\photos mkdir static\uploads\photos

echo Démarrage du serveur...
echo URL: http://127.0.0.1:8000
echo ========================================
python run_prod.py

pause