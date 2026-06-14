@echo off
echo Building LittleMiner executable...

REM Check if PyInstaller is installed
pyinstaller --version >nul 2>&1
if errorlevel 1 (
    echo Installing PyInstaller...
    pip install pyinstaller
)

REM Build the executable
echo Building executable with PyInstaller...
pyinstaller --onefile --windowed --icon=icon.ico littleminer.spec

echo.
echo Build completed!
echo The executable is located in the 'dist' directory.
pause