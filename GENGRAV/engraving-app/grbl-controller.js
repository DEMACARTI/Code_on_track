const { SerialPort } = require('serialport');
const { ReadlineParser } = require('@serialport/parser-readline');
const DatabaseClient = require('../shared/db-client');
const GCodeGenerator = require('../shared/gcode-generator');
const path = require('path');
require('dotenv').config({ path: path.join(__dirname, '.env') });

class GRBLController {
  constructor() {
    this.port = null;
    this.parser = null;
    this.isConnected = false;
    this.commandQueue = [];
    this.isProcessing = false;
    this.currentStatus = 'Idle';
    this.onStatusUpdate = null;
    
    // Position tracking (home is always origin 0,0,0)
    this.homePosition = { x: 0, y: 0, z: 0 };
    this.currentPosition = { x: 0, y: 0, z: 0 };
    
    // Initialize database client with error handling
    try {
      this.dbClient = new DatabaseClient();
    } catch (err) {
      console.error('Database client init failed:', err.message);
      this.dbClient = null;
    }
    
    this.gcodeGenerator = new GCodeGenerator();
    this.currentJobId = null;
    this.isEngraving = false;
    this.stopRequested = false;
    
    // Command response tracking
    this.pendingCommands = [];
    this.commandResolvers = new Map();
  }

  // Find available Arduino ports
  async listPorts() {
    try {
      const ports = await SerialPort.list();
      return ports.filter(port => 
        port.manufacturer?.toLowerCase().includes('arduino') ||
        port.path.includes('usbserial') ||
        port.path.includes('usbmodem') ||
        port.path.includes('ttyUSB') ||
        port.path.includes('ttyACM')
      );
    } catch (error) {
      console.error('Error listing ports:', error);
      return [];
    }
  }

  // Connect to Arduino with GRBL
  async connect(portPath) {
    return new Promise((resolve, reject) => {
      try {
        this.port = new SerialPort({
          path: portPath,
          baudRate: 115200,
          dataBits: 8,
          parity: 'none',
          stopBits: 1,
          flowControl: false
        });

        this.parser = this.port.pipe(new ReadlineParser({ delimiter: '\r\n' }));

        this.port.on('open', () => {
          console.log('Serial port opened');
          this.isConnected = true;
          
          // Wait for GRBL initialization
          setTimeout(() => {
            this.sendCommand('\r\n\r\n'); // Wake up GRBL
            setTimeout(() => {
              this.sendCommand('$X'); // Unlock GRBL
              this.updateStatus('Connected');
              resolve(true);
            }, 1000);
          }, 2000);
        });

        this.parser.on('data', (data) => {
          console.log('GRBL Response:', data);
          this.handleResponse(data);
        });

        this.port.on('error', (err) => {
          console.error('Serial port error:', err);
          this.isConnected = false;
          reject(err);
        });

        this.port.on('close', () => {
          console.log('Serial port closed');
          this.isConnected = false;
          this.updateStatus('Disconnected');
        });

      } catch (error) {
        reject(error);
      }
    });
  }

  // Disconnect from Arduino
  async disconnect() {
    if (this.port && this.port.isOpen) {
      return new Promise((resolve) => {
        this.port.close(() => {
          this.isConnected = false;
          this.updateStatus('Disconnected');
          resolve();
        });
      });
    }
  }

  // Send G-code command
  sendCommand(command) {
    if (!this.isConnected || !this.port) {
      console.error('Not connected to device');
      return false;
    }

    return new Promise((resolve, reject) => {
      this.port.write(command + '\n', (err) => {
        if (err) {
          console.error('Error writing to port:', err);
          reject(err);
        } else {
          console.log('Command sent:', command);
          resolve(true);
        }
      });
    });
  }

  // Handle GRBL responses
  handleResponse(data) {
    const response = data.trim();
    
    if (response === 'ok') {
      console.log('Command acknowledged');
      
      // Resolve pending command
      if (this.pendingCommands.length > 0) {
        const commandId = this.pendingCommands.shift();
        const resolver = this.commandResolvers.get(commandId);
        if (resolver) {
          clearTimeout(resolver.timeoutId);
          this.commandResolvers.delete(commandId);
          resolver.resolve(true);
        }
      }
      
      this.processNextCommand();
    } else if (response.startsWith('error:')) {
      console.error('GRBL Error:', response);
      this.updateStatus('Error: ' + response);
      
      // Reject pending command
      if (this.pendingCommands.length > 0) {
        const commandId = this.pendingCommands.shift();
        const resolver = this.commandResolvers.get(commandId);
        if (resolver) {
          clearTimeout(resolver.timeoutId);
          this.commandResolvers.delete(commandId);
          resolver.reject(new Error(response));
        }
      }
    } else if (response.startsWith('<') && response.endsWith('>')) {
      // Status report
      const status = response.slice(1, -1).split('|')[0];
      this.currentStatus = status;
      this.updateStatus(status);
    } else if (response.startsWith('Grbl')) {
      console.log('GRBL Version:', response);
      this.updateStatus('Ready');
    } else if (response.startsWith('ALARM:')) {
      console.error('GRBL Alarm:', response);
      this.updateStatus('ALARM: ' + response);
    }
  }

