@echo off
setlocal
cd /d "%~dp0"
title Cat Fantasy Survivors - build executable

rem Pick a Python: the "py" launcher if available, otherwise "python"
set "PY=python"
where py >nul 2>nul && set "PY=py -3"

echo.
echo === Cat Fantasy Survivors - building the executable ===
echo Using: %PY%
%PY% --version || (echo Python not found. Install it from python.org and try again. & pause & exit /b 1)

echo.
echo [1/3] Checking dependencies...
%PY% -c "import pygame" 2>nul || %PY% -m pip install pygame-ce
%PY% -c "import openpyxl" 2>nul || %PY% -m pip install openpyxl
%PY% -m pip install --upgrade pyinstaller || (echo Could not install PyInstaller. & pause & exit /b 1)

echo.
echo [2/3] Building (this takes about a minute)...
%PY% -m PyInstaller --noconfirm --clean --onefile --windowed ^
    --name CatFantasySurvivors --icon icon.ico ^
    --add-data "classes.xlsx;." ^
    --add-data "Jersey10-Regular.ttf;." ^
    --exclude-module numpy --exclude-module tkinter ^
    survivors.py || (echo Build failed - see the messages above. & pause & exit /b 1)

echo.
echo [3/3] Packing the release...
rem game version (version.py) in the .zip name: CatFantasySurvivors-0.0.20.zip
set "VER="
for /f "delims=" %%v in ('%PY% -c "import version; print(version.VERSION)"') do set "VER=%%v"
if "%VER%"=="" (set "ZIP=CatFantasySurvivors.zip") else (set "ZIP=CatFantasySurvivors-%VER%.zip")
if not exist Release mkdir Release
copy /y "dist\CatFantasySurvivors.exe" "Release\CatFantasySurvivors.exe" >nul
if exist "LEIA-ME.txt" copy /y "LEIA-ME.txt" "Release\LEIA-ME.txt" >nul
if exist "OFL-Jersey10.txt" copy /y "OFL-Jersey10.txt" "Release\OFL-Jersey10.txt" >nul
powershell -NoProfile -Command "Compress-Archive -Force -Path 'Release\CatFantasySurvivors.exe','Release\LEIA-ME.txt' -DestinationPath 'Release\%ZIP%'"

rmdir /s /q build 2>nul
del /q CatFantasySurvivors.spec 2>nul

echo.
echo Done!
echo   Release\CatFantasySurvivors.exe  - double-click to play
echo   Release\%ZIP%  - send this one to testers (includes LEIA-ME.txt)
echo The tester's progress is saved in save.json next to the .exe.
echo.
pause
