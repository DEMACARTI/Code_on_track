const QRCode = require('qrcode');
const { v4: uuidv4 } = require('uuid');

class QRCodeService {
  /**
   * Generate QR code with data
   * @param {Object} data - Data to encode in QR code
   * @param {Object} options - QR code generation options
   * @returns {Object} - QR code data and image
   */
  async generateQRCode(data, options = {}) {
    try {
      const qrId = uuidv4();
      const qrData = {
        qrId,
        ...data,
        generatedAt: new Date().toISOString(),
      };

      const qrString = JSON.stringify(qrData);

      // Generate QR code with specified options
      const qrCodeOptions = {
        errorCorrectionLevel: options.errorLevel || 'H',
        type: options.type || 'image/png',
        quality: options.quality || 0.92,
        margin: options.margin || 1,
        width: options.width || 300,
        color: {
          dark: options.darkColor || '#000000',
          light: options.lightColor || '#FFFFFF',
        },
      };

      const qrImage = await QRCode.toDataURL(qrString, qrCodeOptions);

      return {
        qrId,
        qrData,
        qrImage,
        qrString,
      };
    } catch (error) {
      throw new Error(`QR code generation failed: ${error.message}`);
    }
  }

  /**
   * Generate QR code for specific material and dimensions
   * @param {Object} specs - Specifications for the QR code
   * @returns {Object} - Optimized QR code for material
   */
  async generateForMaterial(specs) {
    const { materialType, dimensions, data } = specs;

    // Adjust QR code parameters based on material type
    const materialOptions = this.getMaterialOptions(materialType, dimensions);

    return await this.generateQRCode(data, materialOptions);
  }

  /**
   * Generate batch of QR codes
   * @param {Array} dataArray - Array of data objects
   * @param {Object} options - Generation options
   * @returns {Array} - Array of generated QR codes
   */
  async generateBatch(dataArray, options = {}) {
    const qrCodes = [];

    for (const data of dataArray) {
      const qrCode = await this.generateQRCode(data, options);
      qrCodes.push(qrCode);
    }

    return qrCodes;
  }

  /**
   * Validate QR code data
   * @param {string} qrString - QR code string data
   * @returns {Object} - Validation result
   */
  validateQRCode(qrString) {
    try {
      const data = JSON.parse(qrString);
      
      if (!data.qrId) {
        return { valid: false, error: 'Missing QR ID' };
      }

      return { valid: true, data };
    } catch (error) {
      return { valid: false, error: 'Invalid QR code format' };
    }
  }

  /**
   * Get optimal QR code options for material type
   * @private
   */
  getMaterialOptions(materialType, dimensions) {
    const baseOptions = {
      errorLevel: 'H', // High error correction for durability
      margin: 2,
    };

    const materialConfigs = {
      metal: {
        darkColor: '#000000',
        lightColor: '#FFFFFF',
        width: Math.min(dimensions.width * 0.8, 400),
        quality: 0.95,
      },
      plastic: {
        darkColor: '#000000',
        lightColor: '#FFFFFF',
        width: Math.min(dimensions.width * 0.75, 350),
        quality: 0.90,
      },
      wood: {
        darkColor: '#2C1810',
        lightColor: '#F5DEB3',
        width: Math.min(dimensions.width * 0.7, 300),
        quality: 0.88,
      },
      stone: {
        darkColor: '#1A1A1A',
        lightColor: '#E5E5E5',
        width: Math.min(dimensions.width * 0.8, 400),
        quality: 0.95,
      },
      glass: {
        darkColor: '#000080',
        lightColor: '#FFFFFF',
        width: Math.min(dimensions.width * 0.75, 350),
        quality: 0.92,
      },
      other: {
        darkColor: '#000000',
        lightColor: '#FFFFFF',
        width: Math.min(dimensions.width * 0.75, 350),
        quality: 0.90,
      },
    };

    return {
      ...baseOptions,
      ...(materialConfigs[materialType] || materialConfigs.other),
    };
  }

  /**
   * Generate engraving specifications
   * @param {Object} qrCode - QR code object
   * @param {Object} material - Material specifications
   * @returns {Object} - Engraving specifications
   */
  generateEngravingSpecs(qrCode, material) {
    const { materialType, dimensions } = material;

    const specs = {
      qrId: qrCode.qrId,
      materialType,
      dimensions,
      engravingMethod: this.getEngravingMethod(materialType),
      depthRecommendation: this.getEngravingDepth(materialType),
      estimatedTime: this.estimateEngravingTime(dimensions),
      qualityChecks: this.getQualityChecks(materialType),
    };

    return specs;
  }

  /**
   * Get recommended engraving method for material
   * @private
   */
  getEngravingMethod(materialType) {
    const methods = {
      metal: 'laser',
      plastic: 'laser',
      wood: 'cnc',
      stone: 'diamond_tip',
      glass: 'laser',
      other: 'laser',
    };

    return methods[materialType] || 'laser';
  }

  /**
   * Get recommended engraving depth
   * @private
   */
  getEngravingDepth(materialType) {
    const depths = {
      metal: '0.1-0.2mm',
      plastic: '0.05-0.15mm',
      wood: '0.5-1.0mm',
      stone: '0.2-0.5mm',
      glass: '0.05-0.1mm',
      other: '0.1-0.2mm',
    };

    return depths[materialType] || '0.1-0.2mm';
  }

  /**
   * Estimate engraving time
   * @private
   */
  estimateEngravingTime(dimensions) {
    const area = dimensions.width * dimensions.height;
    const baseTime = 5; // minutes
    const timePerUnit = 0.01; // minutes per square mm

    return Math.ceil(baseTime + (area * timePerUnit));
  }

  /**
   * Get quality check requirements
   * @private
   */
  getQualityChecks(materialType) {
    return [
      'Scan readability test',
      'Durability assessment',
      'Contrast verification',
      'Edge clarity check',
      materialType === 'metal' ? 'Corrosion resistance test' : 'Weather resistance test',
    ];
  }
}

module.exports = new QRCodeService();
