CREATE TABLE IF NOT EXISTS lot_health (
    id SERIAL PRIMARY KEY,
    lot_no TEXT UNIQUE NOT NULL,
    component_type TEXT,
    vendor_id INTEGER,
    total_items INTEGER DEFAULT 0,
    failed_items INTEGER DEFAULT 0,
    failure_rate DOUBLE PRECISION DEFAULT 0.0,
    health_score DOUBLE PRECISION DEFAULT 100.0,
    risk_level TEXT,
    recommended_action TEXT,
    next_suggested_inspection_date DATE,
    computed_at TIMESTAMP DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_lot_health_lot_no ON lot_health(lot_no);
