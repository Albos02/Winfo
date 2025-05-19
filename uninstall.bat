@echo off

REM Remove startup file
del "%USERPROFILE%\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup\winfo_startup.bat" 2>nul

REM Store current directory
set "APP_DIR=%CD%"

REM Get out of folder before creating temp file
cd /d "%TEMP%"

REM Create simple cleanup script
echo @rd /s /q "%APP_DIR%" > "%TEMP%\cleanup.bat"

REM Launch cleanup and exit
start "" cmd /c "%TEMP%\cleanup.bat"
exit