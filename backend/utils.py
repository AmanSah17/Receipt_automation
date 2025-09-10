import pdfplumber
import pandas as pd
from parser_logic import extract_receipt_to_dataframe, CUSTOM_LABELS

import os
import pdfplumber


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


def extract_receipt_data(file_path: str) -> pd.DataFrame:
    raw_dict = extract_receipt_to_dataframe(file_path)

    raw_total = raw_dict.get("TOTAL_AMOUNT")
    try:
        total_amount = float(raw_total) if raw_total not in (None, "", "NA") else 0.0
    except (ValueError, TypeError):
        total_amount = 0.0

    parsed = {
        "purchased_at": raw_dict.get("PURCHASE_DATE"),
        "merchant_name": raw_dict.get("MERCHANT_NAME"),
        "total_amount": total_amount,
        "file_path": file_path,
        "extra_metadata": {
            k: v for k, v in raw_dict.items()
            if k not in ["PURCHASE_DATE", "MERCHANT_NAME", "TOTAL_AMOUNT"]
        }
    }

    # ✅ Return DataFrame
    return pd.DataFrame([parsed])






def validate_and_extract_pdf(file_path: str):
    """
    Validate a PDF file:
    1. Check file extension is .pdf
    2. Try to open with pdfplumber
    3. If valid, extract text
    Returns: (is_valid: bool, reason: str | None, extracted_text: str | None)
    """
    # 1. Check extension
    if not file_path.lower().endswith(".pdf"):
        return False, "Invalid file extension (not .pdf)", None

    # 2. Try opening with pdfplumber
    try:
        text = ""
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"

        if not text.strip():
            return False, "PDF is empty or unreadable", None

        # Valid PDF
        return True, None, text

    except Exception as e:
        return False, f"Error opening PDF: {str(e)}", None
