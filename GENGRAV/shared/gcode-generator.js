// GENGRAV/shared/gcode-generator.js
// Purpose: Generate G-code from QR images for laser engraving
// Uses LaserGRBL-style raster scanning for accurate engraving
// Author: Antigravity

const https = require('https');
const http = require('http');
const path = require('path');
// Load pngjs from engraving-app's node_modules
const { PNG } = require(path.join(__dirname, '../engraving-app/node_modules/pngjs'));
require('dotenv').config({ path: path.join(__dirname, '../engraving-app/.env') });

/**
 * Speed presets (mm/min) - LaserGRBL style
 * Lower speeds = more burn time = darker engraving
 * Higher speeds = less burn time = lighter engraving
 */
const SPEED_PRESETS = {
  'very_slow': 200,   // Maximum burn - for hard materials
  'slow': 400,        // Good for detailing
  'medium': 800,      // Balanced - recommended default
  'fast': 1200,       // Light engraving
  'very_fast': 2000   // Very light, quick preview
};

/**
 * Intensity/Power presets (0-1000 S-value for GRBL)
 */
const INTENSITY_PRESETS = {
  'very_low': 200,    // 20% power - for sensitive materials
  'low': 400,         // 40% power
  'medium': 600,      // 60% power - recommended default
  'high': 800,        // 80% power
  'max': 1000         // 100% power - maximum burn
};

class GCodeGenerator {
  constructor(options = {}) {
    // QR code size in mm (50-150mm range)
    this.size = options.size || parseInt(process.env.ENGRAVE_SIZE_MM) || 50;
    if (this.size < 50) this.size = 50;
    if (this.size > 150) this.size = 150;

    // Work area limits
    this.workAreaX = options.workAreaX || parseInt(process.env.ENGRAVE_WORK_AREA_X) || 150;
    this.workAreaY = options.workAreaY || parseInt(process.env.ENGRAVE_WORK_AREA_Y) || 150;

    // Speed settings (mm/min)
    this.feedRate = options.feedRate || SPEED_PRESETS[options.speedPreset] ||
      parseInt(process.env.GRBL_FEEDRATE) || SPEED_PRESETS.medium;

    // Laser power (0-1000 for GRBL S-value)
    this.laserPower = options.laserPower || INTENSITY_PRESETS[options.intensityPreset] ||
      parseInt(process.env.GRBL_LASER_POWER) || INTENSITY_PRESETS.medium;

    // Quality settings (lines per mm) - LaserGRBL style
    // Higher = more lines = better fill but slower
    // Typical range: 5-20 lines/mm
    this.linesPerMm = options.linesPerMm || 8;  // 8 lines/mm = 0.125mm spacing

    // Use M4 dynamic mode (recommended for engraving)
    this.useDynamicMode = options.useDynamicMode !== false;

    // Rapid move speed for non-engraving moves
    this.rapidSpeed = 3000;  // mm/min

    // Pre-calculate line spacing
    this.lineSpacing = 1 / this.linesPerMm;  // mm between lines
  }

  /**
   * Set speed using preset name
   */
  setSpeedPreset(presetName) {
    if (SPEED_PRESETS[presetName]) {
      this.feedRate = SPEED_PRESETS[presetName];
      return true;
    }
    return false;
  }

  /**
   * Set intensity using preset name
   */
  setIntensityPreset(presetName) {
    if (INTENSITY_PRESETS[presetName]) {
      this.laserPower = INTENSITY_PRESETS[presetName];
      return true;
    }
    return false;
  }

  /**
   * Set custom speed in mm/min
   */
  setSpeed(speedMmMin) {
    this.feedRate = Math.max(50, Math.min(5000, speedMmMin));
  }

  /**
   * Set custom intensity (0-100 percent)
   */
  setIntensity(percent) {
    this.laserPower = Math.round(Math.max(0, Math.min(100, percent)) * 10);
  }

  /**
   * Set lines per mm (quality)
   */
  setQuality(linesPerMm) {
    this.linesPerMm = Math.max(2, Math.min(30, linesPerMm));
    this.lineSpacing = 1 / this.linesPerMm;
  }