  // Queue and process commands
  async queueCommand(command) {
    this.commandQueue.push(command);
    if (!this.isProcessing) {
      this.processNextCommand();
    }
  }

  async processNextCommand() {
    if (this.commandQueue.length === 0) {
      this.isProcessing = false;
      return;
    }

    this.isProcessing = true;
    const command = this.commandQueue.shift();
    await this.sendCommand(command);
  }

  // Set current position as home (0,0,0)
  // This sets the current position as the origin without moving the machine
  async homeMachine() {
    this.updateStatus('Setting home position...');
    // G92 sets the current position as the specified coordinates
    // This makes wherever the machine currently is become (0,0,0)
    await this.sendCommand('G92 X0 Y0 Z0');
    this.homePosition = { x: 0, y: 0, z: 0 };
    this.currentPosition = { x: 0, y: 0, z: 0 };
    this.updateStatus('Home position set');
    console.log('Home position set at current location');
  }

  // Go to home position (0,0,0)
  async goToHome() {
    this.updateStatus('Moving to home...');
    await this.sendCommand('G0 X0 Y0 Z0');
    this.currentPosition = { x: 0, y: 0, z: 0 };
    this.updateStatus('At home position');
  }

  // Clamp coordinates to prevent negative values (stay within work area)
  clampCoordinates(x, y, z = 0) {
    const workAreaX = parseInt(process.env.ENGRAVE_WORK_AREA_X) || 150;
    const workAreaY = parseInt(process.env.ENGRAVE_WORK_AREA_Y) || 150;
    
    return {
      x: Math.max(0, Math.min(x, workAreaX)),
      y: Math.max(0, Math.min(y, workAreaY)),
      z: Math.max(0, z)  // Z should not go negative either
    };
  }

  // Move to position (with coordinate clamping)
  async moveTo(x, y, z = 0, feedRate = 1000) {
    const clamped = this.clampCoordinates(x, y, z);
    const command = `G0 X${clamped.x} Y${clamped.y} Z${clamped.z} F${feedRate}`;
    await this.queueCommand(command);
    this.currentPosition = clamped;
  }

  // Turn laser on with power (S0-S1000)
  async laserOn(power = 100) {
    await this.sendCommand(`M3 S${power}`);
  }

  // Turn laser off
  async laserOff() {
    await this.sendCommand('M5');
  }

  // Engrave a line (with coordinate clamping)
  async engraveLine(x1, y1, x2, y2, power = 100, feedRate = 500) {
    const start = this.clampCoordinates(x1, y1);
    const end = this.clampCoordinates(x2, y2);
    
    this.updateStatus('Engraving...');
    await this.queueCommand(`G0 X${start.x} Y${start.y}`); // Move to start
    await this.queueCommand(`M3 S${power}`); // Laser on
    await this.queueCommand(`G1 X${end.x} Y${end.y} F${feedRate}`); // Engrave line
    await this.queueCommand('M5'); // Laser off
  }

  // Engrave QR code pattern
  async engraveQRCode(qrData, size = 30, power = 100) {
    this.updateStatus('Engraving QR Code...');
    
    // Simple QR code engraving - engrave black modules
    const moduleSize = size / qrData.length;
    
    for (let row = 0; row < qrData.length; row++) {
      for (let col = 0; col < qrData[row].length; col++) {
        if (qrData[row][col] === 1) { // Black module
          const x = col * moduleSize;
          const y = row * moduleSize;
          
          // Engrave a filled square
          await this.queueCommand(`G0 X${x} Y${y}`);
          await this.queueCommand(`M3 S${power}`);
          await this.queueCommand(`G1 X${x + moduleSize} Y${y} F500`);
          await this.queueCommand(`G1 X${x + moduleSize} Y${y + moduleSize}`);
          await this.queueCommand(`G1 X${x} Y${y + moduleSize}`);
          await this.queueCommand(`G1 X${x} Y${y}`);
          await this.queueCommand('M5');
        }
      }
    }
    
    this.updateStatus('Engraving Complete');
  }

