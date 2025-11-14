#!/bin/bash

echo "======================================"
echo "Railway QR Code Tracking System Setup"
echo "======================================"
echo ""

# Check prerequisites
echo "Checking prerequisites..."

# Check Node.js
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js 16+ first."
    exit 1
fi

echo "✅ Node.js $(node -v) found"

# Check npm
if ! command -v npm &> /dev/null; then
    echo "❌ npm is not installed."
    exit 1
fi

echo "✅ npm $(npm -v) found"

# Check MongoDB
if ! command -v mongod &> /dev/null; then
    echo "⚠️  MongoDB is not installed. Please install MongoDB 5+ for database functionality."
fi

echo ""
echo "Installing dependencies..."
echo ""

# Install backend dependencies
echo "📦 Installing backend dependencies..."
cd backend
npm install
if [ $? -eq 0 ]; then
    echo "✅ Backend dependencies installed"
else
    echo "❌ Failed to install backend dependencies"
    exit 1
fi
cd ..

# Install frontend dependencies
echo ""
echo "📦 Installing frontend dependencies..."
cd frontend
npm install
if [ $? -eq 0 ]; then
    echo "✅ Frontend dependencies installed"
else
    echo "❌ Failed to install frontend dependencies"
    exit 1
fi
cd ..

# Install mobile dependencies
echo ""
echo "📦 Installing mobile dependencies..."
cd mobile
npm install
if [ $? -eq 0 ]; then
    echo "✅ Mobile dependencies installed"
else
    echo "❌ Failed to install mobile dependencies"
    exit 1
fi
cd ..

# Install QR generation dependencies
echo ""
echo "📦 Installing QR generation dependencies..."
cd qr-generation
npm install
if [ $? -eq 0 ]; then
    echo "✅ QR generation dependencies installed"
else
    echo "❌ Failed to install QR generation dependencies"
    exit 1
fi
cd ..

# Setup environment files
echo ""
echo "Setting up environment configuration..."
if [ ! -f backend/.env ]; then
    cp backend/.env.example backend/.env
    echo "✅ Created backend/.env from template"
    echo "⚠️  Please edit backend/.env and add your configuration"
else
    echo "ℹ️  backend/.env already exists"
fi

echo ""
echo "======================================"
echo "✅ Setup completed successfully!"
echo "======================================"
echo ""
echo "Next steps:"
echo "1. Configure backend/.env with your settings"
echo "2. Start MongoDB: mongod"
echo "3. Start backend: cd backend && npm start"
echo "4. Start frontend: cd frontend && npm run dev"
echo "5. Start mobile: cd mobile && npx expo start"
echo ""
echo "For complete documentation, see docs/README.md"
echo ""
