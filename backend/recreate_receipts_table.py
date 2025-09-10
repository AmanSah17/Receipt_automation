# recreate_receipts_table.py

from sqlalchemy import create_engine, Column, String, Float, DateTime, Integer, Text
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

# ====== Update this to your DB path ======
DATABASE_URL = "sqlite:///./receipts.db"


Base = declarative_base()
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

# ====== Your CUSTOM_LABELS ======
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

# ====== Define the Receipt table dynamically ======
class Receipt(Base):
    __tablename__ = "receipts"
    
    id = Column(Integer, primary_key=True, index=True)  # DB primary key

    # Dynamically create columns for all CUSTOM_LABELS
    for label in CUSTOM_LABELS:
        if label in ["TOTAL_AMOUNT"]:
            vars()[label.lower()] = Column(Float, default=0.0)
        elif label in ["CREATED_AT", "UPDATED_AT", "PURCHASED_AT"]:
            vars()[label.lower()] = Column(DateTime, default=datetime.utcnow)
        else:
            vars()[label.lower()] = Column(Text, nullable=True)


# ====== Drop old table and recreate ======
def recreate_table():
    print("Dropping old receipts table (if exists)...")
    Receipt.__table__.drop(bind=engine, checkfirst=True)
    print("Creating receipts table with all CUSTOM_LABELS...")
    Base.metadata.create_all(bind=engine)
    print("Done! Table is ready.")


if __name__ == "__main__":
    recreate_table()
