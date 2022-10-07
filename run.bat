@echo off 
python3 DemucsVextraGUI.py
if "%ERRORLEVEL%"=="9009" echo python3 cmd didnt work, trying python && python DemucsVextraGUI.py
@echo on
