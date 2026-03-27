@echo off
REM Setup script for Presidio NER dependencies

echo Installing Redactosaurus NER dependencies...
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python 3.8 or later from https://www.python.org/
    pause
    exit /b 1
)

REM Install Python packages
echo Installing Presidio and spaCy...
python -m pip install --upgrade pip
python -m pip install -r "%~dp0requirements.txt"

if errorlevel 1 (
    echo Error: Failed to install Python packages
    pause
    exit /b 1
)

echo.
echo Downloading spaCy en_core_web_md model...
python -m spacy download en_core_web_md

if errorlevel 1 (
    echo Error: Failed to download spaCy model
    pause
    exit /b 1
)

REM Verify installation
echo.
echo Verifying installation...
python -c "import presidio_analyzer; print('Presidio:', presidio_analyzer.__version__)"
python -c "import spacy; nlp = spacy.load('en_core_web_md'); print('spaCy model loaded successfully')"

if errorlevel 0 (
    echo.
    echo Installation complete! NER mode is ready to use.
) else (
    echo.
    echo Installation verification failed. Please check the errors above.
    pause
    exit /b 1
)

pause