  // Test engraving - simple square
  async testEngrave() {
    this.updateStatus('Test Engraving...');
    
    // Engrave a 10mm x 10mm square
    await this.queueCommand('G0 X0 Y0'); // Move to origin
    await this.queueCommand('M3 S100'); // Laser on at 10% power
    await this.queueCommand('G1 X10 Y0 F500'); // Line 1
    await this.queueCommand('G1 X10 Y10 F500'); // Line 2
    await this.queueCommand('G1 X0 Y10 F500'); // Line 3
    await this.queueCommand('G1 X0 Y0 F500'); // Line 4
    await this.queueCommand('M5'); // Laser off
    await this.queueCommand('G0 X0 Y0'); // Return to origin
    
    this.updateStatus('Test Complete');
  }

  // Get current status
  async getStatus() {
    if (this.isConnected) {
      await this.sendCommand('?');
    }
    return this.currentStatus;
  }

  // Reset GRBL
  async reset() {
    await this.sendCommand('\x18'); // Ctrl-X soft reset
    this.updateStatus('Reset');
  }

  // Update status callback
  updateStatus(status) {
    this.currentStatus = status;
    if (this.onStatusUpdate) {
      this.onStatusUpdate(status);
    }
  }

  // Database integration methods
  async getPendingJobs() {
    try {
      if (!this.dbClient) {
        console.log('Database not connected, skipping pending jobs fetch');
        return [];
      }
      const jobs = await this.dbClient.getPendingEngravingJobs();
      return jobs;
    } catch (error) {
      console.error('Error fetching pending jobs:', error);
      return [];
    }
  }

  async startEngravingJob(jobId) {
    try {
      if (!this.isConnected) {
        throw new Error('Machine not connected');
      }

      this.currentJobId = jobId;
      this.isEngraving = true;
      this.stopRequested = false;
      
      await this.dbClient.updateEngravingJobStatus(jobId, 'IN_PROGRESS', 'Starting engraving');
      
      const job = await this.dbClient.getEngravingJob(jobId);
      if (!job) {
        throw new Error('Job not found');
      }

      this.updateStatus(`Engraving job ${jobId}...`);
      
      // Get the item to find the QR image URL
      const item = await this.dbClient.getItemByUid(job.item_uid);
      const qrImageUrl = job.svg_url || (item && item.qr_image_url);
      
      if (qrImageUrl) {
        // Download and convert SVG to G-code
        this.updateStatus('Generating G-code from QR image...');
        try {
          const gcode = await this.gcodeGenerator.generateFromURL(qrImageUrl);
          
          // Execute the G-code
          this.updateStatus('Executing G-code...');
          await this.executeGCode(gcode);
          
          // Mark as completed
          await this.completeEngravingJob(jobId, true);
        } catch (gcodeError) {
          // Fall back to test pattern if G-code generation fails
          console.warn('G-code generation failed, using test pattern:', gcodeError.message);
          this.updateStatus('Using test pattern (SVG parse failed)...');
          
          const testGcode = this.gcodeGenerator.generateTestSquare(20);
          await this.executeGCode(testGcode);
          
          await this.completeEngravingJob(jobId, true, 'Completed with test pattern');
        }
      } else {
        // No QR image URL - use test pattern
        this.updateStatus('No QR image URL - using test pattern');
        const testGcode = this.gcodeGenerator.generateTestSquare(20);
        await this.executeGCode(testGcode);
        
        await this.completeEngravingJob(jobId, true, 'Completed with test pattern (no SVG URL)');
      }
      
      return { success: true, job };
    } catch (error) {
      console.error('Error starting engraving job:', error);
      this.isEngraving = false;
      
      if (this.currentJobId) {
        await this.dbClient.updateEngravingJobStatus(this.currentJobId, 'FAILED', error.message);
        await this.dbClient.incrementJobAttempts(this.currentJobId);
      }
      return { success: false, error: error.message };
    }
  }

  /**
   * Execute G-code commands sequentially
   */
  async executeGCode(gcode) {
    const lines = gcode.split('\n')
      .map(line => line.trim())
      .filter(line => line && !line.startsWith(';'));  // Remove empty lines and comments

    this.updateStatus(`Executing ${lines.length} G-code commands...`);

    for (let i = 0; i < lines.length; i++) {
      if (this.stopRequested) {
        this.updateStatus('Engraving stopped by user');
        throw new Error('Engraving stopped by user');
      }

      const line = lines[i];
      await this.sendCommandAndWait(line);
      
      // Update progress every 10 commands
      if (i % 10 === 0) {
        const progress = Math.round((i / lines.length) * 100);
        this.updateStatus(`Engraving: ${progress}% (${i}/${lines.length})`);
      }
    }

    this.updateStatus('G-code execution complete');
  }

