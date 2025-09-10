from fastapi import FastAPI, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session
import shutil
import os
from fastapi.responses import JSONResponse
from database import Base, engine, SessionLocal
import models, crud, utils, schemas
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
import models, crud, schemas, utils
from database import get_db
from parser_logic import extract_custom_fields_by_id, CUSTOM_LABELS

from fastapi.responses import JSONResponse
import utils, crud, schemas, models

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
@app.post("/upload", response_model=schemas.ReceiptFileSchema)
def upload_file(file: UploadFile = File(...), db: Session = Depends(get_db)):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")
    
    file_path = os.path.join(UPLOAD_FOLDER, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return crud.create_receipt_file(db, file.filename, file_path)





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







@app.post("/process/{file_id}", response_model=schemas.ReceiptSchema)
def process_file(file_id: int, db: Session = Depends(get_db)):
    # Fetch file record
    receipt_file = db.query(models.ReceiptFile).filter(models.ReceiptFile.id == file_id).first()
    if not receipt_file or not receipt_file.is_valid:
        raise HTTPException(status_code=400, detail="File is invalid or not found")

    # Extract fields from PDF
    data = utils.extract_custom_fields_by_id(db, file_id)

    # Store into Receipt table
    receipt = crud.create_receipt(db, data)

    # Mark file as processed
    crud.mark_as_processed(db, receipt_file)

    return receipt









@app.get("/receipts", response_model=list[schemas.ReceiptSchema])
def list_receipts(db: Session = Depends(get_db)):
    return crud.get_receipts(db)

@app.get("/receipts/{receipt_id}", response_model=schemas.ReceiptSchema)
def get_receipt(receipt_id: int, db: Session = Depends(get_db)):
    receipt = crud.get_receipt_by_id(db, receipt_id)
    if not receipt:
        raise HTTPException(status_code=404, detail="Receipt not found")
    return receipt


