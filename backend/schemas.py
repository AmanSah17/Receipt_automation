from pydantic import BaseModel
from typing import Optional,Dict,SupportsFloat



class ReceiptFileSchema(BaseModel):
    id: int
    file_name: str
    file_path: str
    is_valid: bool
    invalid_reason: Optional[str]
    is_processed: bool

    class Config:
        orm_mode = True



class ReceiptSchema(BaseModel):
    id: int
    purchased_at: Optional[str]
    merchant_name: Optional[str]
    total_amount: Optional[float]
    file_path: str
    extra_metadata: Optional[Dict[str, str]]  # flexible for key-value pairs

    class Config:
        orm_mode = True
