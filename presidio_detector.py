"""
Presidio NER detector for Redactosaurus
Uses Microsoft Presidio with spaCy en_core_web_md for local PII detection
No internet access, no auto-downloads, completely offline
"""

import sys
import json
import os

# Disable all remote model loading and auto-downloads
os.environ['HF_DATASETS_OFFLINE'] = '1'  # Disable Hugging Face auto-download
os.environ['TRANSFORMERS_OFFLINE'] = '1'  # Disable transformers auto-download
os.environ['HF_HUB_OFFLINE'] = '1'  # Disable Hugging Face Hub


def detect_pii(text):
    """
    Detect PII using Presidio with spaCy local model
    """
    try:
        # Import Presidio components
        from presidio_analyzer import AnalyzerEngine, RecognizerRegistry, EntityRecognizer, RecognizerResult
        from presidio_analyzer.nlp_engine import NlpEngineProvider
        
        # Configure NLP engine to use ONLY local spaCy model
        # Explicitly disable transformers, stanza, and any remote models
        configuration = {
            "nlp_engine_name": "spacy",
            "models": [
                {
                    "lang_code": "en",
                    "model_name": "en_core_web_md"
                }
            ]
        }
        
        # Create NLP engine provider with local-only configuration
        provider = NlpEngineProvider(nlp_configuration=configuration)
        nlp_engine = provider.create_engine()
        
        # Create a custom recognizer for ORGANIZATION using spaCy ORG entities
        class OrganizationRecognizer(EntityRecognizer):
            """Custom recognizer for organizations using spaCy ORG entities"""
            def __init__(self):
                super().__init__(supported_entities=["ORGANIZATION"], supported_language="en")
            
            def load(self):
                pass
            
            def analyze(self, text, entities, nlp_artifacts):
                results = []
                try:
                    if nlp_artifacts and hasattr(nlp_artifacts, "doc") and nlp_artifacts.doc:
                        doc = nlp_artifacts.doc
                        for ent in doc.ents:
                            if ent.label_ == "ORG":
                                results.append(RecognizerResult(
                                    entity_type="ORGANIZATION",
                                    start=ent.start_char,
                                    end=ent.end_char,
                                    score=0.85
                                ))
                except Exception as e:
                    # Silently continue if doc access fails
                    pass
                return results
        
        # Create registry and add default recognizers + our custom one
        registry = RecognizerRegistry()
        registry.load_predefined_recognizers(nlp_engine=nlp_engine, languages=["en"])
        registry.add_recognizer(OrganizationRecognizer())
        
        # Create analyzer with custom registry
        analyzer = AnalyzerEngine(
            registry=registry,
            nlp_engine=nlp_engine,
            supported_languages=["en"]
        )
        
        # Analyze text for PII using local recognizers
        # Presidio's default recognizers are all local (pattern-based or spaCy-based)
        # Request all available entity types
        results = analyzer.analyze(
            text=text,
            language="en",
            entities=None  # None = detect all entity types
        )
        
        # Post-process: Add organizations directly from spaCy since Presidio doesn't detect them by default
        # This ensures we catch organizations that Presidio's SpacyRecognizer misses
        import spacy
        try:
            nlp = spacy.load("en_core_web_md")
            doc = nlp(text)
            
            # Add ORG entities from spaCy
            for ent in doc.ents:
                if ent.label_ == "ORG":
                    # Check if this entity is already detected (avoid duplicates)
                    already_detected = any(
                        r.start == ent.start_char and r.end == ent.end_char 
                        for r in results
                    )
                    if not already_detected:
                        results.append(RecognizerResult(
                            entity_type="ORGANIZATION",
                            start=ent.start_char,
                            end=ent.end_char,
                            score=0.85
                        ))
        except Exception:
            # If spaCy post-processing fails, continue with Presidio results only
            pass
        
        # Filter out irrelevant entity types and low confidence detections
        # These entity types are not relevant for English text privacy protection
        EXCLUDED_TYPES = {
            'IN_PAN',        # Indian PAN - causes false positives on English words
            'IN_AADHAAR',    # Indian Aadhaar
            'IN_VEHICLE_REGISTRATION',
            'SG_NRIC_FIN',   # Singapore IDs
            'AU_ABN',        # Australian Business Number
            'AU_ACN',        # Australian Company Number
            'AU_TFN',        # Australian Tax File Number
            'AU_MEDICARE',   # Australian Medicare
            'ES_NIF',        # Spanish IDs
            'IT_FISCAL_CODE',
            'IT_DRIVER_LICENSE',
            'IT_VAT_CODE',
            'IT_PASSPORT',
            'IT_IDENTITY_CARD',
        }
        
        # Minimum confidence threshold to reduce false positives
        MIN_CONFIDENCE = 0.5
        
        # Convert Presidio results to our format with filtering
        entities = []
        for result in results:
            # Skip excluded entity types
            if result.entity_type in EXCLUDED_TYPES:
                continue
            
            # Skip low confidence detections
            if result.score < MIN_CONFIDENCE:
                continue
            
            # Additional filtering for overly generic DATE_TIME detections
            detected_text = text[result.start:result.end].lower()
            if result.entity_type == 'DATE_TIME':
                # Filter out common false positives for dates
                if detected_text in ['daily', 'weekly', 'monthly', 'yearly', 'today', 'tomorrow', 
                                     'yesterday', 'now', 'decades', 'years', 'months', 'days',
                                     'morning', 'afternoon', 'evening', 'night', 'mornings',
                                     'saturday', 'sunday', 'monday', 'tuesday', 'wednesday', 
                                     'thursday', 'friday', 'next year', 'last year', 'this year']:
                    continue
            
            # Filter out NRP when it's just language names (Portuguese, Spanish, etc.)
            # Keep it when it's more sensitive (ethnicity, nationality in identifying context)
            if result.entity_type == 'NRP':
                # If it's a single word and looks like a language, skip it
                if ' ' not in detected_text and detected_text.lower() in [
                    'portuguese', 'spanish', 'french', 'german', 'italian', 
                    'chinese', 'japanese', 'korean', 'arabic', 'russian',
                    'english', 'mandarin', 'hindi', 'bengali'
                ]:
                    continue
            
            entities.append({
                "type": result.entity_type,
                "text": text[result.start:result.end],
                "start": result.start,
                "end": result.end,
                "confidence": result.score
            })
        
        return {"ok": True, "entities": entities, "error": None}
        
    except ImportError as e:
        return {
            "ok": False,
            "entities": [],
            "error": f"Presidio not installed or spaCy model missing: {str(e)}\nRun setup_ner.bat to install."
        }
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        return {
            "ok": False,
            "entities": [],
            "error": f"Error during PII detection: {str(e)}\n{error_details}"
        }


def main():
    """
    Read input from stdin (JSON), detect PII, write output to stdout (JSON)
    """
    try:
        # Read input
        input_data = sys.stdin.read()
        
        if not input_data.strip():
            print(json.dumps({
                "ok": False,
                "entities": [],
                "error": "No input provided"
            }))
            return
        
        request = json.loads(input_data)
        text = request.get("text", "")
        
        if not text:
            print(json.dumps({
                "ok": True,
                "entities": [],
                "error": None
            }))
            return
        
        # Detect PII
        result = detect_pii(text)
        
        # Write output
        print(json.dumps(result))
        
    except json.JSONDecodeError as e:
        print(json.dumps({
            "ok": False,
            "entities": [],
            "error": f"Invalid JSON input: {str(e)}"
        }))
    except Exception as e:
        print(json.dumps({
            "ok": False,
            "entities": [],
            "error": f"Unexpected error: {str(e)}"
        }))


if __name__ == "__main__":
    main()
