@echo off
setlocal
cd /d "%~dp0"

echo ========================================================
echo  MANUAL DOWNLOAD REQUIRED (Updated Link)
echo ========================================================
echo.
echo The previous link might have been broken. Please try this one:
echo.
echo OPTION A (GitHub):
echo https://github.com/winpython/winpython/releases/download/7.2.20240427/Winpython64-3.11.9.0dot.exe
echo.
echo OPTION B (SourceForge - Reliable):
echo https://sourceforge.net/projects/winpython/files/WinPython_3.11/3.11.9.0/betas/Winpython64-3.11.9.0dotb5.exe/download
echo.
echo 1. Download one of these files.
echo 2. RENAME it to: Winpython64.exe
echo 3. Move it to this folder:
echo    %CD%
echo.
echo 4. Press any key here AFTER you have done that.
echo ========================================================
pause

if not exist "Winpython64.exe" (
    echo.
    echo ERROR: Could not find "Winpython64.exe".
    echo Did you forget to rename it?
    pause
    exit /b
)

echo.
echo Found file! Extracting...
Winpython64.exe -y

echo.
echo Cleaning up installer...
del Winpython64.exe

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
