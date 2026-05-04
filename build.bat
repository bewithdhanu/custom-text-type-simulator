@echo off
echo Cleaning up old build files...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist simulator.spec del /q simulator.spec

echo.
if not exist "tesseract_bin" (
    echo Downloading and extracting Portable Tesseract OCR...
    powershell -Command "Invoke-WebRequest -Uri 'https://github.com/UB-Mannheim/tesseract/releases/download/v5.3.3.20231005/tesseract-ocr-w64-setup-5.3.3.20231005.exe' -OutFile 'tesseract-setup.exe'"
    start /wait tesseract-setup.exe /S /D=%CD%\tesseract_bin
    del tesseract-setup.exe
)

echo.
echo Building simulator.exe using PyInstaller...
echo This may take a few moments...
.venv\Scripts\pyinstaller.exe --onefile --icon=icon.ico --add-data "icon.ico;." --add-data "tesseract_bin;tesseract_bin" simulator.py

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
