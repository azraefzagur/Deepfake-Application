@echo off
echo ===================================================
echo Starting DeepFake Services...
echo ===================================================

echo.
echo [1/3] Starting GPU Worker (RTX 3050 Ti)...
start "GPU Worker" powershell -NoExit -Command "cd C:\DeepFake\gpu_worker; .\venv\Scripts\activate; $env:PATH = 'C:\DeepFake\gpu_worker\venv\Lib\site-packages\nvidia\cudnn\bin;C:\DeepFake\gpu_worker\venv\Lib\site-packages\torch\lib;' + $env:PATH; .\start_worker.bat"

echo [2/3] Starting Signaling Server...
start "Signaling Server" powershell -NoExit -Command "cd C:\DeepFake\aws_server\signaling; ..\venv\Scripts\activate; uvicorn main:app --host 0.0.0.0 --port 8000"

echo [3/3] Starting React Frontend...
start "React Frontend" powershell -NoExit -Command "cd C:\DeepFake\aws_server\frontend; npm run dev"

echo.
echo All services have been launched in separate PowerShell windows!
echo You can minimize them once you see the successful startup messages.
echo ===================================================