  /**
   * Clamp coordinate to work area
   */
  clampCoord(val, max) {
    return Math.max(0, Math.min(val, max));
  }

  formatX(x) {
    return this.clampCoord(x, this.workAreaX).toFixed(3);
  }

  formatY(y) {
    return this.clampCoord(y, this.workAreaY).toFixed(3);
  }

  /**
   * Generate G-code header with GRBL 1.1 settings
   */
  generateHeader() {
    const laserCmd = this.useDynamicMode ? 'M4' : 'M3';
    return [
      '; ============================================',
      '; GENGRAV QR Code Laser Engraving',
      '; LaserGRBL-style Raster Scanning',
      '; ============================================',
      `; Date: ${new Date().toISOString()}`,
      `; QR Size: ${this.size}mm x ${this.size}mm`,
      `; Feed Rate: ${this.feedRate} mm/min`,
      `; Laser Power: S${this.laserPower} (${(this.laserPower / 10).toFixed(0)}%)`,
      `; Quality: ${this.linesPerMm} lines/mm (${this.lineSpacing.toFixed(3)}mm spacing)`,
      `; Laser Mode: ${this.useDynamicMode ? 'M4 Dynamic (recommended)' : 'M3 Constant'}`,
      ';',
      '; GRBL Settings Required:',
      ';   $32=1 (Laser mode enabled)',
      ';   $30=1000 (Max spindle speed = S1000)',
      '; ============================================',
      '',
      'G21 ; Units: millimeters',
      'G90 ; Absolute positioning',
      'G94 ; Feed rate: mm/min',
      'M5 ; Laser OFF',
      `G0 X0 Y0 F${this.rapidSpeed} ; Home position`,
      ''
    ].join('\n');
  }

  /**
   * Generate G-code footer
   */
  generateFooter() {
    return [
      '',
      'M5 ; Laser OFF',
      'G0 X0 Y0 ; Return home',
      '; Engraving complete',
      ''
    ].join('\n');
  }

  /**
   * Generate test square for calibration
   */
  generateTestSquare(size = 10) {
    const laserCmd = this.useDynamicMode ? 'M4' : 'M3';
    return [
      this.generateHeader(),
      `; Test Square: ${size}mm x ${size}mm`,
      `; Use this to verify size accuracy`,
      '',
      'G0 X0 Y0',
      `${laserCmd} S${Math.round(this.laserPower * 0.5)} ; 50% power for test`,
      `G1 X${size} Y0 F${this.feedRate}`,
      `G1 X${size} Y${size}`,
      `G1 X0 Y${size}`,
      'G1 X0 Y0',
      this.generateFooter()
    ].join('\n');
  }

  /**
   * MAIN METHOD: Generate G-code from PNG buffer using LaserGRBL-style raster scanning
   * This produces accurate, evenly-spaced fill lines
   */
  generateFromPNGBuffer(buffer) {
    try {
      const png = PNG.sync.read(buffer);
      const { width, height, data } = png;

      console.log(`PNG: ${width}x${height} pixels`);

      // Convert to binary matrix
      const matrix = [];
      for (let y = 0; y < height; y++) {
        const row = [];
        for (let x = 0; x < width; x++) {
          const idx = (y * width + x) * 4;
          const r = data[idx];
          const g = data[idx + 1];
          const b = data[idx + 2];
          const a = data[idx + 3];

          // Dark pixel = 1 (engrave), Light pixel = 0 (skip)
          const brightness = (r + g + b) / 3;
          row.push((brightness < 128 && a > 128) ? 1 : 0);
        }
        matrix.push(row);
      }

      // Find QR code bounds
      const bounds = this.findBounds(matrix);

      // Extract QR code portion
      const qrMatrix = [];
      for (let y = bounds.minY; y <= bounds.maxY; y++) {
        const row = [];
        for (let x = bounds.minX; x <= bounds.maxX; x++) {
          row.push(matrix[y][x]);
        }
        qrMatrix.push(row);
      }

      // Detect module size and downsample
      const moduleSize = this.detectModuleSize(qrMatrix);
      const moduleMatrix = this.downsample(qrMatrix, moduleSize);

      console.log(`QR: ${moduleMatrix.length}x${moduleMatrix[0]?.length} modules`);

      // Generate G-code using raster scanning
      return this.generateRasterGCode(moduleMatrix);

    } catch (error) {
      console.error('PNG parse error:', error);
      throw error;
    }
  }

