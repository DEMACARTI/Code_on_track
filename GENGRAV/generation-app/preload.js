const { contextBridge, ipcRenderer } = require('electron');

// Expose protected methods that allow the renderer process to use
// the ipcRenderer without exposing the entire object
contextBridge.exposeInMainWorld(
  'electronAPI',
  {
    createItem: (itemData) => ipcRenderer.invoke('create-item', itemData),
    getAllItems: () => ipcRenderer.invoke('get-all-items'),
    getItem: (uid) => ipcRenderer.invoke('get-item', uid),
    updateItem: (uid, updates) => ipcRenderer.invoke('update-item', uid, updates),
    getQRImage: (qrPath) => ipcRenderer.invoke('get-qr-image', qrPath),
    onCreationProgress: (callback) => ipcRenderer.on('creation-progress', (event, data) => callback(data))
  }
);

window.addEventListener('DOMContentLoaded', () => {
  const replaceText = (selector, text) => {
    const element = document.getElementById(selector);
    if (element) element.innerText = text;
  };

  for (const dependency of ['chrome', 'node', 'electron']) {
    replaceText(`${dependency}-version`, process.versions[dependency]);
  }
});