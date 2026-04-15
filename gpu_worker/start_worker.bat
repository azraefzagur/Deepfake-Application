@echo off
echo ============================================
echo  DeepFake GPU Worker - Baslatiliyor
echo ============================================
echo.

REM Proje kök dizinine git (gpu_worker/ bir üst klasörde)
cd /d "%~dp0.."

REM Sanal ortamı aktif et
call .venv_deepfake\Scripts\activate.bat

echo [1/2] gpu_worker ortam kontrol ediliyor...
python -c "import torch; print('CUDA:', torch.cuda.is_available(), '| GPU:', torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'N/A')"

echo.
echo [2/2] GPU Worker baslatiyor (port 8001)...
cd gpu_worker
uvicorn api:app --host 0.0.0.0 --port 8001 --reload

pause
