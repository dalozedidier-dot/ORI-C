@echo off
set WORKSPACE=%1
if "%WORKSPACE%"=="" set WORKSPACE=travail_ORI-C
python -m pip install -e .
if errorlevel 1 exit /b 1
oric-full bootstrap "%WORKSPACE%"
