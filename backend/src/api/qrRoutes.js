const express = require('express');
const router = express.Router();
const qrCodeService = require('../services/qrCodeService');
const llmService = require('../llm/llmService');
const QRCode = require('../models/QRCode');
const DataRecord = require('../models/DataRecord');

/**
 * @route   POST /api/qr/generate
 * @desc    Generate a new QR code
 * @access  Public
 */
router.post('/generate', async (req, res) => {
  try {
    const { data, materialType, dimensions, location } = req.body;

    // Generate QR code
    const qrCode = await qrCodeService.generateForMaterial({
      materialType,
      dimensions,
      data: { ...data, location },
    });

    // Save to database
    const newQRCode = new QRCode({
      qrId: qrCode.qrId,
      data: qrCode.qrString,
      materialType,
      dimensions,
      location,
    });

    await newQRCode.save();

    // Generate engraving specifications
    const engravingSpecs = qrCodeService.generateEngravingSpecs(qrCode, {
      materialType,
      dimensions,
    });

    res.status(201).json({
      success: true,
      qrCode: {
        ...qrCode,
        engravingSpecs,
      },
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error.message,
    });
  }
});

/**
 * @route   POST /api/qr/batch
 * @desc    Generate multiple QR codes
 * @access  Public
 */
router.post('/batch', async (req, res) => {
  try {
    const { items } = req.body;
    const results = [];

    for (const item of items) {
      const qrCode = await qrCodeService.generateForMaterial(item);
      
      const newQRCode = new QRCode({
        qrId: qrCode.qrId,
        data: qrCode.qrString,
        materialType: item.materialType,
        dimensions: item.dimensions,
        location: item.location,
      });

      await newQRCode.save();
      results.push(qrCode);
    }

    res.status(201).json({
      success: true,
      count: results.length,
      qrCodes: results,
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error.message,
    });
  }
});

/**
 * @route   GET /api/qr/:qrId
 * @desc    Get QR code details
 * @access  Public
 */
router.get('/:qrId', async (req, res) => {
  try {
    const qrCode = await QRCode.findOne({ qrId: req.params.qrId });

    if (!qrCode) {
      return res.status(404).json({
        success: false,
        error: 'QR code not found',
      });
    }

    res.json({
      success: true,
      qrCode,
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error.message,
    });
  }
});

/**
 * @route   POST /api/qr/:qrId/scan
 * @desc    Record a QR code scan
 * @access  Public
 */
router.post('/:qrId/scan', async (req, res) => {
  try {
    const { scannedBy, deviceId } = req.body;
    
    const qrCode = await QRCode.findOne({ qrId: req.params.qrId });

    if (!qrCode) {
      return res.status(404).json({
        success: false,
        error: 'QR code not found',
      });
    }

    // Record scan
    qrCode.scans.push({
      scannedAt: new Date(),
      scannedBy,
      deviceId,
    });

    await qrCode.save();

    // Create data record
    const dataRecord = new DataRecord({
      qrId: req.params.qrId,
      dataType: 'scan',
      data: {
        scannedBy,
        deviceId,
        location: qrCode.location,
      },
      source: 'mobile',
    });

    await dataRecord.save();

    // Process with LLM for insights
    const historicalData = await DataRecord.find({ qrId: req.params.qrId }).limit(50);
    const llmInsights = await llmService.processQRData(qrCode.toObject(), historicalData);

    res.json({
      success: true,
      qrCode,
      insights: llmInsights,
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error.message,
    });
  }
});

/**
 * @route   GET /api/qr
 * @desc    Get all QR codes with filters
 * @access  Public
 */
router.get('/', async (req, res) => {
  try {
    const { status, materialType, station, page = 1, limit = 20 } = req.query;
    
    const filter = {};
    if (status) filter.status = status;
    if (materialType) filter.materialType = materialType;
    if (station) filter['location.station'] = station;

    const qrCodes = await QRCode.find(filter)
      .limit(limit * 1)
      .skip((page - 1) * limit)
      .sort({ createdAt: -1 });

    const count = await QRCode.countDocuments(filter);

    res.json({
      success: true,
      qrCodes,
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
 * @route   PUT /api/qr/:qrId/status
 * @desc    Update QR code status
 * @access  Public
 */
router.put('/:qrId/status', async (req, res) => {
  try {
    const { status } = req.body;
    
    const qrCode = await QRCode.findOneAndUpdate(
      { qrId: req.params.qrId },
      { status },
      { new: true }
    );

    if (!qrCode) {
      return res.status(404).json({
        success: false,
        error: 'QR code not found',
      });
    }

    res.json({
      success: true,
      qrCode,
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error.message,
    });
  }
});

module.exports = router;
