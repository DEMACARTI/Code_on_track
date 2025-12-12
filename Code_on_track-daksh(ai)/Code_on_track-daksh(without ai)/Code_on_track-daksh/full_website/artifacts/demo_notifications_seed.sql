-- ============================================================================
-- DEMO NOTIFICATIONS SEED SCRIPT
-- Purpose: Insert 6 realistic notifications into the database
-- Run: Execute via psql or database client
-- ============================================================================

-- Clear existing notifications (optional, comment out if not desired)
-- DELETE FROM notifications;

-- Insert demo notifications
INSERT INTO notifications (type, title, message, severity, read, dismissed, created_at, metadata)
VALUES 
-- 1. Near-expiry ERC (Critical)
(
    'warranty_expiring',
    'Critical: ERC Warranty Expiring',
    '15 Elastic Rail Clips in LOT-2024-089 expiring within 5 days. Immediate inspection recommended.',
    'danger',
    false,
    false,
    NOW() - INTERVAL '2 hours',
    '{"bucket": "critical", "total_items": 15, "by_lot": [{"lot_no": "LOT-2024-089", "count": 15, "components": "ERC"}], "days_remaining": 5}'::jsonb
),

-- 2. Near-expiry Rail Pad (Warning)
(
    'warranty_expiring',
    'Warning: Rail Pad Warranty Alert',
    '28 Rail Pads across 3 lots expiring in 12 days. Schedule preventive maintenance.',
    'warning',
    false,
    false,
    NOW() - INTERVAL '6 hours',
    '{"bucket": "warning", "total_items": 28, "by_lot": [{"lot_no": "LOT-2024-055", "count": 12}, {"lot_no": "LOT-2024-078", "count": 10}, {"lot_no": "LOT-2024-092", "count": 6}], "days_remaining": 12}'::jsonb
),

-- 3. High Anomaly Score Detection
(
    'anomaly_detected',
    'Anomaly: Unusual Failure Pattern',
    'LOT-2024-037 showing 2.3x higher failure rate than baseline. Vendor quality review recommended.',
    'danger',
    false,
    false,
    NOW() - INTERVAL '1 day',
    '{"lot_no": "LOT-2024-037", "component": "ERC", "anomaly_score": 0.89, "failure_rate": 0.12, "baseline_rate": 0.05}'::jsonb
),

-- 4. Failed Inspection Alert
(
    'inspection_failed',
    'Inspection Failed: Sleeper Cracks',
    'Visual inspection of LOT-2024-106 detected micro-cracks in 8 sleeper units. Replacement required.',
    'danger',
    false,
    false,
    NOW() - INTERVAL '3 hours',
    '{"lot_no": "LOT-2024-106", "component": "Sleeper", "defect_type": "micro_cracks", "affected_count": 8, "inspector": "Rail-Vision AI"}'::jsonb
),

-- 5. Vendor Reliability Alert
(
    'vendor_alert',
    'Vendor Quality Concern: Bharat Forge',
    'Vendor reliability score dropped to 72%. 3 lots with above-average failure rates in last 30 days.',
    'warning',
    false,
    false,
    NOW() - INTERVAL '12 hours',
    '{"vendor_id": 3, "vendor_name": "Bharat Forge", "reliability_score": 72, "affected_lots": ["LOT-2024-037", "LOT-2024-045", "LOT-2024-098"]}'::jsonb
),

-- 6. Replacement Overdue
(
    'replacement_overdue',
    'Overdue: Component Replacement Required',
    '42 components across 5 lots are past warranty and due for replacement. Action required.',
    'danger',
    true,
    false,
    NOW() - INTERVAL '2 days',
    '{"bucket": "expired", "total_items": 42, "by_lot": [{"lot_no": "LOT-2023-156", "count": 18}, {"lot_no": "LOT-2023-189", "count": 12}, {"lot_no": "LOT-2024-012", "count": 8}, {"lot_no": "LOT-2024-023", "count": 4}]}'::jsonb
);

-- Verify insertion
SELECT id, type, title, severity, read, created_at 
FROM notifications 
ORDER BY created_at DESC;