  /**
   * Send command and wait for 'ok' response
   */
  async sendCommandAndWait(command, timeout = 10000) {
    return new Promise((resolve, reject) => {
      const timeoutId = setTimeout(() => {
        reject(new Error(`Command timeout: ${command}`));
      }, timeout);

      // Store the resolver to be called when 'ok' is received
      const commandId = Date.now() + Math.random();
      this.commandResolvers.set(commandId, { resolve, reject, timeoutId, command });
      this.pendingCommands.push(commandId);

      this.port.write(command + '\n', (err) => {
        if (err) {
          clearTimeout(timeoutId);
          this.commandResolvers.delete(commandId);
          reject(err);
        }
      });
    });
  }

  async completeEngravingJob(jobId, success = true, errorMessage = null) {
    try {
      const status = success ? 'COMPLETED' : 'FAILED';
      const job = await this.dbClient.getEngravingJob(jobId);
      
      await this.dbClient.updateEngravingJobStatus(jobId, status, errorMessage);
      
      if (!success) {
        await this.dbClient.incrementJobAttempts(jobId);
      } else if (job && job.item_uid) {
        // Update item status to 'engraved' on success
        await this.dbClient.updateItemStatus(job.item_uid, 'engraved');
      }
      
      this.currentJobId = null;
      this.isEngraving = false;
      this.updateStatus(success ? 'Job completed' : 'Job failed');
      return { success: true };
    } catch (error) {
      console.error('Error completing engraving job:', error);
      return { success: false, error: error.message };
    }
  }

  async batchEngrave(batchSize = 5, delayBetweenJobs = 5000) {
    try {
      if (!this.isConnected) {
        throw new Error('Machine not connected');
      }

      const jobs = await this.getPendingJobs();
      const jobsToProcess = jobs.slice(0, batchSize);
      
      if (jobsToProcess.length === 0) {
        this.updateStatus('No pending jobs in queue');
        return { success: true, processedJobs: 0, message: 'No pending jobs' };
      }
      
      this.updateStatus(`Starting batch of ${jobsToProcess.length} jobs`);
      this.stopRequested = false;
      
      let successCount = 0;
      let failCount = 0;
      
      for (let i = 0; i < jobsToProcess.length; i++) {
        if (this.stopRequested) {
          this.updateStatus('Batch stopped by user');
          break;
        }
        
        const job = jobsToProcess[i];
        this.updateStatus(`Processing job ${i + 1}/${jobsToProcess.length} (ID: ${job.id})`);
        
        const result = await this.startEngravingJob(job.id);
        
        if (result.success) {
          successCount++;
        } else {
          failCount++;
        }
        
        // Delay between jobs (except for the last one)
        if (i < jobsToProcess.length - 1 && delayBetweenJobs > 0 && !this.stopRequested) {
          this.updateStatus(`Waiting ${delayBetweenJobs / 1000}s before next job...`);
          await new Promise(resolve => setTimeout(resolve, delayBetweenJobs));
        }
      }
      
      this.updateStatus(`Batch complete: ${successCount} success, ${failCount} failed`);
      return { success: true, processedJobs: successCount, failedJobs: failCount };
    } catch (error) {
      console.error('Error in batch engraving:', error);
      return { success: false, error: error.message };
    }
  }

  async stopCurrentJob() {
    if (this.currentJobId) {
      await this.reset();
      await this.completeEngravingJob(this.currentJobId, false, 'Job stopped by user');
      return { success: true, message: 'Job stopped' };
    }
    return { success: false, message: 'No active job' };
  }

  async getJobHistory(jobId) {
    try {
      const history = await this.dbClient.getEngravingHistory(jobId);
      return { success: true, history };
    } catch (error) {
      console.error('Error fetching job history:', error);
      return { success: false, error: error.message };
    }
  }

  async getAllItemsWithStatus() {
    try {
      const items = await this.dbClient.getItemsWithEngravingStatus();
      return { success: true, items };
    } catch (error) {
      console.error('Error fetching items:', error);
      return { success: false, error: error.message };
    }
  }

  async closeDatabase() {
    if (this.dbClient) {
      await this.dbClient.close();
    }
  }

