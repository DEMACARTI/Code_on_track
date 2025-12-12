/**
 * GENGRAV Main Process - GRBL 1.1 Controller
 * With Direct Supabase Database Connection
 */
const { app, BrowserWindow, ipcMain, dialog } = require('electron');
const path = require('node:path');
const { GRBLController, GRBL_SETTINGS, LASER_DEFAULTS, BAUD_RATES, CONNECTION_OPTIONS, REALTIME_COMMANDS, GRBL_VERSION } = require('./grbl-controller');
const db = require('./database');
const QRCode = require('qrcode');

if (require('electron-squirrel-startup')) app.quit();

const grbl = new GRBLController();
let mainWindow = null;
let dbConnected = false;

const createWindow = () => {
  mainWindow = new BrowserWindow({
    width: 1400, height: 900, minWidth: 1200, minHeight: 700,
    webPreferences: { preload: MAIN_WINDOW_PRELOAD_WEBPACK_ENTRY, nodeIntegration: false, contextIsolation: true },
    backgroundColor: '#0a0a0f', title: 'GENGRAV Laser Engraver (GRBL 1.1)'
  });
  mainWindow.loadURL(MAIN_WINDOW_WEBPACK_ENTRY);

  // GRBL event forwarding
  grbl.on('status', (s) => mainWindow?.webContents.send('grbl:status', s));
  grbl.on('log', (m) => mainWindow?.webContents.send('grbl:log', m));
  grbl.on('tx', (c) => mainWindow?.webContents.send('grbl:tx', c));
  grbl.on('rx', (l) => mainWindow?.webContents.send('grbl:rx', l));
  grbl.on('progress', (p) => mainWindow?.webContents.send('grbl:progress', p));
  grbl.on('settings', (s) => mainWindow?.webContents.send('grbl:settings', s));
  grbl.on('error', (e) => mainWindow?.webContents.send('grbl:error', e.toString()));
  grbl.on('estop', () => mainWindow?.webContents.send('grbl:estop'));
  grbl.on('complete', () => mainWindow?.webContents.send('grbl:complete'));
  grbl.on('version', (v) => mainWindow?.webContents.send('grbl:version', v));
  grbl.on('alarm', (a) => mainWindow?.webContents.send('grbl:alarm', a));
  grbl.on('message', (m) => mainWindow?.webContents.send('grbl:message', m));

  // Send database connection status to renderer
  mainWindow.webContents.on('did-finish-load', () => {
    mainWindow.webContents.send('db:status', { connected: dbConnected });
  });

  if (process.env.NODE_ENV === 'development') mainWindow.webContents.openDevTools();
};

// Test database connection before starting the app
async function initializeApp() {
  console.log('🚀 GENGRAV Starting...');
  console.log('📡 Testing database connection...');

  const dbResult = await db.testConnection();

  if (dbResult.success) {
    console.log('✅ Database connection successful!');
    dbConnected = true;
  } else {
    console.error('❌ Database connection failed:', dbResult.error);
    dbConnected = false;

    // Show error dialog but continue anyway
    dialog.showMessageBox({
      type: 'warning',
      title: 'Database Connection Failed',
      message: 'Could not connect to the database.',
      detail: `Error: ${dbResult.error}\n\nThe app will continue but QR code fetching may not work.`,
      buttons: ['Continue Anyway', 'Quit'],
    }).then(({ response }) => {
      if (response === 1) {
        app.quit();
      }
    });
  }

  createWindow();
}

app.whenReady().then(initializeApp);
app.on('activate', () => { if (BrowserWindow.getAllWindows().length === 0) createWindow(); });
app.on('window-all-closed', () => {
  grbl.disconnect();
  db.closePool();
  if (process.platform !== 'darwin') app.quit();
});

// ========== Core IPC Handlers ==========
ipcMain.handle('grbl:listPorts', () => grbl.listPorts());
ipcMain.handle('grbl:listAllPorts', () => grbl.listAllPorts());
ipcMain.handle('grbl:connect', (_, { port, baudRate, options }) => {
  return grbl.connect(port, { baudRate, ...options })
    .then(() => ({ success: true, state: grbl.getState() }))
    .catch(e => ({ success: false, error: e.message }));
});
ipcMain.handle('grbl:disconnect', () => { grbl.disconnect(); return { success: true }; });
ipcMain.handle('grbl:getState', () => grbl.getState());
ipcMain.handle('grbl:getBaudRates', () => BAUD_RATES);
ipcMain.handle('grbl:getConnectionOptions', () => CONNECTION_OPTIONS);
ipcMain.handle('grbl:getGrblVersion', () => GRBL_VERSION);

