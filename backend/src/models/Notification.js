const mongoose = require('mongoose');

const notificationSchema = new mongoose.Schema({
  qrId: {
    type: String,
    required: true,
  },
  type: {
    type: String,
    enum: ['maintenance', 'alert', 'suggestion', 'insight', 'anomaly'],
    required: true,
  },
  priority: {
    type: String,
    enum: ['low', 'medium', 'high', 'critical'],
    default: 'medium',
  },
  title: {
    type: String,
    required: true,
  },
  message: {
    type: String,
    required: true,
  },
  llmGenerated: {
    type: Boolean,
    default: false,
  },
  llmContext: {
    type: String,
  },
  status: {
    type: String,
    enum: ['pending', 'acknowledged', 'resolved', 'dismissed'],
    default: 'pending',
  },
  assignedTo: {
    type: String,
  },
  resolvedAt: {
    type: Date,
  },
}, {
  timestamps: true,
});

// Index for faster queries
notificationSchema.index({ qrId: 1 });
notificationSchema.index({ status: 1 });
notificationSchema.index({ priority: 1 });

module.exports = mongoose.model('Notification', notificationSchema);
