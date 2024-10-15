@echo off
setlocal enabledelayedexpansion

:loop1
    for %%F in ("launch_customtkinter*") do (
        set "filename=%%~nxF"
        echo this file exists, %cd%\%filename%
        del !filename!
        start /d winfo.exe
    )
    goto loop1