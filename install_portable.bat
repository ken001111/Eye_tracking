@echo off
setlocal
cd /d "%~dp0"

echo ========================================================
echo  Setting up Portable Python 3.11 (No Admin Required)
echo ========================================================

IF EXIST "python_portable" (
    echo Python portable folder already exists. Skipping download.
    GOTO :INSTALL_DEPS
)

echo Downloading Python 3.11.9 Video Embeddable Package...
curl -L -o python_portable.zip "https://www.python.org/ftp/python/3.11.9/python-3.11.9-embed-amd64.zip"

echo Extracting...
mkdir python_portable
tar -xf python_portable.zip -C python_portable

echo Cleaning up zip...
del python_portable.zip

echo Configuring environment...
REM Enable site-packages to allow pip to work
echo import site>> "python_portable\python311._pth"

echo Downloading pip...
curl -L -o get-pip.py "https://bootstrap.pypa.io/get-pip.py"
"python_portable\python.exe" get-pip.py
del get-pip.py

:INSTALL_DEPS
echo.
echo Installing requirements into portable Python...
"python_portable\python.exe" -m pip install -r requirements.txt

echo.
echo ========================================================
echo  Setup Complete!
echo  To run the app, double-click: run_portable.bat
echo ========================================================

REM Create the runner script
(
echo @echo off
echo cd /d "%%~dp0"
echo "python_portable\python.exe" main.py --mode gui
echo pause
) > run_portable.bat

pause
