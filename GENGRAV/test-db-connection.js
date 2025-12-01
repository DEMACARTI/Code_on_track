const DatabaseClient = require('./shared/db-client');

async function testDatabaseConnection() {
  console.log('Testing Database Connection...\n');
  
  const dbClient = new DatabaseClient();
  
  try {
    // Test 1: Query all items
    console.log('Test 1: Fetching all items...');
    const result = await dbClient.query('SELECT COUNT(*) FROM items');
    console.log(`✓ Items count: ${result.rows[0].count}\n`);
    
    // Test 2: Query engraving queue
    console.log('Test 2: Fetching engraving queue...');
    const queueResult = await dbClient.query('SELECT COUNT(*) FROM engraving_queue');
    console.log(`✓ Engraving jobs count: ${queueResult.rows[0].count}\n`);
    
    // Test 3: Query engraving history
    console.log('Test 3: Fetching engraving history...');
    const historyResult = await dbClient.query('SELECT COUNT(*) FROM engraving_history');
    console.log(`✓ History records count: ${historyResult.rows[0].count}\n`);
    
    // Test 4: Test creating a sample item (then delete it)
    console.log('Test 4: Creating a test item...');
    const testItem = {
      uid: `TEST-${Date.now()}`,
      component_type: 'EC',
      lot_number: 'TEST-LOT',
      vendor_id: 999,
      quantity: 1,
      warranty_years: 5,
      manufacture_date: new Date(),
      qr_image_url: 'http://example.com/test.png',
      current_status: 'manufactured',
      metadata: JSON.stringify({ test: true })
    };
    
    const createdItem = await dbClient.createItem(testItem);
    console.log(`✓ Item created with UID: ${createdItem.uid}\n`);
    
    // Test 5: Create engraving job for the item
    console.log('Test 5: Creating engraving job...');
    const engravingJob = await dbClient.createEngravingJob({
      item_uid: createdItem.uid,
      svg_url: 'http://example.com/test-qr.svg'
    });
    console.log(`✓ Engraving job created with ID: ${engravingJob.id}\n`);
    
    // Test 6: Update job status
    console.log('Test 6: Updating job status...');
    await dbClient.updateEngravingJobStatus(engravingJob.id, 'in_progress', 'Test in progress');
    console.log(`✓ Job status updated to 'in_progress'\n`);
    
    // Test 7: Get job history
    console.log('Test 7: Fetching job history...');
    const history = await dbClient.getEngravingHistory(engravingJob.id);
    console.log(`✓ History records for job: ${history.length}\n`);
    
    // Test 8: Clean up - delete test data
    console.log('Test 8: Cleaning up test data...');
    await dbClient.query('DELETE FROM engraving_history WHERE engraving_job_id = $1', [engravingJob.id]);
    await dbClient.query('DELETE FROM engraving_queue WHERE id = $1', [engravingJob.id]);
    await dbClient.query('DELETE FROM items WHERE uid = $1', [createdItem.uid]);
    console.log(`✓ Test data cleaned up\n`);
    
    console.log('═══════════════════════════════════════');
    console.log('✓ All tests passed successfully!');
    console.log('✓ Database is ready for both apps!');
    console.log('═══════════════════════════════════════\n');
    
  } catch (error) {
    console.error('✗ Test failed:', error.message);
    console.error(error);
  } finally {
    await dbClient.close();
  }
}

testDatabaseConnection();
