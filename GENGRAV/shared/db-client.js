const { Pool } = require('pg');
const path = require('path');

// Try to load .env from multiple locations
const envPaths = [
  path.join(__dirname, '../engraving-app/.env'),  // GENGRAV/engraving-app/.env
  path.join(__dirname, '../../App_a/.env'),        // App_a/.env (fallback)
  path.join(__dirname, '../../.env')               // Root .env (fallback)
];

let envLoaded = false;
for (const envPath of envPaths) {
  try {
    require('dotenv').config({ path: envPath });
    if (process.env.DATABASE_URL) {
      console.log(`✅ Loaded environment from: ${envPath}`);
      envLoaded = true;
      break;
    }
  } catch (e) {
    // Continue to next path
  }
}

if (!envLoaded) {
  console.log('⚠️  No .env file found, using defaults or environment variables');
}

class DatabaseClient {
  constructor() {
    // Use Supabase connection from environment
    const dbUrl = process.env.DATABASE_URL;
    
    if (dbUrl) {
      // Use DATABASE_URL from .env (Supabase connection)
      this.pool = new Pool({
        connectionString: dbUrl,
        ssl: { rejectUnauthorized: false },
        // Settings for Supabase Transaction Pooler
        max: 10,
        idleTimeoutMillis: 30000,
        connectionTimeoutMillis: 30000
      });
      console.log('✅ Using Supabase database connection');
    } else {
      // Fallback to localhost (for development)
      this.pool = new Pool({
        host: 'localhost',
        port: 5433,
        database: 'irf_dev',
        user: 'irf_user',
        password: 'irf_pass'
      });
      console.log('⚠️  Connected to local database');
    }
    
    // Set up error handler to prevent crashes
    this.pool.on('error', (err) => {
      console.error('Database pool error:', err.message);
    });
    
    // Test connection on startup
    this.testConnection();
  }

  async testConnection() {
    try {
      const client = await this.pool.connect();
      const result = await client.query('SELECT NOW() as current_time');
      client.release();
      console.log('✅ Database connection verified at:', result.rows[0].current_time);
      this.connectionTested = true;
      return true;
    } catch (error) {
      console.error('❌ Database connection failed:', error.message);
      return false;
    }
  }

  async query(text, params) {
    let client;
    try {
      client = await this.pool.connect();
      const result = await client.query(text, params);
      return result;
    } catch (error) {
      console.error('Query error:', error.message);
      throw error;
    } finally {
      if (client) {
        client.release();
      }
    }
  }

  async createItem(itemData) {
    const { uid, component_type, lot_number, vendor_id, quantity, warranty_years, manufacture_date, qr_image_url, current_status, metadata } = itemData;
    
    const query = `
      INSERT INTO items (uid, component_type, lot_number, vendor_id, quantity, warranty_years, manufacture_date, qr_image_url, current_status, metadata)
      VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
      RETURNING *
    `;
    
    const values = [uid, component_type, lot_number, vendor_id, quantity, warranty_years, manufacture_date, qr_image_url, current_status, metadata];
    const result = await this.query(query, values);
    return result.rows[0];
  }

  async getItemByUid(uid) {
    const query = 'SELECT * FROM items WHERE uid = $1';
    const result = await this.query(query, [uid]);
    return result.rows[0];
  }

  async getAllItems() {
    const query = 'SELECT * FROM items ORDER BY created_at DESC';
    const result = await this.query(query);
    return result.rows;
  }

  async updateItem(uid, updates) {
    const fields = Object.keys(updates);
    const values = Object.values(updates);
    const setClause = fields.map((field, i) => `${field} = $${i + 2}`).join(', ');
    
    const query = `
      UPDATE items 
      SET ${setClause}, updated_at = NOW()
      WHERE uid = $1
      RETURNING *
    `;
    
    const result = await this.query(query, [uid, ...values]);
    return result.rows[0];
  }

