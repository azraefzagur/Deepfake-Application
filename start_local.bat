@echo off
echo Starting all DeepFake Native Architecture components locally...

echo [1/3] Starting Signaling Server (FastAPI on Port 8000)...
start "Signaling Server" cmd /k "cd aws_server\signaling && call ..\venv\Scripts\activate && uvicorn main:app --host 0.0.0.0 --port 8000"

echo [2/3] Starting GPU Worker (RTX 3050 Ti Devrede)...
:: Yanlış olan .venv_deepfake yerine, tüm AI modellerinin olduğu gerçek gpu_worker\venv klasörüne gidiyoruz!
start "GPU Worker" cmd /k "cd gpu_worker && set PATH=C:\DeepFake\gpu_worker\venv\Lib\site-packages\nvidia\cudnn\bin;C:\DeepFake\gpu_worker\venv\Lib\site-packages\torch\lib;%PATH% && call venv\Scripts\activate && call start_worker.bat"

echo [3/3] Starting Frontend (React on Port 3000)...
start "Frontend" cmd /k "cd aws_server\frontend && npm run dev -- --host --port 3000"

echo All components started! Check the opened terminal windows.
echo Frontend should be available at http://localhost:3000
pause