@echo off
setlocal
cd /d "%~dp0"

set "WINPY_EXE=Winpython64-3.11.9.0dot.exe"

echo ========================================================
echo  MANUAL DOWNLOAD REQUIRED
echo ========================================================
echo.
echo The automatic download failed. Please help me:
echo.
echo 1. Open this link in your browser:
echo    https://github.com/winpython/winpython/releases/download/7.2.20240427/Winpython64-3.11.9.0dot.exe
echo.
echo 2. Download the file (%WINPY_EXE%).
echo.
echo 3. Save/Move it into this folder:
echo    %CD%
echo.
echo 4. Press any key here AFTER you have done that.
echo ========================================================
pause

IF NOT EXIST "%WINPY_EXE%" (
    echo.
    echo ERROR: I still cannot find "%WINPY_EXE%" in this folder.
    echo Please make sure you moved it here.
    pause
    exit /b
)

echo.
echo Found file! Extracting...
%WINPY_EXE% -y

echo.
echo Cleaning up installer...
del %WINPY_EXE%

echo.
echo Installing requirements...
REM Find python.exe
set "PYTHON_EXE="
for /d %%D in (WPy64-*) do (
    if exist "%%D\python-*\python.exe" (
        for /d %%P in ("%%D\python-*") do (
            set "PYTHON_EXE=%%P\python.exe"
        )
    )
)

if "%PYTHON_EXE%"=="" (
    echo ERROR: Extraction failed. Python not found.
    pause
    exit /b
)

"%PYTHON_EXE%" -m pip install -r requirements.txt

echo.
echo ========================================================
echo  Setup Complete!
echo  To start the app, double-click: run_portable.bat
echo ========================================================

REM Create the runner script
(
echo @echo off
echo cd /d "%%~dp0"
echo set "PYTHON_EXE="
echo for /d %%%%D in ^(WPy64-*^) do ^(
echo     if exist "%%%%D\python-*\python.exe" ^(
echo         for /d %%%%P in ^("%%%%D\python-*"^) do set "PYTHON_EXE=%%%%P\python.exe"
echo     ^)
echo ^)
echo "%%PYTHON_EXE%%" main.py --mode gui
echo pause
) > run_portable.bat

pause