// ========== Settings IPC Handlers ==========
ipcMain.handle('grbl:readSettings', () => grbl.readSettings().then(s => ({ success: true, settings: s })).catch(e => ({ success: false, error: e.message })));
ipcMain.handle('grbl:writeSetting', (_, { key, value }) => grbl.writeSetting(key, value).then(() => ({ success: true })).catch(e => ({ success: false, error: e.message })));
ipcMain.handle('grbl:applyDefaults', () => grbl.applyDefaults().then(() => ({ success: true })).catch(e => ({ success: false, error: e.message })));
ipcMain.handle('grbl:enableLaserMode', () => grbl.enableLaserMode().then(() => ({ success: true })).catch(e => ({ success: false, error: e.message })));
ipcMain.handle('grbl:getDefaults', () => ({ settings: GRBL_SETTINGS, defaults: LASER_DEFAULTS }));

// ========== Motion IPC Handlers ==========
ipcMain.handle('grbl:home', () => grbl.home().then(() => ({ success: true })).catch(e => ({ success: false, error: e.message })));
ipcMain.handle('grbl:homeAll', () => grbl.homeAll().then(() => ({ success: true })).catch(e => ({ success: false, error: e.message })));
ipcMain.handle('grbl:goHome', () => grbl.goHome().then(() => ({ success: true })).catch(e => ({ success: false, error: e.message })));
ipcMain.handle('grbl:jog', (_, { axis, distance, feed }) => grbl.jog(axis, distance, feed || 500).then(() => ({ success: true })).catch(e => ({ success: false, error: e.message })));
ipcMain.handle('grbl:jogCancel', () => { grbl.jogCancel(); return { success: true }; });
ipcMain.handle('grbl:moveTo', (_, { x, y, feed }) => grbl.moveTo(x, y, feed || 1000).then(() => ({ success: true })).catch(e => ({ success: false, error: e.message })));
ipcMain.handle('grbl:send', (_, c) => grbl.send(c).then(() => ({ success: true })).catch(e => ({ success: false, error: e.message })));

// ========== Laser IPC Handlers ==========
ipcMain.handle('grbl:laserOn', (_, p) => grbl.laserOn(p).then(() => ({ success: true })).catch(e => ({ success: false, error: e.message })));
ipcMain.handle('grbl:laserOff', () => grbl.laserOff().then(() => ({ success: true })).catch(e => ({ success: false, error: e.message })));
ipcMain.handle('grbl:laserTest', (_, { power, duration }) => grbl.laserTest(power, duration).then(() => ({ success: true })).catch(e => ({ success: false, error: e.message })));
ipcMain.handle('grbl:laserFocus', (_, p) => grbl.laserFocus(p).then(() => ({ success: true })).catch(e => ({ success: false, error: e.message })));

// ========== Control IPC Handlers ==========
ipcMain.handle('grbl:emergencyStop', () => grbl.doEmergencyStop().then(() => ({ success: true })).catch(e => ({ success: false, error: e.message })));
ipcMain.handle('grbl:resetEstop', () => grbl.resetEstop().then(() => ({ success: true })).catch(e => ({ success: false, error: e.message })));
ipcMain.handle('grbl:unlock', () => grbl.unlock().then(() => ({ success: true })).catch(e => ({ success: false, error: e.message })));
ipcMain.handle('grbl:runGCode', (_, g) => grbl.runGCode(g).then(() => ({ success: true })).catch(e => ({ success: false, error: e.message })));
ipcMain.handle('grbl:stop', () => { grbl.stop(); return { success: true }; });

// ========== GRBL 1.1 Real-time Commands ==========
ipcMain.handle('grbl:softReset', () => { grbl.softReset(); return { success: true }; });
ipcMain.handle('grbl:feedHold', () => { grbl.feedHold(); return { success: true }; });
ipcMain.handle('grbl:cycleStart', () => { grbl.cycleStart(); return { success: true }; });
ipcMain.handle('grbl:safetyDoor', () => { grbl.safetyDoor(); return { success: true }; });

// ========== GRBL 1.1 Override Commands ==========
ipcMain.handle('grbl:feedOverrideReset', () => { grbl.feedOverrideReset(); return { success: true }; });
ipcMain.handle('grbl:feedOverrideIncrease', (_, fine) => { grbl.feedOverrideIncrease(fine); return { success: true }; });
ipcMain.handle('grbl:feedOverrideDecrease', (_, fine) => { grbl.feedOverrideDecrease(fine); return { success: true }; });
ipcMain.handle('grbl:rapidOverrideReset', () => { grbl.rapidOverrideReset(); return { success: true }; });
ipcMain.handle('grbl:rapidOverride50', () => { grbl.rapidOverride50(); return { success: true }; });
ipcMain.handle('grbl:rapidOverride25', () => { grbl.rapidOverride25(); return { success: true }; });
ipcMain.handle('grbl:spindleOverrideReset', () => { grbl.spindleOverrideReset(); return { success: true }; });
ipcMain.handle('grbl:spindleOverrideIncrease', (_, fine) => { grbl.spindleOverrideIncrease(fine); return { success: true }; });
ipcMain.handle('grbl:spindleOverrideDecrease', (_, fine) => { grbl.spindleOverrideDecrease(fine); return { success: true }; });
ipcMain.handle('grbl:spindleStop', () => { grbl.spindleStop(); return { success: true }; });

