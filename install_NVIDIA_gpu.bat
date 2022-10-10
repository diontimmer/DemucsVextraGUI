@echo off
pip3 install torch torchvision torchaudio --extra-index-url https://download.pytorch.org/whl/cu116
if "%ERRORLEVEL%"=="9009" echo pip3 cmd didnt work, trying pip install torch torchvision torchaudio --extra-index-url https://download.pytorch.org/whl/cu116
pip3 install -r requirements.txt
if "%ERRORLEVEL%"=="9009" echo python3 cmd didnt work, trying python && pip install -r requirements.txt
@echo on
