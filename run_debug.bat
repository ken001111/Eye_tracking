@echo off
cd /d "%~dp0"
echo ===========================================
echo DEBUGGING MODE
echo ===========================================
echo Current Directory: %CD%
set PYTHONPATH=%CD%
echo PYTHONPATH set to: %PYTHONPATH%

echo.
echo Attempting to launch...
"python_portable\python.exe" -c "import sys; import os; print('Python Executable:', sys.executable); print('System Path:', sys.path); print('Current Working Dir:', os.getcwd()); import gui_app; print('SUCCESS: gui_app found!'); import main"
pause
