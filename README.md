# Redactosaurus Core Engine - NER Module

Local, offline PII (Personally Identifiable Information) detection using Microsoft Presidio and spaCy.

## Features

- **Local-only processing**: No internet access required, no cloud API calls
- **Offline models**: Uses pre-downloaded spaCy model (`en_core_web_md`)
- **No auto-downloads**: Explicitly disables transformers, Stanza, and Hugging Face Hub
- **Custom recognition**: Includes organization detection via spaCy NER
- **Privacy-focused**: All data stays on your machine

## Prerequisites

- Python 3.8 or later
- `pip` (Python package manager)

## Setup

### Option 1: Automated Setup (Windows)

```bash
setup_ner.bat
```

### Option 2: Manual Setup

1. Install Python packages:

   ```bash
   pip install -r requirements.txt
   ```

2. Download spaCy model:

   ```bash
   python -m spacy download en_core_web_md
   ```

3. Verify installation:
   ```bash
   python check_spacy_model.py
   ```

## Usage

### Python API

```python
from presidio_detector import detect_pii

result = detect_pii("My name is John Doe and my email is john@example.com")
print(result)
```

### Command Line

```bash
echo '{"text": "Call me at 555-1234 or email test@example.com"}' | python presidio_detector.py
```

## Files

- **presidio_detector.py**: Main PII detection engine
- **check_spacy_model.py**: Validation utility for spaCy model installation
- **requirements.txt**: Python dependencies (Presidio, spaCy)
- **setup_ner.bat**: Windows setup script (optional)
- **setup_ner.ps1**: PowerShell setup script (optional)

## Configuration

Environment variables (automatically set in code):

- `HF_DATASETS_OFFLINE=1` - Disables Hugging Face data auto-download
- `TRANSFORMERS_OFFLINE=1` - Disables transformers auto-download
- `HF_HUB_OFFLINE=1` - Disables Hugging Face Hub access

## Detected Entity Types

- PERSON
- EMAIL_ADDRESS
- PHONE_NUMBER
- CREDIT_CARD
- ORGANIZATION
- DATE_TIME
- And other PII categories

## Troubleshooting

### "Presidio not installed or spaCy model missing"

Run the setup script:

```bash
setup_ner.bat
```

Or manually install:

```bash
pip install -r requirements.txt
python -m spacy download en_core_web_md
```

### spaCy model fails to load

Verify installation:

```bash
python check_spacy_model.py
```

If it fails, reinstall:

```bash
python -m spacy download en_core_web_md
```
