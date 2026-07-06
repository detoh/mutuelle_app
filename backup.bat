@echo off
setlocal

:: Date du jour
set DATE=%date:~6,4%%date:~3,2%%date:~0,2%_%time:~0,2%%time:~3,2%
set DATE=%DATE: =0%

:: Dossiers
set BACKUP_DIR=C:\mutuelle_app\backups
set DB_SOURCE=C:\mutuelle_app\instance\mutuelle.db
set DB_BACKUP=%BACKUP_DIR%\mutuelle_%DATE%.db

:: Créer le dossier de backup
if not exist %BACKUP_DIR% mkdir %BACKUP_DIR%

:: Sauvegarder la base de données
echo Sauvegarde de la base de données...
copy /Y %DB_SOURCE% %DB_BACKUP%

:: Garder seulement les 7 derniers backups
echo Nettoyage des anciens backups...
forfiles /p %BACKUP_DIR% /s /m *.db /d -7 /c "cmd /c del @path"

echo ========================================
echo   Sauvegarde terminée!
echo   Fichier: %DB_BACKUP%
echo ========================================

pause