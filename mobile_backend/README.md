# Mobile Backend - RailChinh QR Code Tracking System

## Overview
FastAPI backend server for the RailChinh mobile application (Flutter). Provides authentication, QR code scanning, item management, and inspection recording functionality.

## 🌐 Production Deployment
**Live Backend URL:** https://railchinh-mobile-backend.onrender.com

The backend is deployed on Render.com and accessible from any device with internet connection. The Flutter app is pre-configured to use this production URL.

## 🚀 Quick Start (Local Development)

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)
- PostgreSQL database (Supabase)

### Installation

1. **Navigate to mobile backend directory:**
   ```bash
   cd /Users/dakshrathore/Desktop/Code_on_track/mobile_backend
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
   
   Or with conda:
   ```bash
   conda install --file requirements.txt
   ```

3. **Verify environment setup:**
   The backend uses environment variables for database connection. The Supabase connection is pre-configured in the code.

### Running the Server

**Option 1: Standard Run**
```bash
cd mobile_backend
uvicorn main:app --reload --host 0.0.0.0 --port 8080
```

**Option 2: One-line command from project root**
```bash
cd /Users/dakshrathore/Desktop/Code_on_track/mobile_backend && uvicorn main:app --reload --host 0.0.0.0 --port 8080
```

**Option 3: With hot reload (development)**
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8080
```

**Option 4: Production mode (no reload)**
```bash
uvicorn main:app --host 0.0.0.0 --port 8080 --workers 4
```

### Verify Server is Running

Once started, you should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8080 (Press CTRL+C to quit)
INFO:     Started reloader process [XXXX] using WatchFiles
INFO:     Started server process [XXXX]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

**Access Points:**
- **API Base URL:** http://localhost:8080
- **API Documentation:** http://localhost:8080/docs
- **Health Check:** http://localhost:8080/health

## 📱 Login Credentials

### Simple Mobile App Users

| Role | Username | Password | Access Level |
|------|----------|----------|--------------|
| Admin | `admin` | `admin123` | Full administrative access |
| Inspection | `inspection` | `inspect123` | Inspection and quality control |
| Inventory | `inventory` | `inventory123` | Inventory management |
| Installation | `installation` | `install123` | Component installation |
| Management | `management` | `manage123` | Management and reporting |

### Setup Users (First Time)

If users don't exist in the database, run:
```bash
cd mobile_backend
python setup_simple_users.py
```

This will create all users with the credentials listed above.

## 🔧 Configuration

### Database Connection
The backend connects to Supabase PostgreSQL:
- **Database:** Supabase PostgreSQL (pooler connection)
- **Connection:** Pre-configured in `main.py`
- **Tables:** `users`, `items`, `inspections`

### Port Configuration
- **Default Port:** 8080
- To change port, modify the `--port` parameter when running uvicorn

### Environment Variables (Optional)
```bash
DATABASE_URL=postgresql://postgres.aktfgilmfoprdkwkzybd:Alqawwiy%40123@aws-1-ap-northeast-2.pooler.supabase.com:6543/postgres
```

## 📚 API Endpoints

### Authentication
- `POST /api/auth/login` - User login with username/password

### Items
- `GET /api/items/{uid}` - Get item details by UID
- `POST /api/items/{uid}/status` - Update item status

### Inspections
- `POST /api/inspections` - Submit inspection record
- `GET /api/inspections/{uid}` - Get inspections for an item

### Health Check
- `GET /` - Server status
- `GET /health` - Health check endpoint

## 🧪 Testing Database Connection

```bash
cd mobile_backend
python test_db_connection.py
```

This will verify:
- ✅ Database connection
- ✅ Users table access
- ✅ Items table access
- ✅ Authentication functionality

## 🔍 Troubleshooting

### Port Already in Use
```bash
# Kill existing process on port 8080
lsof -ti:8080 | xargs kill -9

# Then restart server
uvicorn main:app --reload --host 0.0.0.0 --port 8080
```

### Module Not Found
```bash
# Reinstall dependencies
pip install -r requirements.txt
```

### Database Connection Issues
```bash
# Test connection
python test_db_connection.py

# Recreate users
python setup_simple_users.py
```

### Cannot Import 'main'
Make sure you're in the mobile_backend directory:
```bash
cd /Users/dakshrathore/Desktop/Code_on_track/mobile_backend
uvicorn main:app --reload --host 0.0.0.0 --port 8080
```

## 📦 Dependencies

Key packages (from requirements.txt):
- `fastapi` - Web framework
- `uvicorn` - ASGI server
- `sqlalchemy` - Database ORM
- `psycopg2` - PostgreSQL adapter
- `pydantic` - Data validation

## 🛑 Stopping the Server

**Keyboard Interrupt:**
```
Press Ctrl+C in the terminal
```

**Force Kill:**
```bash
lsof -ti:8080 | xargs kill -9
```

## 🔒 Security Notes

**⚠️ IMPORTANT:** The current credentials are for **development only**.

**For Production:**
1. Change all passwords to strong, unique values
2. Enable HTTPS/SSL
3. Use environment variables for sensitive data
4. Implement rate limiting
5. Enable CORS restrictions
6. Use JWT token expiration
7. Implement password hashing with bcrypt (already done)

## 📊 Database Schema

### users table
- `id` (Primary Key)
- `username` (Unique)
- `email` (Unique)
- `hashed_password`
- `full_name`
- `department` (UserRole enum)
- `is_active`
- `created_at`
- `last_login`

### items table
- `id` (Primary Key)
- `uid` (Unique, indexed)
- `component_type`
- `lot_number`
- `vendor_id`
- `quantity`
- `warranty_years`
- `manufacture_date`
- `current_status`
- `qr_image_url`
- `created_at`
- `updated_at`

### inspections table
- `id` (Primary Key)
- `item_uid` (Foreign Key)
- `status`
- `remark`
- `inspector_id`
- `photo_url`
- `inspected_at`
- `created_at`

## 🔗 Related Services

- **Website Backend:** http://localhost:8001
- **Website Frontend:** http://localhost:5173
- **Mobile Backend:** http://localhost:8080 (This service)

## 📝 Logs

Server logs are displayed in the terminal. For production, consider:
```bash
uvicorn main:app --log-level info --access-log
```

## 🆘 Support

For issues or questions, check:
1. Server logs in terminal
2. API documentation at `/docs`
3. Database connection test script
4. LOGIN_CREDENTIALS.md in full_website folder

## 📄 License

Internal use only - RailChinh QR Code Tracking System