  /**
   * LaserGRBL-style raster G-code generation
   * 
   * Key features:
   * - Row-by-row scanning (top to bottom)
   * - Bi-directional (zig-zag) for speed
   * - Continuous laser ON during each row segment
   * - Consistent line spacing based on linesPerMm
   * - M4 dynamic mode for even burns during acceleration
   */
  generateRasterGCode(moduleMatrix) {
    if (!moduleMatrix || moduleMatrix.length === 0) {
      throw new Error('Invalid QR module matrix');
    }

    const rows = moduleMatrix.length;
    const cols = moduleMatrix[0]?.length || 0;
    const moduleMm = this.size / Math.max(rows, cols);  // mm per module

    const commands = [this.generateHeader()];
    const laserCmd = this.useDynamicMode ? 'M4' : 'M3';

    commands.push(`; QR Matrix: ${rows}x${cols} modules`);
    commands.push(`; Module size: ${moduleMm.toFixed(3)}mm`);
    commands.push(`; Line spacing: ${this.lineSpacing.toFixed(3)}mm`);
    commands.push(`; Lines per module: ${Math.ceil(moduleMm / this.lineSpacing)}`);
    commands.push('');

    // Calculate number of scan lines needed
    const totalHeight = rows * moduleMm;
    const numScanLines = Math.ceil(totalHeight / this.lineSpacing);

    commands.push(`; Total scan lines: ${numScanLines}`);
    commands.push('');

    // Raster scan: line by line
    for (let lineIdx = 0; lineIdx < numScanLines; lineIdx++) {
      const y = lineIdx * this.lineSpacing;
      const moduleRow = Math.floor(y / moduleMm);

      if (moduleRow >= rows) break;

      // Determine scan direction (alternate each line for zig-zag)
      const leftToRight = (lineIdx % 2) === 0;

      // Find all segments to engrave on this line
      const segments = this.findEngraveSegments(moduleMatrix[moduleRow], moduleMm, leftToRight);

      if (segments.length === 0) continue;

      const yPos = this.formatY(y);

      // Process each segment
      for (const seg of segments) {
        const xStart = this.formatX(seg.start);
        const xEnd = this.formatX(seg.end);

        // Rapid move to start position
        commands.push(`G0 X${xStart} Y${yPos} F${this.rapidSpeed}`);

        // Laser ON with power
        commands.push(`${laserCmd} S${this.laserPower}`);

        // Engrave the segment at feed rate
        commands.push(`G1 X${xEnd} Y${yPos} F${this.feedRate}`);

        // Laser OFF
        commands.push('M5');
      }
    }

    commands.push(this.generateFooter());
    return commands.join('\n');
  }

  /**
   * Find continuous segments to engrave in a row
   * Returns array of {start, end} in mm
   */
  findEngraveSegments(row, moduleMm, leftToRight) {
    if (!row || row.length === 0) return [];

    const segments = [];
    const cols = row.length;

    // Scan direction
    const startCol = leftToRight ? 0 : cols - 1;
    const endCol = leftToRight ? cols : -1;
    const step = leftToRight ? 1 : -1;

    let inSegment = false;
    let segStart = 0;

    for (let col = startCol; col !== endCol; col += step) {
      const isBlack = row[col] === 1;
      const x = col * moduleMm;

      if (isBlack && !inSegment) {
        // Start new segment
        segStart = leftToRight ? x : x + moduleMm;
        inSegment = true;
      } else if (!isBlack && inSegment) {
        // End segment
        const segEnd = leftToRight ? x : x + moduleMm;
        segments.push({
          start: Math.min(segStart, segEnd),
          end: Math.max(segStart, segEnd)
        });
        inSegment = false;
      }
    }

    // Close final segment if still open
    if (inSegment) {
      const finalX = leftToRight ? cols * moduleMm : 0;
      segments.push({
        start: Math.min(segStart, finalX),
        end: Math.max(segStart, finalX)
      });
    }

    return segments;
  }

