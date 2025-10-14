# app/models/block.py
from typing import Optional
from datetime import datetime

class Block:
    def __init__(
        self,
        block_id: str,
        blocker_id: str,
        blocked_id: str,
        reason: str,
        details: Optional[str] = None,
        timestamp: Optional[str] = None
    ):
        self.block_id = block_id
        self.blocker_id = blocker_id
        self.blocked_id = blocked_id
        self.reason = reason
        self.details = details
        self.timestamp = timestamp or datetime.utcnow().isoformat()


class Report:
    def __init__(
        self,
        report_id: str,
        reporter_id: str,
        reported_id: str,
        reason: str,
        details: Optional[str] = None,
        timestamp: Optional[str] = None,
        status: str = "pending"
    ):
        self.report_id = report_id
        self.reporter_id = reporter_id
        self.reported_id = reported_id
        self.reason = reason
        self.details = details
        self.timestamp = timestamp or datetime.utcnow().isoformat()
        self.status = status
