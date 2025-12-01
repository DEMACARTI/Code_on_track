const { exec } = require('child_process');
const path = require('path');

const BACKEND_SCRIPT_PATH = path.join(__dirname, '../SIH_FINAL_PROJECT/Code_on_track/App_a/app');

function generateQRCode(data, uid, callback) {
  const command = `python3 ${path.join(BACKEND_SCRIPT_PATH, 'qr_generator.py')} ${data} ${uid}`;
  exec(command, (error, stdout, stderr) => {
    if (error) {
      callback(`Error: ${stderr}`);
    } else {
      callback(null, stdout);
    }
  });
}

function uploadFile(filePath, contentType, callback) {
  const command = `python3 ${path.join(BACKEND_SCRIPT_PATH, 'minio_client.py')} ${filePath} ${contentType}`;
  exec(command, (error, stdout, stderr) => {
    if (error) {
      callback(`Error: ${stderr}`);
    } else {
      callback(null, stdout);
    }
  });
}

module.exports = {
  generateQRCode,
  uploadFile
};