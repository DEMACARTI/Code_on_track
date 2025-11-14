const express = require('express');
const router = express.Router();
const DataRecord = require('../models/DataRecord');
const QRCode = require('../models/QRCode');
const llmService = require('../llm/llmService');

/**
 * @route   POST /api/data/record
 * @desc    Record new data for a QR code
 * @access  Public
 */
router.post('/record', async (req, res) => {
  try {
    const { qrId, dataType, data, source } = req.body;

    const dataRecord = new DataRecord({
      qrId,
      dataType,
      data,
      source: source || 'manual',
    });

    await dataRecord.save();

    res.status(201).json({
      success: true,
      dataRecord,
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error.message,
    });
  }
});

/**
 * @route   GET /api/data/:qrId
 * @desc    Get all data records for a QR code
 * @access  Public
 */
router.get('/:qrId', async (req, res) => {
  try {
    const { dataType, page = 1, limit = 50 } = req.query;
    
    const filter = { qrId: req.params.qrId };
    if (dataType) filter.dataType = dataType;

    const records = await DataRecord.find(filter)
      .limit(limit * 1)
      .skip((page - 1) * limit)
      .sort({ createdAt: -1 });

    const count = await DataRecord.countDocuments(filter);

    res.json({
      success: true,
      records,
      totalPages: Math.ceil(count / limit),
      currentPage: page,
      total: count,
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error.message,
    });
  }
});

/**
 * @route   POST /api/data/:qrId/analyze
 * @desc    Analyze data with LLM and generate insights
 * @access  Public
 */
router.post('/:qrId/analyze', async (req, res) => {
  try {
    const qrCode = await QRCode.findOne({ qrId: req.params.qrId });
    
    if (!qrCode) {
      return res.status(404).json({
        success: false,
        error: 'QR code not found',
      });
    }

    const historicalData = await DataRecord.find({ qrId: req.params.qrId }).limit(100);
    
    const insights = await llmService.processQRData(qrCode.toObject(), historicalData);

    // Update data records with LLM insights
    const analysisRecord = new DataRecord({
      qrId: req.params.qrId,
      dataType: 'usage',
      data: { analysisRequested: true },
      processedByLLM: true,
      llmInsights: JSON.stringify(insights),
      source: 'automated',
    });

    await analysisRecord.save();

    res.json({
      success: true,
      insights,
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error.message,
    });
  }
});

/**
 * @route   GET /api/data/analytics/overview
 * @desc    Get analytics overview
 * @access  Public
 */
router.get('/analytics/overview', async (req, res) => {
  try {
    const totalQRCodes = await QRCode.countDocuments();
    const activeQRCodes = await QRCode.countDocuments({ status: 'active' });
    const totalScans = await DataRecord.countDocuments({ dataType: 'scan' });
    const totalRecords = await DataRecord.countDocuments();

    // Get recent activity
    const recentRecords = await DataRecord.find()
      .sort({ createdAt: -1 })
      .limit(10);

    res.json({
      success: true,
      analytics: {
        totalQRCodes,
        activeQRCodes,
        totalScans,
        totalRecords,
        recentActivity: recentRecords,
      },
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error.message,
    });
  }
});

module.exports = router;