// ========== GRBL 1.1 Coolant Commands ==========
ipcMain.handle('grbl:toggleFloodCoolant', () => { grbl.toggleFloodCoolant(); return { success: true }; });
ipcMain.handle('grbl:toggleMistCoolant', () => { grbl.toggleMistCoolant(); return { success: true }; });

// ========== GRBL 1.1 Info Commands ==========
ipcMain.handle('grbl:getBuildInfo', () => grbl.getBuildInfo().then(info => ({ success: true, info })).catch(e => ({ success: false, error: e.message })));
ipcMain.handle('grbl:getParserState', () => grbl.getParserState().then(state => ({ success: true, state })).catch(e => ({ success: false, error: e.message })));
ipcMain.handle('grbl:getStartupBlocks', () => grbl.getStartupBlocks().then(blocks => ({ success: true, blocks })).catch(e => ({ success: false, error: e.message })));
ipcMain.handle('grbl:setStartupBlock', (_, { index, gcode }) => grbl.setStartupBlock(index, gcode).then(() => ({ success: true })).catch(e => ({ success: false, error: e.message })));
ipcMain.handle('grbl:toggleCheckMode', () => grbl.toggleCheckMode().then(() => ({ success: true })).catch(e => ({ success: false, error: e.message })));
ipcMain.handle('grbl:sleep', () => grbl.sleep().then(() => ({ success: true })).catch(e => ({ success: false, error: e.message })));

// ========== Database/API Handlers for QR Codes (Direct Supabase Connection) ==========

// Test database connection
ipcMain.handle('db:testConnection', async () => {
  return await db.testConnection();
});

// Get database connection status
ipcMain.handle('db:getStatus', () => {
  return { connected: dbConnected };
});

// Fetch all QR codes/items from database
ipcMain.handle('api:fetchQRCodes', async () => {
  if (!dbConnected) {
    // Try to reconnect
    const result = await db.testConnection();
    if (result.success) {
      dbConnected = true;
    } else {
      return { success: false, error: 'Database not connected' };
    }
  }

  return await db.fetchItems(50);
});

// Fetch items pending engraving
ipcMain.handle('api:fetchPendingEngravings', async () => {
  if (!dbConnected) {
    return { success: false, error: 'Database not connected' };
  }
  return await db.fetchPendingEngravings(50);
});

// Fetch a single item by UID
ipcMain.handle('api:fetchQRImage', async (_, uid) => {
  if (!dbConnected) {
    return { success: false, error: 'Database not connected' };
  }
  return await db.fetchItemByUid(uid);
});

// Update item status after engraving
ipcMain.handle('api:updateItemStatus', async (_, { uid, status }) => {
  if (!dbConnected) {
    return { success: false, error: 'Database not connected' };
  }
  return await db.updateItemStatus(uid, status);
});

// Record an engraving job
ipcMain.handle('api:recordEngraving', async (_, engravingData) => {
  if (!dbConnected) {
    return { success: false, error: 'Database not connected' };
  }
  return await db.recordEngraving(engravingData);
});

// Generate QR code as data URL
ipcMain.handle('api:generateQRCode', async (_, { data, size }) => {
  try {
    const qrSize = size || 256;
    const dataUrl = await QRCode.toDataURL(data, {
      width: qrSize,
      margin: 1,
      color: {
        dark: '#000000',
        light: '#FFFFFF'
      },
      errorCorrectionLevel: 'M'
    });
    return { success: true, dataUrl };
  } catch (error) {
    console.error('QR code generation error:', error);
    return { success: false, error: error.message };
  }
});

// Generate QR code as matrix (for G-code generation)
ipcMain.handle('api:generateQRMatrix', async (_, { data }) => {
  try {
    // Get QR code as a 2D matrix
    const qrData = await QRCode.create(data, { errorCorrectionLevel: 'M' });
    const modules = qrData.modules;
    const size = modules.size;

    // Convert to simple 2D array (1 = black, 0 = white)
    const matrix = [];
    for (let y = 0; y < size; y++) {
      const row = [];
      for (let x = 0; x < size; x++) {
        row.push(modules.get(x, y) ? 1 : 0);
      }
      matrix.push(row);
    }

    return {
      success: true,
      matrix,
      size,
      moduleCount: size
    };
  } catch (error) {
    console.error('QR matrix generation error:', error);
    return { success: false, error: error.message };
  }
});

console.log('GENGRAV loaded - GRBL 1.1 Controller with Supabase Database');
