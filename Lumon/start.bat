@echo off
title AI Business Management Suite
echo.
echo   Starting AI Business Management Suite...
echo   =========================================
echo.
cd /d "%~dp0"
python start.py %*
pause