  async createEngravingJob(jobData) {
    const { item_uid, svg_url, max_attempts = 3 } = jobData;
    
    const query = `
      INSERT INTO engraving_queue (item_uid, svg_url, status, attempts, max_attempts)
      VALUES ($1, $2, $3, $4, $5)
      RETURNING *
    `;
    
    const values = [item_uid, svg_url, 'PENDING', 0, max_attempts];
    const result = await this.query(query, values);
    return result.rows[0];
  }

  async getEngravingJob(jobId) {
    const query = 'SELECT * FROM engraving_queue WHERE id = $1';
    const result = await this.query(query, [jobId]);
    return result.rows[0];
  }

  async getEngravingJobByItemUid(itemUid) {
    const query = 'SELECT * FROM engraving_queue WHERE item_uid = $1 ORDER BY created_at DESC LIMIT 1';
    const result = await this.query(query, [itemUid]);
    return result.rows[0];
  }

  async getEngravingJobsByStatus(status) {
    const query = 'SELECT * FROM engraving_queue WHERE status = $1 ORDER BY created_at ASC';
    const result = await this.query(query, [status.toUpperCase()]);
    return result.rows;
  }

  async getPendingEngravingJobs() {
    return await this.getEngravingJobsByStatus('PENDING');
  }

  async updateEngravingJobStatus(jobId, status, errorMessage = null) {
    let query;
    let values;
    const statusUpper = status.toUpperCase();
    
    if (statusUpper === 'IN_PROGRESS') {
      query = `
        UPDATE engraving_queue 
        SET status = $2, started_at = NOW(), error_message = $3
        WHERE id = $1
        RETURNING *
      `;
      values = [jobId, statusUpper, errorMessage];
    } else if (statusUpper === 'COMPLETED') {
      query = `
        UPDATE engraving_queue 
        SET status = $2, completed_at = NOW(), error_message = $3
        WHERE id = $1
        RETURNING *
      `;
      values = [jobId, statusUpper, errorMessage];
    } else {
      query = `
        UPDATE engraving_queue 
        SET status = $2, error_message = $3
        WHERE id = $1
        RETURNING *
      `;
      values = [jobId, statusUpper, errorMessage];
    }
    
    const result = await this.query(query, values);
    
    // Add to history
    await this.addEngravingHistory(jobId, statusUpper, errorMessage);
    
    return result.rows[0];
  }

  async incrementJobAttempts(jobId) {
    const query = `
      UPDATE engraving_queue 
      SET attempts = attempts + 1
      WHERE id = $1
      RETURNING *
    `;
    
    const result = await this.query(query, [jobId]);
    return result.rows[0];
  }

  async addEngravingHistory(jobId, status, message = null) {
    const query = `
      INSERT INTO engraving_history (engraving_job_id, status, message)
      VALUES ($1, $2, $3)
      RETURNING *
    `;
    
    const values = [jobId, status, message];
    const result = await this.query(query, values);
    return result.rows[0];
  }

  async getEngravingHistory(jobId) {
    const query = `
      SELECT * FROM engraving_history 
      WHERE engraving_job_id = $1 
      ORDER BY created_at DESC
    `;
    const result = await this.query(query, [jobId]);
    return result.rows;
  }

  async getItemsWithEngravingStatus() {
    const query = `
      SELECT 
        i.*,
        eq.id as engraving_job_id,
        eq.status as engraving_status,
        eq.attempts,
        eq.created_at as engraving_created_at,
        eq.started_at as engraving_started_at,
        eq.completed_at as engraving_completed_at,
        eq.error_message
      FROM items i
      LEFT JOIN engraving_queue eq ON i.uid = eq.item_uid
      ORDER BY i.created_at DESC
    `;
    const result = await this.query(query);
    return result.rows;
  }

  async close() {
    await this.pool.end();
  }

  // Additional helper methods
  
  // Get items by component_type (since there's no batch_id in the schema)
  async getItemsByComponentType(componentType) {
    const query = 'SELECT * FROM items WHERE component_type = $1 ORDER BY created_at ASC';
    const result = await this.query(query, [componentType]);
    return result.rows;
  }

