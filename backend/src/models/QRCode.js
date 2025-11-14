const mongoose = require('mongoose');

const qrCodeSchema = new mongoose.Schema({
  qrId: {
    type: String,
    required: true,
    unique: true,
  },
  data: {
    type: String,
    required: true,
  },
  materialType: {
    type: String,
    required: true,
    enum: ['metal', 'plastic', 'wood', 'stone', 'glass', 'other'],
  },
  dimensions: {
    width: { type: Number, required: true },
    height: { type: Number, required: true },
    unit: { type: String, default: 'mm' },
  },
  location: {
    station: String,
    platform: String,
    area: String,
    coordinates: {
      latitude: Number,
      longitude: Number,
    },
  },
  engravingDate: {
    type: Date,
    default: Date.now,
  },
  status: {
    type: String,
    enum: ['active', 'inactive', 'damaged', 'replaced'],
    default: 'active',
  },
  scans: [{
    scannedAt: Date,
    scannedBy: String,
    deviceId: String,
  }],
  metadata: {
    type: Map,
    of: String,
  },
}, {
  timestamps: true,
});

// Index for faster queries
qrCodeSchema.index({ qrId: 1 });
qrCodeSchema.index({ 'location.station': 1 });
qrCodeSchema.index({ status: 1 });

module.exports = mongoose.model('QRCode', qrCodeSchema);
