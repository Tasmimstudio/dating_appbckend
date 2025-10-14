# app/routes/block.py
from fastapi import APIRouter, HTTPException
from app import crud
from app.schemas.Block import BlockCreate, BlockResponse, ReportCreate, ReportResponse
from typing import List

router = APIRouter(prefix="/blocks", tags=["Blocks & Reports"])

# Block endpoints
@router.post("/", response_model=BlockResponse)
def block_user(block: BlockCreate):
    """Block a user"""
    # Verify both users exist
    blocker = crud.user.get_user_by_id(block.blocker_id)
    blocked = crud.user.get_user_by_id(block.blocked_id)

    if not blocker or not blocked:
        raise HTTPException(status_code=404, detail="User not found")

    # Check if already blocked
    already_blocked = crud.block.is_user_blocked(block.blocker_id, block.blocked_id)
    if already_blocked:
        raise HTTPException(status_code=400, detail="User is already blocked")

    new_block = crud.block.create_block(
        block.blocker_id,
        block.blocked_id,
        block.reason,
        block.details
    )

    return new_block.__dict__

@router.get("/{block_id}", response_model=BlockResponse)
def get_block(block_id: str):
    block = crud.block.get_block_by_id(block_id)
    if not block:
        raise HTTPException(status_code=404, detail="Block not found")
    return block.__dict__

@router.get("/user/{user_id}")
def get_user_blocks(user_id: str):
    """Get all users blocked by this user"""
    blocks = crud.block.get_user_blocks(user_id)
    return blocks

@router.delete("/{blocker_id}/{blocked_id}")
def unblock_user(blocker_id: str, blocked_id: str):
    """Unblock a user"""
    crud.block.unblock_user(blocker_id, blocked_id)
    return {"message": "User unblocked successfully"}

# Report endpoints
@router.post("/reports", response_model=ReportResponse)
def report_user(report: ReportCreate):
    """Report a user"""
    # Verify both users exist
    reporter = crud.user.get_user_by_id(report.reporter_id)
    reported = crud.user.get_user_by_id(report.reported_id)

    if not reporter or not reported:
        raise HTTPException(status_code=404, detail="User not found")

    new_report = crud.block.create_report(
        report.reporter_id,
        report.reported_id,
        report.reason,
        report.details
    )

    return new_report.__dict__

@router.get("/reports/{report_id}", response_model=ReportResponse)
def get_report(report_id: str):
    report = crud.block.get_report_by_id(report_id)
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    return report.__dict__

@router.get("/reports", response_model=List[ReportResponse])
def get_all_reports(status: str = None):
    """Get all reports, optionally filtered by status (pending, reviewed, resolved)"""
    reports = crud.block.get_all_reports(status)
    return [r.__dict__ for r in reports]

@router.patch("/reports/{report_id}/status", response_model=ReportResponse)
def update_report_status(report_id: str, status: str):
    """Update report status (pending, reviewed, resolved)"""
    if status not in ["pending", "reviewed", "resolved"]:
        raise HTTPException(status_code=400, detail="Invalid status. Must be: pending, reviewed, or resolved")

    updated_report = crud.block.update_report_status(report_id, status)
    if not updated_report:
        raise HTTPException(status_code=404, detail="Report not found")

    return updated_report.__dict__
