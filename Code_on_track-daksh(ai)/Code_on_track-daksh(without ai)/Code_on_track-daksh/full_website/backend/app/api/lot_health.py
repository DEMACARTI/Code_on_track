from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from app.api.dependencies import get_db
from pydantic import BaseModel
import asyncio

router = APIRouter()

class HealthJobResponse(BaseModel):
    status: str
    stats: dict

@router.get("/", response_model=list)
async def get_health_list(
    skip: int = 0, 
    limit: int = 20, 
    risk_level: str = None, 
    db: AsyncSession = Depends(get_db)
):
    """
    Get list of lot health records.
    Joins with vendors to ensure we have vendor names if needed, 
    but primarily relies on lot_health table being populated correctly.
    """
    query = "SELECT * FROM lot_health"
    params = {"limit": limit, "skip": skip}
    
    if risk_level:
        query += " WHERE risk_level = :risk_level"
        params["risk_level"] = risk_level
    
    query += " ORDER BY health_score DESC LIMIT :limit OFFSET :skip"
    
    try:
        result = await db.execute(text(query), params)
        rows = result.mappings().all()
        # Explicitly convert to dict to ensure serialization works
        return [dict(row) for row in rows]
    except Exception as e:
        print(f"Error fetching lot_health: {e}")
        # Log to file to be sure we see it
        with open("api_error.log", "w") as f:
            f.write(str(e))
        return []

@router.post("/run_job", response_model=HealthJobResponse)
async def run_health_job(db: AsyncSession = Depends(get_db)):
    """
    Runs the comprehensive Health Score analysis.
    Corrects formula and populates missing fields.
    """
    try:
        # We use ON CONFLICT to upsert. 
        # First, ensure we have the latest quality data mapped.
        
        sql_health = """
        INSERT INTO lot_health (
            lot_no, component_type, vendor_id, 
            total_items, failed_items, failure_rate, 
            anomaly_score, health_score, risk_level, 
            recommended_action, next_suggested_inspection_date,
            computed_at
        )
        SELECT 
            lq.lot_no, 
            lq.component_type, 
            lq.vendor_id, 
            lq.total_items, 
            lq.failed_items, 
            lq.failure_rate, 
            lq.anomaly_score,
            -- Correct Formula: 100 - (FR*400) - (AS*40) + random_noise
            ROUND(GREATEST(0, LEAST(100, 
                100 - (COALESCE(lq.failure_rate, 0) * 400.0) - (COALESCE(lq.anomaly_score, 0) * 40.0) + (random() * 3)
            ))::numeric, 2) AS health_score,
            -- Risk Level Logic
            CASE 
                WHEN (100 - (COALESCE(lq.failure_rate, 0) * 400.0) - (COALESCE(lq.anomaly_score, 0) * 40.0)) <= 40 THEN 'CRITICAL' 
                WHEN (100 - (COALESCE(lq.failure_rate, 0) * 400.0) - (COALESCE(lq.anomaly_score, 0) * 40.0)) <= 70 THEN 'HIGH'
                WHEN (100 - (COALESCE(lq.failure_rate, 0) * 400.0) - (COALESCE(lq.anomaly_score, 0) * 40.0)) <= 85 THEN 'MEDIUM'
                ELSE 'LOW' 
            END AS risk_level,
            -- Recommended Action
            CASE
                WHEN (100 - (COALESCE(lq.failure_rate, 0) * 400.0) - (COALESCE(lq.anomaly_score, 0) * 40.0)) <= 40 THEN 'Inspect immediately'
                WHEN (100 - (COALESCE(lq.failure_rate, 0) * 400.0) - (COALESCE(lq.anomaly_score, 0) * 40.0)) <= 70 THEN 'Schedule maintenance'
                ELSE 'Routine check'
            END AS recommended_action,
             -- Next Inspection (Mocking +7 days for now)
            (NOW() + INTERVAL '7 days') as next_suggested_inspection_date,
            NOW() as computed_at
        FROM lot_quality lq
        ON CONFLICT (lot_no) 
        DO UPDATE SET
            component_type = EXCLUDED.component_type,
            vendor_id = EXCLUDED.vendor_id,
            total_items = EXCLUDED.total_items,
            failed_items = EXCLUDED.failed_items,
            failure_rate = EXCLUDED.failure_rate,
            anomaly_score = EXCLUDED.anomaly_score,
            health_score = EXCLUDED.health_score,
            risk_level = EXCLUDED.risk_level,
            recommended_action = EXCLUDED.recommended_action,
            next_suggested_inspection_date = EXCLUDED.next_suggested_inspection_date,
            computed_at = EXCLUDED.computed_at;
        """
        
        result = await db.execute(text(sql_health))
        await db.commit()
    except Exception as e:
        await db.rollback()
        print(f"HEALTH JOB ERROR: {e}")
        raise e
    
    processed = result.rowcount
    
    return {
        "status": "completed",
        "stats": {
            "processed": processed,
            "upserted": processed
        }
    }
