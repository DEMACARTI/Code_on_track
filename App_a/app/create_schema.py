import sys
import os

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import engine
from sqlalchemy import text
import psycopg2

def create_complete_schema():
    """Create complete database schema with all necessary tables, indexes, and constraints."""
    
    # Connect directly with psycopg2 for schema creation
    conn = psycopg2.connect(
        dbname='irf_dev',
        user='irf_user', 
        password='irf_pass',
        host='localhost',
        port=5433
    )
    conn.autocommit = True
    cur = conn.cursor()
    
    print("Creating complete database schema...\n")
    print("=" * 80)
    
    # Drop existing tables to recreate schema
    print("\n1. Cleaning up existing tables...")
    cur.execute("""
        DROP TABLE IF EXISTS engraving_history CASCADE;
        DROP TABLE IF EXISTS engraving_queue CASCADE;
        DROP TABLE IF EXISTS items CASCADE;
        DROP TYPE IF EXISTS engravingstatus CASCADE;
    """)
    print("   ✓ Existing tables dropped")
    
    # Create enum type for engraving status
    print("\n2. Creating enum types...")
    cur.execute("""
        CREATE TYPE engravingstatus AS ENUM (
            'PENDING',
            'IN_PROGRESS', 
            'ENGRAVING',
            'COMPLETED',
            'FAILED'
        );
    """)
    print("   ✓ EngravingStatus enum created")
    
    # Create items table
    print("\n3. Creating items table...")
    cur.execute("""
        CREATE TABLE items (
            id BIGSERIAL PRIMARY KEY,
            uid VARCHAR(128) UNIQUE NOT NULL,
            component_type VARCHAR(16) NOT NULL,
            lot_number VARCHAR(64) NOT NULL,
            vendor_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL DEFAULT 1,
            warranty_years INTEGER,
            manufacture_date TIMESTAMP,
            qr_image_url TEXT,
            current_status VARCHAR(32) NOT NULL DEFAULT 'manufactured',
            metadata JSON,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE,
            
            CONSTRAINT chk_quantity CHECK (quantity > 0),
            CONSTRAINT chk_warranty CHECK (warranty_years IS NULL OR warranty_years > 0),
            CONSTRAINT chk_component_type CHECK (component_type IN ('EC', 'SLP', 'RP', 'LIN'))
        );
    """)
    print("   ✓ Items table created")
    
    # Create engraving_queue table
    print("\n4. Creating engraving_queue table...")
    cur.execute("""
        CREATE TABLE engraving_queue (
            id BIGSERIAL PRIMARY KEY,
            item_uid VARCHAR(128) NOT NULL,
            status engravingstatus NOT NULL DEFAULT 'PENDING',
            svg_url TEXT NOT NULL,
            attempts INTEGER NOT NULL DEFAULT 0,
            max_attempts INTEGER NOT NULL DEFAULT 3,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            started_at TIMESTAMP WITH TIME ZONE,
            completed_at TIMESTAMP WITH TIME ZONE,
            error_message TEXT,
            
            CONSTRAINT fk_item_uid FOREIGN KEY (item_uid) 
                REFERENCES items(uid) ON DELETE CASCADE,
            CONSTRAINT chk_attempts CHECK (attempts >= 0 AND attempts <= max_attempts),
            CONSTRAINT chk_max_attempts CHECK (max_attempts > 0)
        );
    """)
    print("   ✓ Engraving queue table created")
    
    # Create engraving_history table
    print("\n5. Creating engraving_history table...")
    cur.execute("""
        CREATE TABLE engraving_history (
            id BIGSERIAL PRIMARY KEY,
            engraving_job_id BIGINT NOT NULL,
            status engravingstatus NOT NULL,
            message TEXT,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            
            CONSTRAINT fk_engraving_job FOREIGN KEY (engraving_job_id) 
                REFERENCES engraving_queue(id) ON DELETE CASCADE
        );
    """)
    print("   ✓ Engraving history table created")
    
    # Create indexes for better performance
    print("\n6. Creating indexes...")
    cur.execute("""
        CREATE INDEX idx_items_uid ON items(uid);
        CREATE INDEX idx_items_component_type ON items(component_type);
        CREATE INDEX idx_items_lot_number ON items(lot_number);
        CREATE INDEX idx_items_created_at ON items(created_at DESC);
        CREATE INDEX idx_items_status ON items(current_status);
        
        CREATE INDEX idx_engraving_queue_item_uid ON engraving_queue(item_uid);
        CREATE INDEX idx_engraving_queue_status ON engraving_queue(status);
        CREATE INDEX idx_engraving_queue_created_at ON engraving_queue(created_at DESC);
        
        CREATE INDEX idx_engraving_history_job_id ON engraving_history(engraving_job_id);
        CREATE INDEX idx_engraving_history_created_at ON engraving_history(created_at DESC);
    """)
    print("   ✓ Indexes created")
    
    # Create views for common queries
    print("\n7. Creating views...")
    cur.execute("""
        CREATE OR REPLACE VIEW v_items_with_engraving_status AS
        SELECT 
            i.*,
            eq.id as engraving_job_id,
            eq.status as engraving_status,
            eq.attempts,
            eq.created_at as engraving_created_at,
            eq.started_at as engraving_started_at,
            eq.completed_at as engraving_completed_at,
            eq.error_message
        FROM items i
        LEFT JOIN engraving_queue eq ON i.uid = eq.item_uid
        ORDER BY i.created_at DESC;
        
        CREATE OR REPLACE VIEW v_pending_jobs AS
        SELECT 
            eq.*,
            i.component_type,
            i.lot_number,
            i.vendor_id
        FROM engraving_queue eq
        JOIN items i ON eq.item_uid = i.uid
        WHERE eq.status = 'PENDING'
        ORDER BY eq.created_at ASC;
        
        CREATE OR REPLACE VIEW v_engraving_statistics AS
        SELECT 
            COUNT(*) FILTER (WHERE status = 'PENDING') as pending_count,
            COUNT(*) FILTER (WHERE status = 'IN_PROGRESS') as in_progress_count,
            COUNT(*) FILTER (WHERE status = 'ENGRAVING') as engraving_count,
            COUNT(*) FILTER (WHERE status = 'COMPLETED') as completed_count,
            COUNT(*) FILTER (WHERE status = 'FAILED') as failed_count,
            COUNT(*) as total_jobs
        FROM engraving_queue;
    """)
    print("   ✓ Views created")
    
    # Create trigger for updated_at
    print("\n8. Creating triggers...")
    cur.execute("""
        CREATE OR REPLACE FUNCTION update_updated_at_column()
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.updated_at = NOW();
            RETURN NEW;
        END;
        $$ language 'plpgsql';
        
        CREATE TRIGGER update_items_updated_at BEFORE UPDATE ON items
            FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
    """)
    print("   ✓ Triggers created")
    
    # Insert sample data
    print("\n9. Inserting sample reference data...")
    cur.execute("""
        -- Sample data is optional, kept minimal for production
        INSERT INTO items (uid, component_type, lot_number, vendor_id, quantity, warranty_years, current_status, metadata)
        VALUES 
            ('SAMPLE-INIT-001', 'EC', 'INIT-LOT', 999, 1, 5, 'manufactured', '{"sample": true, "purpose": "schema_validation"}')
        ON CONFLICT (uid) DO NOTHING;
    """)
    print("   ✓ Sample data inserted")
    
    # Verify schema
    print("\n10. Verifying schema...")
    cur.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public' 
        AND table_type = 'BASE TABLE'
        ORDER BY table_name;
    """)
    tables = cur.fetchall()
    print(f"   ✓ Tables created: {', '.join([t[0] for t in tables])}")
    
    cur.execute("""
        SELECT indexname 
        FROM pg_indexes 
        WHERE schemaname = 'public'
        ORDER BY indexname;
    """)
    indexes = cur.fetchall()
    print(f"   ✓ Indexes created: {len(indexes)} indexes")
    
    cur.execute("""
        SELECT viewname 
        FROM pg_views 
        WHERE schemaname = 'public'
        ORDER BY viewname;
    """)
    views = cur.fetchall()
    print(f"   ✓ Views created: {', '.join([v[0] for v in views])}")
    
    cur.close()
    conn.close()
    
    print("\n" + "=" * 80)
    print("✓ Schema creation completed successfully!")
    print("\nDatabase structure:")
    print("  Tables:")
    print("    - items: Stores component information and QR codes")
    print("    - engraving_queue: Manages engraving jobs with status tracking")
    print("    - engraving_history: Tracks history of engraving attempts")
    print("\n  Views:")
    print("    - v_items_with_engraving_status: Items with their engraving status")
    print("    - v_pending_jobs: All pending engraving jobs")
    print("    - v_engraving_statistics: Real-time statistics on engraving jobs")
    print("\n  Indexes: Created on all foreign keys and frequently queried columns")
    print("  Triggers: Auto-update timestamps on record modifications")
    print("=" * 80)

if __name__ == "__main__":
    try:
        create_complete_schema()
    except Exception as e:
        print(f"\n✗ Error creating schema: {e}")
        import traceback
        traceback.print_exc()
