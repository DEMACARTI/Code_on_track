const mongoose = require('mongoose');

const dataRecordSchema = new mongoose.Schema({
  qrId: {
    type: String,
    required: true,
  },
  dataType: {
    type: String,
    enum: ['scan', 'maintenance', 'inspection', 'incident', 'usage'],
    required: true,
  },
  data: {
    type: Map,
    of: mongoose.Schema.Types.Mixed,
  },
  processedByLLM: {
    type: Boolean,
    default: false,
  },
  llmInsights: {
    type: String,
  },
  llmSuggestions: [{
    suggestion: String,
    confidence: Number,
  }],
  source: {
    type: String,
    enum: ['mobile', 'web', 'automated', 'manual'],
    default: 'mobile',
  },
}, {
  timestamps: true,
});

// Index for faster queries
dataRecordSchema.index({ qrId: 1 });
dataRecordSchema.index({ dataType: 1 });
dataRecordSchema.index({ createdAt: -1 });

module.exports = mongoose.model('DataRecord', dataRecordSchema);
