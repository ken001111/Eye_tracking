@echo off
setlocal
cd /d "%~dp0"

echo ========================================================
echo  Setting up Portable Python 3.11 (Fixing Imports)
echo ========================================================

IF EXIST "python_portable" (
    echo cleaning up old portable folder...
    rmdir /s /q python_portable
)

echo Downloading Python 3.11.9 Video Embeddable Package...
curl -L -o python_portable.zip "https://www.python.org/ftp/python/3.11.9/python-3.11.9-embed-amd64.zip"

echo Extracting...
mkdir python_portable
tar -xf python_portable.zip -C python_portable

echo Cleaning up zip...
del python_portable.zip

echo Configuring environment (pip + local imports)...
REM 1. Enable 'import site' for pip
powershell -Command "(Get-Content python_portable\python311._pth) -replace '#import site', 'import site' | Set-Content python_portable\python311._pth"

REM 2. Add current directory to path so main.py can import gui_app.py
echo .>> "python_portable\python311._pth"

echo Downloading pip installer...
curl -L -o get-pip.py "https://bootstrap.pypa.io/get-pip.py"

echo Installing Pip...
"python_portable\python.exe" get-pip.py
del get-pip.py

echo.
echo Installing requirements...
"python_portable\python.exe" -m pip install --no-warn-script-location -r requirements.txt

IF %ERRORLEVEL% NEQ 0 (
    echo.
    echo ERROR: Failed to install requirements!
    pause
    exit /b
)

echo.
echo ========================================================
echo  Setup Complete!
echo  To run the app, double-click: run_portable.bat
echo ========================================================

(
echo @echo off
echo cd /d "%%~dp0"
echo "python_portable\python.exe" main.py --mode gui
echo pause
) > run_portable.bat

pause
