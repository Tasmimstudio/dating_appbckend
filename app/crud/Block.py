# app/crud/block.py
from app.config import get_db
from app.models.Block import Block, Report
import uuid
from datetime import datetime

def create_block(blocker_id: str, blocked_id: str, reason: str, details: str = None):
    session = get_db()
    block_id = str(uuid.uuid4())

    query = """
    MATCH (blocker:User {user_id: $blocker_id}), (blocked:User {user_id: $blocked_id})
    CREATE (blocker)-[b:BLOCKS {
        block_id: $block_id,
        reason: $reason,
        details: $details,
        timestamp: $timestamp
    }]->(blocked)
    RETURN b
    """

    result = session.run(query, {
        "blocker_id": blocker_id,
        "blocked_id": blocked_id,
        "block_id": block_id,
        "reason": reason,
        "details": details,
        "timestamp": datetime.utcnow().isoformat()
    })

    record = result.single()
    rel = record["b"]

    return Block(
        block_id=rel["block_id"],
        blocker_id=blocker_id,
        blocked_id=blocked_id,
        reason=rel["reason"],
        details=rel.get("details"),
        timestamp=rel["timestamp"]
    )

def get_block_by_id(block_id: str):
    session = get_db()
    query = """
    MATCH (blocker:User)-[b:BLOCKS {block_id: $block_id}]->(blocked:User)
    RETURN b, blocker.user_id as blocker_id, blocked.user_id as blocked_id
    """
    result = session.run(query, {"block_id": block_id}).single()

    if not result:
        return None

    rel = result["b"]
    return Block(
        block_id=rel["block_id"],
        blocker_id=result["blocker_id"],
        blocked_id=result["blocked_id"],
        reason=rel["reason"],
        details=rel.get("details"),
        timestamp=rel["timestamp"]
    )

def get_user_blocks(user_id: str):
    """Get all users blocked by this user"""
    session = get_db()
    query = """
    MATCH (u:User {user_id: $user_id})-[b:BLOCKS]->(blocked:User)
    RETURN b, blocked.user_id as blocked_id
    ORDER BY b.timestamp DESC
    """
    results = session.run(query, {"user_id": user_id})

    blocks = []
    for record in results:
        rel = record["b"]
        blocks.append({
            "block_id": rel["block_id"],
            "blocker_id": user_id,
            "blocked_id": record["blocked_id"],
            "reason": rel["reason"],
            "details": rel.get("details"),
            "timestamp": rel["timestamp"]
        })

    return blocks

def unblock_user(blocker_id: str, blocked_id: str):
    session = get_db()
    query = """
    MATCH (blocker:User {user_id: $blocker_id})-[b:BLOCKS]->(blocked:User {user_id: $blocked_id})
    DELETE b
    """
    session.run(query, {"blocker_id": blocker_id, "blocked_id": blocked_id})
    return True

def is_user_blocked(blocker_id: str, blocked_id: str):
    """Check if blocker has blocked the blocked user"""
    session = get_db()
    query = """
    MATCH (blocker:User {user_id: $blocker_id})-[b:BLOCKS]->(blocked:User {user_id: $blocked_id})
    RETURN count(b) as block_count
    """
    result = session.run(query, {"blocker_id": blocker_id, "blocked_id": blocked_id}).single()

    return result["block_count"] > 0

# Report functions
def create_report(reporter_id: str, reported_id: str, reason: str, details: str = None):
    session = get_db()
    report_id = str(uuid.uuid4())

    query = """
    CREATE (r:Report {
        report_id: $report_id,
        reporter_id: $reporter_id,
        reported_id: $reported_id,
        reason: $reason,
        details: $details,
        timestamp: $timestamp,
        status: 'pending'
    })
    RETURN r
    """

    result = session.run(query, {
        "report_id": report_id,
        "reporter_id": reporter_id,
        "reported_id": reported_id,
        "reason": reason,
        "details": details,
        "timestamp": datetime.utcnow().isoformat()
    })

    record = result.single()
    node = record["r"]

    return Report(
        report_id=node["report_id"],
        reporter_id=node["reporter_id"],
        reported_id=node["reported_id"],
        reason=node["reason"],
        details=node.get("details"),
        timestamp=node["timestamp"],
        status=node["status"]
    )

def get_report_by_id(report_id: str):
    session = get_db()
    query = "MATCH (r:Report {report_id: $report_id}) RETURN r"
    result = session.run(query, {"report_id": report_id}).single()

    if not result:
        return None

    node = result["r"]
    return Report(
        report_id=node["report_id"],
        reporter_id=node["reporter_id"],
        reported_id=node["reported_id"],
        reason=node["reason"],
        details=node.get("details"),
        timestamp=node["timestamp"],
        status=node["status"]
    )

def get_all_reports(status: str = None):
    """Get all reports, optionally filtered by status"""
    session = get_db()

    if status:
        query = "MATCH (r:Report {status: $status}) RETURN r ORDER BY r.timestamp DESC"
        results = session.run(query, {"status": status})
    else:
        query = "MATCH (r:Report) RETURN r ORDER BY r.timestamp DESC"
        results = session.run(query)

    reports = []
    for record in results:
        node = record["r"]
        reports.append(Report(
            report_id=node["report_id"],
            reporter_id=node["reporter_id"],
            reported_id=node["reported_id"],
            reason=node["reason"],
            details=node.get("details"),
            timestamp=node["timestamp"],
            status=node["status"]
        ))

    return reports

def update_report_status(report_id: str, status: str):
    session = get_db()
    query = """
    MATCH (r:Report {report_id: $report_id})
    SET r.status = $status
    RETURN r
    """
    result = session.run(query, {"report_id": report_id, "status": status}).single()

    if not result:
        return None

    node = result["r"]
    return Report(
        report_id=node["report_id"],
        reporter_id=node["reporter_id"],
        reported_id=node["reported_id"],
        reason=node["reason"],
        details=node.get("details"),
        timestamp=node["timestamp"],
        status=node["status"]
    )
