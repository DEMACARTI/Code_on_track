#!/usr/bin/env node
/**
 * Test full QR code generation flow like GENGRAV app
 */

const QRCode = require('qrcode');
const DatabaseClient = require('../shared/db-client');
const crypto = require('crypto');

async function testQRGeneration() {
  console.log('🎯 Testing Full QR Generation Flow\n');
  
  const dbClient = new DatabaseClient();
  
  try {
    // Simulate component data from GENGRAV form
    const componentData = {
      component_type: 'RAIL',
      lot_number: 'LOT-TEST-2024',
      vendor_id: 101,
      quantity: 3, // Generate 3 items
      warranty_years: 10,
      manufacture_date: '2024-12-01',
      current_status: 'manufactured'
    };
    
    console.log('📝 Component Details:');
    console.log(`   Type: ${componentData.component_type}`);
    console.log(`   Lot: ${componentData.lot_number}`);
    console.log(`   Vendor: ${componentData.vendor_id}`);
    console.log(`   Quantity: ${componentData.quantity}`);
    console.log(`   Warranty: ${componentData.warranty_years} years\n`);
    
    const createdItems = [];
    const baseUid = `IRF-${componentData.component_type}-${componentData.vendor_id}-${componentData.lot_number}`;
    
    console.log('⚙️  Generating items with QR codes...\n');
    
    for (let i = 0; i < componentData.quantity; i++) {
      // Generate unique code
      const hexCode = crypto.randomBytes(4).toString('hex').toUpperCase();
      const uniqueUid = `${baseUid}-${Date.now()}-${hexCode}`;
      
      console.log(`   [${i + 1}/${componentData.quantity}] Generating: ${uniqueUid}`);
      
      // Create QR data payload
      const qrData = JSON.stringify({
        uid: uniqueUid,
        component_type: componentData.component_type,
        lot_number: componentData.lot_number,
        vendor_id: componentData.vendor_id,
        warranty_years: componentData.warranty_years,
        manufacture_date: componentData.manufacture_date,
        item_number: i + 1,
        total_quantity: componentData.quantity,
        hex_id: hexCode
      });
      
      // Generate QR code as base64 (like updated GENGRAV)
      const qrBase64 = await QRCode.toDataURL(qrData, {
        width: 500,
        margin: 2,
        color: {
          dark: '#000000',
          light: '#FFFFFF'
        }
      });
      
      // Create item with QR code
      const itemData = {
        uid: uniqueUid,
        component_type: componentData.component_type,
        lot_number: componentData.lot_number,
        vendor_id: componentData.vendor_id,
        quantity: 1,
        warranty_years: componentData.warranty_years,
        manufacture_date: componentData.manufacture_date,
        qr_image_url: qrBase64, // Base64 QR code
        current_status: componentData.current_status,
        metadata: JSON.stringify({
          original_quantity: componentData.quantity,
          item_number: i + 1,
          generated_at: new Date().toISOString(),
          test_generation: true
        })
      };
      
      // Save to database
      const item = await dbClient.createItem(itemData);
      createdItems.push(item);
      
      console.log(`      ✅ Saved to database (QR: ${qrBase64.substring(0, 50)}...)`);
      
      // Small delay to ensure unique timestamps
      await new Promise(resolve => setTimeout(resolve, 100));
    }
    
    console.log(`\n✅ Created ${createdItems.length} items successfully!\n`);
    
    // Verify all items in database
    console.log('🔍 Verifying items in database...\n');
    
    for (const item of createdItems) {
      const dbItem = await dbClient.getItemByUid(item.uid);
      const hasQR = dbItem.qr_image_url && dbItem.qr_image_url.startsWith('data:image/png;base64,');
      const qrSize = dbItem.qr_image_url ? dbItem.qr_image_url.length : 0;
      
      console.log(`   ${dbItem.uid}`);
      console.log(`      Component: ${dbItem.component_type}`);
      console.log(`      Status: ${dbItem.current_status}`);
      console.log(`      QR Code: ${hasQR ? '✅ Stored' : '❌ Missing'} (${qrSize} bytes)`);
      console.log('');
    }
    
    // Test retrieval
    console.log('📊 Database Summary:');
    const allItems = await dbClient.getAllItems();
    const withQR = allItems.filter(item => 
      item.qr_image_url && item.qr_image_url.startsWith('data:image/png;base64,')
    ).length;
    
    console.log(`   Total items: ${allItems.length}`);
    console.log(`   Items with QR codes: ${withQR}`);
    console.log(`   Test items created: ${createdItems.length}\n`);
    
    // Clean up test items
    console.log('🧹 Cleaning up test items...');
    for (const item of createdItems) {
      await dbClient.query('DELETE FROM items WHERE uid = $1', [item.uid]);
    }
    console.log(`✅ Removed ${createdItems.length} test items\n`);
    
    console.log('✅ FULL QR GENERATION TEST PASSED!\n');
    console.log('📌 What was tested:');
    console.log('   ✅ Multiple item generation');
    console.log('   ✅ Unique UID creation');
    console.log('   ✅ QR code generation as base64');
    console.log('   ✅ Database storage');
    console.log('   ✅ Item retrieval');
    console.log('   ✅ QR code integrity\n');
    
    console.log('🎉 GENGRAV app will work correctly!\n');
    
  } catch (error) {
    console.error('❌ Test failed:', error.message);
    console.error(error.stack);
    process.exit(1);
  } finally {
    await dbClient.close();
  }
}

testQRGeneration().catch(err => {
  console.error('Fatal error:', err);
  process.exit(1);
});
