@echo off
setlocal
set "ROOT=%~dp0"
call "%ROOT%.venv\Scripts\activate.bat"
oric-full import-existing "%ROOT%.." --data-dir "%ROOT%campagne_maximale_reelle\data"
oric-full run --all --real-data-only --data-dir "%ROOT%campagne_maximale_reelle\data" --output-dir "%ROOT%campagne_maximale_reelle\resultats_reproduits" --oric-root "%ROOT%.."
endlocal
