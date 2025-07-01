import re
import spacy
from typing import List, Dict, Optional

nlp = spacy.load("en_core_web_sm")

def extract_information(text: str, lines: List[str]) -> Dict[str, Optional[str]]:
    if not isinstance(text, str):
        raise ValueError("Expected text to be a string")
    if not isinstance(lines, list):
        raise ValueError("Expected lines to be a list of strings")

    return {
        "name": extract_name(lines),
        "email": extract_email(text),
        "phone": extract_phone(text)
    }

def extract_email(text: str) -> Optional[str]:
    if not isinstance(text, str):
        raise ValueError("Expected text to be a string")

    match = re.search(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", text)
    return match.group(0) if match else None

def extract_phone(text: str) -> Optional[str]:
    if not isinstance(text, str):
        raise ValueError("Expected text to be a string")

    patterns = [
        r'(\+?\d{1,3})?[\s.-]?\(?\d{3,4}\)?[\s.-]?\d{3,4}[\s.-]?\d{3,4}',
        r'\b\d{10}\b',
        r'\b\d{3}[-.]\d{3}[-.]\d{4}\b',
        r'\b\d{5}\s\d{5}\b'
    ]

    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            return match.group(0)
    return None

def extract_name(lines: List[str]) -> Optional[str]:
    """
    Improved name extraction:
    Accept 1–4 words, skip lines with email/phone/linkedin
    """
    if not isinstance(lines, list):
        raise ValueError("Expected lines to be a list of strings")

    for line in lines[:10]:
        line = line.strip()
        if line and not any(keyword in line.lower() for keyword in ['email', '@', 'phone', 'mobile', 'linkedin']):
            if 0 < len(line.split()) <= 4:
                if any(c.isalpha() for c in line):
                    return line

    doc = nlp(" ".join(lines[:50]))
    for ent in doc.ents:
        if ent.label_ == "PERSON":
            return ent.text

    return None
