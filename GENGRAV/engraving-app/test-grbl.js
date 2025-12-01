#!/usr/bin/env node

const fs = require('fs');
const { SerialPort } = require('serialport');
const { ReadlineParser } = require('@serialport/parser-readline');

async function advancedTest() {
  console.log('=== Advanced Arduino/GRBL Test ===\n');
  
  const ports = await SerialPort.list();
  const arduinoPorts = ports.filter(port => 
    port.path.includes('usbserial') ||
    port.path.includes('usbmodem')
  );
  
  if (arduinoPorts.length === 0) {
    console.log('❌ No Arduino found');
    return;
  }
  
  const portPath = arduinoPorts[0].path;
  console.log(`Testing: ${portPath}\n`);
  
  const port = new SerialPort({
    path: portPath,
    baudRate: 115200,
    autoOpen: false
  });
  
  const parser = port.pipe(new ReadlineParser({ delimiter: '\r\n' }));
  
  let responseReceived = false;
  let responses = [];
  
  parser.on('data', (data) => {
    responseReceived = true;
    responses.push(data);
    console.log(`← ${data}`);
    
    if (data.startsWith('Grbl')) {
      console.log('\n✅ GRBL Detected!');
      console.log(`Version: ${data}`);
    }
  });
  
  port.on('error', (err) => {
    console.error('❌ Port Error:', err.message);
  });
  
  port.open((err) => {
    if (err) {
      console.error('❌ Failed to open port:', err.message);
      return;
    }
    
    console.log('✅ Port opened\n');
    console.log('Sending commands:\n');
    
    setTimeout(() => {
      console.log('→ Wake up GRBL (\\r\\n)');
      port.write('\r\n\r\n');
    }, 1000);
    
    setTimeout(() => {
      console.log('→ Unlock ($X)');
      port.write('$X\n');
    }, 2000);
    
    setTimeout(() => {
      console.log('→ Get version ($$)');
      port.write('$$\n');
    }, 3000);
    
    setTimeout(() => {
      console.log('→ Status query (?)');
      port.write('?\n');
    }, 4000);
    
    setTimeout(() => {
      console.log('\n=== Summary ===');
      console.log(`Responses received: ${responses.length}`);
      
      if (responses.length === 0) {
        console.log('\n⚠️  No responses from device');
        console.log('This could mean:');
        console.log('  1. GRBL is not flashed on the Arduino');
        console.log('  2. Wrong baud rate (try 9600 or 57600)');
        console.log('  3. Arduino is not properly connected');
        console.log('  4. Arduino is in bootloader mode');
        console.log('\nRecommendation: Flash GRBL firmware first');
        console.log('Download from: https://github.com/grbl/grbl');
      } else if (!responses.some(r => r.startsWith('Grbl'))) {
        console.log('\n⚠️  Device responding but not GRBL');
        console.log('Responses:', responses);
      } else {
        console.log('\n✅ GRBL is working correctly!');
      }
      
      // Load and send G-code file
      const gcodeFile = './test_qr_engraving.gcode';
      const gcode = fs.readFileSync(gcodeFile, 'utf8');

      const lines = gcode.split('\n');
      lines.forEach((line, index) => {
        setTimeout(() => {
          console.log(`→ ${line}`);
          port.write(`${line}\n`);
        }, index * 200); // Send each line with a delay
      });
      
      port.close();
      process.exit(0);
    }, 6000);
  });
}

advancedTest().catch(console.error);
