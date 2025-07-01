import os
import textract
from PyPDF2 import PdfReader
from typing import Union

class UnsupportedFileFormat(Exception):
    pass

def extract_text(file_path: str) -> str:
    ext = os.path.splitext(file_path)[1].lower()
    print(f"Attempting to extract text from file: {file_path} with extension: {ext}")  # Debugging line
    
    try:
        if ext == '.pdf':
            return extract_text_from_pdf(file_path)
        elif ext in ('.docx', '.doc'):
            return textract.process(file_path).decode('utf-8')
        elif ext == '.txt':
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        else:
            raise UnsupportedFileFormat(f"Unsupported file format: {ext}")
    except Exception as e:
        print(f"Error occurred: {str(e)}")  # Debugging line
        raise IOError(f"Error extracting text from {file_path}: {str(e)}")


def extract_text_from_pdf(file_path: str) -> str:
    """
    Extracts text from PDF files using PyPDF2
    
    Args:
        file_path: Path to PDF file
        
    Returns:
        Extracted text as a string
    """
    text = ""
    with open(file_path, 'rb') as f:
        pdf = PdfReader(f)
        for page in pdf.pages:
            text += page.extract_text() or ""
    return text
