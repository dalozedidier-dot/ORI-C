@echo off
setlocal
set "ROOT=%~dp0"
py -m venv "%ROOT%.venv"
call "%ROOT%.venv\Scripts\activate.bat"
python -m pip install --no-index "%ROOT%wheel_corrige\oric_full_research-0.2.0-py3-none-any.whl"
oric-full validate-data --data-dir "%ROOT%donnees"
oric-full run --all --data-dir "%ROOT%donnees" --output-dir "%ROOT%resultats_reproduits"
endlocal
