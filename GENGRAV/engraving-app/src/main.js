/**
 * GENGRAV Main Process - GRBL 1.1 Controller
 */
const { app, BrowserWindow, ipcMain } = require('electron');
const path = require('node:path');
const { GRBLController, GRBL_SETTINGS, LASER_DEFAULTS, BAUD_RATES, CONNECTION_OPTIONS, REALTIME_COMMANDS, GRBL_VERSION } = require('./grbl-controller');

if (require('electron-squirrel-startup')) app.quit();

const grbl = new GRBLController();
let mainWindow = null;

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

  if (process.env.NODE_ENV === 'development') mainWindow.webContents.openDevTools();
};

app.whenReady().then(() => {
  createWindow();
  app.on('activate', () => { if (BrowserWindow.getAllWindows().length === 0) createWindow(); });
});
app.on('window-all-closed', () => { grbl.disconnect(); if (process.platform !== 'darwin') app.quit(); });

// ========== Core IPC Handlers ==========
ipcMain.handle('grbl:listPorts', () => grbl.listPorts());
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

console.log('GENGRAV loaded - GRBL 1.1 Controller');
