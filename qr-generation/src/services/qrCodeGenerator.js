const QRCode = require('qrcode');

class QRCodeGenerator {
  /**
   * Generate QR code
   */
  async generate(specs) {
    const {
      data,
      materialType,
      dimensions,
      location,
      options = {}
    } = specs;

    try {
      const qrData = {
        ...data,
        location,
        materialType,
        generatedAt: new Date().toISOString(),
      };

      const qrString = JSON.stringify(qrData);

      const qrOptions = {
        errorCorrectionLevel: 'H',
        type: 'image/png',
        quality: 0.95,
        margin: 2,
        width: dimensions.width * 0.8,
        ...options,
      };

      const qrImage = await QRCode.toDataURL(qrString, qrOptions);

      return {
        qrData,
        qrImage,
        qrString,
        specs: {
          materialType,
          dimensions,
        },
      };
    } catch (error) {
      throw new Error(`QR generation failed: ${error.message}`);
    }
  }

  /**
   * Generate engraving file
   */
  async generateEngravingFile(qrCode, format = 'gcode') {
    // This would generate machine-specific files
    // G-code for CNC, vector files for laser engraving, etc.
    
    return {
      format,
      content: `; G-code for QR ${qrCode.qrData.qrId}\nG00 X0 Y0\n; Engraving instructions here`,
      filename: `engraving_${qrCode.qrData.qrId}.${format}`,
    };
  }
}

module.exports = new QRCodeGenerator();
