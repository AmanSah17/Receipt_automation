import pdfplumber
import pandas as pd
from parser_logic import extract_custom_fields, CUSTOM_LABELS


def extract_text_pdfplumber(pdf_path: str) -> str:
    text = ""
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
    except Exception as e:
        raise ValueError(f"Error extracting text from PDF: {str(e)}")

    return text


def extract_receipt_data(pdf_path: str) -> pd.DataFrame:
    """
    Pipeline:
    1. Extract text
    2. Parse with custom logic
    3. Return DataFrame (first 20 columns)
    """
    text = extract_text_pdfplumber(pdf_path)
    parsed_data = extract_custom_fields(text, file_path=pdf_path)

    # enforce DataFrame return type
    df = pd.DataFrame([parsed_data], columns=CUSTOM_LABELS[:20])
    return df
