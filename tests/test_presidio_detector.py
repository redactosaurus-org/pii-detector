import pytest
import sys
import os
import json

# Add the project root to sys.path to import presidio_detector
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from presidio_detector import detect_pii

def test_detect_pii_email():
    text = "My email is test@example.com"
    result = detect_pii(text)
    assert result["ok"] is True
    assert any(ent["type"] == "EMAIL_ADDRESS" for ent in result["entities"])
    assert any(ent["text"] == "test@example.com" for ent in result["entities"])

def test_detect_pii_phone():
    text = "Call me at 555-123-4567"
    result = detect_pii(text)
    assert result["ok"] is True
    assert any(ent["type"] == "PHONE_NUMBER" for ent in result["entities"])
    assert any("555-123-4567" in ent["text"] for ent in result["entities"])

def test_detect_pii_organization():
    text = "I work at Microsoft Corporation"
    result = detect_pii(text)
    assert result["ok"] is True
    assert any(ent["type"] == "ORGANIZATION" for ent in result["entities"])
    assert any("Microsoft" in ent["text"] for ent in result["entities"])

def test_detect_pii_empty():
    text = ""
    result = detect_pii(text)
    # The current implementation returns {"ok": True, "entities": [], "error": None} for empty text in main()
    # But detect_pii itself might handle it differently inside.
    # Looking at the code: it analyzes the text.
    assert result["ok"] is True
    assert len(result["entities"]) == 0

def test_detect_pii_no_pii():
    text = "Hello world, this is a normal sentence."
    result = detect_pii(text)
    assert result["ok"] is True
    assert len(result["entities"]) == 0

def test_detect_pii_multiple():
    text = "John Doe works at Google. Reach him at john.doe@google.com"
    result = detect_pii(text)
    assert result["ok"] is True
    entity_types = [ent["type"] for ent in result["entities"]]
    assert "PERSON" in entity_types
    assert "ORGANIZATION" in entity_types
    assert "EMAIL_ADDRESS" in entity_types
