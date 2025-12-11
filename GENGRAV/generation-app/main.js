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
    const isBatchMode = itemData.batch_mode || false;
    const batchRefId = itemData.batch_ref_id || null;

    console.log(`Starting ${isBatchMode ? 'BATCH' : 'SINGLE'} generation: ${quantity} items`);
    if (isBatchMode) {
      console.log(`Batch Reference ID: ${batchRefId}`);
    }

    // For batch mode, use a more efficient progress update interval
    const progressInterval = isBatchMode ? Math.max(100, Math.floor(quantity / 100)) : 10;

    // Process in batches for better performance
    const batchSize = 100; // Process 100 items at a time
    const numBatches = Math.ceil(quantity / batchSize);

    for (let batchIdx = 0; batchIdx < numBatches; batchIdx++) {
      const startIdx = batchIdx * batchSize;
      const endIdx = Math.min(startIdx + batchSize, quantity);
      const batchPromises = [];

      // Generate multiple items in parallel within each batch
      for (let i = startIdx; i < endIdx; i++) {
        const itemPromise = (async () => {
          // Component type codes for backend validation
          // 01 = ERC, 02 = LINER, 03 = PAD, 04 = SLEEPER
          const componentTypeCodes = {
            'ERC': '01',
            'LINER': '02',
            'PAD': '03',
            'SLEEPER': '04'
          };

          // Get component code (default to '00' for unknown types)
          const componentCode = componentTypeCodes[itemData.component_type] || '00';

          // Generate unique UID: ComponentCode-MillisecondEpoch
          // Format: XX-XXXXXXXXXXXXX (e.g., 01-1733932199123)
          const epochTimestamp = Date.now().toString();
          const uniqueUid = `${componentCode}-${epochTimestamp}`;

          // Add small delay to ensure unique timestamps in loops
          await new Promise(resolve => setTimeout(resolve, 1));

          // QR data contains ONLY the UID - all other data is stored in database
          // Format: ComponentCode-EpochMs (e.g., 01-1733932199123)
          const qrData = uniqueUid;

          // Generate QR code as base64 (stored directly in database)
          const qrBase64 = await QRCode.toDataURL(qrData, {
            width: 500,
            margin: 2,
            color: {
              dark: '#000000',
              light: '#FFFFFF'
            }
          });

          // Only save physical files for first 10 items (for backup/verification)
          if (!isBatchMode || i < 10) {
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
          }

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
              batch_ref_id: batchRefId,
              batch_mode: isBatchMode
            })
          };

          // Save to database
          const item = await dbClient.createItem(singleItemData);

          // Create engraving job with batch reference
          await dbClient.createEngravingJob({
            item_uid: item.uid,
            svg_url: item.qr_image_url,
            batch_ref_id: batchRefId
          });

          return item;
        })();

        batchPromises.push(itemPromise);
      }

      // Wait for current batch to complete
      const batchResults = await Promise.all(batchPromises);
      createdItems.push(...batchResults);

      // Send progress update to renderer
      if (mainWindow) {
        mainWindow.webContents.send('creation-progress', {
          current: endIdx,
          total: quantity,
          percentage: Math.round((endIdx / quantity) * 100)
        });
      }

      console.log(`Batch ${batchIdx + 1}/${numBatches} complete: ${endIdx}/${quantity} items`);
    }

    // Send final progress update
    if (mainWindow) {
      mainWindow.webContents.send('creation-progress', {
        current: quantity,
        total: quantity,
        percentage: 100
      });
    }

    console.log(`Generation complete: ${createdItems.length} items created`);
    return { success: true, items: createdItems, count: createdItems.length, batch_ref_id: batchRefId };
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