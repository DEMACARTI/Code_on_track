import random
from datetime import datetime, timedelta
from app import create_app
from services.db import db
from sqlalchemy import text

def setup_vendor_reliability():
    app = create_app()
    with app.app_context():
        print("Setting up Vendor Reliability tables and data...")
        
        # 1. Create Tables
        # orders
        db.session.execute(text("""
            CREATE TABLE IF NOT EXISTS orders (
                order_id SERIAL PRIMARY KEY,
                vendor_id INTEGER REFERENCES vendors(id),
                order_qty INTEGER NOT NULL,
                fulfilled_qty INTEGER,
                order_date DATE,
                promised_date DATE,
                delivered_date DATE,
                status TEXT
            )
        """))
        
        # inspections
        db.session.execute(text("""
            CREATE TABLE IF NOT EXISTS inspections (
                id SERIAL PRIMARY KEY,
                order_id INTEGER REFERENCES orders(order_id),
                vendor_id INTEGER REFERENCES vendors(id),
                inspected_qty INTEGER,
                defective_qty INTEGER
            )
        """))
        
        # vendor_responses
        db.session.execute(text("""
            CREATE TABLE IF NOT EXISTS vendor_responses (
                id SERIAL PRIMARY KEY,
                vendor_id INTEGER REFERENCES vendors(id),
                response_hours NUMERIC
            )
        """))
        
        # warranty_claims
        db.session.execute(text("""
            CREATE TABLE IF NOT EXISTS warranty_claims (
                id SERIAL PRIMARY KEY,
                vendor_id INTEGER REFERENCES vendors(id),
                order_id INTEGER REFERENCES orders(order_id),
                claim_date DATE
            )
        """))
        
        db.session.commit()
        print("Tables created.")

        # 2. Seed Data
        # Get existing vendors
        vendors = db.session.execute(text("SELECT id FROM vendors")).fetchall()
        vendor_ids = [v[0] for v in vendors]
        
        if not vendor_ids:
            print("No vendors found! Please seed vendors first.")
            return

        print(f"Seeding data for {len(vendor_ids)} vendors...")
        
        # Clear existing dummy data to avoid duplicates on re-run
        db.session.execute(text("TRUNCATE TABLE warranty_claims, vendor_responses, inspections, orders RESTART IDENTITY CASCADE"))
        
        for v_id in vendor_ids:
            # Create 10 orders per vendor
            for i in range(10):
                order_date = datetime.now() - timedelta(days=random.randint(10, 100))
                promised_date = order_date + timedelta(days=10)
                
                # Randomize delivery performance
                late_days = random.choice([-2, -1, 0, 0, 0, 2, 5]) # mostly on time
                delivered_date = promised_date + timedelta(days=late_days)
                
                order_qty = random.randint(50, 500)
                fulfilled_qty = int(order_qty * random.uniform(0.9, 1.0)) # 90-100% fulfillment
                
                status = 'delivered'
                
                # Insert Order
                sql_order = text("""
                    INSERT INTO orders (vendor_id, order_qty, fulfilled_qty, order_date, promised_date, delivered_date, status)
                    VALUES (:vid, :oqty, :fqty, :odate, :pdate, :ddate, :stat)
                    RETURNING order_id
                """)
                order_id = db.session.execute(sql_order, {
                    "vid": v_id, "oqty": order_qty, "fqty": fulfilled_qty,
                    "odate": order_date, "pdate": promised_date, "ddate": delivered_date, "stat": status
                }).scalar()
                
                # Insert Inspection (for delivered orders)
                inspected_qty = fulfilled_qty
                defective_qty = int(inspected_qty * random.uniform(0, 0.05)) # 0-5% defect rate
                
                sql_insp = text("""
                    INSERT INTO inspections (order_id, vendor_id, inspected_qty, defective_qty)
                    VALUES (:oid, :vid, :iqty, :dqty)
                """)
                db.session.execute(sql_insp, {"oid": order_id, "vid": v_id, "iqty": inspected_qty, "dqty": defective_qty})
                
                # Insert Warranty Claim (Occasional)
                if random.random() < 0.1: # 10% chance
                    sql_claim = text("INSERT INTO warranty_claims (vendor_id, order_id, claim_date) VALUES (:vid, :oid, NOW())")
                    db.session.execute(sql_claim, {"vid": v_id, "oid": order_id})

            # Response Times (Average out)
            for _ in range(5):
                hours = random.uniform(1, 48) # 1 to 48 hours response
                sql_resp = text("INSERT INTO vendor_responses (vendor_id, response_hours) VALUES (:vid, :hours)")
                db.session.execute(sql_resp, {"vid": v_id, "hours": hours})
                
        db.session.commit()
        print("Data seeded.")

        # 3. Create Materialized View (as View for simplicity now, can make Materialized if needed)
        print("Creating View 'vendor_reliability_view'...")
        view_sql = text("""
            CREATE OR REPLACE VIEW vendor_reliability_view AS
            WITH 
            metrics AS (
                SELECT
                    v.id as vendor_id,
                    v.name as vendor_name,
                    
                    -- OTR: On-Time Delivery Rate
                    -- Count orders where delivered_date <= promised_date / Total delivered orders
                    COALESCE(
                        CAST(count(CASE WHEN o.delivered_date <= o.promised_date THEN 1 END) AS FLOAT) / NULLIF(count(o.order_id), 0), 
                        0
                    ) as otr,
                    
                    -- FR: Fulfillment Rate
                    -- Sum(fulfilled) / Sum(ordered)
                    COALESCE(
                        CAST(sum(o.fulfilled_qty) AS FLOAT) / NULLIF(sum(o.order_qty), 0), 
                        0
                    ) as fr,

                    -- QR: Quality Rate (from inspections)
                    -- 1 - (sum(defective) / sum(inspected))
                    COALESCE(
                        1 - (CAST(sum(i.defective_qty) AS FLOAT) / NULLIF(sum(i.inspected_qty), 0)),
                        1
                    ) as qr

                FROM vendors v
                LEFT JOIN orders o ON v.id = o.vendor_id
                LEFT JOIN inspections i ON o.order_id = i.order_id
                GROUP BY v.id, v.name
            ),
            response_metrics AS (
                SELECT 
                    vendor_id, 
                    -- RTS: 1 - min(avg_hours / 72, 1)
                    1 - LEAST(AVG(response_hours) / 72.0, 1) as rts
                FROM vendor_responses
                GROUP BY vendor_id
            ),
            claim_metrics AS (
                SELECT
                    v.id as vendor_id,
                    -- CCR: 1 - (claims / total_orders)
                    -- Note: total_orders needs to be fetched correctly, we'll join metrics again or separate logic
                    count(wc.id) as claim_count
                FROM vendors v
                LEFT JOIN warranty_claims wc ON v.id = wc.vendor_id
                GROUP BY v.id
            ),
            order_counts AS (
                SELECT vendor_id, count(*) as total_orders FROM orders GROUP BY vendor_id
            )

            SELECT
                m.vendor_id,
                m.vendor_name,
                ROUND(CAST(m.otr AS NUMERIC), 2) as otr,
                ROUND(CAST(m.qr AS NUMERIC), 2) as qr,
                ROUND(CAST(m.fr AS NUMERIC), 2) as fr,
                ROUND(CAST(COALESCE(rm.rts, 0) AS NUMERIC), 2) as rts,
                
                -- CCR Calculation
                ROUND(CAST(
                    COALESCE(
                        1 - (CAST(cm.claim_count AS FLOAT) / NULLIF(oc.total_orders, 0)), 
                        1
                    ) AS NUMERIC), 2
                ) as ccr,
                
                -- Final Score
                ROUND(CAST(
                    100 * (
                        0.30 * m.otr + 
                        0.30 * m.qr + 
                        0.20 * m.fr + 
                        0.10 * COALESCE(rm.rts, 0) + 
                        0.10 * COALESCE(
                            1 - (CAST(cm.claim_count AS FLOAT) / NULLIF(oc.total_orders, 0)), 
                            1
                        )
                    ) AS NUMERIC), 1
                ) as reliability_score

            FROM metrics m
            LEFT JOIN response_metrics rm ON m.vendor_id = rm.vendor_id
            LEFT JOIN claim_metrics cm ON m.vendor_id = cm.vendor_id
            LEFT JOIN order_counts oc ON m.vendor_id = oc.vendor_id;
        """)
        db.session.execute(view_sql)
        db.session.commit()
        print("View created successfully.")

        # Verify
        result = db.session.execute(text("SELECT * FROM vendor_reliability_view LIMIT 5")).fetchall()
        print("\n--- Sample Data ---")
        for r in result:
            print(r)

if __name__ == "__main__":
    setup_vendor_reliability()