  // Additional methods for engraving workflow
  async startBatchEngraving(batchId, delay) {
    try {
      if (!this.isConnected) {
        throw new Error('Machine not connected');
      }

      // Fetch all items in the batch (by lot_number)
      const items = await this.dbClient.getItemsByLotNumber(batchId.toString());
      
      if (!items || items.length === 0) {
        return { success: false, error: `No items found with lot number: ${batchId}` };
      }

      this.updateStatus(`Starting batch ${batchId} with ${items.length} items, ${delay}s delay`);
      this.stopRequested = false;
      
      let successCount = 0;
      let failCount = 0;
      
      // Process each item in the batch
      for (let i = 0; i < items.length; i++) {
        if (this.stopRequested) {
          this.updateStatus('Batch stopped by user');
          break;
        }
        
        const item = items[i];
        this.updateStatus(`Engraving item ${i + 1}/${items.length}: ${item.uid}`);
        
        // Create engraving job if not exists
        let job = await this.dbClient.getEngravingJobByItemUid(item.uid);
        
        if (!job) {
          job = await this.dbClient.createEngravingJob({
            item_uid: item.uid,
            svg_url: item.qr_image_url || ''
          });
        }
        
        // Start engraving
        const result = await this.startEngravingJob(job.id);
        
        if (result.success) {
          successCount++;
        } else {
          failCount++;
        }
        
        // Delay between items (except for the last one)
        if (i < items.length - 1 && delay > 0 && !this.stopRequested) {
          this.updateStatus(`Waiting ${delay}s before next item...`);
          await new Promise(resolve => setTimeout(resolve, delay * 1000));
        }
      }
      
      this.updateStatus(`Batch ${batchId} complete: ${successCount} success, ${failCount} failed`);
      return { success: true, processedItems: successCount, failedItems: failCount };
    } catch (error) {
      console.error('Error in batch engraving:', error);
      return { success: false, error: error.message };
    }
  }

  async engraveSingle(qrCodeId) {
    try {
      if (!this.isConnected) {
        throw new Error('Machine not connected');
      }

      // Find item by UID
      const item = await this.dbClient.getItemByQRCode(qrCodeId);
      
      if (!item) {
        return { success: false, error: `Item not found with UID: ${qrCodeId}` };
      }

      this.updateStatus(`Engraving single item: ${qrCodeId}`);
      
      // Check if engraving job already exists
      let job = await this.dbClient.getEngravingJobByItemUid(item.uid);
      
      if (!job) {
        // Create new engraving job
        job = await this.dbClient.createEngravingJob({
          item_uid: item.uid,
          svg_url: item.qr_image_url || ''
        });
      } else if (job.status === 'completed') {
        // Re-engraving - create a new job
        job = await this.dbClient.createEngravingJob({
          item_uid: item.uid,
          svg_url: item.qr_image_url || ''
        });
      }
      
      // Start engraving
      const result = await this.startEngravingJob(job.id);
      
      if (result.success) {
        this.updateStatus('Single item engraving complete');
        return { success: true, qrCode: qrCodeId, jobId: job.id };
      } else {
        return { success: false, error: result.error };
      }
    } catch (error) {
      console.error('Error in single engraving:', error);
      return { success: false, error: error.message };
    }
  }

  stopEngraving() {
    try {
      this.stopRequested = true;
      
      // Stop current job
      if (this.currentJobId) {
        this.reset();
        this.completeEngravingJob(this.currentJobId, false, 'Stopped by operator');
        this.updateStatus('Engraving stopped');
        this.isEngraving = false;
        return { success: true };
      }
      return { success: false, error: 'No active engraving job' };
    } catch (error) {
      console.error('Error stopping engraving:', error);
      return { success: false, error: error.message };
    }
  }

  setTimeDelay(delay) {
    this.timeDelay = delay;
    console.log(`Time delay set to ${delay}ms`);
  }

  async fetchQRCodes(batchId) {
    try {
      if (batchId) {
        const items = await this.dbClient.getItemsByBatch(batchId);
        return items;
      } else {
        const items = await this.dbClient.getAllItems();
        return items;
      }
    } catch (error) {
      console.error('Error fetching QR codes:', error);
      return [];
    }
  }

  async generateQRCode(data, batchId) {
    try {
      // This method would interface with the generation app or database
      // For now, we'll just create a database entry
      const item = await this.dbClient.createItem({
        qr_code: data,
        batch_id: batchId || null,
        status: 'PENDING'
      });
      
      return {
        status: 'success',
        qr_code: item.qr_code,
        message: 'QR code generated and saved to database'
      };
    } catch (error) {
      console.error('Error generating QR code:', error);
      return {
        status: 'error',
        message: error.message
      };
    }
  }
}

module.exports = GRBLController;
