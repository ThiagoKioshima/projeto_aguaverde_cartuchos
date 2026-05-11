@echo off
cd /d "%~dp0"
echo Iniciando AVC Gestao...
start "" "http://localhost:8501"
python -m streamlit run app.py
