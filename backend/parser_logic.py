import os
import re
import pandas as pd
import spacy
import pdfplumber
from sqlalchemy.orm import Session
from models import ReceiptFile  # Your SQLAlchemy model

# Load spaCy model once
nlp = spacy.load("en_core_web_sm")



# Custom Labels
CUSTOM_LABELS = [
    "RECEIPT_ID",
    "PURCHASED_AT",
    "MERCHANT_NAME",
    "TOTAL_AMOUNT",
    "TOTAL_EXPENDITURE",
    "FILE_PATH",
    "CARD_DETAILS",
    "PAYMENT_METHOD",
    "ADDRESS",
    "PURCHASE_QUANTITY",
    "TRANSACTION_ID",
    "ITEMS",
    "MERCHANT_EMAIL_ID",
    "MERCHANT_PHONE",
    "CUSTOMER_EMAIL",
    "CUSTOMER_PHONE",
    "CUSTOMER_ADDRESS",
    "BUSINESS_TYPE",
    "CREATED_AT",
    "UPDATED_AT",
]

# Regex patterns for structured fields
PATTERNS = {
    "EMAIL": re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"),
    "PHONE": re.compile(r"\b(?:\+91[- ]?)?[6-9]\d{9}\b"),
    "AMOUNT": re.compile(
        r"(?:Rs\.?|INR|USD|\$|EUR|€|JPY|¥|GBP|£)\s?[\d,]+(?:\.\d{2})?"
    ),
    "CARD": re.compile(r"(?:\d{4}[- ]?){3,4}\d{4}"),
    "TRANSACTION_ID": re.compile(r"(?:TXN|TRX|TRANS|ORDER|PAY)[-_]?\w+"),
    "RECEIPT_ID": re.compile(r"(?:REC|RCPT|RCP|INVOICE|BILL)[-_]?\w+"),
}

# Business type keywords
BUSINESS_CATEGORIES = {
    "retail": ["store", "mall", "retail", "shop", "purchase"],
    "travel": ["flight", "airline", "train", "bus ticket", "boarding"],
    "public_transport": ["metro", "bus", "ticket", "platform"],
    "taxi": ["uber", "ola", "ride", "taxi", "cab"],
    "restaurant": ["restaurant", "cafe", "hotel", "dine", "food", "menu", "bill"],
    "tourism": ["museum", "tourist", "entry fee", "monument", "park"],
}




def extract_custom_fields_by_id(db: Session, file_id: int):
    """
    Given a receipt_id:
      1. Fetch PDF file path from DB.
      2. Extract text using pdfplumber.
      3. Parse custom fields (regex + spaCy + heuristics).
      4. Return extracted dictionary.
    """

    # ---------- 1. Fetch PDF path ----------
    receipt = db.query(ReceiptFile).filter(ReceiptFile.id == file_id).first()
    if not receipt:
        raise ValueError(f"No receipt found with ID {file_id}")

    file_path = receipt.file_path

    # ---------- 2. Extract text ----------
    def extract_text_pdfplumber(pdf_path):
        text = ""
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        return text

    text = extract_text_pdfplumber(file_path)
    doc = nlp(text)

    # ---------- 3. Initialize data ----------
    data = {label: None for label in CUSTOM_LABELS}

    # ===== Regex-driven fields =====
    if match := PATTERNS["EMAIL"].search(text):
        data["MERCHANT_EMAIL_ID"] = match.group()
    if match := PATTERNS["PHONE"].search(text):
        data["MERCHANT_PHONE"] = match.group()
    if match := PATTERNS["CARD"].search(text):
        data["CARD_DETAILS"] = match.group()
    if match := PATTERNS["TRANSACTION_ID"].search(text):
        data["TRANSACTION_ID"] = match.group()
    if match := PATTERNS["RECEIPT_ID"].search(text):
        data["RECEIPT_ID"] = match.group()

    # Extract all amounts → last one is often TOTAL
    amounts = PATTERNS["AMOUNT"].findall(text)
    if amounts:
        data["TOTAL_EXPENDITURE"] = ", ".join(amounts)
        raw_total = amounts[-1]
        try:
            data["TOTAL_AMOUNT"] = float(raw_total)
        except (ValueError, TypeError):
            data["TOTAL_AMOUNT"] = 0.0

    # ===== spaCy-driven fields =====
    for ent in doc.ents:
        if ent.label_ == "ORG" and not data["MERCHANT_NAME"]:
            data["MERCHANT_NAME"] = ent.text
        elif ent.label_ in ["DATE", "TIME"] and not data["PURCHASED_AT"]:
            data["PURCHASED_AT"] = ent.text
        elif ent.label_ == "GPE" and not data["ADDRESS"]:
            data["ADDRESS"] = ent.text
        elif ent.label_ == "PERSON" and not data["CUSTOMER_EMAIL"]:
            data["CUSTOMER_EMAIL"] = ent.text  # heuristic placeholder

    # ===== Other heuristics =====
    # Payment method detection
    if re.search(r"(upi|gpay|phonepe|paytm)", text, re.I):
        data["PAYMENT_METHOD"] = "UPI"
    elif re.search(r"(credit|debit|visa|mastercard)", text, re.I):
        data["PAYMENT_METHOD"] = "CARD"
    elif re.search(r"(cash)", text, re.I):
        data["PAYMENT_METHOD"] = "CASH"
    elif re.search(r"(netbanking|bank transfer)", text, re.I):
        data["PAYMENT_METHOD"] = "NETBANKING"

    # Purchase quantities & items
    if "qty" in text.lower() or "quantity" in text.lower():
        qty_matches = re.findall(r"(?:qty|quantity)[:\- ]?(\d+)", text, re.I)
        if qty_matches:
            data["PURCHASE_QUANTITY"] = ", ".join(qty_matches)

    if "item" in text.lower() or "product" in text.lower():
        items_section = re.findall(r"(?:item|product)[:\- ](.+)", text, re.I)
        if items_section:
            data["ITEMS"] = "; ".join(items_section[:5])  # limit to first 5 items

    # Business type classification
    for category, keywords in BUSINESS_CATEGORIES.items():
        if any(kw in text.lower() for kw in keywords):
            data["BUSINESS_TYPE"] = category
            break

    # File path metadata
    data["FILE_PATH"] = file_path

    return data