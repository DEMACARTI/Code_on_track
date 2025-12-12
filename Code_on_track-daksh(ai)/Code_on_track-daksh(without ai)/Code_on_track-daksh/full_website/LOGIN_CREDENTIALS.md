# Website Portal Login Credentials

## 🔐 Admin Access

### Website Portal (Main Dashboard)
- **Username:** `admin`
- **Password:** `Admin@123`
- **Email:** admin@railchinh.com
- **Role:** ADMIN
- **Access Level:** Full system access (Create, Read, Update, Delete)

### Mobile App Users (Simple Login)

**Admin User:**
- **Username:** `admin`
- **Password:** `admin123`
- **Email:** admin@railchinh.com
- **Role:** admin
- **Access Level:** Full administrative access

**Inspection Team:**
- **Username:** `inspection`
- **Password:** `inspect123`
- **Email:** inspection@railchinh.com
- **Role:** inspection
- **Access Level:** Inspection and quality control

**Inventory Manager:**
- **Username:** `inventory`
- **Password:** `inventory123`
- **Email:** inventory@railchinh.com
- **Role:** inventory
- **Access Level:** Inventory management

**Installation Team:**
- **Username:** `installation`
- **Password:** `install123`
- **Email:** installation@railchinh.com
- **Role:** installation
- **Access Level:** Component installation

**Management:**
- **Username:** `management`
- **Password:** `manage123`
- **Email:** management@railchinh.com
- **Role:** management
- **Access Level:** Management and reporting

## 📱 Access URLs

- **Website Portal:** http://localhost:3000
- **Website Backend API:** http://localhost:8001
- **Website API Docs:** http://localhost:8001/docs
- **Mobile Backend API:** http://localhost:8080 (or http://0.0.0.0:8080)
- **Mobile API Docs:** http://localhost:8080/docs

## ✨ New Features

### Remember Me (Save Password)
- Check the "Remember me" checkbox on login to save your credentials
- Your username and password will be automatically filled on next visit
- Stored securely in browser's local storage
- Uncheck to clear saved credentials

## 🔒 Security Notes

**IMPORTANT:** These are default credentials for development purposes.

**For Production:**
1. Change these passwords immediately
2. Use strong, unique passwords (minimum 12 characters)
3. Enable two-factor authentication if available
4. Regularly rotate passwords
5. Never commit credentials to version control
6. Use environment variables for sensitive data

## 👥 User Roles

### ADMIN
- Full access to all features
- Can create, edit, and delete items
- Access to vendor management
- Can import bulk items
- View all reports and analytics

### SERVICE
- Can create and update items
- Limited delete permissions
- Access to inspection data

### VIEWER
- Read-only access
- Can view items and reports
- Cannot modify data

## 🚀 First Time Setup

1. Start the backend server:
   ```bash
   cd full_website/backend
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

2. Run the user setup script (if not already done):
   ```bash
   cd full_website/backend
   PYTHONPATH=. python scripts/setup_users.py
   ```

3. Start the frontend:
   ```bash
   cd full_website/frontend
   npm start
   ```

4. Login with the credentials above

## 📧 Support

For issues or questions, contact your system administrator.
