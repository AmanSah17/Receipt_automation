from fastapi import FastAPI, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session
import shutil
import os
import traceback
from typing import List
from fastapi.responses import JSONResponse
from database import Base, engine, SessionLocal
import models, crud, utils, schemas
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
import models, crud, schemas, utils
from database import get_db
from parser_logic import  CUSTOM_LABELS , extract_receipt_to_dataframe
from datetime import datetime
from fastapi.responses import JSONResponse
import utils, crud, schemas, models
from database import get_db  # your DB session generator
from parser_logic import extract_receipt_to_dataframe 
from pydantic import BaseModel

import pandas as pd
from models import ReceiptFile

class ReceiptRequest(BaseModel):
    file_id: int
    file_name: str

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

UPLOAD_FOLDER = "./uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# --- Routes ---


@app.get("/list_receipts/")
def list_receipts(db: Session = Depends(get_db)):
    """Return all receipt_file entries as JSON (DataFrame compatible)"""
    receipts = db.query(ReceiptFile).all()
    data = []
    for r in receipts:
        data.append({
            "id": r.id,
            "file_name": r.file_name,
            "is_valid": r.is_valid,
            "invalid_reason": r.invalid_reason,
            "is_processed": r.is_processed,
            "created_at": r.created_at,
            "updated_at": r.updated_at
        })
    return {"data": data}



@app.post("/upload", response_model=schemas.ReceiptFileSchema)
def upload_file(file: UploadFile = File(...), db: Session = Depends(get_db)):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")
    
    # Generate a unique filename using current datetime
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S%f")
    unique_filename = f"{timestamp}.pdf"
    file_path = os.path.join(UPLOAD_FOLDER, unique_filename)
    
    # Save the file
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Save to DB
    return crud.create_receipt_file(db, unique_filename, file_path)





@app.post("/validate/{file_id}", response_model=schemas.ReceiptFileSchema)
def validate_file(file_id: int, db: Session = Depends(get_db)):
    receipt_file = db.query(models.ReceiptFile).filter(models.ReceiptFile.id == file_id).first()
    if not receipt_file:
        raise HTTPException(status_code=404, detail="File not found")

    is_valid, reason, extracted_text = utils.validate_and_extract_pdf(receipt_file.file_path)

    # Update DB with validation result
    updated_file = crud.update_receipt_file_validation(db, receipt_file, is_valid, reason)

    # Return response with extracted text if valid
    return {
        "id": updated_file.id,
        "file_name": updated_file.file_name,
        "file_path": updated_file.file_path,
        "is_valid": updated_file.is_valid,
        "invalid_reason": updated_file.invalid_reason,
        "is_processed": updated_file.is_processed,
        "extracted_text": extracted_text if is_valid else None
    }


class ReceiptRequest(BaseModel):
    file_id: int
    file_name: str


@app.post("/process_receipt/{receipt_id}")
def process_receipt(receipt_id: int, db: Session = Depends(get_db)):
    """
    Given a receipt_id:
    1. Fetch the PDF path from DB.
    2. Extract text and parse all CUSTOM_LABELS.
    3. Return as DataFrame (JSON-compatible).
    """
    receipt = db.query(ReceiptFile).filter(ReceiptFile.id == receipt_id).first()
    if not receipt:
        raise HTTPException(status_code=404, detail=f"No receipt found with ID {receipt_id}")

    # Call the extraction function
    df = extract_receipt_to_dataframe(db, receipt.id, receipt.file_name)

    # Add timestamps
    df["CREATED_AT"] = receipt.created_at
    df["UPDATED_AT"] = receipt.updated_at

    # Mark as processed
    receipt.is_processed = True
    db.commit()

    return {"data": df.to_dict(orient="records")}


@app.get("/list_receipts/")
def list_receipts(db: Session = Depends(get_db)):
    """Return all receipt_file entries as JSON (DataFrame compatible)"""
    receipts = db.query(ReceiptFile).all()
    data = []
    for r in receipts:
        data.append({
            "id": r.id,
            "file_name": r.file_name,
            "is_valid": r.is_valid,
            "invalid_reason": r.invalid_reason,
            "is_processed": r.is_processed,
            "created_at": r.created_at,
            "updated_at": r.updated_at
        })
    return {"data": data}

@app.get("/receipts/{receipt_id}", response_model=schemas.ReceiptSchema)
def get_receipt(receipt_id: int, db: Session = Depends(get_db)):
    receipt = crud.get_receipt_by_id(db, receipt_id)
    if not receipt:
        raise HTTPException(status_code=404, detail="Receipt not found")
    return receipt


