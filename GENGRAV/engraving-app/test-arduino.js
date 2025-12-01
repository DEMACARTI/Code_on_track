#!/usr/bin/env node

const { SerialPort } = require('serialport');
const { ReadlineParser } = require('@serialport/parser-readline');

async function testArduino() {
  console.log('=== Arduino GRBL Connection Test ===\n');
  
  // List all ports
  console.log('Scanning for available serial ports...');
  const ports = await SerialPort.list();
  
  console.log('\nAvailable ports:');
  ports.forEach(port => {
    console.log(`  - ${port.path}`);
    if (port.manufacturer) console.log(`    Manufacturer: ${port.manufacturer}`);
    if (port.serialNumber) console.log(`    Serial: ${port.serialNumber}`);
  });
  
  // Find Arduino
  const arduinoPorts = ports.filter(port => 
    port.path.includes('usbserial') ||
    port.path.includes('usbmodem') ||
    port.manufacturer?.toLowerCase().includes('arduino')
  );
  
  if (arduinoPorts.length === 0) {
    console.log('\n❌ No Arduino found. Please check connection.');
    return;
  }
  
  console.log(`\n✅ Found Arduino at: ${arduinoPorts[0].path}`);
  console.log('\nAttempting to connect...');
  
  // Connect to Arduino
  const port = new SerialPort({
    path: arduinoPorts[0].path,
    baudRate: 115200
  });
  
  const parser = port.pipe(new ReadlineParser({ delimiter: '\r\n' }));
  
  port.on('open', () => {
    console.log('✅ Serial port opened successfully!');
    console.log('Baudrate: 115200');
    console.log('\nWaiting for GRBL initialization...\n');
    
    // Send wake-up commands
    setTimeout(() => {
      console.log('Sending wake-up command...');
      port.write('\r\n\r\n');
      
      setTimeout(() => {
        console.log('Sending unlock command ($X)...');
        port.write('$X\n');
        
        setTimeout(() => {
          console.log('Requesting status (?)...');
          port.write('?\n');
          
          setTimeout(() => {
            console.log('\n=== Test Complete ===');
            console.log('Closing connection...');
            port.close();
          }, 2000);
        }, 1000);
      }, 1000);
    }, 2000);
  });
  
  parser.on('data', (data) => {
    console.log(`GRBL Response: ${data}`);
  });
  
  port.on('error', (err) => {
    console.error('❌ Error:', err.message);
  });
  
  port.on('close', () => {
    console.log('Connection closed.');
    process.exit(0);
  });
}

testArduino().catch(console.error);