  // Get items by lot_number (use as batch identifier)
  async getItemsByLotNumber(lotNumber) {
    const query = 'SELECT * FROM items WHERE lot_number = $1 ORDER BY created_at ASC';
    const result = await this.query(query, [lotNumber]);
    return result.rows;
  }

  // Legacy method - alias for getItemsByLotNumber
  async getItemsByBatch(batchId) {
    // Use lot_number as the batch identifier
    return await this.getItemsByLotNumber(batchId.toString());
  }

  // Get item by UID or QR code (uid is the unique identifier)
  async getItemByQRCode(qrCodeOrUid) {
    const query = 'SELECT * FROM items WHERE uid = $1';
    const result = await this.query(query, [qrCodeOrUid]);
    return result.rows[0];
  }

  // Get items that need engraving (not yet in queue)
  async getItemsNeedingEngraving() {
    const query = `
      SELECT i.* FROM items i
      LEFT JOIN engraving_queue eq ON i.uid = eq.item_uid
      WHERE eq.id IS NULL OR (eq.status = 'failed' AND eq.attempts < eq.max_attempts)
      ORDER BY i.created_at ASC
    `;
    const result = await this.query(query);
    return result.rows;
  }

  // Get pending items (manufactured status, not yet engraved)
  async getPendingItems() {
    const query = `
      SELECT * FROM items 
      WHERE current_status = 'manufactured'
      ORDER BY created_at ASC
    `;
    const result = await this.query(query);
    return result.rows;
  }

  // Update item status
  async updateItemStatus(uid, status) {
    const query = `
      UPDATE items 
      SET current_status = $2, updated_at = NOW()
      WHERE uid = $1
      RETURNING *
    `;
    const result = await this.query(query, [uid, status]);
    return result.rows[0];
  }

  // Get engraving statistics
  async getEngravingStats() {
    const query = `
      SELECT 
        COUNT(*) FILTER (WHERE status = 'PENDING') as pending_count,
        COUNT(*) FILTER (WHERE status = 'IN_PROGRESS') as in_progress_count,
        COUNT(*) FILTER (WHERE status = 'COMPLETED') as completed_count,
        COUNT(*) FILTER (WHERE status = 'FAILED') as failed_count,
        COUNT(*) as total_count
      FROM engraving_queue
    `;
    const result = await this.query(query);
    return result.rows[0];
  }

  // Get all unique batch reference IDs
  async getAllBatches() {
    const query = `
      SELECT 
        metadata->>'batch_ref_id' as batch_ref_id,
        component_type,
        lot_number,
        COUNT(*) as qr_count,
        MIN(created_at) as created_at,
        SUM(CASE WHEN current_status = 'engraved' THEN 1 ELSE 0 END) as engraved_count
      FROM items
      WHERE metadata->>'batch_ref_id' IS NOT NULL
      GROUP BY metadata->>'batch_ref_id', component_type, lot_number
      ORDER BY MIN(created_at) DESC
    `;
    const result = await this.query(query);
    return result.rows;
  }

  // Get items by batch reference ID
  async getItemsByBatchRefId(batchRefId) {
    const query = `
      SELECT * FROM items
      WHERE metadata->>'batch_ref_id' = $1
      ORDER BY created_at ASC
    `;
    const result = await this.query(query, [batchRefId]);
    return result.rows;
  }

  // Get batch statistics
  async getBatchStats(batchRefId) {
    const query = `
      SELECT 
        COUNT(*) as total_count,
        COUNT(*) FILTER (WHERE current_status = 'manufactured') as manufactured_count,
        COUNT(*) FILTER (WHERE current_status = 'engraved') as engraved_count,
        COUNT(*) FILTER (WHERE current_status = 'installed') as installed_count,
        component_type,
        lot_number,
        MIN(created_at) as batch_created_at
      FROM items
      WHERE metadata->>'batch_ref_id' = $1
      GROUP BY component_type, lot_number
    `;
    const result = await this.query(query, [batchRefId]);
    return result.rows[0];
  }
}

module.exports = DatabaseClient;
