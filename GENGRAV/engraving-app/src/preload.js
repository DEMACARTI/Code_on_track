/**
 * Preload - exposes GRBL API to renderer
 */
const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('grbl', {
    listPorts: () => ipcRenderer.invoke('grbl:listPorts'),
    connect: (p) => ipcRenderer.invoke('grbl:connect', p),
    disconnect: () => ipcRenderer.invoke('grbl:disconnect'),
    getState: () => ipcRenderer.invoke('grbl:getState'),
    readSettings: () => ipcRenderer.invoke('grbl:readSettings'),
    writeSetting: (k, v) => ipcRenderer.invoke('grbl:writeSetting', { key: k, value: v }),
    applyDefaults: () => ipcRenderer.invoke('grbl:applyDefaults'),
    enableLaserMode: () => ipcRenderer.invoke('grbl:enableLaserMode'),
    getDefaults: () => ipcRenderer.invoke('grbl:getDefaults'),
    home: () => ipcRenderer.invoke('grbl:home'),
    goHome: () => ipcRenderer.invoke('grbl:goHome'),
    jog: (a, d, f) => ipcRenderer.invoke('grbl:jog', { axis: a, distance: d, feed: f }),
    moveTo: (x, y, f) => ipcRenderer.invoke('grbl:moveTo', { x, y, feed: f }),
    send: (c) => ipcRenderer.invoke('grbl:send', c),
    laserOn: (p) => ipcRenderer.invoke('grbl:laserOn', p),
    laserOff: () => ipcRenderer.invoke('grbl:laserOff'),
    emergencyStop: () => ipcRenderer.invoke('grbl:emergencyStop'),
    resetEstop: () => ipcRenderer.invoke('grbl:resetEstop'),
    runGCode: (g) => ipcRenderer.invoke('grbl:runGCode', g),
    stop: () => ipcRenderer.invoke('grbl:stop'),

    onStatus: (cb) => ipcRenderer.on('grbl:status', (_, d) => cb(d)),
    onLog: (cb) => ipcRenderer.on('grbl:log', (_, m) => cb(m)),
    onTx: (cb) => ipcRenderer.on('grbl:tx', (_, c) => cb(c)),
    onRx: (cb) => ipcRenderer.on('grbl:rx', (_, l) => cb(l)),
    onProgress: (cb) => ipcRenderer.on('grbl:progress', (_, p) => cb(p)),
    onSettings: (cb) => ipcRenderer.on('grbl:settings', (_, s) => cb(s)),
    onError: (cb) => ipcRenderer.on('grbl:error', (_, e) => cb(e)),
    onEstop: (cb) => ipcRenderer.on('grbl:estop', () => cb()),
    onComplete: (cb) => ipcRenderer.on('grbl:complete', () => cb())
});
