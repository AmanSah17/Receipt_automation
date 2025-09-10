from sqlalchemy.orm import Session
from models import ReceiptFile, Receipt

from sqlalchemy.orm import Session
import models






def create_receipt_file(db: Session, file_name: str, file_path: str):
    receipt_file = ReceiptFile(file_name=file_name, file_path=file_path)
    db.add(receipt_file)
    db.commit()
    db.refresh(receipt_file)
    return receipt_file

def update_receipt_file_validation(db: Session, receipt_file: ReceiptFile, is_valid: bool, invalid_reason: str = None):
    receipt_file.is_valid = is_valid
    receipt_file.invalid_reason = invalid_reason
    db.commit()
    db.refresh(receipt_file)
    return receipt_file

def mark_as_processed(db: Session, receipt_file: ReceiptFile):
    receipt_file.is_processed = True
    db.commit()
    db.refresh(receipt_file)

def create_receipt(db: Session, data: dict):
    # split primary and extra fields
    main_fields = {k: data[k] for k in ["purchased_at", "merchant_name", "total_amount", "file_path"] if k in data}
    extra_fields = {k: v for k, v in data.items() if k not in main_fields and k != "id"}

    receipt = models.Receipt(**main_fields, extra_metadata=extra_fields)
    db.add(receipt)
    db.commit()
    db.refresh(receipt)
    return receipt


def get_receipts(db: Session):
    return db.query(Receipt).all()

def get_receipt_by_id(db: Session, receipt_id: int):
    return db.query(Receipt).filter(Receipt.id == receipt_id).first()




def create_receipt(db: Session, data: dict):
    receipt = models.Receipt(**data)
    db.add(receipt)
    db.commit()
    db.refresh(receipt)
    return receipt


def mark_as_processed(db: Session, receipt_file: models.ReceiptFile):
    """
    Marks uploaded file as processed.
    """
    receipt_file.is_processed = True
    db.commit()
    db.refresh(receipt_file)
    return receipt_file


def update_receipt_file_validation(db: Session, receipt_file, is_valid: bool, reason: str = None):
    receipt_file.is_valid = is_valid
    receipt_file.invalid_reason = reason
    db.add(receipt_file)
    db.commit()
    db.refresh(receipt_file)
    return receipt_file
