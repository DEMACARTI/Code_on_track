#!/usr/bin/env python3
"""
Setup script to create user tables and admin users in Supabase
Run from full_website/backend directory with: PYTHONPATH=. python scripts/setup_users.py
"""

import asyncio
import uuid
from sqlalchemy import text
import sys
import os

# Add parent to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.session import engine
from app.auth.security import get_password_hash


async def setup_database():
    print("🔧 Setting up database tables and users...")
    
    async with engine.begin() as conn:
        # Create website_users table
        print("\n📋 Creating website_users table...")
        await conn.execute(text("""
            CREATE TABLE IF NOT EXISTS website_users (
                id VARCHAR PRIMARY KEY,
                username VARCHAR UNIQUE NOT NULL,
                email VARCHAR UNIQUE,
                password_hash VARCHAR NOT NULL,
                role VARCHAR(10) NOT NULL,
                is_active BOOLEAN DEFAULT true NOT NULL,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL
            )
        """))
        print("   ✅ website_users table created!")
        
        # Create app_users table
        print("\n📋 Creating app_users table...")
        await conn.execute(text("""
            CREATE TABLE IF NOT EXISTS app_users (
                id BIGSERIAL PRIMARY KEY,
                username VARCHAR(50) UNIQUE NOT NULL,
                email VARCHAR(100) UNIQUE NOT NULL,
                hashed_password VARCHAR(255) NOT NULL,
                full_name VARCHAR(100),
                department VARCHAR(20) NOT NULL,
                is_active BOOLEAN DEFAULT true NOT NULL,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
                updated_at TIMESTAMP WITH TIME ZONE,
                last_login TIMESTAMP WITH TIME ZONE
            )
        """))
        print("   ✅ app_users table created!")
        
        # Create website admin user
        print("\n👤 Creating website admin user...")
        result = await conn.execute(text("SELECT id FROM website_users WHERE username = 'admin'"))
        if result.fetchone():
            print("   ⚠️  Website admin user already exists")
        else:
            password_hash = get_password_hash("Admin@123")
            await conn.execute(text("""
                INSERT INTO website_users (id, username, email, password_hash, role, is_active)
                VALUES (:id, :username, :email, :password_hash, :role, :is_active)
            """), {
                "id": str(uuid.uuid4()),
                "username": "admin",
                "email": "admin@railchinh.com",
                "password_hash": password_hash,
                "role": "admin",
                "is_active": True
            })
            print("   ✅ Website admin user created!")
        
        # Create app admin user (using SHA256 hash as in the App_a auth)
        print("\n👤 Creating app admin user...")
        result = await conn.execute(text("SELECT id FROM app_users WHERE username = 'appadmin'"))
        if result.fetchone():
            print("   ⚠️  App admin user already exists")
        else:
            import hashlib
            app_password_hash = hashlib.sha256("AppAdmin@123".encode()).hexdigest()
            await conn.execute(text("""
                INSERT INTO app_users (username, email, hashed_password, full_name, department, is_active)
                VALUES (:username, :email, :hashed_password, :full_name, :department, :is_active)
            """), {
                "username": "appadmin",
                "email": "appadmin@railchinh.com",
                "hashed_password": app_password_hash,
                "full_name": "App Administrator",
                "department": "admin",
                "is_active": True
            })
            print("   ✅ App admin user created!")
    
    print("\n" + "="*50)
    print("🎉 Setup Complete!")
    print("="*50)
    print("\n📋 LOGIN CREDENTIALS:")
    print("\n🌐 WEBSITE (http://localhost:5174):")
    print("   Username: admin")
    print("   Password: Admin@123")
    print("\n📱 MOBILE APP:")
    print("   Username: appadmin")
    print("   Password: AppAdmin@123")
    print("="*50)


if __name__ == "__main__":
    asyncio.run(setup_database())
