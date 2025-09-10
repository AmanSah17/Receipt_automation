from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float
from datetime import datetime
from database import Base

from sqlalchemy.dialects.sqlite import JSON  

class ReceiptFile(Base):
    __tablename__ = "receipt_file"
    id = Column(Integer, primary_key=True, index=True)
    file_name = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    is_valid = Column(Boolean, default=False)
    invalid_reason = Column(String, nullable=True)
    is_processed = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
# or PostgreSQL JSONB if using Postgres




class Receipt(Base):
    __tablename__ = "receipts"

    id = Column(Integer, primary_key=True, index=True)

    RECEIPT_ID = Column(String, nullable=True)
    PURCHASED_AT = Column(String, nullable=True)  # Can store datetime as string or use DateTime
    MERCHANT_NAME = Column(String, nullable=True)
    TOTAL_AMOUNT = Column(Float, default=0.0)
    TOTAL_EXPENDITURE = Column(String, nullable=True)
    FILE_PATH = Column(String, nullable=True)
    CARD_DETAILS = Column(String, nullable=True)
    PAYMENT_METHOD = Column(String, nullable=True)
    ADDRESS = Column(String, nullable=True)
    PURCHASE_QUANTITY = Column(String, nullable=True)
    TRANSACTION_ID = Column(String, nullable=True)
    ITEMS = Column(String, nullable=True)
    MERCHANT_EMAIL_ID = Column(String, nullable=True)
    MERCHANT_PHONE = Column(String, nullable=True)
    CUSTOMER_EMAIL = Column(String, nullable=True)
    CUSTOMER_PHONE = Column(String, nullable=True)
    CUSTOMER_ADDRESS = Column(String, nullable=True)
    BUSINESS_TYPE = Column(String, nullable=True)

    CREATED_AT = Column(DateTime, default=datetime.utcnow)
    UPDATED_AT = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)









