@echo off
setlocal

set "ROOT=%~dp0"
set "VENV=%ROOT%.venv39\Scripts\python.exe"
set "MPLCONFIGDIR=%ROOT%.matplotlib"
set "ALBUMENTATIONS_DISABLE_VERSION_CHECK=1"

if not exist "%VENV%" (
    echo Python 3.9 virtual environment not found:
    echo %VENV%
    echo.
    echo Create it first:
    echo cd /d "%ROOT%"
    echo py -3.9 -m venv .venv39
    pause
    exit /b 1
)

if not exist "%MPLCONFIGDIR%" mkdir "%MPLCONFIGDIR%"

echo ===================================================
echo Starting DeepFake Services from:
echo %ROOT%
echo ===================================================

echo.
echo [1/3] Starting GPU Worker API on http://127.0.0.1:8001
start "DeepFake GPU Worker" powershell -NoExit -Command "$env:MPLCONFIGDIR='%MPLCONFIGDIR%'; $env:ALBUMENTATIONS_DISABLE_VERSION_CHECK='1'; cd '%ROOT%gpu_worker'; '%VENV%' -m uvicorn api:app --host 127.0.0.1 --port 8001"

echo [2/3] Starting Signaling Server on http://127.0.0.1:8000
start "DeepFake Signaling" powershell -NoExit -Command "$env:MPLCONFIGDIR='%MPLCONFIGDIR%'; $env:ALBUMENTATIONS_DISABLE_VERSION_CHECK='1'; cd '%ROOT%aws_server\signaling'; '%VENV%' -m uvicorn main:app --host 127.0.0.1 --port 8000"

echo [3/3] Starting React Frontend on http://127.0.0.1:3000
start "DeepFake Frontend" powershell -NoExit -Command "cd '%ROOT%aws_server\frontend'; npm run dev -- --host 127.0.0.1 --port 3000"

echo.
echo Open this in your browser:
echo http://127.0.0.1:3000/
echo.
echo In the frontend, use this signaling URL:
echo ws://127.0.0.1:8000
echo ===================================================
pause
