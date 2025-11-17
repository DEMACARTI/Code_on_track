# Railway QR Code Tracking System

A comprehensive three-way centralized database and LLM-infused system for railway QR code generation, engraving, tracking, and management.

## System Overview

This system consists of four main components:

1. **Backend API** - Centralized database with LLM integration for data processing and insights
2. **Web Portal** - Dashboard for railway department staff to monitor and manage QR codes
3. **QR Generation Application** - Software for generating and preparing QR codes for engraving
4. **Mobile Application** - Field staff app for scanning QR codes and recording data

## Features

### Backend System
- **Centralized MongoDB Database** - Stores all QR code data, scan records, and notifications
- **LLM Integration** - AI-powered insights for:
  - Maintenance recommendations
  - Anomaly detection
  - Usage pattern analysis
  - Predictive maintenance
  - Automated notifications
- **RESTful API** - Complete API for all system operations
- **Data Processing** - Real-time data processing and analytics

### QR Code Generation
- **Multi-Material Support** - Optimized QR codes for:
  - Metal
  - Plastic
  - Wood
  - Stone
  - Glass
  - Other materials
- **Dimension-Aware** - Adjusts QR code parameters based on material dimensions
- **Engraving Specifications** - Generates machine-specific engraving files
- **Batch Generation** - Create multiple QR codes efficiently

### Web Portal
- **Dashboard** - Real-time overview of system metrics
- **QR Code Management** - View, filter, and manage all QR codes
- **Notifications** - LLM-generated alerts and recommendations
- **Analytics** - Comprehensive insights and reporting
- **Responsive Design** - Works on desktop and tablet devices

### Mobile Application
- **QR Code Scanning** - Camera-based scanning with barcode reader
- **Real-time Sync** - Instant data synchronization with backend
- **Offline Support** - Record data even without internet connection
- **Field Data Recording** - Capture maintenance, inspection, and incident data
- **Location Tracking** - GPS-based location recording

## Technology Stack

### Backend
- Node.js with Express
- MongoDB with Mongoose
- QRCode library
- Axios for HTTP requests
- LLM API integration (OpenAI compatible)

### Web Portal
- React 18
- Vite for build tooling
- React Router for navigation
- Axios for API calls
- Responsive CSS

### Mobile App
- React Native with Expo
- Expo Camera & Barcode Scanner
- React Navigation
- Axios for API calls

### QR Generation
- Node.js
- QRCode library
- Electron (optional for desktop app)

## Installation & Setup

### Prerequisites
- Node.js 16+ and npm
- MongoDB 5+
- Expo CLI (for mobile development)
- Android Studio or Xcode (for mobile app testing)

### Backend Setup

```bash
cd backend
npm install
cp .env.example .env
# Edit .env with your configuration
npm start
```

### Web Portal Setup

```bash
cd frontend
npm install
npm run dev
```

### Mobile App Setup

```bash
cd mobile
npm install
npx expo start
```

### QR Generation App Setup

```bash
cd qr-generation
npm install
npm start
```

## Configuration

### Environment Variables

#### Backend (.env)
```
PORT=5000
MONGODB_URI=mongodb://localhost:27017/railway_qr_system
LLM_API_KEY=your_api_key_here
LLM_API_URL=https://api.openai.com/v1/chat/completions
LLM_MODEL=gpt-3.5-turbo
JWT_SECRET=your_jwt_secret
```

#### Frontend
Update API URL in `frontend/src/services/apiService.js`

#### Mobile
Update API URL in `mobile/src/services/apiService.js`

## API Documentation

### QR Code Endpoints

#### Generate QR Code
```
POST /api/qr/generate
Body: {
  data: {...},
  materialType: "metal",
  dimensions: { width: 50, height: 50, unit: "mm" },
  location: { station: "Central", platform: "3" }
}
```

#### Get QR Code
```
GET /api/qr/:qrId
```

#### Scan QR Code
```
POST /api/qr/:qrId/scan
Body: {
  scannedBy: "user_id",
  deviceId: "device_001"
}
```

#### List QR Codes
```
GET /api/qr?status=active&materialType=metal&page=1&limit=20
```

### Data Endpoints

#### Record Data
```
POST /api/data/record
Body: {
  qrId: "...",
  dataType: "maintenance",
  data: {...},
  source: "mobile"
}
```

