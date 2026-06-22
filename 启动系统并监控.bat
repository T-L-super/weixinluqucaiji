@echo off
chcp 65001 >nul
title 大学录取信息整理系统

echo ==============================================
echo   大学录取信息整理系统 - 自动重启监控
echo ==============================================
echo.
echo Server: http://localhost:8000
echo Press Ctrl+C to stop
echo.

:RESTART
echo [%time%] Starting server...
cd /d "%~dp0backend"
".venv\Scripts\python.exe" run.py

echo [%time%] Server stopped. Restarting in 5 seconds...
timeout /t 5 /nobreak >nul
goto RESTART
