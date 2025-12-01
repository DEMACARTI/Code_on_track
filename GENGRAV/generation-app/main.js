const { app, BrowserWindow, ipcMain, globalShortcut } = require('electron');
const path = require('path');
const fs = require('fs');
const QRCode = require('qrcode');
const DatabaseClient = require('../shared/db-client');

let mainWindow;
let dbClient;

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1400,
    height: 900,
    minWidth: 1200,
    minHeight: 700,
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      nodeIntegration: false,
      contextIsolation: true,
      devTools: false
    }
  });

  mainWindow.loadFile('index.html');
  
  // Remove all keyboard shortcuts that open DevTools
  mainWindow.webContents.on('before-input-event', (event, input) => {
    if (input.key === 'F12' || 
        (input.control && input.shift && input.key === 'I') ||
        (input.meta && input.alt && input.key === 'I') ||
        (input.control && input.shift && input.key === 'J') ||
        (input.meta && input.alt && input.key === 'J')) {
      event.preventDefault();
    }
  });

  mainWindow.on('closed', async () => {
    mainWindow = null;
    if (dbClient) {
      try {
        await dbClient.close();
      } catch (err) {
        console.error('Error closing database:', err);
      }
      dbClient = null;
    }
  });
}

// Initialize database client
function initializeApp() {
  createWindow();
  dbClient = new DatabaseClient();
}

// IPC Handlers for database operations
ipcMain.handle('create-item', async (event, itemData) => {
  try {
    // Create QR codes directory if it doesn't exist
    const qrCodesDir = path.join(__dirname, 'qr-codes');
    if (!fs.existsSync(qrCodesDir)) {
      fs.mkdirSync(qrCodesDir, { recursive: true });
    }

    const quantity = itemData.quantity || 1;
    const createdItems = [];
    const crypto = require('crypto');

    // Generate multiple items based on quantity
    for (let i = 0; i < quantity; i++) {
      // Generate unique hexadecimal code (8 characters)
      const hexCode = crypto.randomBytes(4).toString('hex').toUpperCase();
      
      // Create unique UID with timestamp and hex code
      const uniqueUid = `${itemData.uid}-${Date.now()}-${hexCode}`;
      
      // Generate QR code data
      const qrData = JSON.stringify({
        uid: uniqueUid,
        component_type: itemData.component_type,
        lot_number: itemData.lot_number,
        vendor_id: itemData.vendor_id,
        warranty_years: itemData.warranty_years,
        manufacture_date: itemData.manufacture_date,
        item_number: i + 1,
        total_quantity: quantity,
        hex_id: hexCode
      });

      // Generate QR code as base64 (stored directly in database)
      const qrBase64 = await QRCode.toDataURL(qrData, {
        width: 500,
        margin: 2,
        color: {
          dark: '#000000',
          light: '#FFFFFF'
        }
      });

      // Also save to file for backup/local viewing
      const qrFilename = `${uniqueUid}.png`;
      const qrFilePath = path.join(qrCodesDir, qrFilename);
      await QRCode.toFile(qrFilePath, qrData, {
        width: 500,
        margin: 2,
        color: {
          dark: '#000000',
          light: '#FFFFFF'
        }
      });

      // Create item data for this specific item
      const singleItemData = {
        uid: uniqueUid,
        component_type: itemData.component_type,
        lot_number: itemData.lot_number,
        vendor_id: itemData.vendor_id,
        quantity: 1, // Each item represents 1 unit
        warranty_years: itemData.warranty_years,
        manufacture_date: itemData.manufacture_date,
        qr_image_url: qrBase64, // Store base64 directly
        current_status: itemData.current_status || 'manufactured',
        metadata: JSON.stringify({
          original_quantity: quantity,
          item_number: i + 1,
          generated_at: new Date().toISOString(),
          local_file: `qr-codes/${qrFilename}` // Keep reference to local file
        })
      };

      // Save to database
      const item = await dbClient.createItem(singleItemData);
      
      // Create engraving job
      await dbClient.createEngravingJob({
        item_uid: item.uid,
        svg_url: item.qr_image_url
      });

      createdItems.push(item);

      // Send progress update to renderer
      if (mainWindow && i % 10 === 0) {
        mainWindow.webContents.send('creation-progress', {
          current: i + 1,
          total: quantity,
          percentage: Math.round(((i + 1) / quantity) * 100)
        });
      }
    }

    return { success: true, items: createdItems, count: createdItems.length };
  } catch (error) {
    console.error('Error creating item:', error);
    return { success: false, error: error.message };
  }
});

ipcMain.handle('get-all-items', async () => {
  try {
    const items = await dbClient.getAllItems();
    return { success: true, items };
  } catch (error) {
    return { success: false, error: error.message };
  }
});

ipcMain.handle('get-item', async (event, uid) => {
  try {
    const item = await dbClient.getItemByUid(uid);
    return { success: true, item };
  } catch (error) {
    return { success: false, error: error.message };
  }
});

ipcMain.handle('update-item', async (event, uid, updates) => {
  try {
    const item = await dbClient.updateItem(uid, updates);
    return { success: true, item };
  } catch (error) {
    return { success: false, error: error.message };
  }
});

ipcMain.handle('get-qr-image', async (event, qrPath) => {
  try {
    const fullPath = path.join(__dirname, qrPath);
    if (fs.existsSync(fullPath)) {
      const imageBuffer = fs.readFileSync(fullPath);
      const base64Image = imageBuffer.toString('base64');
      return { success: true, dataUrl: `data:image/png;base64,${base64Image}` };
    } else {
      return { success: false, error: 'QR code image not found' };
    }
  } catch (error) {
    return { success: false, error: error.message };
  }
});

app.on('ready', initializeApp);

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