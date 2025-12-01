const { app, BrowserWindow, ipcMain } = require('electron');
const path = require('path');
const GRBLController = require('./grbl-controller');

let mainWindow;
let grblController;

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1200,
    height: 800,
    minWidth: 1000,
    minHeight: 600,
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      nodeIntegration: true,
      contextIsolation: false
    }
  });

  mainWindow.loadFile('index.html');

  mainWindow.on('closed', async () => {
    mainWindow = null;
    if (grblController) {
      await grblController.disconnect();
      await grblController.closeDatabase();
    }
  });
}

// Initialize GRBL controller
app.on('ready', () => {
  createWindow();
  grblController = new GRBLController();
  
  // Set up status update callback
  grblController.onStatusUpdate = (status) => {
    if (mainWindow) {
      mainWindow.webContents.send('status-update', status);
    }
  };
});

// IPC Handlers
ipcMain.handle('list-ports', async () => {
  return await grblController.listPorts();
});

ipcMain.handle('connect', async (event, portPath) => {
  try {
    await grblController.connect(portPath);
    return { success: true };
  } catch (error) {
    return { success: false, error: error.message };
  }
});

ipcMain.handle('disconnect', async () => {
  await grblController.disconnect();
  return { success: true };
});

ipcMain.handle('send-command', async (event, command) => {
  try {
    await grblController.sendCommand(command);
    return { success: true };
  } catch (error) {
    return { success: false, error: error.message };
  }
});

ipcMain.handle('home-machine', async () => {
  try {
    await grblController.homeMachine();
    return { success: true };
  } catch (error) {
    return { success: false, error: error.message };
  }
});

ipcMain.handle('test-engrave', async () => {
  try {
    await grblController.testEngrave();
    return { success: true };
  } catch (error) {
    return { success: false, error: error.message };
  }
});

ipcMain.handle('laser-on', async (event, power) => {
  try {
    await grblController.laserOn(power);
    return { success: true };
  } catch (error) {
    return { success: false, error: error.message };
  }
});

ipcMain.handle('laser-off', async () => {
  try {
    await grblController.laserOff();
    return { success: true };
  } catch (error) {
    return { success: false, error: error.message };
  }
});

ipcMain.handle('get-status', async () => {
  return await grblController.getStatus();
});

ipcMain.handle('reset', async () => {
  try {
    await grblController.reset();
    return { success: true };
  } catch (error) {
    return { success: false, error: error.message };
  }
});

ipcMain.handle('set-time-delay', async (event, delay) => {
  try {
    grblController.setTimeDelay(delay);
    return { success: true };
  } catch (error) {
    return { success: false, error: error.message };
  }
});

ipcMain.handle('start-batch-engraving', async (event, batchId, delay) => {
  try {
    await grblController.startBatchEngraving(batchId, delay);
    return { success: true };
  } catch (error) {
    return { success: false, error: error.message };
  }
});

ipcMain.handle('stop-engraving', async () => {
  try {
    grblController.stopEngraving();
    return { success: true };
  } catch (error) {
    return { success: false, error: error.message };
  }
});

ipcMain.handle('fetch-qr-codes', async (event, batchId) => {
  try {
    const qrCodes = await grblController.fetchQRCodes(batchId);
    return { success: true, qrCodes };
  } catch (error) {
    return { success: false, error: error.message };
  }
});

ipcMain.handle('generate-qr-code', async (event, data, batchId) => {
  try {
    const result = await grblController.generateQRCode(data, batchId);
    return result;
  } catch (error) {
    return { status: 'error', message: error.message };
  }
});

ipcMain.handle('get-pending-jobs', async () => {
  try {
    const jobs = await grblController.getPendingJobs();
    return { success: true, jobs };
  } catch (error) {
    return { success: false, error: error.message };
  }
});

ipcMain.handle('start-engraving-job', async (event, jobId) => {
  try {
    const result = await grblController.startEngravingJob(jobId);
    return result;
  } catch (error) {
    return { success: false, error: error.message };
  }
});

ipcMain.handle('complete-engraving-job', async (event, jobId, success, errorMessage) => {
  try {
    const result = await grblController.completeEngravingJob(jobId, success, errorMessage);
    return result;
  } catch (error) {
    return { success: false, error: error.message };
  }
});

ipcMain.handle('batch-engrave', async (event, batchSize, delay) => {
  try {
    const result = await grblController.batchEngrave(batchSize, delay);
    return result;
  } catch (error) {
    return { success: false, error: error.message };
  }
});

ipcMain.handle('stop-current-job', async () => {
  try {
    const result = await grblController.stopCurrentJob();
    return result;
  } catch (error) {
    return { success: false, error: error.message };
  }
});

ipcMain.handle('get-job-history', async (event, jobId) => {
  try {
    const result = await grblController.getJobHistory(jobId);
    return result;
  } catch (error) {
    return { success: false, error: error.message };
  }
});

ipcMain.handle('get-all-items-with-status', async () => {
  try {
    const result = await grblController.getAllItemsWithStatus();
    return result;
  } catch (error) {
    return { success: false, error: error.message };
  }
});

ipcMain.handle('engrave-single', async (event, qrCodeId) => {
  try {
    const result = await grblController.engraveSingle(qrCodeId);
    return result;
  } catch (error) {
    return { success: false, error: error.message };
  }
});

ipcMain.handle('refresh-queue', async () => {
  try {
    const jobs = await grblController.getPendingJobs();
    return { success: true, jobs };
  } catch (error) {
    return { success: false, error: error.message };
  }
});

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

app.on('activate', () => {
  if (BrowserWindow.getAllWindows().length === 0) {
    createWindow();
  }
});