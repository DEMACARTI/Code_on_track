const { SerialPort } = require('serialport');
const { ReadlineParser } = require('@serialport/parser-readline');
const DatabaseClient = require('../shared/db-client');

class GRBLController {
  constructor() {
    this.port = null;
    this.parser = null;
    this.isConnected = false;
    this.commandQueue = [];
    this.isProcessing = false;
    this.currentStatus = 'Idle';
    this.onStatusUpdate = null;
    this.dbClient = new DatabaseClient();
    this.currentJobId = null;
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
      this.processNextCommand();
    } else if (response.startsWith('error:')) {
      console.error('GRBL Error:', response);
      this.updateStatus('Error: ' + response);
    } else if (response.startsWith('<') && response.endsWith('>')) {
      // Status report
      const status = response.slice(1, -1).split('|')[0];
      this.currentStatus = status;
      this.updateStatus(status);
    } else if (response.startsWith('Grbl')) {
      console.log('GRBL Version:', response);
      this.updateStatus('Ready');
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

  // Home the machine
  async homeMachine() {
    this.updateStatus('Homing...');
    await this.sendCommand('$H');
  }

  // Move to position
  async moveTo(x, y, z = 0, feedRate = 1000) {
    const command = `G0 X${x} Y${y} Z${z} F${feedRate}`;
    await this.queueCommand(command);
  }

  // Turn laser on with power (S0-S1000)
  async laserOn(power = 100) {
    await this.sendCommand(`M3 S${power}`);
  }

  // Turn laser off
  async laserOff() {
    await this.sendCommand('M5');
  }

  // Engrave a line
  async engraveLine(x1, y1, x2, y2, power = 100, feedRate = 500) {
    this.updateStatus('Engraving...');
    await this.queueCommand(`G0 X${x1} Y${y1}`); // Move to start
    await this.queueCommand(`M3 S${power}`); // Laser on
    await this.queueCommand(`G1 X${x2} Y${y2} F${feedRate}`); // Engrave line
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
      const jobs = await this.dbClient.getPendingEngravingJobs();
      return jobs;
    } catch (error) {
      console.error('Error fetching pending jobs:', error);
      return [];
    }
  }

  async startEngravingJob(jobId) {
    try {
      this.currentJobId = jobId;
      await this.dbClient.updateEngravingJobStatus(jobId, 'IN_PROGRESS', 'Starting engraving');
      
      const job = await this.dbClient.getEngravingJob(jobId);
      if (!job) {
        throw new Error('Job not found');
      }

      // Here you would load the G-code from the job.svg_url and engrave
      this.updateStatus(`Engraving job ${jobId}...`);
      
      // Simulate engraving process
      // In a real implementation, you would:
      // 1. Download/load the G-code from job.svg_url
      // 2. Send the G-code commands to the machine
      // 3. Monitor progress
      
      return { success: true, job };
    } catch (error) {
      console.error('Error starting engraving job:', error);
      if (this.currentJobId) {
        await this.dbClient.updateEngravingJobStatus(this.currentJobId, 'FAILED', error.message);
        await this.dbClient.incrementJobAttempts(this.currentJobId);
      }
      return { success: false, error: error.message };
    }
  }

  async completeEngravingJob(jobId, success = true, errorMessage = null) {
    try {
      const status = success ? 'COMPLETED' : 'FAILED';
      await this.dbClient.updateEngravingJobStatus(jobId, status, errorMessage);
      
      if (!success) {
        await this.dbClient.incrementJobAttempts(jobId);
      }
      
      this.currentJobId = null;
      this.updateStatus(success ? 'Job completed' : 'Job failed');
      return { success: true };
    } catch (error) {
      console.error('Error completing engraving job:', error);
      return { success: false, error: error.message };
    }
  }

  async batchEngrave(batchSize = 5, delayBetweenJobs = 5000) {
    try {
      const jobs = await this.getPendingJobs();
      const jobsToProcess = jobs.slice(0, batchSize);
      
      this.updateStatus(`Starting batch of ${jobsToProcess.length} jobs`);
      
      for (const job of jobsToProcess) {
        await this.startEngravingJob(job.id);
        
        // Simulate engraving time
        await new Promise(resolve => setTimeout(resolve, 3000));
        
        await this.completeEngravingJob(job.id, true);
        
        // Delay between jobs
        if (delayBetweenJobs > 0) {
          await new Promise(resolve => setTimeout(resolve, delayBetweenJobs));
        }
      }
      
      this.updateStatus('Batch complete');
      return { success: true, processedJobs: jobsToProcess.length };
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
      // Fetch all items in the batch
      const items = await this.dbClient.getItemsByBatch(batchId);
      
      if (!items || items.length === 0) {
        return { success: false, error: 'No items found in batch' };
      }

      this.updateStatus(`Starting batch ${batchId} with ${items.length} items, ${delay}s delay`);
      
      // Process each item in the batch
      for (let i = 0; i < items.length; i++) {
        const item = items[i];
        
        // Create engraving job
        const job = await this.dbClient.createEngravingJob({
          item_uid: item.uid,
          svg_url: item.qr_image_url || ''
        });
        
        // Start engraving
        await this.startEngravingJob(job.id);
        
        // Simulate engraving time
        await new Promise(resolve => setTimeout(resolve, 5000));
        
        // Complete the job
        await this.completeEngravingJob(job.id, true);
        
        // Delay between items (except for the last one)
        if (i < items.length - 1 && delay > 0) {
          this.updateStatus(`Waiting ${delay}s before next item...`);
          await new Promise(resolve => setTimeout(resolve, delay * 1000));
        }
      }
      
      this.updateStatus('Batch engraving complete');
      return { success: true, processedItems: items.length };
    } catch (error) {
      console.error('Error in batch engraving:', error);
      return { success: false, error: error.message };
    }
  }

  async engraveSingle(qrCodeId) {
    try {
      // Find item by QR code
      const item = await this.dbClient.getItemByQRCode(qrCodeId);
      
      if (!item) {
        return { success: false, error: 'QR code not found' };
      }

      this.updateStatus(`Engraving single item: ${qrCodeId}`);
      
      // Create engraving job
      const job = await this.dbClient.createEngravingJob({
        item_uid: item.uid,
        svg_url: item.qr_image_url || ''
      });
      
      // Start engraving
      await this.startEngravingJob(job.id);
      
      // Simulate engraving time
      await new Promise(resolve => setTimeout(resolve, 5000));
      
      // Complete the job
      await this.completeEngravingJob(job.id, true);
      
      this.updateStatus('Single item engraving complete');
      return { success: true, qrCode: qrCodeId };
    } catch (error) {
      console.error('Error in single engraving:', error);
      return { success: false, error: error.message };
    }
  }

  stopEngraving() {
    try {
      // Stop current job
      if (this.currentJobId) {
        this.reset();
        this.completeEngravingJob(this.currentJobId, false, 'Stopped by operator');
        this.updateStatus('Engraving stopped');
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
