const express = require('express');
const router = express.Router();
const Notification = require('../models/Notification');
const QRCode = require('../models/QRCode');
const DataRecord = require('../models/DataRecord');
const llmService = require('../llm/llmService');

/**
 * @route   POST /api/notifications/generate
 * @desc    Generate notifications for a QR code using LLM
 * @access  Public
 */
router.post('/generate', async (req, res) => {
  try {
    const { qrId } = req.body;

    const qrCode = await QRCode.findOne({ qrId });
    
    if (!qrCode) {
      return res.status(404).json({
        success: false,
        error: 'QR code not found',
      });
    }

    // Get historical data for context
    const historicalData = await DataRecord.find({ qrId }).limit(50);

    // Generate notifications with LLM
    const context = {
      qrCode: qrCode.toObject(),
      historicalData,
      scanCount: qrCode.scans.length,
      lastScan: qrCode.scans[qrCode.scans.length - 1],
    };

    const generatedNotifications = await llmService.generateNotifications(context);

    // Save notifications to database
    const savedNotifications = [];
    for (const notif of generatedNotifications) {
      const notification = new Notification({
        qrId,
        ...notif,
        llmGenerated: true,
        llmContext: JSON.stringify(context),
      });
      await notification.save();
      savedNotifications.push(notification);
    }

    res.status(201).json({
      success: true,
      notifications: savedNotifications,
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error.message,
    });
  }
});

/**
 * @route   GET /api/notifications
 * @desc    Get all notifications with filters
 * @access  Public
 */
router.get('/', async (req, res) => {
  try {
    const { status, priority, type, qrId, page = 1, limit = 20 } = req.query;
    
    const filter = {};
    if (status) filter.status = status;
    if (priority) filter.priority = priority;
    if (type) filter.type = type;
    if (qrId) filter.qrId = qrId;

    const notifications = await Notification.find(filter)
      .limit(limit * 1)
      .skip((page - 1) * limit)
      .sort({ createdAt: -1 });

    const count = await Notification.countDocuments(filter);

    res.json({
      success: true,
      notifications,
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
 * @route   GET /api/notifications/:id
 * @desc    Get notification by ID
 * @access  Public
 */
router.get('/:id', async (req, res) => {
  try {
    const notification = await Notification.findById(req.params.id);

    if (!notification) {
      return res.status(404).json({
        success: false,
        error: 'Notification not found',
      });
    }

    res.json({
      success: true,
      notification,
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error.message,
    });
  }
});

/**
 * @route   PUT /api/notifications/:id/status
 * @desc    Update notification status
 * @access  Public
 */
router.put('/:id/status', async (req, res) => {
  try {
    const { status, assignedTo } = req.body;
    
    const updateData = { status };
    if (assignedTo) updateData.assignedTo = assignedTo;
    if (status === 'resolved') updateData.resolvedAt = new Date();

    const notification = await Notification.findByIdAndUpdate(
      req.params.id,
      updateData,
      { new: true }
    );

    if (!notification) {
      return res.status(404).json({
        success: false,
        error: 'Notification not found',
      });
    }

    res.json({
      success: true,
      notification,
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error.message,
    });
  }
});

/**
 * @route   POST /api/notifications/maintenance
 * @desc    Generate maintenance recommendations
 * @access  Public
 */
router.post('/maintenance', async (req, res) => {
  try {
    const { qrId } = req.body;

    const qrCode = await QRCode.findOne({ qrId });
    
    if (!qrCode) {
      return res.status(404).json({
        success: false,
        error: 'QR code not found',
      });
    }

    const recommendations = await llmService.generateMaintenanceRecommendations(
      qrCode.toObject(),
      qrCode.scans
    );

    if (recommendations) {
      const notification = new Notification({
        qrId,
        type: 'maintenance',
        priority: recommendations.priority,
        title: 'Maintenance Recommendations',
        message: JSON.stringify(recommendations),
        llmGenerated: true,
      });

      await notification.save();

      res.status(201).json({
        success: true,
        notification,
        recommendations,
      });
    } else {
      res.status(500).json({
        success: false,
        error: 'Failed to generate recommendations',
      });
    }
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error.message,
    });
  }
});

module.exports = router;
