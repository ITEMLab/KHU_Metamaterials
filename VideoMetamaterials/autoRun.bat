@echo off
setlocal

call C:\Users\user\anaconda3\Scripts\activate.bat video_abaqus

set PROJECT_DIR=C:\Users\user\Desktop\Metamaterials\VideoMetamaterials
set SAMPLES_PATH=%PROJECT_DIR%\runs\training\eval_target_w_5.0_1\step_200000

set PATH=C:\SIMULIA\Commands;%PATH%

cd /d "%PROJECT_DIR%"

echo Python path:
where python
python -c "import sys, numpy, scipy; print(sys.executable); print('numpy', numpy.__version__); print('scipy', scipy.__version__)"
echo.

for /L %%i in (0,1,31) do (
    echo Running Abaqus eval for sample_index %%i
    python eval_abaqus.py --samples_path "%SAMPLES_PATH%" --sample_index %%i
)

echo Done.
pause
