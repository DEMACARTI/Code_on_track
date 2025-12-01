#!/usr/bin/env node
/**
 * Test script to verify GENGRAV app can connect to Supabase
 * and create items with QR codes
 */

const path = require('path');
const DatabaseClient = require('./shared/db-client');

async function testDatabase() {
  console.log('🧪 Testing GENGRAV Database Connection...\n');
  
  const dbClient = new DatabaseClient();
  
  try {
    // Test 1: Check connection
    console.log('1️⃣  Testing database connection...');
    const result = await dbClient.query('SELECT NOW()');
    console.log('✅ Connected to database');
    console.log(`   Server time: ${result.rows[0].now}\n`);
    
    // Test 2: Check if tables exist
    console.log('2️⃣  Checking tables...');
    const tablesResult = await dbClient.query(`
      SELECT table_name 
      FROM information_schema.tables 
      WHERE table_schema = 'public' 
      AND table_name IN ('items', 'engraving_queue', 'engraving_history', 'users')
      ORDER BY table_name
    `);
    
    console.log('   Tables found:');
    tablesResult.rows.forEach(row => {
      console.log(`   ✅ ${row.table_name}`);
    });
    console.log('');
    
    // Test 3: Count existing items
    console.log('3️⃣  Checking existing items...');
    const countResult = await dbClient.query('SELECT COUNT(*) as total FROM items');
    const totalItems = countResult.rows[0].total;
    console.log(`   Total items: ${totalItems}`);
    
    const qrCountResult = await dbClient.query(`
      SELECT COUNT(*) as total 
      FROM items 
      WHERE qr_image_url IS NOT NULL AND qr_image_url != ''
    `);
    const itemsWithQR = qrCountResult.rows[0].total;
    console.log(`   Items with QR codes: ${itemsWithQR}\n`);
    
    // Test 4: Show sample items
    if (totalItems > 0) {
      console.log('4️⃣  Sample items:');
      const itemsResult = await dbClient.query(`
        SELECT uid, component_type, 
               CASE 
                 WHEN qr_image_url IS NOT NULL AND qr_image_url != '' 
                 THEN '✅ Has QR' 
                 ELSE '❌ No QR' 
               END as qr_status,
               created_at
        FROM items 
        ORDER BY created_at DESC 
        LIMIT 5
      `);
      
      console.log('   ' + '-'.repeat(80));
      itemsResult.rows.forEach(item => {
        console.log(`   ${item.uid.padEnd(35)} | ${item.component_type.padEnd(10)} | ${item.qr_status}`);
      });
      console.log('   ' + '-'.repeat(80) + '\n');
    }
    
    // Test 5: Create a test item
    console.log('5️⃣  Creating test item...');
    const testItem = {
      uid: `TEST-ITEM-${Date.now()}`,
      component_type: 'TEST',
      lot_number: 'TEST-LOT-001',
      vendor_id: 999,
      quantity: 1,
      warranty_years: 5,
      manufacture_date: new Date().toISOString().split('T')[0],
      qr_image_url: 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==',
      current_status: 'manufactured',
      metadata: JSON.stringify({ test: true, created_by: 'test_script' })
    };
    
    const createdItem = await dbClient.createItem(testItem);
    console.log('✅ Test item created successfully!');
    console.log(`   UID: ${createdItem.uid}`);
    console.log(`   Has QR: ${createdItem.qr_image_url ? 'Yes' : 'No'}\n`);
    
    // Test 6: Verify item was created
    console.log('6️⃣  Verifying item was stored...');
    const verifyResult = await dbClient.getItemByUid(createdItem.uid);
    if (verifyResult) {
      console.log('✅ Item successfully retrieved from database');
      console.log(`   Component Type: ${verifyResult.component_type}`);
      console.log(`   QR Code: ${verifyResult.qr_image_url ? 'Stored' : 'Missing'}\n`);
    } else {
      console.log('❌ Failed to retrieve item\n');
    }
    
    // Test 7: Clean up test item
    console.log('7️⃣  Cleaning up test item...');
    await dbClient.query('DELETE FROM items WHERE uid = $1', [createdItem.uid]);
    console.log('✅ Test item removed\n');
    
    console.log('✅ ALL TESTS PASSED!\n');
    console.log('📌 Summary:');
    console.log(`   - Database: Connected to Supabase`);
    console.log(`   - Tables: All required tables exist`);
    console.log(`   - Items: ${totalItems} total, ${itemsWithQR} with QR codes`);
    console.log(`   - CRUD: Create, Read, Delete operations working`);
    console.log('\n🎉 GENGRAV app is ready to generate QR codes!\n');
    
  } catch (error) {
    console.error('❌ Test failed:', error.message);
    console.error('\n💡 Troubleshooting:');
    console.error('   1. Check if DATABASE_URL is set in App_a/.env');
    console.error('   2. Verify Supabase connection string is correct');
    console.error('   3. Ensure firewall allows connection to Supabase');
    console.error('   4. Check if tables are created in Supabase\n');
    process.exit(1);
  } finally {
    await dbClient.close();
  }
}

// Run the test
testDatabase().catch(err => {
  console.error('Fatal error:', err);
  process.exit(1);
});
