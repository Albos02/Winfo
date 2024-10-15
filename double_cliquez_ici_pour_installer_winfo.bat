@echo off
setlocal enabledelayedexpansion

set "current_dir=%cd%"

set "winfo_dir_file=%current_dir%\winfo_dir"

set "filename1=winfo_file_exists.bat"
set "filename2=winfo_shortcut.bat"
set "filename3=winfo_wind_limit.bat"


(
    echo @echo off
    echo cd "%current_dir%" 
    echo start /MIN %filename1%
    echo start /MIN %filename2%
    echo start /MIN %filename3%
) > "%USERPROFILE%\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup\winfo_startup.bat"

cd "%USERPROFILE%\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup\"
start /MIN winfo_startup.bat