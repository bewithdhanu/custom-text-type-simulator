@echo off
echo Cleaning up old build files...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
echo.
echo Building simulator.exe using PyInstaller...
echo This may take a few moments...
.venv\Scripts\pyinstaller.exe --onefile --icon=icon.ico --add-data "icon.ico;." simulator.py

echo.
if exist dist\simulator.exe (
    echo ========================================================
    echo SUCCESS: Build complete! 
    echo Your executable is located at: dist\simulator.exe
    echo ========================================================
) else (
    echo ========================================================
    echo ERROR: Build failed. Please check the logs above.
    echo ========================================================
)

pause
