@echo off
setlocal enabledelayedexpansion

set "current_dir=%cd%"

set "filename1=winfo_shortcut.exe"
set "filename2=winfo_wind_limit.exe"

cd "%USERPROFILE%\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup\"
(
    echo @echo off
    echo cd "%current_dir%" 
    echo start /MIN "winfo background tasks : shortcut" %filename1%
    echo start /MIN "winfo background tasks : wind limit" %filename2%

    echo exit
) > "winfo_startup.bat"

start /MIN "winfo_startup.bat" "winfo_startup.bat"