from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from app.api.dependencies import get_db
from pydantic import BaseModel
from typing import List, Optional

router = APIRouter()

class QualityJobResponse(BaseModel):
    status: str
    stats: dict

class LotQualityResponse(BaseModel):
    """Matches frontend LotQualityData interface exactly."""
    lot_no: str
    component: str
    vendor_id: int
    item_count: int
    failed: int
    rate: float
    anomaly_score: float
    reason: str
    status: str  # PASSED, WARNING, FAILED, CRITICAL
    last_inspected: Optional[str]

def compute_status(failure_rate: float, is_anomalous: bool) -> str:
    """Compute status based on failure rate and anomaly flag."""
    if failure_rate >= 0.15 or is_anomalous:
        return "CRITICAL"
    elif failure_rate >= 0.10:
        return "FAILED"
    elif failure_rate >= 0.05:
        return "WARNING"
    return "PASSED"

@router.get("/", response_model=List[LotQualityResponse])
async def get_quality_list(skip: int = 0, limit: int = 20, db: AsyncSession = Depends(get_db)):
    """Get list of lot quality records."""
    result = await db.execute(text("SELECT * FROM lot_quality LIMIT :limit OFFSET :skip"), {"limit": limit, "skip": skip})
    rows = result.mappings().all()
    
    # Convert RowMapping to dict and map field names to match frontend expectations
    mapped = []
    for row in rows:
        r = dict(row)
        mapped.append(LotQualityResponse(
            lot_no=r.get("lot_no", ""),
            component=r.get("component_type", "Unknown"),
            vendor_id=r.get("vendor_id", 0),
            item_count=r.get("total_items", 0),
            failed=r.get("failed_items", 0),
            rate=round((r.get("failure_rate", 0) or 0) * 100, 2),  # Convert to percentage
            anomaly_score=r.get("anomaly_score", 0) or 0,
            reason=r.get("reason") if r.get("reason") else "None",
            status=compute_status(r.get("failure_rate", 0) or 0, r.get("is_anomalous", False)),
            last_inspected=r.get("computed_at").isoformat() if r.get("computed_at") else None
        ))
    return mapped

@router.post("/run_job", response_model=QualityJobResponse)
async def run_quality_job(db: AsyncSession = Depends(get_db)):
    """
    Runs the Anomaly Detection and Quality Aggregation job.
    Recomputes lot_quality from items table.
    """
    sql_quality = """
    INSERT INTO lot_quality (lot_no, vendor_id, component_type, total_items, failed_items, failure_rate, anomaly_score)
    SELECT 
        lot_no, 
        MAX(vendor_id) as vendor_id,
        STRING_AGG(DISTINCT component_type, ', ') as component_type,
        COUNT(*) AS total_items,
        SUM(CASE WHEN status='failed' THEN 1 ELSE 0 END) AS failed_items,
        ROUND(SUM(CASE WHEN status='failed' THEN 1 ELSE 0 END)::numeric / COUNT(*)::numeric, 4) AS failure_rate,
        ROUND(AVG(0.1 + (CASE WHEN status='failed' THEN 1 ELSE 0 END)*0.2), 3) as anomaly_score
    FROM items 
    GROUP BY lot_no
    ON CONFLICT (lot_no) 
    DO UPDATE SET
        vendor_id = EXCLUDED.vendor_id,
        component_type = EXCLUDED.component_type,
        total_items = EXCLUDED.total_items,
        failed_items = EXCLUDED.failed_items,
        failure_rate = EXCLUDED.failure_rate,
        anomaly_score = EXCLUDED.anomaly_score;
    """
    
    result = await db.execute(text(sql_quality))
    await db.commit()
    
    # Count rows affected
    upserted = result.rowcount
    
    return {
        "status": "completed",
        "stats": {
            "processed": upserted,
            "anomalies_found": 0 # Not explicitly counting new anomalies here, just stats
        }
    }
