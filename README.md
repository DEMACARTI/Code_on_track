# Code_on_track
SIH Project 2025 - Railway QR Code Tracking System

## Overview

A comprehensive three-way centralized database and LLM-infused system for railway QR code generation, engraving, tracking, and intelligent data processing.

## System Components

1. **Backend API** (`/backend`) - Node.js/Express API with MongoDB and LLM integration
2. **Web Portal** (`/frontend`) - React-based dashboard for railway department
3. **Mobile App** (`/mobile`) - React Native app for QR code scanning
4. **QR Generation** (`/qr-generation`) - QR code generation and engraving software

## Key Features

- ✅ QR code generation optimized for multiple materials (metal, plastic, wood, stone, glass)
- ✅ Centralized MongoDB database for all tracking data
- ✅ LLM integration for AI-powered insights and recommendations
- ✅ Mobile app for field staff to scan and record data
- ✅ Web portal with real-time analytics and notifications
- ✅ Automated maintenance recommendations
- ✅ Anomaly detection and alerts
- ✅ Comprehensive API for all operations

## Quick Start

### Prerequisites
- Node.js 16+
- MongoDB 5+
- npm or yarn

### Installation

```bash
# Install all dependencies
npm run install-all

# Start backend server
cd backend && npm start

# Start web portal (in new terminal)
cd frontend && npm run dev

# Start mobile app (in new terminal)
cd mobile && npx expo start
```

## Documentation

Complete documentation is available in `/docs/README.md`

## Architecture

```
┌─────────────────┐
│   Mobile App    │ ──┐
│  (React Native) │   │
└─────────────────┘   │
                      │
┌─────────────────┐   │    ┌──────────────────┐
│   Web Portal    │───┼────│   Backend API    │
│     (React)     │   │    │  (Node.js/Express)│
└─────────────────┘   │    └──────────────────┘
                      │             │
┌─────────────────┐   │             │
│ QR Generation   │───┘             │
│   Software      │                 │
└─────────────────┘                 │
                                    │
                            ┌───────▼────────┐
                            │    MongoDB     │
                            │   Database     │
                            └────────────────┘
                                    │
                            ┌───────▼────────┐
                            │  LLM Service   │
                            │   (OpenAI)     │
                            └────────────────┘
```

## Project Structure

```
Code_on_track/
├── backend/           # Backend API and database
│   ├── src/
│   │   ├── api/      # API routes
│   │   ├── models/   # Database models
│   │   ├── services/ # Business logic
│   │   ├── llm/      # LLM integration
│   │   └── database/ # Database connection
│   └── package.json
├── frontend/          # Web portal
│   ├── src/
│   │   ├── pages/    # React pages
│   │   ├── components/
│   │   └── services/
│   └── package.json
├── mobile/            # Mobile application
│   ├── src/
│   │   ├── screens/
│   │   └── services/
│   └── package.json
├── qr-generation/     # QR generation app
│   ├── src/
│   │   └── services/
│   └── package.json
└── docs/             # Documentation
```

## Technology Stack

- **Backend**: Node.js, Express, MongoDB, Mongoose
- **Frontend**: React, Vite, React Router
- **Mobile**: React Native, Expo
- **AI/ML**: LLM API integration (OpenAI compatible)
- **QR Codes**: qrcode library
- **Database**: MongoDB

## API Endpoints

See `/docs/README.md` for complete API documentation.

Key endpoints:
- `POST /api/qr/generate` - Generate QR code
- `POST /api/qr/:qrId/scan` - Record scan
- `GET /api/notifications` - Get notifications
- `POST /api/data/:qrId/analyze` - LLM analysis

## Development

```bash
# Backend development
cd backend
npm run dev

# Frontend development
cd frontend
npm run dev

# Mobile development
cd mobile
npx expo start
```

## Environment Configuration

Copy `.env.example` to `.env` in the backend directory and configure:

```env
PORT=5000
MONGODB_URI=mongodb://localhost:27017/railway_qr_system
LLM_API_KEY=your_api_key_here
LLM_MODEL=gpt-3.5-turbo
```

## Contributing

This is an SIH 2025 project. Contributions are welcome!

## License

MIT License

## Team

Smart India Hackathon 2025 - Railway QR Code Tracking System Team
