# app/schemas/block.py
from pydantic import BaseModel
from typing import Optional
from enum import Enum

class BlockReasonEnum(str, Enum):
    inappropriate_content = "inappropriate_content"
    harassment = "harassment"
    fake_profile = "fake_profile"
    spam = "spam"
    other = "other"

class BlockCreate(BaseModel):
    blocker_id: str
    blocked_id: str
    reason: BlockReasonEnum
    details: Optional[str] = None

class BlockResponse(BaseModel):
    block_id: str
    blocker_id: str
    blocked_id: str
    reason: BlockReasonEnum
    details: Optional[str] = None
    timestamp: str

class ReportCreate(BaseModel):
    reporter_id: str
    reported_id: str
    reason: BlockReasonEnum
    details: Optional[str] = None

class ReportResponse(BaseModel):
    report_id: str
    reporter_id: str
    reported_id: str
    reason: BlockReasonEnum
    details: Optional[str] = None
    timestamp: str
    status: str = "pending"  # pending, reviewed, resolved
