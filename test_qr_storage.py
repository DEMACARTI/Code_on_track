#!/usr/bin/env python3
"""
Test script to check if QR codes are stored in the database
"""
import os
import sys
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Load environment from App_a
sys.path.append('/Users/dakshrathore/Desktop/Code_on_track/App_a')
load_dotenv('/Users/dakshrathore/Desktop/Code_on_track/App_a/.env')

DATABASE_URL = os.getenv('DATABASE_URL')

if not DATABASE_URL:
    print("❌ DATABASE_URL not found in .env file")
    sys.exit(1)

print(f"🔗 Connecting to database...")
print(f"📍 Connection: {DATABASE_URL.replace(DATABASE_URL.split('@')[0].split('//')[1], '***')}")

try:
    engine = create_engine(DATABASE_URL)
    
    with engine.connect() as conn:
        # Check if items table exists
        result = conn.execute(text("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'items'
            );
        """))
        table_exists = result.scalar()
        
        if not table_exists:
            print("❌ 'items' table does not exist!")
            sys.exit(1)
        
        print("✅ 'items' table exists")
        
        # Count total items
        result = conn.execute(text("SELECT COUNT(*) FROM items"))
        total_items = result.scalar()
        print(f"📊 Total items in database: {total_items}")
        
        # Count items with QR codes
        result = conn.execute(text("""
            SELECT COUNT(*) FROM items 
            WHERE qr_image_url IS NOT NULL AND qr_image_url != ''
        """))
        items_with_qr = result.scalar()
        print(f"🎯 Items with QR codes: {items_with_qr}")
        
        # Get sample items
        result = conn.execute(text("""
            SELECT uid, component_type, qr_image_url, created_at 
            FROM items 
            ORDER BY created_at DESC 
            LIMIT 5
        """))
        items = result.fetchall()
        
        if items:
            print("\n📋 Sample items:")
            print("-" * 80)
            for item in items:
                uid, comp_type, qr_url, created = item
                qr_status = "✅ Has QR" if qr_url else "❌ No QR"
                print(f"{uid:30} | {comp_type:15} | {qr_status}")
                if qr_url:
                    print(f"   QR URL: {qr_url}")
            print("-" * 80)
        else:
            print("\n⚠️  No items found in database")
            print("\n💡 To add items:")
            print("   1. Open GENGRAV app")
            print("   2. Fill in component details")
            print("   3. Click 'Generate QR Code'")
            print("   4. Items will be saved to Supabase")
        
        print("\n✅ Database check complete!")
        
except Exception as e:
    print(f"❌ Error: {e}")
    sys.exit(1)