  /**
   * Find bounds of QR code in matrix (exclude white border)
   */
  findBounds(matrix) {
    const height = matrix.length;
    const width = matrix[0].length;

    let minX = width, maxX = 0;
    let minY = height, maxY = 0;

    for (let y = 0; y < height; y++) {
      for (let x = 0; x < width; x++) {
        if (matrix[y][x] === 1) {
          minX = Math.min(minX, x);
          maxX = Math.max(maxX, x);
          minY = Math.min(minY, y);
          maxY = Math.max(maxY, y);
        }
      }
    }

    return { minX, maxX, minY, maxY };
  }

  /**
   * Detect QR module size in pixels
   */
  detectModuleSize(matrix) {
    const firstRow = matrix[0] || [];
    let runLength = 0;

    for (let x = 0; x < firstRow.length && firstRow[x] === 1; x++) {
      runLength++;
    }

    // QR finder pattern is 7 modules, so run / 7
    if (runLength >= 7) {
      return Math.max(1, Math.round(runLength / 7));
    }

    // Fallback: estimate from transitions
    let transitions = 0;
    let last = firstRow[0];
    for (let x = 1; x < Math.min(50, firstRow.length); x++) {
      if (firstRow[x] !== last) {
        transitions++;
        last = firstRow[x];
      }
    }

    return transitions > 0 ? Math.max(1, Math.round(50 / (transitions + 1))) : 1;
  }

  /**
   * Downsample pixel matrix to module matrix
   */
  downsample(pixelMatrix, moduleSize) {
    const pixelHeight = pixelMatrix.length;
    const pixelWidth = pixelMatrix[0]?.length || 0;

    const moduleHeight = Math.ceil(pixelHeight / moduleSize);
    const moduleWidth = Math.ceil(pixelWidth / moduleSize);

    const result = [];

    for (let my = 0; my < moduleHeight; my++) {
      const row = [];
      for (let mx = 0; mx < moduleWidth; mx++) {
        // Sample center of module
        const px = Math.min(Math.floor(mx * moduleSize + moduleSize / 2), pixelWidth - 1);
        const py = Math.min(Math.floor(my * moduleSize + moduleSize / 2), pixelHeight - 1);
        row.push(pixelMatrix[py][px]);
      }
      result.push(row);
    }

    return result;
  }

  /**
   * Generate from data URL (base64)
   */
  generateFromDataURL(dataUrl) {
    const matches = dataUrl.match(/^data:([^;,]+)?(?:;base64)?,(.+)$/);
    if (!matches) {
      throw new Error('Invalid data URL');
    }

    const buffer = Buffer.from(matches[2], 'base64');
    return this.generateFromPNGBuffer(buffer);
  }

  /**
   * Generate from URL (HTTP/HTTPS or data URL)
   */
  async generateFromURL(url) {
    if (url.startsWith('data:')) {
      return this.generateFromDataURL(url);
    }

    return new Promise((resolve, reject) => {
      const client = url.startsWith('https') ? https : http;

      client.get(url, (response) => {
        if (response.statusCode !== 200) {
          reject(new Error(`HTTP ${response.statusCode}`));
          return;
        }

        const chunks = [];
        response.on('data', chunk => chunks.push(chunk));
        response.on('end', () => {
          try {
            const buffer = Buffer.concat(chunks);
            const gcode = this.generateFromPNGBuffer(buffer);
            resolve(gcode);
          } catch (error) {
            reject(error);
          }
        });
      }).on('error', reject);
    });
  }

  // Legacy methods for compatibility
  generateFromMatrix(matrix) {
    return this.generateRasterGCode(matrix);
  }

  generateFromModuleMatrix(matrix) {
    return this.generateRasterGCode(matrix);
  }
}

// Export speed and intensity presets for UI
GCodeGenerator.SPEED_PRESETS = SPEED_PRESETS;
GCodeGenerator.INTENSITY_PRESETS = INTENSITY_PRESETS;

module.exports = GCodeGenerator;
