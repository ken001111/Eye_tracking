@echo off
echo ===========================================
echo SYSTEM DIAGNOSTICS
echo ===========================================

echo 1. Checking Architecture...
if "%PROCESSOR_ARCHITECTURE%"=="AMD64" goto 64BIT
if "%PROCESSOR_ARCHITEW6432%"=="AMD64" goto 64BIT
echo [FAIL] You seem to be running 32-bit Windows.
echo        This software REQUIRED 64-bit Windows (for MediaPipe).
goto END

:64BIT
echo [OK] 64-bit Windows detected.

echo.
echo 2. Checking Downloaded File Size...
if exist "Winpython64-3.11.9.0dot.exe" (
    for %%F in ("Winpython64-3.11.9.0dot.exe") do (
        echo File: %%F
        echo Size: %%~zF bytes
        
        REM Check if smaller than 10MB (approx 10000000 bytes)
        if %%~zF LSS 10000000 (
            echo [FAIL] The downloaded file is too small! Download failed.
        ) else (
            echo [OK] File size looks reasonable.
        )
    )
) else (
    echo [FAIL] WinPython installer not found!
)

:END
echo.
pause
