@echo off
echo ========================================
echo   Project Cleanup Script
echo ========================================
echo.

echo [1/5] Cleaning Python cache files...
for /d /r . %%d in (__pycache__) do @if exist "%%d" rd /s /q "%%d"
del /s /q *.pyc 2>nul
del /s /q *.pyo 2>nul
echo Done.

echo.
echo [2/5] Cleaning Node modules cache...
cd frontend
if exist node_modules\.cache rmdir /s /q node_modules\.cache
echo Done.

echo.
echo [3/5] Cleaning ML artifacts...
cd ..
if exist ml\models\*.png del /q ml\models\*.png
if exist ml\results\*.pkl del /q ml\results\*.pkl
echo Done.

echo.
echo [4/5] Cleaning build artifacts...
if exist frontend\build rmdir /s /q frontend\build
if exist .pytest_cache rmdir /s /q .pytest_cache
if exist .coverage del /q .coverage
echo Done.

echo.
echo [5/5] Cleaning temporary files...
del /q *.log 2>nul
del /q *.tmp 2>nul
echo Done.

echo.
echo ========================================
echo   Cleanup Complete!
echo ========================================
echo.
echo Project is now clean and organized.
pause
