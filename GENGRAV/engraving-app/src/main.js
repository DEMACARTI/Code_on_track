/**
 * GENGRAV Main Process
 */
const { app, BrowserWindow, ipcMain } = require('electron');
const path = require('node:path');
const { GRBLController, GRBL_SETTINGS, LASER_DEFAULTS } = require('./grbl-controller');

if (require('electron-squirrel-startup')) app.quit();

const grbl = new GRBLController();
let mainWindow = null;

const createWindow = () => {
  mainWindow = new BrowserWindow({
    width: 1400, height: 900, minWidth: 1200, minHeight: 700,
    webPreferences: { preload: MAIN_WINDOW_PRELOAD_WEBPACK_ENTRY, nodeIntegration: false, contextIsolation: true },
    backgroundColor: '#0a0a0f', title: 'GENGRAV Laser Engraver'
  });
  mainWindow.loadURL(MAIN_WINDOW_WEBPACK_ENTRY);

  grbl.on('status', (s) => mainWindow?.webContents.send('grbl:status', s));
  grbl.on('log', (m) => mainWindow?.webContents.send('grbl:log', m));
  grbl.on('tx', (c) => mainWindow?.webContents.send('grbl:tx', c));
  grbl.on('rx', (l) => mainWindow?.webContents.send('grbl:rx', l));
  grbl.on('progress', (p) => mainWindow?.webContents.send('grbl:progress', p));
  grbl.on('settings', (s) => mainWindow?.webContents.send('grbl:settings', s));
  grbl.on('error', (e) => mainWindow?.webContents.send('grbl:error', e.toString()));
  grbl.on('estop', () => mainWindow?.webContents.send('grbl:estop'));
  grbl.on('complete', () => mainWindow?.webContents.send('grbl:complete'));

  if (process.env.NODE_ENV === 'development') mainWindow.webContents.openDevTools();
};

app.whenReady().then(() => {
  createWindow();
  app.on('activate', () => { if (BrowserWindow.getAllWindows().length === 0) createWindow(); });
});
app.on('window-all-closed', () => { grbl.disconnect(); if (process.platform !== 'darwin') app.quit(); });

// IPC Handlers
ipcMain.handle('grbl:listPorts', () => grbl.listPorts());
ipcMain.handle('grbl:connect', (_, p) => grbl.connect(p).then(() => ({ success: true })).catch(e => ({ success: false, error: e.message })));
ipcMain.handle('grbl:disconnect', () => { grbl.disconnect(); return { success: true }; });
ipcMain.handle('grbl:getState', () => grbl.getState());
ipcMain.handle('grbl:readSettings', () => grbl.readSettings().then(s => ({ success: true, settings: s })).catch(e => ({ success: false, error: e.message })));
ipcMain.handle('grbl:writeSetting', (_, { key, value }) => grbl.writeSetting(key, value).then(() => ({ success: true })).catch(e => ({ success: false, error: e.message })));
ipcMain.handle('grbl:applyDefaults', () => grbl.applyDefaults().then(() => ({ success: true })).catch(e => ({ success: false, error: e.message })));
ipcMain.handle('grbl:enableLaserMode', () => grbl.enableLaserMode().then(() => ({ success: true })).catch(e => ({ success: false, error: e.message })));
ipcMain.handle('grbl:getDefaults', () => ({ settings: GRBL_SETTINGS, defaults: LASER_DEFAULTS }));
ipcMain.handle('grbl:home', () => grbl.home().then(() => ({ success: true })).catch(e => ({ success: false, error: e.message })));
ipcMain.handle('grbl:goHome', () => grbl.goHome().then(() => ({ success: true })).catch(e => ({ success: false, error: e.message })));
ipcMain.handle('grbl:jog', (_, { axis, distance, feed }) => grbl.jog(axis, distance, feed || 500).then(() => ({ success: true })).catch(e => ({ success: false, error: e.message })));
ipcMain.handle('grbl:moveTo', (_, { x, y, feed }) => grbl.moveTo(x, y, feed || 1000).then(() => ({ success: true })).catch(e => ({ success: false, error: e.message })));
ipcMain.handle('grbl:send', (_, c) => grbl.send(c).then(() => ({ success: true })).catch(e => ({ success: false, error: e.message })));
ipcMain.handle('grbl:laserOn', (_, p) => grbl.laserOn(p).then(() => ({ success: true })).catch(e => ({ success: false, error: e.message })));
ipcMain.handle('grbl:laserOff', () => grbl.laserOff().then(() => ({ success: true })).catch(e => ({ success: false, error: e.message })));
ipcMain.handle('grbl:emergencyStop', () => grbl.doEmergencyStop().then(() => ({ success: true })).catch(e => ({ success: false, error: e.message })));
ipcMain.handle('grbl:resetEstop', () => grbl.resetEstop().then(() => ({ success: true })).catch(e => ({ success: false, error: e.message })));
ipcMain.handle('grbl:runGCode', (_, g) => grbl.runGCode(g).then(() => ({ success: true })).catch(e => ({ success: false, error: e.message })));
ipcMain.handle('grbl:stop', () => { grbl.stop(); return { success: true }; });

console.log('GENGRAV loaded');
