/**
 * GENGRAV Database Connection - Supabase PostgreSQL
 * Direct connection to the IRF QR Tracking database
 */
const { Pool } = require('pg');

// Supabase PostgreSQL connection configuration
const DB_CONFIG = {
  user: 'postgres.aktfgilmfoprdkwkzybd',
  password: 'Alqawwiy@123',
  host: 'aws-1-ap-northeast-2.pooler.supabase.com',
  port: 6543,
  database: 'postgres',
  ssl: {
    rejectUnauthorized: false  // Required for Supabase
  },
  // Connection pool settings
  max: 5,
  idleTimeoutMillis: 30000,
  connectionTimeoutMillis: 10000,
};

let pool = null;

/**
 * Initialize the database connection pool
 */
function initPool() {
  if (!pool) {
    pool = new Pool(DB_CONFIG);
    
    pool.on('error', (err) => {
      console.error('Database pool error:', err);
    });
  }
  return pool;
}

/**
 * Test the database connection
 * @returns {Promise<{success: boolean, message?: string, error?: string}>}
 */
async function testConnection() {
  try {
    const p = initPool();
    const client = await p.connect();
    
    // Test query
    const result = await client.query('SELECT NOW() as current_time, current_database() as database');
    client.release();
    
    const { current_time, database } = result.rows[0];
    console.log(`✅ Database connected: ${database} at ${current_time}`);
    
    return {
      success: true,
      message: `Connected to ${database}`,
      timestamp: current_time
    };
  } catch (error) {
    console.error('❌ Database connection failed:', error.message);
    return {
      success: false,
      error: error.message
    };
  }
}

/**
 * Fetch items from the database with QR information
 * @param {number} limit - Maximum number of items to fetch
 * @returns {Promise<{success: boolean, items?: Array, error?: string}>}
 */
async function fetchItems(limit = 50) {
  try {
    const p = initPool();
    const client = await p.connect();
    
    // Query items table - adjust column names based on actual schema
    const query = `
      SELECT 
        uid,
        component_type,
        lot_number,
        vendor_id,
        quantity,
        current_status,
        qr_image_url,
        created_at,
        updated_at
      FROM items 
      ORDER BY created_at DESC 
      LIMIT $1
    `;
    
    const result = await client.query(query, [limit]);
    client.release();
    
    console.log(`📦 Fetched ${result.rows.length} items from database`);
    
    return {
      success: true,
      items: result.rows
    };
  } catch (error) {
    console.error('Error fetching items:', error.message);
    return {
      success: false,
      error: error.message
    };
  }
}

/**
 * Fetch a single item by UID
 * @param {string} uid - The unique identifier of the item
 * @returns {Promise<{success: boolean, item?: object, error?: string}>}
 */
async function fetchItemByUid(uid) {
  try {
    const p = initPool();
    const client = await p.connect();
    
    const query = `
      SELECT 
        uid,
        component_type,
        lot_number,
        vendor_id,
        quantity,
        current_status,
        qr_image_url,
        created_at,
        updated_at
      FROM items 
      WHERE uid = $1
    `;
    
    const result = await client.query(query, [uid]);
    client.release();
    
    if (result.rows.length === 0) {
      return {
        success: false,
        error: 'Item not found'
      };
    }
    
    return {
      success: true,
      item: result.rows[0]
    };
  } catch (error) {
    console.error('Error fetching item:', error.message);
    return {
      success: false,
      error: error.message
    };
  }
}

/**
 * Fetch items pending engraving
 * @param {number} limit - Maximum number of items to fetch
 * @returns {Promise<{success: boolean, items?: Array, error?: string}>}
 */
async function fetchPendingEngravings(limit = 50) {
  try {
    const p = initPool();
    const client = await p.connect();
    
    // Fetch items that need engraving (status = 'pending' or 'registered')
    const query = `
      SELECT 
        uid,
        component_type,
        lot_number,
        vendor_id,
        quantity,
        current_status,
        qr_image_url,
        created_at
      FROM items 
      WHERE current_status IN ('pending', 'registered', 'manufactured')
      ORDER BY created_at DESC 
      LIMIT $1
    `;
    
    const result = await client.query(query, [limit]);
    client.release();
    
    console.log(`📋 Fetched ${result.rows.length} items pending engraving`);
    
    return {
      success: true,
      items: result.rows
    };
  } catch (error) {
    console.error('Error fetching pending engravings:', error.message);
    return {
      success: false,
      error: error.message
    };
  }
}

/**
 * Update item status after engraving
 * @param {string} uid - The unique identifier of the item
 * @param {string} status - New status (e.g., 'engraved')
 * @returns {Promise<{success: boolean, error?: string}>}
 */
async function updateItemStatus(uid, status) {
  try {
    const p = initPool();
    const client = await p.connect();
    
    const query = `
      UPDATE items 
      SET current_status = $1, updated_at = NOW() 
      WHERE uid = $2
      RETURNING uid, current_status
    `;
    
    const result = await client.query(query, [status, uid]);
    client.release();
    
    if (result.rows.length === 0) {
      return {
        success: false,
        error: 'Item not found'
      };
    }
    
    console.log(`✅ Updated item ${uid} status to: ${status}`);
    
    return {
      success: true,
      item: result.rows[0]
    };
  } catch (error) {
    console.error('Error updating item status:', error.message);
    return {
      success: false,
      error: error.message
    };
  }
}

/**
 * Record an engraving job in the database
 * @param {object} engravingData - Engraving job details
 * @returns {Promise<{success: boolean, engraving?: object, error?: string}>}
 */
async function recordEngraving(engravingData) {
  try {
    const p = initPool();
    const client = await p.connect();
    
    const { item_uid, operator_id, machine_id, settings, status } = engravingData;
    
    const query = `
      INSERT INTO engravings (item_uid, operator_id, machine_id, settings, status, created_at)
      VALUES ($1, $2, $3, $4, $5, NOW())
      RETURNING *
    `;
    
    const result = await client.query(query, [
      item_uid,
      operator_id || 'gengrav-operator',
      machine_id || 'gengrav-laser-1',
      JSON.stringify(settings || {}),
      status || 'completed'
    ]);
    client.release();
    
    console.log(`📝 Recorded engraving for item: ${item_uid}`);
    
    return {
      success: true,
      engraving: result.rows[0]
    };
  } catch (error) {
    console.error('Error recording engraving:', error.message);
    return {
      success: false,
      error: error.message
    };
  }
}

/**
 * Close the database connection pool
 */
async function closePool() {
  if (pool) {
    await pool.end();
    pool = null;
    console.log('Database pool closed');
  }
}

module.exports = {
  initPool,
  testConnection,
  fetchItems,
  fetchItemByUid,
  fetchPendingEngravings,
  updateItemStatus,
  recordEngraving,
  closePool
};
