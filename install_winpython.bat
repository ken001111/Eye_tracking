@echo off
setlocal
cd /d "%~dp0"

echo ========================================================
echo  Downloading WinPython (GUI Version)
echo  This fixes the missing Tikinter/GUI error.
echo ========================================================

REM Defining a known working 3.11 release (dot version is small ~25MB)
set "WINPY_URL=https://github.com/winpython/winpython/releases/download/7.2.20240427/Winpython64-3.11.9.0dot.exe"
set "WINPY_EXE=Winpython64-3.11.9.0dot.exe"

echo Downloading %WINPY_EXE%...
curl -L -o %WINPY_EXE% "%WINPY_URL%"

IF %ERRORLEVEL% NEQ 0 (
    echo.
    echo ERROR: Download failed!
    echo Please check your internet connection.
    pause
    exit /b
)

echo.
echo Extracting WinPython...
echo (A black window might pop up for a second - that's normal)
%WINPY_EXE% -y

echo.
echo Cleaning up installer...
del %WINPY_EXE%

echo.
echo Installing requirements into WinPython...
REM Logic to find the python.exe in the extracted "WPy64-*" folder
set "PYTHON_EXE="
for /d %%D in (WPy64-*) do (
    if exist "%%D\python-*\python.exe" (
        for /d %%P in ("%%D\python-*") do (
            set "PYTHON_EXE=%%P\python.exe"
        )
    )
)

if "%PYTHON_EXE%"=="" (
    echo.
    echo ERROR: Could not find extracted Python executable!
    pause
    exit /b
)

"%PYTHON_EXE%" -m pip install -r requirements.txt

echo.
echo ========================================================
echo  Setup Complete!
echo  To start the app, double-click: run_portable.bat
echo ========================================================

REM Create the runner script pointing to WinPython
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
