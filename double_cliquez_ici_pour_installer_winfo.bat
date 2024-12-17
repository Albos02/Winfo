@echo off
setlocal enabledelayedexpansion

set "current_dir=%cd%"

set "filename1=winfo_shortcut.py"
set "filename2=winfo_wind_limit.py"

cd "%USERPROFILE%\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup\"
(
    echo @echo off
    echo cd "%current_dir%" 
    echo start /MIN "winfo background tasks : shortcut" %filename1%
    echo start /MIN "winfo background tasks : wind limit" %filename2%

    echo exit
) > "winfo_startup.bat"

@REM set "desktop=%USERPROFILE%\Desktop"
@REM set "shortcut_name=Winfo.lnk"
@REM powershell "$ws = New-Object -ComObject WScript.Shell; $s = $ws.CreateShortcut('%desktop%\%shortcut_name%'); $s.TargetPath = '%current_dir%\Winfo.py'; $s.Save()"


start /MIN "winfo_startup.bat" "winfo_startup.bat"
start "Winfo" "Winfo.py"