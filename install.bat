@echo off
pip3 install -r requirements.txt
if "%ERRORLEVEL%"=="9009" echo python3 cmd didnt work, trying python && pip install -r requirements.txt