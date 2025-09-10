import os
import re
import pandas as pd
import spacy
import pdfplumber
from sqlalchemy.orm import Session
from models import ReceiptFile  # Your SQLAlchemy model
from spacy.cli import download

def load_spacy_model(model_name="en_core_web_sm"):
    try:
        return spacy.load(model_name)
    except OSError:
        print(f"Downloading spaCy model: {model_name}...")
        download(model_name)
        return spacy.load(model_name)

# Load spaCy model once
nlp = spacy.load("en_core_web_sm")

# ------------------ Custom Labels ------------------
CUSTOM_LABELS = [
    "RECEIPT_ID", "PURCHASED_AT", "MERCHANT_NAME", "TOTAL_AMOUNT",
    "TOTAL_EXPENDITURE", "FILE_PATH", "CARD_DETAILS", "PAYMENT_METHOD",
    "ADDRESS", "PURCHASE_QUANTITY", "TRANSACTION_ID", "ITEMS",
    "MERCHANT_EMAIL_ID", "MERCHANT_PHONE", "CUSTOMER_EMAIL", "CUSTOMER_PHONE",
    "CUSTOMER_ADDRESS", "BUSINESS_TYPE", "CREATED_AT", "UPDATED_AT",
]

# ------------------ Regex Patterns ------------------
PATTERNS = {
    "EMAIL": re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", re.I),
    "PHONE": re.compile(r"\b(?:\+91[- ]?)?[6-9]\d{9}\b", re.I),
    "AMOUNT": re.compile(r"(?:Rs\.?|INR|USD|\$|EUR|€|JPY|¥|GBP|£)\s?[\d,]+(?:\.\d{2})?", re.I),
    "CARD": re.compile(r"(?:\d{4}[- ]?){3,4}\d{4}", re.I),
    "TRANSACTION_ID": re.compile(r"(?:TXN|TRX|TRANS|ORDER|PAY)[-_]?\w+", re.I),
    "RECEIPT_ID": re.compile(r"(?:REC|RCPT|RCP|INVOICE|BILL)[-_]?\w+", re.I),
}

# ------------------ Business Categories ------------------
BUSINESS_CATEGORIES = {
    "retail": ["store", "mall", "retail", "shop", "purchase"],
    "travel": ["flight", "airline", "train", "bus ticket", "boarding"],
    "public_transport": ["metro", "bus", "ticket", "platform"],
    "taxi": ["uber", "ola", "ride", "taxi", "cab"],
    "restaurant": ["restaurant", "cafe", "hotel", "dine", "food", "menu", "bill"],
    "tourism": ["museum", "tourist", "entry fee", "monument", "park"],
}

# ------------------ Extraction Function ------------------
def extract_receipt_to_dataframe(db: Session, file_id: int, file_name: str):
    """
    Extracts receipt data given an ID and file_name.
    Returns a pandas DataFrame with one row for the receipt.
    """

    # Fetch file path from DB
    receipt = db.query(ReceiptFile).filter(
        (ReceiptFile.id == file_id) & (ReceiptFile.file_name.ilike(file_name))
    ).first()
    
    if not receipt:
        raise ValueError(f"No receipt found with ID {file_id} and file_name {file_name}")

    file_path = receipt.file_path

    # Extract text from PDF
    text = ""
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    
    text_lower = text.lower()  # For case-insensitive heuristics
    doc = nlp(text)

    # Initialize output
    data = {label: None for label in CUSTOM_LABELS}

    # --------- Regex Fields ---------
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

    amounts = PATTERNS["AMOUNT"].findall(text)
    if amounts:
        data["TOTAL_EXPENDITURE"] = ", ".join(amounts)
        try:
            data["TOTAL_AMOUNT"] = float(re.sub(r"[^\d.]", "", amounts[-1]))
        except (ValueError, TypeError):
            data["TOTAL_AMOUNT"] = 0.0

    # --------- spaCy Entities ---------
    for ent in doc.ents:
        label = ent.label_
        ent_text = ent.text
        if label == "ORG" and not data["MERCHANT_NAME"]:
            data["MERCHANT_NAME"] = ent_text
        elif label in ["DATE", "TIME"] and not data["PURCHASED_AT"]:
            data["PURCHASED_AT"] = ent_text
        elif label == "GPE" and not data["ADDRESS"]:
            data["ADDRESS"] = ent_text
        elif label == "PERSON" and not data["CUSTOMER_EMAIL"]:
            data["CUSTOMER_EMAIL"] = ent_text  # heuristic placeholder

    # --------- Payment Method ---------
    if re.search(r"(upi|gpay|phonepe|paytm)", text_lower):
        data["PAYMENT_METHOD"] = "UPI"
    elif re.search(r"(credit|debit|visa|mastercard)", text_lower):
        data["PAYMENT_METHOD"] = "CARD"
    elif re.search(r"(cash)", text_lower):
        data["PAYMENT_METHOD"] = "CASH"
    elif re.search(r"(netbanking|bank transfer)", text_lower):
        data["PAYMENT_METHOD"] = "NETBANKING"

    # --------- Purchase Quantity & Items ---------
    if "qty" in text_lower or "quantity" in text_lower:
        qty_matches = re.findall(r"(?:qty|quantity)[:\- ]?(\d+)", text_lower, re.I)
        if qty_matches:
            data["PURCHASE_QUANTITY"] = ", ".join(qty_matches)

    if "item" in text_lower or "product" in text_lower:
        items_section = re.findall(r"(?:item|product)[:\- ](.+)", text, re.I)
        if items_section:
            data["ITEMS"] = "; ".join(items_section[:5])

    # --------- Business Type ---------
    for category, keywords in BUSINESS_CATEGORIES.items():
        if any(kw in text_lower for kw in keywords):
            data["BUSINESS_TYPE"] = category
            break

    # File path metadata
    data["FILE_PATH"] = file_path

    # --------- Convert to DataFrame ---------
    df = pd.DataFrame([data])
    return df

# Example usage:
# df_receipt = extract_receipt_to_dataframe(db_session, file_id=3, file_name="receipt.pdf")
# print(df_receipt)