#### Get Data Records
```
GET /api/data/:qrId?dataType=scan&page=1&limit=50
```

#### Analyze Data
```
POST /api/data/:qrId/analyze
```

### Notification Endpoints

#### Get Notifications
```
GET /api/notifications?status=pending&priority=high
```

#### Generate Notifications
```
POST /api/notifications/generate
Body: { qrId: "..." }
```

#### Update Notification Status
```
PUT /api/notifications/:id/status
Body: {
  status: "acknowledged",
  assignedTo: "user_id"
}
```

## Database Schema

### QRCode Collection
- qrId: Unique identifier
- data: Encoded data string
- materialType: Type of material
- dimensions: Width, height, unit
- location: Station, platform, area, coordinates
- engravingDate: Date of engraving
- status: active, inactive, damaged, replaced
- scans: Array of scan records
- metadata: Additional key-value pairs

### DataRecord Collection
- qrId: Reference to QR code
- dataType: scan, maintenance, inspection, incident, usage
- data: Record data object
- processedByLLM: Boolean flag
- llmInsights: AI-generated insights
- llmSuggestions: Array of suggestions
- source: mobile, web, automated, manual

### Notification Collection
- qrId: Reference to QR code
- type: maintenance, alert, suggestion, insight, anomaly
- priority: low, medium, high, critical
- title: Notification title
- message: Notification message
- llmGenerated: Boolean flag
- status: pending, acknowledged, resolved, dismissed
- assignedTo: User assignment

## LLM Integration

The system uses LLM for:

1. **Data Analysis** - Process QR code data and generate insights
2. **Maintenance Recommendations** - Predict maintenance needs
3. **Anomaly Detection** - Identify unusual patterns
4. **Notification Generation** - Create contextual alerts
5. **Pattern Recognition** - Discover trends and patterns

### LLM Service Methods

```javascript
// Process QR data
await llmService.processQRData(qrData, historicalData)

// Generate maintenance recommendations
await llmService.generateMaintenanceRecommendations(qrData, scanHistory)

// Detect anomalies
await llmService.detectAnomalies(scanData)

// Generate notifications
await llmService.generateNotifications(context)
```

## Usage Workflows

### Workflow 1: QR Code Generation & Engraving

1. Access QR Generation application
2. Input specifications (material, dimensions, location)
3. Generate QR code with optimized settings
4. Review engraving specifications
5. Export to engraving machine format
6. Engrave on material
7. Quality check and activate in system

### Workflow 2: Field Scanning & Data Recording

1. Field staff opens mobile app
2. Scans QR code with camera
3. Views QR code details and location
4. Records maintenance/inspection data
5. Data syncs to central database
6. LLM processes data and generates insights
7. Notifications created for relevant personnel

### Workflow 3: Monitoring & Management

1. Railway staff logs into web portal
2. Views dashboard with system overview
3. Reviews notifications and alerts
4. Filters and searches QR codes
5. Views analytics and insights
6. Takes action on recommendations
7. Updates QR code status as needed

## Deployment

### Backend Deployment
- Deploy to cloud platform (AWS, Azure, Google Cloud)
- Use MongoDB Atlas for database
- Set up environment variables
- Configure SSL/TLS
- Set up monitoring and logging

### Frontend Deployment
- Build: `npm run build`
- Deploy to static hosting (Netlify, Vercel, S3)
- Configure API endpoint

### Mobile App Deployment
- Build APK for Android: `expo build:android`
- Build IPA for iOS: `expo build:ios`
- Publish to app stores

## Security Considerations

- Use HTTPS for all API communication
- Implement JWT authentication
- Validate all input data
- Secure LLM API keys
- Implement rate limiting
- Regular security audits
- Encrypt sensitive data
- Implement role-based access control

## Maintenance & Support

- Regular database backups
- Monitor system performance
- Update dependencies
- Review and optimize LLM prompts
- Analyze usage patterns
- User feedback collection
- Regular system updates

## Future Enhancements

- Real-time collaboration features
- Advanced analytics dashboard
- Multi-language support
- Offline-first mobile app
- IoT sensor integration
- Blockchain for audit trail
- AR features for mobile app
- Voice-based data entry
- Advanced ML models for predictions

## Contributing

This is a Smart India Hackathon 2025 project. For contributions and improvements, please follow the project guidelines.

## License

MIT License - See LICENSE file for details

## Support

For questions and support, please contact the development team.
